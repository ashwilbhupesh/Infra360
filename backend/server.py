from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Header, Response
from fastapi.concurrency import run_in_threadpool
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os, uuid, logging, requests, re
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from seed_data import LOCALITIES, PROPERTIES, PRICE_HISTORY, INFRASTRUCTURE, NEWS
from market_seed import MARKET_GROUPS, MARKET_CATEGORIES, SUPPLIERS

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="InfraLocal API")
api_router = APIRouter(prefix="/api")

# ---------------- Object storage ----------------
STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "infralocal"
_storage_key = None

def init_storage():
    global _storage_key
    if _storage_key:
        return _storage_key
    if not EMERGENT_KEY:
        raise RuntimeError("EMERGENT_LLM_KEY not set")
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    _storage_key = resp.json()["storage_key"]
    return _storage_key

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type}, data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()

def get_object(path: str):
    global _storage_key
    key = init_storage()
    resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    if resp.status_code == 503:
        _storage_key = None
        key = init_storage()
        resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

# ---------------- Models ----------------
def now_iso():
    return datetime.now(timezone.utc).isoformat()

class OnboardRequest(BaseModel):
    name: str
    mobile: str
    area: Optional[str] = None

class User(BaseModel):
    id: str
    name: str
    mobile: str
    area: Optional[str] = None
    created_at: str

class PropertyIn(BaseModel):
    title: str
    type: str
    price: float
    area: float
    area_unit: str
    lat: float
    lng: float
    locality_id: str
    address: Optional[str] = ""
    bedrooms: Optional[int] = None
    facing: Optional[str] = None
    road_width_ft: Optional[int] = None
    source: str = "Owner"
    images: List[str] = []
    owner_user_id: Optional[str] = None
    description: Optional[str] = ""

class SaveRequest(BaseModel):
    user_id: str
    property_id: str

class FollowRequest(BaseModel):
    user_id: str
    locality_id: str

# ---------------- Seeding ----------------
async def seed_if_needed():
    if await db.localities.count_documents({}) == 0:
        await db.localities.insert_many([{**l} for l in LOCALITIES])
    if await db.properties.count_documents({}) == 0:
        await db.properties.insert_many([{**p} for p in PROPERTIES])
    if await db.infrastructure.count_documents({}) == 0:
        await db.infrastructure.insert_many([{**i} for i in INFRASTRUCTURE])
    if await db.news.count_documents({}) == 0:
        await db.news.insert_many([{**n} for n in NEWS])
    if await db.price_history.count_documents({}) == 0:
        docs = [{"locality_id": lid, "series": series} for lid, series in PRICE_HISTORY.items()]
        await db.price_history.insert_many(docs)
    if await db.market_groups.count_documents({}) == 0:
        await db.market_groups.insert_many([{**g} for g in MARKET_GROUPS])
    if await db.market_categories.count_documents({}) == 0:
        await db.market_categories.insert_many([{**c} for c in MARKET_CATEGORIES])
    if await db.suppliers.count_documents({}) == 0:
        await db.suppliers.insert_many([{**s} for s in SUPPLIERS])

@app.on_event("startup")
async def on_startup():
    try:
        await seed_if_needed()
    except Exception as e:
        logging.exception("Seed error: %s", e)
    try:
        init_storage()
    except Exception as e:
        logging.exception("Storage init failed: %s", e)

# ---------------- Helpers ----------------
NO_ID = {"_id": 0}

# ---------------- Endpoints ----------------
@api_router.get("/health")
async def health():
    return {"status": "ok", "service": "infralocal"}

# Auth
@api_router.post("/auth/onboard")
async def onboard(req: OnboardRequest):
    mobile = req.mobile.strip()
    if not mobile or len(mobile) < 7:
        raise HTTPException(400, "Invalid mobile")
    existing = await db.users.find_one({"mobile": mobile}, NO_ID)
    if existing:
        # Update name/area if provided
        await db.users.update_one({"mobile": mobile}, {"$set": {"name": req.name, "area": req.area}})
        existing["name"] = req.name
        existing["area"] = req.area
        return {"user": existing}
    uid = str(uuid.uuid4())
    user = {"id": uid, "name": req.name.strip(), "mobile": mobile, "area": req.area, "created_at": now_iso()}
    await db.users.insert_one({**user})
    return {"user": user}

@api_router.get("/auth/me")
async def me(user_id: str):
    u = await db.users.find_one({"id": user_id}, NO_ID)
    if not u:
        raise HTTPException(404, "User not found")
    return u

# Localities
@api_router.get("/localities")
async def list_localities():
    docs = await db.localities.find({}, NO_ID).to_list(500)
    return docs

@api_router.get("/localities/{loc_id}")
async def get_locality(loc_id: str):
    l = await db.localities.find_one({"id": loc_id}, NO_ID)
    if not l:
        raise HTTPException(404, "Locality not found")
    ph = await db.price_history.find_one({"locality_id": loc_id}, NO_ID)
    l["price_history"] = ph["series"] if ph else []
    infra = await db.infrastructure.find({"locality_ids": loc_id}, NO_ID).to_list(200)
    l["infrastructure"] = infra
    news = await db.news.find({"locality_id": loc_id}, NO_ID).sort("date", -1).to_list(20)
    l["news"] = news
    l["properties_count"] = await db.properties.count_documents({"locality_id": loc_id})
    return l

# Properties
@api_router.get("/properties")
async def list_properties(
    type: Optional[str] = None,
    locality_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    bedrooms: Optional[int] = None,
    verified_only: bool = False,
    source: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 100,
):
    query = {}
    if type: query["type"] = type
    if locality_id: query["locality_id"] = locality_id
    if bedrooms is not None: query["bedrooms"] = bedrooms
    if verified_only: query["verified"] = True
    if source: query["source"] = source
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"locality_name": {"$regex": q, "$options": "i"}},
            {"address": {"$regex": q, "$options": "i"}},
        ]
    price_q = {}
    if min_price is not None: price_q["$gte"] = min_price
    if max_price is not None: price_q["$lte"] = max_price
    if price_q: query["price"] = price_q
    docs = await db.properties.find(query, NO_ID).limit(limit).to_list(limit)
    return docs

@api_router.get("/properties/{pid}")
async def get_property(pid: str):
    p = await db.properties.find_one({"id": pid}, NO_ID)
    if not p:
        raise HTTPException(404, "Property not found")
    loc = await db.localities.find_one({"id": p["locality_id"]}, NO_ID)
    p["locality"] = loc
    # InfraValue estimate
    if loc:
        area = p["area"]
        if p["area_unit"] == "sq yd":
            base_low = loc["estimated_range_low"] * area
            base_high = loc["estimated_range_high"] * area
        elif p["area_unit"] == "sq ft":
            # rough: 1 sq yd = 9 sq ft
            base_low = (loc["estimated_range_low"] / 9) * area
            base_high = (loc["estimated_range_high"] / 9) * area
        else:
            base_low = p["price"] * 0.9
            base_high = p["price"] * 1.1
        govt = loc["govt_dlc_per_sq_yd"] * (area if p["area_unit"] == "sq yd" else area / 9 if p["area_unit"] == "sq ft" else area)
        p["infravalue"] = {
            "low": int(base_low),
            "high": int(base_high),
            "confidence": loc["confidence"],
        }
        p["govt_value"] = int(govt)
    return p

@api_router.post("/properties")
async def create_property(prop: PropertyIn):
    loc = await db.localities.find_one({"id": prop.locality_id}, NO_ID)
    if not loc:
        raise HTTPException(400, "Invalid locality")
    pid = f"p-user-{uuid.uuid4().hex[:8]}"
    price_per_unit = round(prop.price / prop.area) if prop.area else 0
    doc = {
        "id": pid,
        "title": prop.title,
        "type": prop.type,
        "price": prop.price,
        "area": prop.area,
        "area_unit": prop.area_unit,
        "price_per_unit": price_per_unit,
        "lat": prop.lat,
        "lng": prop.lng,
        "locality_id": prop.locality_id,
        "locality_name": loc["name"],
        "city": loc["city"],
        "state": loc["state"],
        "address": prop.address or loc["name"],
        "bedrooms": prop.bedrooms,
        "facing": prop.facing,
        "road_width_ft": prop.road_width_ft,
        "source": prop.source,
        "images": prop.images,
        "verified": False,
        "verification_status": "Verification Pending",
        "owner_user_id": prop.owner_user_id,
        "description": prop.description,
        "listed_at": now_iso(),
        "is_demo": False,
    }
    await db.properties.insert_one({**doc})
    return doc

# Infrastructure
@api_router.get("/infrastructure")
async def list_infra(locality_id: Optional[str] = None):
    q = {}
    if locality_id: q["locality_ids"] = locality_id
    docs = await db.infrastructure.find(q, NO_ID).to_list(200)
    return docs

# News
@api_router.get("/news")
async def list_news(locality_id: Optional[str] = None, category: Optional[str] = None, limit: int = 50):
    q = {}
    if locality_id: q["locality_id"] = locality_id
    if category: q["category"] = category
    docs = await db.news.find(q, NO_ID).sort("date", -1).limit(limit).to_list(limit)
    return docs

# Saved / Follows
@api_router.post("/saved/toggle")
async def toggle_save(req: SaveRequest):
    existing = await db.saved.find_one({"user_id": req.user_id, "property_id": req.property_id})
    if existing:
        await db.saved.delete_one({"user_id": req.user_id, "property_id": req.property_id})
        return {"saved": False}
    await db.saved.insert_one({"user_id": req.user_id, "property_id": req.property_id, "created_at": now_iso()})
    return {"saved": True}

@api_router.get("/saved")
async def list_saved(user_id: str):
    saves = await db.saved.find({"user_id": user_id}, NO_ID).to_list(500)
    pids = [s["property_id"] for s in saves]
    props = await db.properties.find({"id": {"$in": pids}}, NO_ID).to_list(500)
    return props

@api_router.post("/follows/toggle")
async def toggle_follow(req: FollowRequest):
    existing = await db.follows.find_one({"user_id": req.user_id, "locality_id": req.locality_id})
    if existing:
        await db.follows.delete_one({"user_id": req.user_id, "locality_id": req.locality_id})
        return {"following": False}
    await db.follows.insert_one({"user_id": req.user_id, "locality_id": req.locality_id, "created_at": now_iso()})
    return {"following": True}

@api_router.get("/follows")
async def list_follows(user_id: str):
    follows = await db.follows.find({"user_id": user_id}, NO_ID).to_list(500)
    lids = [f["locality_id"] for f in follows]
    locs = await db.localities.find({"id": {"$in": lids}}, NO_ID).to_list(500)
    return locs

# Uploads
@api_router.post("/upload")
async def upload_image(file: UploadFile = File(...), user_id: Optional[str] = None):
    data = await file.read()
    ext = (file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "jpg").lower()
    uid = user_id or "anon"
    path = f"{APP_NAME}/uploads/{uid}/{uuid.uuid4().hex}.{ext}"
    try:
        await run_in_threadpool(put_object, path, data, file.content_type or "image/jpeg")
    except requests.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    return {"storage_path": path, "url": f"/api/files/{path}"}

@api_router.get("/files/{path:path}")
async def get_file(path: str):
    try:
        data, ctype = await run_in_threadpool(get_object, path)
    except requests.HTTPError:
        raise HTTPException(404, "File not found")
    return Response(content=data, media_type=ctype)

# ---------------- Market (construction ecosystem) ----------------
@api_router.get("/market/groups")
async def list_market_groups():
    groups = await db.market_groups.find({}, NO_ID).to_list(50)
    cats = await db.market_categories.find({}, NO_ID).to_list(200)
    # attach categories to their group
    by_group: Dict[str, List[dict]] = {}
    for c in cats:
        by_group.setdefault(c["group_id"], []).append(c)
    # supplier counts per category
    sup_counts: Dict[str, int] = {}
    async for s in db.suppliers.find({}, {"category_id": 1, "_id": 0}):
        cid = s.get("category_id")
        if cid:
            sup_counts[cid] = sup_counts.get(cid, 0) + 1
    for c in cats:
        c["suppliers_count"] = sup_counts.get(c["id"], 0)
    for g in groups:
        g["categories"] = by_group.get(g["id"], [])
    return groups

@api_router.get("/market/categories")
async def list_market_categories(group_id: Optional[str] = None):
    q: Dict[str, Any] = {}
    if group_id:
        q["group_id"] = group_id
    cats = await db.market_categories.find(q, NO_ID).to_list(200)
    return cats

@api_router.get("/market/suppliers")
async def list_suppliers(
    category_id: Optional[str] = None,
    group_id: Optional[str] = None,
    q: Optional[str] = None,
    featured_only: bool = False,
    verified_only: bool = False,
    city: Optional[str] = None,
    limit: int = 100,
):
    query: Dict[str, Any] = {}
    if category_id:
        query["category_id"] = category_id
    if group_id:
        # expand to categories in this group
        cat_ids = [c["id"] async for c in db.market_categories.find({"group_id": group_id}, {"id": 1, "_id": 0})]
        query["category_id"] = {"$in": cat_ids}
    if featured_only:
        query["featured"] = True
    if verified_only:
        query["verified"] = True
    if city:
        query["city"] = city
    if q:
        pat = re.escape(q)
        query["$or"] = [
            {"name": {"$regex": pat, "$options": "i"}},
            {"tagline": {"$regex": pat, "$options": "i"}},
            {"offerings": {"$regex": pat, "$options": "i"}},
        ]
    suppliers = await db.suppliers.find(query, NO_ID).limit(limit).to_list(limit)
    return suppliers

@api_router.get("/market/suppliers/{sid}")
async def get_supplier(sid: str):
    s = await db.suppliers.find_one({"id": sid}, NO_ID)
    if not s:
        raise HTTPException(404, "Supplier not found")
    cat = await db.market_categories.find_one({"id": s.get("category_id")}, NO_ID)
    s["category"] = cat
    return s

class QuoteRequest(BaseModel):
    supplier_id: str
    user_id: Optional[str] = None
    name: str
    mobile: str
    message: Optional[str] = None

@api_router.post("/market/quote-requests")
async def create_quote(req: QuoteRequest):
    if not await db.suppliers.find_one({"id": req.supplier_id}, {"_id": 0, "id": 1}):
        raise HTTPException(404, "Supplier not found")
    doc = {
        "id": f"qr-{uuid.uuid4().hex[:10]}",
        "supplier_id": req.supplier_id,
        "user_id": req.user_id,
        "name": req.name,
        "mobile": req.mobile,
        "message": req.message,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "New",
    }
    await db.quote_requests.insert_one(doc)
    return {"id": doc["id"], "status": doc["status"]}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
