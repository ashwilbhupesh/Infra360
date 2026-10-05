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
from materials_seed import MATERIALS_CATEGORIES, MATERIALS_STORES, MATERIALS_PRODUCTS
from agents_seed import AGENT_CATEGORIES, AGENTS
from enrich import with_lifestyle, with_tier

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
    profession: Optional[str] = None

class User(BaseModel):
    id: str
    name: str
    mobile: str
    area: Optional[str] = None
    profession: Optional[str] = None
    dob: Optional[str] = None            # ISO date YYYY-MM-DD
    spouse_dob: Optional[str] = None     # ISO date YYYY-MM-DD
    anniversary: Optional[str] = None    # ISO date YYYY-MM-DD
    created_at: str

class UserDatesUpdate(BaseModel):
    dob: Optional[str] = None
    spouse_dob: Optional[str] = None
    anniversary: Optional[str] = None

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
    else:
        # Backfill: ensure rental properties (r-*) exist and every property has a listing_type
        seed_ids = {p["id"] for p in PROPERTIES}
        existing_ids = set()
        async for x in db.properties.find({"id": {"$in": list(seed_ids)}}, {"id": 1, "_id": 0}):
            existing_ids.add(x["id"])
        missing = [p for p in PROPERTIES if p["id"] not in existing_ids]
        if missing:
            await db.properties.insert_many([{**p} for p in missing])
        # Any legacy record without listing_type is a Buy
        await db.properties.update_many({"listing_type": {"$exists": False}}, {"$set": {"listing_type": "Buy"}})
    if await db.infrastructure.count_documents({}) == 0:
        await db.infrastructure.insert_many([{**i} for i in INFRASTRUCTURE])
    if await db.news.count_documents({}) == 0:
        await db.news.insert_many([{**n} for n in NEWS])
    # Backfill status field on legacy news docs (so they still show up with status=published filter)
    await db.news.update_many({"status": {"$exists": False}}, {"$set": {"status": "published"}})
    # Backfill image on legacy docs that pre-date the image field — pull from the current seed by id
    for n in NEWS:
        if n.get("image"):
            await db.news.update_one({"id": n["id"], "$or": [{"image": {"$exists": False}}, {"image": None}, {"image": ""}]}, {"$set": {"image": n["image"]}})
    if await db.price_history.count_documents({}) == 0:
        docs = [{"locality_id": lid, "series": series} for lid, series in PRICE_HISTORY.items()]
        await db.price_history.insert_many(docs)
    if await db.market_groups.count_documents({}) == 0:
        await db.market_groups.insert_many([{**g} for g in MARKET_GROUPS])
    if await db.market_categories.count_documents({}) == 0:
        await db.market_categories.insert_many([{**c} for c in MARKET_CATEGORIES])
    if await db.suppliers.count_documents({}) == 0:
        await db.suppliers.insert_many([{**s} for s in SUPPLIERS])
    if await db.agent_categories.count_documents({}) == 0:
        await db.agent_categories.insert_many([{**c} for c in AGENT_CATEGORIES])
    if await db.agents.count_documents({}) == 0:
        await db.agents.insert_many([{**a} for a in AGENTS])
    # Materials shopping ecosystem (new) - re-sync on every startup so edits propagate
    await db.materials_categories.delete_many({})
    await db.materials_categories.insert_many([{**c} for c in MATERIALS_CATEGORIES])
    await db.materials_stores.delete_many({})
    await db.materials_stores.insert_many([{**s} for s in MATERIALS_STORES])
    await db.materials_products.delete_many({})
    await db.materials_products.insert_many([{**p} for p in MATERIALS_PRODUCTS])

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

# Deterministic broker/lister picker: source -> agent category, hash by pid
_SOURCE_TO_CAT = {
    "Owner": None,       # Owners aren't agents; we'll fabricate a lister
    "Broker": "acat-broker",
    "Developer": "acat-broker",
}

async def pick_lister(prop: dict) -> dict:
    """Return a deterministic 'listed by' contact for a property."""
    pid = prop.get("id", "")
    source = prop.get("source", "Owner")
    if source == "Owner":
        # Owner: synthesize a contact from property id (demo)
        digits = "".join([c for c in pid if c.isdigit()]) or "00"
        phone = f"+91 98290 44{int(digits[-2:]):02d}0"
        return {
            "type": "Owner",
            "name": "Owner (Direct)",
            "firm": None,
            "phone": phone,
            "whatsapp": phone,
            "agent_id": None,
            "rera_id": None,
            "verified": False,
            "image": None,
        }
    # Broker/Developer: pick one from acat-broker deterministically
    brokers = [a for a in AGENTS if a["category_id"] == "acat-broker"]
    if not brokers:
        return {"type": source, "name": "Listed by broker", "phone": None, "whatsapp": None}
    idx = sum(ord(c) for c in pid) % len(brokers)
    a = brokers[idx]
    return {
        "type": source,
        "name": a["name"],
        "firm": a.get("firm"),
        "phone": a["phone"],
        "whatsapp": a.get("whatsapp") or a["phone"],
        "agent_id": a["id"],
        "rera_id": a.get("rera_id"),
        "verified": a.get("verified", False),
        "image": a.get("image"),
    }

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
        # Update mutable fields only if provided
        update: Dict[str, Any] = {"name": req.name}
        if req.area is not None:
            update["area"] = req.area
        if req.profession is not None:
            update["profession"] = req.profession
        await db.users.update_one({"mobile": mobile}, {"$set": update})
        existing.update(update)
        return {"user": existing}
    uid = str(uuid.uuid4())
    user = {
        "id": uid,
        "name": req.name.strip(),
        "mobile": mobile,
        "area": req.area,
        "profession": req.profession,
        "created_at": now_iso(),
    }
    await db.users.insert_one({**user})
    return {"user": user}

@api_router.get("/auth/me")
async def me(user_id: str):
    u = await db.users.find_one({"id": user_id}, NO_ID)
    if not u:
        raise HTTPException(404, "User not found")
    return u


def _validate_date(s: Optional[str]) -> Optional[str]:
    """Validate YYYY-MM-DD; return the string or raise."""
    if s is None or s == "":
        return None
    try:
        d = datetime.strptime(s, "%Y-%m-%d").date()
        if d.year < 1900 or d.year > datetime.now().year + 1:
            raise ValueError()
        return s
    except Exception:
        raise HTTPException(400, f"Invalid date: {s}. Use YYYY-MM-DD.")


@api_router.put("/users/{user_id}/dates")
async def update_user_dates(user_id: str, req: UserDatesUpdate):
    """Update birth / spouse birth / anniversary dates for personalised reminders."""
    u = await db.users.find_one({"id": user_id}, NO_ID)
    if not u:
        raise HTTPException(404, "User not found")
    # Build $set with only provided fields; empty string clears the field
    update: Dict[str, Any] = {}
    for field, value in [("dob", req.dob), ("spouse_dob", req.spouse_dob), ("anniversary", req.anniversary)]:
        if value is None:
            continue
        if value == "":
            update[field] = None
        else:
            update[field] = _validate_date(value)
    if not update:
        return u
    await db.users.update_one({"id": user_id}, {"$set": update})
    u.update(update)
    return u

# Localities
@api_router.get("/localities")
async def list_localities():
    docs = await db.localities.find({}, NO_ID).to_list(500)
    return [with_lifestyle(d) for d in docs]

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
    return with_lifestyle(l)

# Properties
@api_router.get("/properties")
async def list_properties(
    type: Optional[str] = None,
    listing_type: Optional[str] = None,
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
    if listing_type: query["listing_type"] = listing_type
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
    # Attach a "listed by" agent deterministically
    p["lister"] = await pick_lister(p)
    return p

@api_router.get("/properties/{pid}/similar")
async def similar_properties(pid: str, limit: int = 6):
    p = await db.properties.find_one({"id": pid}, NO_ID)
    if not p:
        raise HTTPException(404, "Property not found")
    price = p["price"]
    lo, hi = price * 0.6, price * 1.6
    q = {
        "id": {"$ne": pid},
        "type": p["type"],
        "listing_type": p.get("listing_type", "Buy"),
        "price": {"$gte": lo, "$lte": hi},
    }
    # Prefer same locality first
    same = await db.properties.find({**q, "locality_id": p["locality_id"]}, NO_ID).limit(limit).to_list(limit)
    if len(same) >= limit:
        return same
    remaining = limit - len(same)
    seen_ids = {x["id"] for x in same}
    others = await db.properties.find({**q, "id": {"$nin": list(seen_ids) + [pid]}}, NO_ID).limit(remaining).to_list(remaining)
    return same + others

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
async def list_news(
    locality_id: Optional[str] = None,
    category: Optional[str] = None,
    q: Optional[str] = None,
    status: str = "published",   # default: only published; use "pending"/"all" for admin review
    limit: int = 50,
):
    query: Dict[str, Any] = {}
    if status and status != "all":
        query["status"] = status
    if locality_id: query["locality_id"] = locality_id
    if category: query["category"] = category
    if q:
        pat = re.escape(q)
        query["$or"] = [
            {"title":   {"$regex": pat, "$options": "i"}},
            {"summary": {"$regex": pat, "$options": "i"}},
        ]
    docs = await db.news.find(query, NO_ID).sort("date", -1).limit(limit).to_list(limit)
    # Attach locality name for display
    if docs:
        loc_ids = list({d.get("locality_id") for d in docs if d.get("locality_id")})
        if loc_ids:
            locs = await db.localities.find({"id": {"$in": loc_ids}}, {"_id": 0, "id": 1, "name": 1}).to_list(100)
            lmap = {l["id"]: l["name"] for l in locs}
            for d in docs:
                d["locality_name"] = lmap.get(d.get("locality_id"))
    return docs


class NewsSubmission(BaseModel):
    title: str
    summary: str
    category: str
    locality_id: Optional[str] = None
    image: Optional[str] = None
    source: Optional[str] = "Reader submission"
    submitted_by: Optional[str] = None  # user_id


@api_router.post("/news/submit")
async def submit_news(req: NewsSubmission):
    """Reader-submitted news. Goes to 'pending' until an admin approves it."""
    title = req.title.strip()
    summary = req.summary.strip()
    if len(title) < 6:
        raise HTTPException(400, "Title too short")
    if len(summary) < 20:
        raise HTTPException(400, "Summary too short — share more context")
    doc = {
        "id": f"n-sub-{uuid.uuid4().hex[:10]}",
        "title": title,
        "summary": summary,
        "category": req.category or "Development",
        "locality_id": req.locality_id,
        "image": (req.image or "").strip() or None,
        "source": (req.source or "Reader submission").strip(),
        "date": now_iso().split("T")[0],
        "status": "pending",
        "submitted_by": req.submitted_by,
        "submitted_at": now_iso(),
    }
    await db.news.insert_one({**doc})
    return {k: v for k, v in doc.items() if k != "_id"}


@api_router.get("/news/mine")
async def list_my_submissions(user_id: str):
    docs = await db.news.find({"submitted_by": user_id}, NO_ID).sort("submitted_at", -1).to_list(100)
    return docs


class ReviewDecision(BaseModel):
    decision: str  # "approve" | "reject"
    admin_token: Optional[str] = None


@api_router.post("/news/{nid}/review")
async def review_submission(nid: str, req: ReviewDecision):
    """Admin reviews a pending submission. Simple shared-secret token guard for the MVP."""
    expected = os.environ.get("ADMIN_TOKEN", "infrajagat-admin")
    if (req.admin_token or "") != expected:
        raise HTTPException(403, "Not authorised")
    n = await db.news.find_one({"id": nid}, NO_ID)
    if not n:
        raise HTTPException(404, "Submission not found")
    new_status = "published" if req.decision == "approve" else "rejected"
    await db.news.update_one({"id": nid}, {"$set": {"status": new_status, "reviewed_at": now_iso()}})
    n["status"] = new_status
    return n

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

# ---------------- Supplier reviews ----------------
class ReviewRequest(BaseModel):
    user_id: Optional[str] = None
    name: str
    rating: int
    text: Optional[str] = None

@api_router.get("/market/suppliers/{sid}/reviews")
async def list_reviews(sid: str):
    if not await db.suppliers.find_one({"id": sid}, {"_id": 0, "id": 1}):
        raise HTTPException(404, "Supplier not found")
    revs = await db.supplier_reviews.find({"supplier_id": sid}, NO_ID).sort("created_at", -1).to_list(100)
    return revs

@api_router.post("/market/suppliers/{sid}/reviews")
async def add_review(sid: str, req: ReviewRequest):
    if not await db.suppliers.find_one({"id": sid}, {"_id": 0, "id": 1}):
        raise HTTPException(404, "Supplier not found")
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(400, "Rating must be 1-5")
    if not req.name.strip():
        raise HTTPException(400, "Name required")
    doc = {
        "id": f"rev-{uuid.uuid4().hex[:10]}",
        "supplier_id": sid,
        "user_id": req.user_id,
        "name": req.name.strip()[:60],
        "rating": req.rating,
        "text": (req.text or "").strip()[:500] or None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.supplier_reviews.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}

# ---------------- Heatmap ----------------
@api_router.get("/heatmap")
async def heatmap():
    """Return locality centres with normalised price intensity [0..1]."""
    locs = await db.localities.find({}, NO_ID).to_list(200)
    if not locs:
        return []
    prices = [l["median_price_per_sq_yd"] for l in locs]
    lo, hi = min(prices), max(prices)
    span = (hi - lo) or 1
    out = []
    for l in locs:
        intensity = (l["median_price_per_sq_yd"] - lo) / span
        out.append({
            "id": l["id"],
            "name": l["name"],
            "lat": l["lat"],
            "lng": l["lng"],
            "median_price_per_sq_yd": l["median_price_per_sq_yd"],
            "govt_dlc_per_sq_yd": l["govt_dlc_per_sq_yd"],
            "intensity": round(intensity, 3),
        })
    return {"min": lo, "max": hi, "points": out}

# ---------------- Agents ----------------
@api_router.get("/agent-categories")
async def list_agent_categories():
    cats = await db.agent_categories.find({}, NO_ID).to_list(50)
    counts: Dict[str, int] = {}
    async for a in db.agents.find({}, {"category_id": 1, "_id": 0}):
        cid = a.get("category_id")
        if cid:
            counts[cid] = counts.get(cid, 0) + 1
    for c in cats:
        c["agents_count"] = counts.get(c["id"], 0)
    return cats

@api_router.get("/agents")
async def list_agents(
    category_id: Optional[str] = None,
    q: Optional[str] = None,
    verified_only: bool = False,
    featured_only: bool = False,
    area: Optional[str] = None,
    limit: int = 100,
):
    query: Dict[str, Any] = {}
    if category_id:
        query["category_id"] = category_id
    if verified_only:
        query["verified"] = True
    if featured_only:
        query["featured"] = True
    if area:
        query["$or"] = [
            {"area": {"$regex": re.escape(area), "$options": "i"}},
            {"coverage": {"$regex": re.escape(area), "$options": "i"}},
        ]
    if q:
        pat = re.escape(q)
        query.setdefault("$and", []).append({
            "$or": [
                {"name": {"$regex": pat, "$options": "i"}},
                {"firm": {"$regex": pat, "$options": "i"}},
                {"specialties": {"$regex": pat, "$options": "i"}},
                {"coverage": {"$regex": pat, "$options": "i"}},
            ]
        })
    docs = await db.agents.find(query, NO_ID).limit(limit).to_list(limit)
    return [with_tier(d) for d in docs]

@api_router.get("/agents/{aid}")
async def get_agent(aid: str):
    a = await db.agents.find_one({"id": aid}, NO_ID)
    if not a:
        raise HTTPException(404, "Agent not found")
    cat = await db.agent_categories.find_one({"id": a.get("category_id")}, NO_ID)
    a["category"] = cat
    # attach recent listings for property brokers / land agents
    if a.get("category_id") in ("acat-broker", "acat-land"):
        listings: List[dict] = []
        # Naive match: properties in agent's coverage areas
        cov = a.get("coverage") or []
        for area in cov[:3]:
            docs = await db.properties.find({"address": {"$regex": re.escape(area), "$options": "i"}}, NO_ID).limit(3).to_list(3)
            listings.extend(docs)
        # dedupe
        seen = set()
        uniq = []
        for p in listings:
            if p["id"] not in seen:
                seen.add(p["id"])
                uniq.append(p)
        a["recent_listings"] = uniq[:6]
    return with_tier(a)

class AgentEnquiry(BaseModel):
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    name: str
    mobile: str
    message: Optional[str] = None

@api_router.post("/agents/{aid}/enquiries")
async def create_agent_enquiry(aid: str, req: AgentEnquiry):
    if not await db.agents.find_one({"id": aid}, {"_id": 0, "id": 1}):
        raise HTTPException(404, "Agent not found")
    if len(req.mobile.strip()) < 10:
        raise HTTPException(400, "Invalid mobile")
    doc = {
        "id": f"aen-{uuid.uuid4().hex[:10]}",
        "agent_id": aid,
        "user_id": req.user_id,
        "name": req.name.strip(),
        "mobile": req.mobile.strip(),
        "message": (req.message or "").strip() or None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "New",
    }
    await db.agent_enquiries.insert_one(doc)
    return {"id": doc["id"], "status": doc["status"]}

# ---------------- Compare ----------------
@api_router.get("/compare")
async def compare_properties(ids: str):
    """Return full property payload (with infravalue + govt + lister + locality lifestyle/YoY) for up to 4 comma-separated ids."""
    id_list = [x.strip() for x in ids.split(",") if x.strip()][:4]
    if not id_list:
        return []
    results: List[dict] = []
    for pid in id_list:
        try:
            r = await get_property(pid)  # reuse existing endpoint
            # Attach lifestyle & yoy from the property's locality for richer compare
            loc = await db.localities.find_one({"id": r.get("locality_id")}, NO_ID)
            if loc:
                r["lifestyle"] = loc.get("lifestyle")
                r["yoy_change_pct"] = loc.get("yoy_change_pct")
            results.append(r)
        except HTTPException:
            continue
    return results

# ---------------- Materials (shopping-style catalogue) ----------------
@api_router.get("/materials/categories")
async def list_materials_categories():
    """10 shopping categories for the Materials section, with store counts."""
    cats = await db.materials_categories.find({}, NO_ID).sort("order", 1).to_list(100)
    # count stores per category
    counts: Dict[str, int] = {}
    async for s in db.materials_stores.find({}, {"category_ids": 1, "_id": 0}):
        for cid in s.get("category_ids", []):
            counts[cid] = counts.get(cid, 0) + 1
    for c in cats:
        c["stores_count"] = counts.get(c["id"], 0)
    return cats


@api_router.get("/materials/categories/{cid}/stores")
async def list_materials_stores_in_category(cid: str):
    """Return stores selling in this category, each with their product catalogue for this category."""
    stores = await db.materials_stores.find({"category_ids": cid}, NO_ID).to_list(200)
    out = []
    for s in stores:
        prods = await db.materials_products.find(
            {"store_id": s["id"], "category_id": cid}, NO_ID
        ).to_list(200)
        out.append({**s, "products": prods, "products_count": len(prods)})
    # Featured first, then by rating
    out.sort(key=lambda x: (-int(x.get("featured", False)), -x.get("rating", 0)))
    return out


@api_router.get("/materials/stores/{sid}")
async def get_materials_store(sid: str):
    """Full store detail with ALL products grouped by category."""
    s = await db.materials_stores.find_one({"id": sid}, NO_ID)
    if not s:
        raise HTTPException(404, "Store not found")
    prods = await db.materials_products.find({"store_id": sid}, NO_ID).to_list(500)
    # group by category
    cat_map: Dict[str, List[dict]] = {}
    for p in prods:
        cat_map.setdefault(p["category_id"], []).append(p)
    cats = await db.materials_categories.find(
        {"id": {"$in": s.get("category_ids", [])}}, NO_ID
    ).to_list(100)
    s["catalogue"] = [{"category": c, "products": cat_map.get(c["id"], [])} for c in cats]
    s["products_count"] = len(prods)
    return s


@api_router.get("/materials/products")
async def search_materials_products(q: Optional[str] = None, category_id: Optional[str] = None, limit: int = 60):
    query: Dict[str, Any] = {}
    if category_id:
        query["category_id"] = category_id
    if q:
        pat = re.escape(q)
        query["$or"] = [
            {"name": {"$regex": pat, "$options": "i"}},
            {"brand": {"$regex": pat, "$options": "i"}},
        ]
    prods = await db.materials_products.find(query, NO_ID).limit(limit).to_list(limit)
    # attach store info
    sids = list({p["store_id"] for p in prods})
    stores = await db.materials_stores.find(
        {"id": {"$in": sids}}, {"_id": 0, "id": 1, "name": 1, "area": 1, "rating": 1, "verified": 1}
    ).to_list(200)
    smap = {s["id"]: s for s in stores}
    for p in prods:
        p["store"] = smap.get(p["store_id"])
    return prods


class MaterialsCartItem(BaseModel):
    product_id: str
    store_id: str
    qty: int = 1


class MaterialsCartEnquiry(BaseModel):
    user_id: Optional[str] = None
    name: str
    mobile: str
    address: Optional[str] = None
    note: Optional[str] = None
    items: List[MaterialsCartItem]


@api_router.post("/materials/cart-enquiry")
async def create_cart_enquiry(req: MaterialsCartEnquiry):
    if not req.items:
        raise HTTPException(400, "Cart is empty")
    if len(req.mobile.strip()) < 10:
        raise HTTPException(400, "Invalid mobile")
    # Expand items with product + store info
    product_ids = [i.product_id for i in req.items]
    products = await db.materials_products.find({"id": {"$in": product_ids}}, NO_ID).to_list(500)
    pmap = {p["id"]: p for p in products}
    store_ids = list({i.store_id for i in req.items})
    stores = await db.materials_stores.find({"id": {"$in": store_ids}}, NO_ID).to_list(200)
    smap = {s["id"]: s for s in stores}
    # per-store subtotal
    per_store: Dict[str, Dict[str, Any]] = {}
    total = 0
    for it in req.items:
        p = pmap.get(it.product_id)
        if not p:
            continue
        subtotal = p["price"] * it.qty
        total += subtotal
        bucket = per_store.setdefault(it.store_id, {
            "store": smap.get(it.store_id),
            "items": [],
            "subtotal": 0,
        })
        bucket["items"].append({
            "product_id": p["id"], "name": p["name"], "brand": p.get("brand"),
            "image": p.get("image"), "unit": p.get("unit"), "price": p["price"],
            "qty": it.qty, "line_total": subtotal,
        })
        bucket["subtotal"] += subtotal
    doc = {
        "id": f"mce-{uuid.uuid4().hex[:10]}",
        "user_id": req.user_id,
        "name": req.name.strip(),
        "mobile": req.mobile.strip(),
        "address": (req.address or "").strip() or None,
        "note": (req.note or "").strip() or None,
        "items": [i.model_dump() for i in req.items],
        "per_store": list(per_store.values()),
        "total": total,
        "status": "New",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.materials_cart_enquiries.insert_one({**doc})
    return {k: v for k, v in doc.items() if k != "_id"}


# ---------------- User activity (Orders / Enquiries / History) ----------------
@api_router.get("/user/{uid}/activity")
async def user_activity(uid: str):
    u = await db.users.find_one({"id": uid}, NO_ID)
    if not u:
        raise HTTPException(404, "User not found")
    # Saved properties -- enrich with property snapshot
    saved_docs = await db.saved.find({"user_id": uid}, NO_ID).sort("created_at", -1).to_list(200)
    saved = []
    for s in saved_docs:
        p = await db.properties.find_one({"id": s.get("property_id")}, {"_id": 0, "id": 1, "title": 1, "price": 1, "images": 1, "type": 1, "listing_type": 1, "address": 1})
        saved.append({**s, "property": p})
    # Follows -- enrich with locality snapshot
    follow_docs = await db.follows.find({"user_id": uid}, NO_ID).sort("created_at", -1).to_list(200)
    follows = []
    for f in follow_docs:
        l = await db.localities.find_one({"id": f.get("locality_id")}, {"_id": 0, "id": 1, "name": 1, "city": 1, "image": 1, "median_price_per_sq_yd": 1, "yoy_change_pct": 1})
        follows.append({**f, "locality": l})
    my_listings = await db.properties.find({"owner_user_id": uid}, NO_ID).sort("listed_at", -1).to_list(200)
    quote_requests = await db.quote_requests.find({"user_id": uid}, NO_ID).sort("created_at", -1).to_list(200)
    for qr in quote_requests:
        sup = await db.suppliers.find_one({"id": qr.get("supplier_id")}, {"_id": 0, "name": 1, "image": 1, "category_id": 1})
        qr["supplier"] = sup
    agent_enquiries = await db.agent_enquiries.find({"user_id": uid}, NO_ID).sort("created_at", -1).to_list(200)
    for ae in agent_enquiries:
        a = await db.agents.find_one({"id": ae.get("agent_id")}, {"_id": 0, "name": 1, "image": 1, "firm": 1})
        ae["agent"] = a
    materials_orders = await db.materials_cart_enquiries.find({"user_id": uid}, NO_ID).sort("created_at", -1).to_list(200)
    return {
        "saved": saved,
        "follows": follows,
        "my_listings": my_listings,
        "quote_requests": quote_requests,
        "agent_enquiries": agent_enquiries,
        "materials_orders": materials_orders,
    }

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
