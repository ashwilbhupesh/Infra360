from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Header, Response
from fastapi.concurrency import run_in_threadpool
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os, uuid, logging, requests, re
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import math

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
    # Deterministic demo seeding: mark ~15% of properties "featured" so the UI reads live.
    featured_ids = ["p-02", "p-07", "p-10", "p-15", "p-20", "b-01", "b-03", "r-02"]
    far_future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    await db.properties.update_many({"id": {"$in": featured_ids}}, {"$set": {"featured": True, "featured_until": far_future, "featured_tier": "basic"}})
    await db.properties.update_many({"featured": {"$exists": False}}, {"$set": {"featured": False}})
    await db.properties.update_many({"verification_status": {"$exists": False}}, {"$set": {"verification_status": "Not Submitted"}})
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
    # Agent categories/agents — re-sync on every startup so seed edits propagate (new finance category etc.)
    await db.agent_categories.delete_many({})
    await db.agent_categories.insert_many([{**c} for c in AGENT_CATEGORIES])
    await db.agents.delete_many({})
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
    featured_only: bool = False,
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
    if featured_only: query["featured"] = True
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
    # Featured first (lead-based placement), then newest/listed_at desc
    docs = await db.properties.find(query, NO_ID).sort([("featured", -1), ("listed_at", -1)]).limit(limit).to_list(limit)
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
    address: Optional[str] = None       # detailed free-text address
    locality_id: Optional[str] = None   # optional - auto-classified from address if not given
    image: Optional[str] = None
    source: Optional[str] = "Reader submission"
    submitted_by: Optional[str] = None  # user_id


async def _classify_locality_from_address(address: str) -> Optional[str]:
    """Light-touch classifier: look up every locality name/alias in the address text (case-insensitive)."""
    if not address or not address.strip():
        return None
    hay = address.lower()
    locs = await db.localities.find({}, {"_id": 0, "id": 1, "name": 1, "aliases": 1}).to_list(200)
    # Prefer longer matches first
    def tokens_for(l):
        toks = [l.get("name", "")] + list(l.get("aliases") or [])
        return [t for t in toks if t]
    scored = []
    for l in locs:
        for t in tokens_for(l):
            t_low = t.lower()
            if t_low and t_low in hay:
                scored.append((len(t_low), l["id"]))
                break
    if not scored:
        return None
    scored.sort(reverse=True)
    return scored[0][1]


@api_router.post("/news/submit")
async def submit_news(req: NewsSubmission):
    """Reader-submitted news. Goes to 'pending' until an admin approves it.
    The sub-area is auto-classified from the free-text address so users don't have to pick."""
    title = req.title.strip()
    summary = req.summary.strip()
    if len(title) < 6:
        raise HTTPException(400, "Title too short")
    if len(summary) < 20:
        raise HTTPException(400, "Summary too short — share more context")
    address = (req.address or "").strip() or None
    locality_id = req.locality_id or (await _classify_locality_from_address(address or ""))
    doc = {
        "id": f"n-sub-{uuid.uuid4().hex[:10]}",
        "title": title,
        "summary": summary,
        "category": req.category or "Development",
        "address": address,
        "locality_id": locality_id,
        "image": (req.image or "").strip() or None,
        "source": (req.source or "Reader submission").strip(),
        "date": now_iso().split("T")[0],
        "status": "pending",
        "submitted_by": req.submitted_by,
        "submitted_at": now_iso(),
    }
    await db.news.insert_one({**doc})
    return {k: v for k, v in doc.items() if k != "_id"}


@api_router.get("/news/classify-locality")
async def classify_locality(address: str):
    lid = await _classify_locality_from_address(address)
    if lid:
        loc = await db.localities.find_one({"id": lid}, {"_id": 0, "id": 1, "name": 1})
        return {"locality_id": lid, "name": loc.get("name") if loc else None}
    return {"locality_id": None, "name": None}


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


# ---------------- Materials orders (checkout + payment + delivery tracking) ----------------
class MaterialsOrderRequest(BaseModel):
    user_id: Optional[str] = None
    name: str
    mobile: str
    address: str
    note: Optional[str] = None
    payment_method: str  # "upi" | "card" | "cod"
    payment_ref: Optional[str] = None  # mock txn id for upi/card
    items: List[MaterialsCartItem]


# Reasonable store pickup coords (approximate Jaipur neighbourhoods)
_STORE_COORDS = {
    "mst-balaji": (26.9015, 75.7250),
    "mst-steelsynd": (26.9550, 75.7900),
    "mst-rajcement": (26.9550, 75.7900),
    "mst-voltronics": (26.9240, 75.8230),
    "mst-signify": (26.9120, 75.8200),
    "mst-havells": (26.9050, 75.7520),
    "mst-jaquar": (26.8980, 75.8000),
    "mst-cera": (26.8520, 75.8120),
    "mst-hindware": (26.8850, 75.8160),
    "mst-marblemosaic": (26.8520, 75.8120),
    "mst-laticrete": (26.7850, 75.8540),
    "mst-colourworks": (26.9120, 75.8500),
    "mst-asianpaints": (26.9100, 75.8020),
    "mst-crompton": (26.8550, 75.7580),
    "mst-bajaj": (26.9050, 75.7520),
    "mst-drfixit": (26.9280, 75.7050),
    "mst-fosroc": (26.9550, 75.7900),
    "mst-astral": (26.8850, 75.8160),
    "mst-prince": (26.9240, 75.8230),
    "mst-dorset": (26.9120, 75.8200),
    "mst-hettich": (26.8520, 75.8120),
    "mst-godrejlock": (26.9120, 75.8500),
    "mst-greenply": (26.7850, 75.8540),
    "mst-century": (26.8050, 75.8150),
    "mst-merino": (26.9100, 75.8020),
}
_DEFAULT_DROP = (26.8891, 75.7500)  # Jaipur city centre as mock drop


def _mk_waypoints(start, end, n=6):
    """n intermediate points incl. start & end for a straight-line interpolation."""
    (lat1, lng1), (lat2, lng2) = start, end
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append({"lat": lat1 + (lat2 - lat1) * t, "lng": lng1 + (lng2 - lng1) * t})
    return pts


@api_router.post("/materials/orders")
async def create_materials_order(req: MaterialsOrderRequest):
    """Checkout endpoint. Creates one order per store (so each shipment is tracked separately)."""
    if not req.items:
        raise HTTPException(400, "Cart is empty")
    if len(req.mobile.strip()) < 10:
        raise HTTPException(400, "Invalid mobile")
    if req.payment_method not in ("upi", "card", "cod"):
        raise HTTPException(400, "Invalid payment method")
    if len(req.address.strip()) < 8:
        raise HTTPException(400, "Please provide a complete delivery address")

    # Expand items with product info
    product_ids = [i.product_id for i in req.items]
    products = await db.materials_products.find({"id": {"$in": product_ids}}, NO_ID).to_list(500)
    pmap = {p["id"]: p for p in products}

    # Group items by store
    per_store: Dict[str, Dict[str, Any]] = {}
    for it in req.items:
        p = pmap.get(it.product_id)
        if not p:
            continue
        subtotal = p["price"] * it.qty
        bucket = per_store.setdefault(it.store_id, {"items": [], "subtotal": 0})
        bucket["items"].append({
            "product_id": p["id"], "name": p["name"], "brand": p.get("brand"),
            "image": p.get("image"), "unit": p.get("unit"), "price": p["price"],
            "qty": it.qty, "line_total": subtotal,
        })
        bucket["subtotal"] += subtotal

    stores = await db.materials_stores.find({"id": {"$in": list(per_store.keys())}}, NO_ID).to_list(200)
    smap = {s["id"]: s for s in stores}

    paid_status = "paid" if req.payment_method in ("upi", "card") else "cod_pending"
    now = datetime.now(timezone.utc)

    orders_out = []
    group_id = f"mg-{uuid.uuid4().hex[:8]}"
    for store_id, bucket in per_store.items():
        store = smap.get(store_id, {})
        pickup = _STORE_COORDS.get(store_id, _DEFAULT_DROP)
        waypoints = _mk_waypoints(pickup, _DEFAULT_DROP, n=8)
        eta_mins = int((store.get("delivery_mins") or 90))
        oid = f"mo-{uuid.uuid4().hex[:10]}"
        doc = {
            "id": oid,
            "group_id": group_id,
            "user_id": req.user_id,
            "name": req.name.strip(),
            "mobile": req.mobile.strip(),
            "address": req.address.strip(),
            "note": (req.note or "").strip() or None,
            "payment_method": req.payment_method,
            "payment_status": paid_status,
            "payment_ref": req.payment_ref,
            "store": {"id": store.get("id"), "name": store.get("name"), "phone": store.get("phone"), "area": store.get("area"), "image": store.get("image")},
            "items": bucket["items"],
            "subtotal": bucket["subtotal"],
            "delivery_fee": 0 if bucket["subtotal"] >= 2500 else 99,
            "total": bucket["subtotal"] + (0 if bucket["subtotal"] >= 2500 else 99),
            "pickup": {"lat": pickup[0], "lng": pickup[1]},
            "drop": {"lat": _DEFAULT_DROP[0], "lng": _DEFAULT_DROP[1]},
            "waypoints": waypoints,
            "eta_mins": eta_mins,
            "status": "picked_up",   # picked_up -> en_route -> nearby -> delivered
            "status_history": [
                {"status": "placed", "at": now.isoformat()},
                {"status": "picked_up", "at": now.isoformat()},
            ],
            "created_at": now.isoformat(),
        }
        await db.materials_orders.insert_one({**doc})
        orders_out.append({k: v for k, v in doc.items() if k != "_id"})
    return {"group_id": group_id, "orders": orders_out, "total": sum(o["total"] for o in orders_out)}


def _progress_for(order: dict) -> dict:
    """Compute delivery progress from elapsed time + eta_mins. Mock-only."""
    try:
        created = datetime.fromisoformat(order["created_at"])
    except Exception:
        created = datetime.now(timezone.utc)
    elapsed_s = (datetime.now(timezone.utc) - created).total_seconds()
    # Compress real time into the demo: 1 real minute = ~eta_mins * 10 virtual seconds, so a 90-min delivery completes in ~9 real minutes
    virtual_mins = elapsed_s / 60.0 * 10.0
    pct = max(0.0, min(1.0, virtual_mins / max(1, order.get("eta_mins", 60))))
    wps = order.get("waypoints") or []
    if not wps:
        return {"pct": pct, "driver": order.get("pickup"), "status": "picked_up", "mins_left": order.get("eta_mins", 60)}
    idx = min(int(pct * (len(wps) - 1)), len(wps) - 1)
    driver = wps[idx]
    status = (
        "delivered" if pct >= 1.0 else
        "nearby" if pct >= 0.8 else
        "en_route" if pct >= 0.2 else
        "picked_up"
    )
    mins_left = max(0, int(order.get("eta_mins", 60) * (1 - pct)))
    return {"pct": pct, "driver": driver, "status": status, "mins_left": mins_left}


@api_router.get("/materials/orders/{oid}")
async def get_materials_order(oid: str):
    o = await db.materials_orders.find_one({"id": oid}, NO_ID)
    if not o:
        raise HTTPException(404, "Order not found")
    prog = _progress_for(o)
    # Append new status to history if moved forward
    if prog["status"] != o.get("status"):
        await db.materials_orders.update_one(
            {"id": oid},
            {"$set": {"status": prog["status"]}, "$push": {"status_history": {"status": prog["status"], "at": datetime.now(timezone.utc).isoformat()}}},
        )
        o["status"] = prog["status"]
    o["driver_pos"] = prog["driver"]
    o["pct"] = prog["pct"]
    o["mins_left"] = prog["mins_left"]
    return o


@api_router.get("/materials/orders")
async def list_materials_orders(user_id: str, limit: int = 20):
    orders = await db.materials_orders.find({"user_id": user_id}, NO_ID).sort("created_at", -1).limit(limit).to_list(limit)
    for o in orders:
        prog = _progress_for(o)
        o["status"] = prog["status"]
        o["mins_left"] = prog["mins_left"]
    return orders


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
    materials_orders = await db.materials_orders.find({"user_id": uid}, NO_ID).sort("created_at", -1).to_list(50)
    for o in materials_orders:
        prog = _progress_for(o)
        o["status"] = prog["status"]
        o["mins_left"] = prog["mins_left"]
    materials_enquiries = await db.materials_cart_enquiries.find({"user_id": uid}, NO_ID).sort("created_at", -1).to_list(100)
    return {
        "saved": saved,
        "follows": follows,
        "my_listings": my_listings,
        "quote_requests": quote_requests,
        "agent_enquiries": agent_enquiries,
        "materials_orders": materials_orders,
        "materials_enquiries": materials_enquiries,
    }

# ---------------- Featured listings & promotions (lead-based pricing) ----------------
PROMOTE_PLANS = [
    {"id": "plan-7", "days": 7, "price": 499, "name": "Boost · 1 week",
     "perks": ["Pinned above all listings in your type", "Highlighted on map", "WhatsApp lead routing"]},
    {"id": "plan-14", "days": 14, "price": 899, "name": "Spotlight · 2 weeks",
     "perks": ["Pinned above all listings in your type", "Highlighted on map", "WhatsApp lead routing", "Priority in similar-property blocks"]},
    {"id": "plan-30", "days": 30, "price": 1499, "name": "Headline · 1 month",
     "perks": ["Pinned above all listings in your type", "Highlighted on map", "WhatsApp lead routing", "Priority in similar-property blocks", "Featured in city digest emails"]},
]


class PromoteRequest(BaseModel):
    user_id: Optional[str] = None
    plan_id: str                     # plan-7 / plan-14 / plan-30
    payment_method: str = "upi"      # mock
    payment_ref: Optional[str] = None


@api_router.get("/promote/plans")
async def list_promote_plans():
    return {"plans": PROMOTE_PLANS}


@api_router.post("/properties/{pid}/promote")
async def promote_property(pid: str, req: PromoteRequest):
    """Mark a listing as featured for N days (mock-paid). Lead-based pricing is modelled per lead too."""
    prop = await db.properties.find_one({"id": pid}, NO_ID)
    if not prop:
        raise HTTPException(404, "Property not found")
    plan = next((p for p in PROMOTE_PLANS if p["id"] == req.plan_id), None)
    if not plan:
        raise HTTPException(400, "Invalid plan")
    now = datetime.now(timezone.utc)
    # If already featured and not expired, extend from the current end-date
    current_until = prop.get("featured_until")
    base = now
    try:
        if current_until:
            dt = datetime.fromisoformat(current_until)
            if dt > now:
                base = dt
    except Exception:
        pass
    expires = (base + timedelta(days=plan["days"])).isoformat()
    tier = "headline" if plan["days"] >= 30 else "spotlight" if plan["days"] >= 14 else "basic"
    await db.properties.update_one({"id": pid}, {"$set": {"featured": True, "featured_until": expires, "featured_tier": tier}})
    doc = {
        "id": f"prom-{uuid.uuid4().hex[:10]}",
        "property_id": pid,
        "user_id": req.user_id,
        "plan_id": plan["id"],
        "plan_name": plan["name"],
        "days": plan["days"],
        "price": plan["price"],
        "payment_method": req.payment_method,
        "payment_ref": req.payment_ref,
        "payment_status": "paid",
        "created_at": now.isoformat(),
        "expires_at": expires,
    }
    await db.promotions.insert_one({**doc})
    return {"property_id": pid, "featured_until": expires, "tier": tier, "plan": plan,
            "promotion": {k: v for k, v in doc.items() if k != "_id"}}


class LeadRequest(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    mobile: Optional[str] = None
    channel: str  # "whatsapp" | "call" | "visit"
    message: Optional[str] = None


# Lead-based pricing: each paid lead charges the broker a slab (deducted from a mock wallet)
LEAD_RATES = {"whatsapp": 25, "call": 35, "visit": 75}


@api_router.post("/properties/{pid}/leads")
async def create_lead(pid: str, req: LeadRequest):
    p = await db.properties.find_one({"id": pid}, {"_id": 0, "id": 1, "lister": 1, "featured": 1, "source": 1, "owner_user_id": 1})
    if not p:
        raise HTTPException(404, "Property not found")
    cost = LEAD_RATES.get(req.channel, 25)
    doc = {
        "id": f"lead-{uuid.uuid4().hex[:10]}",
        "property_id": pid,
        "user_id": req.user_id,
        "name": (req.name or "").strip() or None,
        "mobile": (req.mobile or "").strip() or None,
        "channel": req.channel,
        "message": (req.message or "").strip() or None,
        "cost": cost,
        "paid_by": p.get("source"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.property_leads.insert_one({**doc})
    return {"id": doc["id"], "cost": cost, "channel": req.channel}


@api_router.get("/properties/{pid}/leads")
async def list_property_leads(pid: str, admin_token: Optional[str] = None):
    """Owner / admin only. Simple shared-secret for the demo."""
    expected = os.environ.get("ADMIN_TOKEN", "infrajagat-admin")
    if (admin_token or "") != expected:
        raise HTTPException(403, "Not authorised")
    docs = await db.property_leads.find({"property_id": pid}, NO_ID).sort("created_at", -1).to_list(200)
    total_cost = sum(d.get("cost", 0) for d in docs)
    return {"leads": docs, "total_cost": total_cost, "count": len(docs)}


# ---------------- Verification system ----------------
class VerificationDoc(BaseModel):
    type: str   # "patta" / "sale_deed" / "khasra" / "rera" / "owner_id"
    url: str    # storage path from /api/upload
    label: Optional[str] = None


class VerificationRequest(BaseModel):
    user_id: Optional[str] = None
    docs: List[VerificationDoc]
    note: Optional[str] = None


@api_router.post("/properties/{pid}/verification-request")
async def submit_verification(pid: str, req: VerificationRequest):
    p = await db.properties.find_one({"id": pid}, {"_id": 0, "id": 1, "owner_user_id": 1})
    if not p:
        raise HTTPException(404, "Property not found")
    if not req.docs:
        raise HTTPException(400, "Attach at least one document")
    doc = {
        "id": f"vr-{uuid.uuid4().hex[:10]}",
        "property_id": pid,
        "user_id": req.user_id,
        "docs": [d.model_dump() for d in req.docs],
        "note": (req.note or "").strip() or None,
        "status": "Pending Review",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.verification_requests.insert_one({**doc})
    await db.properties.update_one({"id": pid}, {"$set": {"verification_status": "Pending Review"}})
    return {k: v for k, v in doc.items() if k != "_id"}


@api_router.get("/verification-requests")
async def list_verification_requests(status: Optional[str] = None, admin_token: Optional[str] = None):
    expected = os.environ.get("ADMIN_TOKEN", "infrajagat-admin")
    if (admin_token or "") != expected:
        raise HTTPException(403, "Not authorised")
    q = {}
    if status:
        q["status"] = status
    docs = await db.verification_requests.find(q, NO_ID).sort("created_at", -1).to_list(500)
    # enrich with property snapshot
    pids = [d["property_id"] for d in docs]
    props = await db.properties.find({"id": {"$in": pids}}, {"_id": 0, "id": 1, "title": 1, "address": 1, "images": 1, "price": 1}).to_list(500)
    pmap = {p["id"]: p for p in props}
    for d in docs:
        d["property"] = pmap.get(d["property_id"])
    return docs


class VerifyDecision(BaseModel):
    decision: str  # "approve" | "reject"
    admin_token: Optional[str] = None
    reason: Optional[str] = None


@api_router.post("/verification-requests/{vid}/review")
async def review_verification(vid: str, req: VerifyDecision):
    expected = os.environ.get("ADMIN_TOKEN", "infrajagat-admin")
    if (req.admin_token or "") != expected:
        raise HTTPException(403, "Not authorised")
    vr = await db.verification_requests.find_one({"id": vid}, NO_ID)
    if not vr:
        raise HTTPException(404, "Request not found")
    new_status = "Verified" if req.decision == "approve" else "Rejected"
    await db.verification_requests.update_one({"id": vid}, {"$set": {"status": new_status, "reviewed_at": datetime.now(timezone.utc).isoformat(), "reason": req.reason}})
    # Update property verified flag
    pid = vr["property_id"]
    if req.decision == "approve":
        await db.properties.update_one({"id": pid}, {"$set": {"verified": True, "verification_status": "Verified"}})
    else:
        await db.properties.update_one({"id": pid}, {"$set": {"verification_status": "Rejected"}})
    vr["status"] = new_status
    return vr


# ---------------- Agent subscription tiers + analytics ----------------
TIER_PERKS = {
    "Gold": {
        "monthly_price": 2499,
        "annual_price": 24900,
        "perks": [
            "Top placement in your city & specialty",
            "Unlimited verified listings",
            "WhatsApp lead routing with auto-reply",
            "Priority in buyer search & similar-property blocks",
            "Full analytics dashboard (views, leads, conversion)",
            "Gold shield badge next to your name",
            "Dedicated success manager",
        ],
        "listings_cap": None,
        "lead_cap": None,
        "badge_color": "#D4A72C",
    },
    "Silver": {
        "monthly_price": 1299,
        "annual_price": 12900,
        "perks": [
            "Featured placement in your top 2 localities",
            "Up to 25 verified listings",
            "WhatsApp lead routing",
            "Monthly performance digest",
            "Silver shield badge",
        ],
        "listings_cap": 25,
        "lead_cap": 150,
        "badge_color": "#B8B8B8",
    },
    "Bronze": {
        "monthly_price": 499,
        "annual_price": 4990,
        "perks": [
            "Up to 10 verified listings",
            "Standard placement with Bronze badge",
            "Weekly lead summary",
        ],
        "listings_cap": 10,
        "lead_cap": 50,
        "badge_color": "#B07048",
    },
    "Unverified": {
        "monthly_price": 0,
        "annual_price": 0,
        "perks": [
            "Up to 3 unverified listings",
            "Basic enquiry inbox",
        ],
        "listings_cap": 3,
        "lead_cap": 10,
        "badge_color": "#9A9A9A",
    },
}


@api_router.get("/agent-subscription-tiers")
async def subscription_tiers():
    return {"tiers": [{"name": k, **v} for k, v in TIER_PERKS.items()]}


@api_router.get("/agents/{aid}/analytics")
async def agent_analytics(aid: str):
    a = await db.agents.find_one({"id": aid}, NO_ID)
    if not a:
        raise HTTPException(404, "Agent not found")
    tier = agent_tier_for(a)
    # Deterministic mock metrics seeded off agent id so the demo feels alive
    seed = sum(ord(c) for c in aid)
    views_30d = 320 + (seed % 480)
    leads_30d = 18 + (seed % 42)
    whatsapp_30d = int(leads_30d * 0.68)
    deals_closed = max(0, leads_30d // 7 - (seed % 2))
    conversion = round((deals_closed / leads_30d) * 100, 1) if leads_30d else 0
    daily = []
    for i in range(14):
        d = (datetime.now(timezone.utc) - timedelta(days=13 - i)).date().isoformat()
        v = int(views_30d / 30 + ((seed + i) % 11))
        daily.append({"date": d, "views": v, "leads": max(0, (v // 15) + ((seed + i) % 3) - 1)})
    perks = TIER_PERKS.get(tier, TIER_PERKS["Bronze"])
    return {
        "agent_id": aid, "tier": tier, "perks": perks,
        "metrics": {
            "views_30d": views_30d,
            "leads_30d": leads_30d,
            "whatsapp_leads_30d": whatsapp_30d,
            "deals_closed_30d": deals_closed,
            "conversion_pct": conversion,
            "profile_rank_city": max(1, 60 - (seed % 55)),
        },
        "trend_14d": daily,
    }


# Re-use the enrich.agent_tier helper here (defined already)
from enrich import agent_tier as agent_tier_for  # noqa: E402


# ---------------- Saved searches ----------------
class SavedSearch(BaseModel):
    user_id: str
    name: str
    params: Dict[str, Any]
    notify: bool = True


@api_router.post("/saved-searches")
async def create_saved_search(req: SavedSearch):
    if not req.user_id:
        raise HTTPException(400, "Login required")
    if not req.name.strip():
        raise HTTPException(400, "Give your search a name")
    doc = {
        "id": f"ss-{uuid.uuid4().hex[:10]}",
        "user_id": req.user_id,
        "name": req.name.strip()[:80],
        "params": req.params,
        "notify": bool(req.notify),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_match_count": 0,
        "last_run_at": None,
    }
    await db.saved_searches.insert_one({**doc})
    # Compute initial match count
    cnt = await _run_saved_search(req.params, count_only=True)
    await db.saved_searches.update_one({"id": doc["id"]}, {"$set": {"last_match_count": cnt, "last_run_at": datetime.now(timezone.utc).isoformat()}})
    doc["last_match_count"] = cnt
    return {k: v for k, v in doc.items() if k != "_id"}


@api_router.get("/saved-searches")
async def list_saved_searches(user_id: str):
    docs = await db.saved_searches.find({"user_id": user_id}, NO_ID).sort("created_at", -1).to_list(200)
    return docs


@api_router.delete("/saved-searches/{sid}")
async def delete_saved_search(sid: str, user_id: str):
    r = await db.saved_searches.delete_one({"id": sid, "user_id": user_id})
    if not r.deleted_count:
        raise HTTPException(404, "Not found")
    return {"deleted": True}


async def _run_saved_search(params: Dict[str, Any], count_only: bool = False):
    q: Dict[str, Any] = {}
    if params.get("type"): q["type"] = params["type"]
    if params.get("listing_type"): q["listing_type"] = params["listing_type"]
    if params.get("locality_id"): q["locality_id"] = params["locality_id"]
    if params.get("bedrooms") is not None: q["bedrooms"] = params["bedrooms"]
    if params.get("verified_only"): q["verified"] = True
    if params.get("source"): q["source"] = params["source"]
    price_q: Dict[str, Any] = {}
    if params.get("min_price") is not None: price_q["$gte"] = params["min_price"]
    if params.get("max_price") is not None: price_q["$lte"] = params["max_price"]
    if price_q: q["price"] = price_q
    if params.get("q"):
        qs = params["q"]
        q["$or"] = [
            {"title": {"$regex": qs, "$options": "i"}},
            {"locality_name": {"$regex": qs, "$options": "i"}},
            {"address": {"$regex": qs, "$options": "i"}},
        ]
    if count_only:
        return await db.properties.count_documents(q)
    return await db.properties.find(q, NO_ID).sort([("featured", -1), ("listed_at", -1)]).limit(60).to_list(60)


@api_router.get("/saved-searches/{sid}/matches")
async def saved_search_matches(sid: str, user_id: str):
    ss = await db.saved_searches.find_one({"id": sid, "user_id": user_id}, NO_ID)
    if not ss:
        raise HTTPException(404, "Not found")
    results = await _run_saved_search(ss.get("params", {}))
    # Items added since last_run_at are "new"
    last_run = ss.get("last_run_at")
    new_ids: List[str] = []
    if last_run:
        for r in results:
            if r.get("listed_at", "") > last_run:
                new_ids.append(r["id"])
    cnt = len(results)
    await db.saved_searches.update_one({"id": sid}, {"$set": {"last_match_count": cnt, "last_run_at": datetime.now(timezone.utc).isoformat()}})
    return {"search": ss, "results": results, "new_ids": new_ids, "count": cnt}


# ---------------- Locality compare ----------------
@api_router.get("/compare/localities")
async def compare_localities(ids: str):
    id_list = [x.strip() for x in ids.split(",") if x.strip()][:4]
    if not id_list:
        return []
    docs = await db.localities.find({"id": {"$in": id_list}}, NO_ID).to_list(10)
    docs = [with_lifestyle(d) for d in docs]
    for d in docs:
        ph = await db.price_history.find_one({"locality_id": d["id"]}, NO_ID)
        d["price_history"] = ph["series"] if ph else []
        d["properties_count"] = await db.properties.count_documents({"locality_id": d["id"]})
        d["featured_count"] = await db.properties.count_documents({"locality_id": d["id"], "featured": True})
        d["infrastructure_count"] = await db.infrastructure.count_documents({"locality_ids": d["id"]})
    # Preserve requested order
    order = {lid: i for i, lid in enumerate(id_list)}
    docs.sort(key=lambda x: order.get(x["id"], 99))
    return docs


# ---------------- Home-loan EMI quote ----------------
class EMIRequest(BaseModel):
    price: float
    down_payment_pct: float = 20.0     # % of price
    annual_rate_pct: float = 8.75      # % per annum
    tenure_years: int = 20
    monthly_income: Optional[float] = None


@api_router.post("/finance/emi")
async def emi_quote(req: EMIRequest):
    if req.price <= 0 or req.tenure_years <= 0 or req.annual_rate_pct <= 0:
        raise HTTPException(400, "Invalid inputs")
    down = req.price * (req.down_payment_pct / 100.0)
    principal = max(0, req.price - down)
    n = req.tenure_years * 12
    r = (req.annual_rate_pct / 100.0) / 12.0
    emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1) if principal > 0 else 0
    total_interest = emi * n - principal if principal > 0 else 0
    total_payable = emi * n if principal > 0 else 0
    # Eligibility heuristic: EMI should be <= 50% of monthly income
    eligibility: Dict[str, Any] = {"ok": None, "note": None, "max_eligible_price": None}
    if req.monthly_income and req.monthly_income > 0:
        max_emi = req.monthly_income * 0.5
        eligibility["ok"] = emi <= max_emi
        eligibility["note"] = (
            f"Your EMI uses {round(emi / req.monthly_income * 100, 1)}% of your monthly income."
            if emi > 0 else "Enter a valid price."
        )
        # back-calculate: max principal from max EMI
        if r > 0:
            max_principal = max_emi / (r * ((1 + r) ** n) / (((1 + r) ** n) - 1))
            eligibility["max_eligible_price"] = int(max_principal / (1 - req.down_payment_pct / 100.0))
    # Illustrative offers
    banks = [
        {"bank": "SBI", "rate": req.annual_rate_pct - 0.1, "processing_fee": "0.35% + GST"},
        {"bank": "HDFC", "rate": req.annual_rate_pct, "processing_fee": "0.50% + GST"},
        {"bank": "ICICI", "rate": req.annual_rate_pct + 0.1, "processing_fee": "0.50% + GST"},
        {"bank": "Axis", "rate": req.annual_rate_pct + 0.15, "processing_fee": "1% up to ₹10K"},
    ]
    for b in banks:
        br = b["rate"] / 100.0 / 12.0
        b["emi"] = int(principal * br * ((1 + br) ** n) / (((1 + br) ** n) - 1)) if principal > 0 else 0
    return {
        "price": req.price,
        "down_payment": int(down),
        "principal": int(principal),
        "tenure_months": n,
        "rate_pct": req.annual_rate_pct,
        "emi": int(round(emi)),
        "total_interest": int(round(total_interest)),
        "total_payable": int(round(total_payable)),
        "eligibility": eligibility,
        "bank_offers": banks,
    }


# ---------------- AI-backed InfraValue ----------------
@api_router.get("/properties/{pid}/ai-valuation")
async def ai_valuation(pid: str, refresh: bool = False):
    p = await db.properties.find_one({"id": pid}, NO_ID)
    if not p:
        raise HTTPException(404, "Property not found")
    # Cache: avoid repeat LLM calls unless refresh=True
    cached = await db.ai_valuations.find_one({"property_id": pid}, NO_ID)
    if cached and not refresh:
        return cached
    loc = await db.localities.find_one({"id": p["locality_id"]}, NO_ID)
    # Infra within locality
    infra = await db.infrastructure.find({"locality_ids": p["locality_id"]}, NO_ID).to_list(20)
    # Build a tight context JSON for the LLM
    ctx = {
        "property": {
            "title": p.get("title"),
            "type": p.get("type"),
            "listing_type": p.get("listing_type"),
            "price": p.get("price"),
            "area": p.get("area"),
            "area_unit": p.get("area_unit"),
            "price_per_unit": p.get("price_per_unit"),
            "bedrooms": p.get("bedrooms"),
            "facing": p.get("facing"),
            "road_width_ft": p.get("road_width_ft"),
            "address": p.get("address"),
            "verified": p.get("verified"),
        },
        "locality": {
            "name": loc.get("name") if loc else None,
            "median_price_per_sq_yd": loc.get("median_price_per_sq_yd") if loc else None,
            "govt_dlc_per_sq_yd": loc.get("govt_dlc_per_sq_yd") if loc else None,
            "yoy_change_pct": loc.get("yoy_change_pct") if loc else None,
            "confidence": loc.get("confidence") if loc else None,
            "estimated_range_low": loc.get("estimated_range_low") if loc else None,
            "estimated_range_high": loc.get("estimated_range_high") if loc else None,
            "lifestyle": (with_lifestyle(loc).get("lifestyle") if loc else None),
        },
        "infrastructure": [{"name": i["name"], "status": i["status"], "type": i["type"], "expected_completion": i.get("expected_completion")} for i in infra],
    }
    heuristic_low = p.get("infravalue", {}).get("low") if p.get("infravalue") else int(p["price"] * 0.9)
    heuristic_high = p.get("infravalue", {}).get("high") if p.get("infravalue") else int(p["price"] * 1.1)
    out = {
        "property_id": pid,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fair_value_low": heuristic_low,
        "fair_value_high": heuristic_high,
        "price_vs_fair": "within_range",   # under / within_range / above
        "confidence": loc.get("confidence") if loc else "MEDIUM",
        "key_factors": [],
        "risks": [],
        "model": "heuristic",
    }
    if EMERGENT_KEY:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage  # local import
            system = (
                "You are a senior Indian real-estate valuation analyst. "
                "Given a property, its locality snapshot and nearby infrastructure, "
                "produce a conservative, defensible fair-value RANGE (low, high in INR) "
                "AND a short list of key_factors (why this value) and risks. "
                "Return STRICT JSON only with keys: fair_value_low, fair_value_high, "
                "price_vs_fair (one of 'under','within_range','above'), confidence "
                "(LOW/MEDIUM/HIGH), key_factors (max 4, each <= 90 chars), "
                "risks (max 3, each <= 90 chars)."
            )
            chat = LlmChat(api_key=EMERGENT_KEY, session_id=f"val-{pid}", system_message=system).with_model("openai", "gpt-4o-mini")
            import json as _json
            prompt = (
                "Analyse this Indian property and output JSON only.\n"
                f"DATA: {_json.dumps(ctx, ensure_ascii=False)}\n"
                f"LISTED PRICE (INR): {p.get('price')}"
            )
            msg = UserMessage(text=prompt)
            raw = await chat.send_message(msg)
            # Strip common code fences
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.lower().startswith("json"):
                    cleaned = cleaned[4:]
            # Find first {..} block
            m = re.search(r"\{.*\}", cleaned, re.DOTALL)
            parsed: Dict[str, Any] = {}
            if m:
                try:
                    parsed = _json.loads(m.group(0))
                except Exception:
                    parsed = {}
            if parsed:
                out["fair_value_low"] = int(parsed.get("fair_value_low") or heuristic_low)
                out["fair_value_high"] = int(parsed.get("fair_value_high") or heuristic_high)
                out["price_vs_fair"] = parsed.get("price_vs_fair") or "within_range"
                out["confidence"] = parsed.get("confidence") or out["confidence"]
                out["key_factors"] = [str(x)[:120] for x in (parsed.get("key_factors") or [])][:4]
                out["risks"] = [str(x)[:120] for x in (parsed.get("risks") or [])][:3]
                out["model"] = "gpt-4o-mini"
        except Exception as e:
            logging.exception("AI valuation failed, falling back to heuristic: %s", e)
    # Fallback: derive factors from available data if LLM path missed
    if not out["key_factors"]:
        kf = []
        if loc and loc.get("yoy_change_pct", 0) >= 8:
            kf.append(f"Strong YoY appreciation of {loc['yoy_change_pct']}% in {loc['name']}")
        if loc and loc.get("confidence") == "HIGH":
            kf.append("High confidence locality with established transaction volumes")
        if p.get("verified"):
            kf.append("Document-verified listing — lower title-risk premium")
        if infra:
            kf.append(f"{len(infra)} active infra projects within locality")
        out["key_factors"] = kf[:4]
    if not out["risks"]:
        rk = []
        if loc and loc.get("confidence") == "MEDIUM":
            rk.append("Medium confidence — fewer recent comparable transactions")
        if not p.get("verified"):
            rk.append("Not document-verified yet — pending title & RERA checks")
        if p.get("source") == "Owner":
            rk.append("Direct-owner sale — negotiate on paperwork & stamp duty")
        out["risks"] = rk[:3]
    # Position price vs fair
    try:
        pr = p["price"]
        if pr < out["fair_value_low"]:
            out["price_vs_fair"] = "under"
        elif pr > out["fair_value_high"]:
            out["price_vs_fair"] = "above"
        else:
            out["price_vs_fair"] = "within_range"
    except Exception:
        pass
    await db.ai_valuations.replace_one({"property_id": pid}, {**out}, upsert=True)
    return out


# ---------------- Parcha scanner (camera → LLM vision → cheapest cart) ----------------
class ParchaScanRequest(BaseModel):
    user_id: Optional[str] = None
    image_url: str                   # e.g. "/api/upload/returned/path.jpg" (relative or absolute)
    note: Optional[str] = None


def _abs_url(path_or_url: str) -> str:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    base = (os.environ.get("PUBLIC_BACKEND_URL") or "").rstrip("/")
    if not base:
        # local fallback
        base = f"http://localhost:8001"
    if not path_or_url.startswith("/"):
        path_or_url = "/" + path_or_url
    return base + path_or_url


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", (s or "").lower()).strip()


@api_router.post("/materials/scan-parcha")
async def scan_parcha(req: ParchaScanRequest):
    """Reads a construction-materials parcha (handwritten/printed list), extracts items,
    matches them against the live materials catalogue, and returns the CHEAPEST product
    per item across vendors so the client can one-tap add everything to the cart."""
    if not EMERGENT_KEY:
        raise HTTPException(500, "LLM key not configured")
    image_url = _abs_url(req.image_url)
    # Step 1: ask the LLM-vision to extract structured items
    system = (
        "You are reading a hand-written Indian construction materials order list (a 'parcha'). "
        "Extract every line item. Return STRICT JSON with key 'items' as an array of "
        "{name, quantity, unit, brand, raw}. "
        "name: canonical material name (English, lower snake case, e.g. 'cement', 'tmt_bars', 'red_bricks'). "
        "quantity: number only (integer or float). unit: short unit like 'bag', 'kg', 'piece', 'ton', 'sq ft'. "
        "brand: brand/company if visible else null. raw: the exact text as written. "
        "If you cannot read the image or there are no items, return {\"items\": []}."
    )
    extracted: List[Dict[str, Any]] = []
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent  # local import
        import base64 as _b64, json as _json
        # Download the image to base64 so the LLM can see it even on private URLs
        try:
            r = requests.get(image_url, timeout=15)
            r.raise_for_status()
            img_b64 = _b64.b64encode(r.content).decode("utf-8")
        except Exception as e:
            raise HTTPException(400, f"Could not read image: {e}")
        chat = LlmChat(api_key=EMERGENT_KEY, session_id=f"parcha-{uuid.uuid4().hex[:8]}", system_message=system).with_model("openai", "gpt-4o")
        msg = UserMessage(
            text="Extract items from this parcha. Respond with JSON only.",
            file_contents=[ImageContent(image_base64=img_b64)],
        )
        raw = await chat.send_message(msg)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        parsed = _json.loads(m.group(0)) if m else {}
        extracted = parsed.get("items") or []
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Parcha scan LLM failed: %s", e)
        extracted = []

    # Step 2: match each extracted item against the catalogue and pick cheapest vendor
    all_products = await db.materials_products.find({}, NO_ID).to_list(2000)
    all_stores = await db.materials_stores.find({}, NO_ID).to_list(500)
    store_by_id = {s["id"]: s for s in all_stores}

    def score(product: Dict[str, Any], query: Dict[str, Any]) -> int:
        name_q = _norm(query.get("name", "")).replace("_", " ")
        brand_q = _norm(query.get("brand") or "")
        n = _norm(product.get("name", ""))
        b = _norm(product.get("brand") or "")
        pts = 0
        # token overlap
        q_tokens = set(name_q.split()) - {"", "the", "a"}
        p_tokens = set(n.split())
        pts += len(q_tokens & p_tokens) * 10
        if name_q and name_q in n:
            pts += 20
        if brand_q and (brand_q in b or b in brand_q):
            pts += 15
        return pts

    def pick_cheapest(query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        scored: List[tuple] = []
        for p in all_products:
            s = score(p, query)
            if s > 0:
                scored.append((s, p))
        if not scored:
            return None
        # keep highest-scoring, then cheapest among the top band
        scored.sort(key=lambda t: (-t[0], t[1].get("price", 1e9)))
        top_score = scored[0][0]
        best_band = [p for s, p in scored if s >= top_score - 5]
        best_band.sort(key=lambda p: p.get("price", 1e9))
        return best_band[0]

    cart_items: List[Dict[str, Any]] = []
    unmatched: List[Dict[str, Any]] = []
    total_estimated = 0
    for it in extracted:
        q = max(1, int(float(it.get("quantity") or 1)))
        match = pick_cheapest(it)
        if not match:
            unmatched.append({"query": it, "reason": "No catalogue match"})
            continue
        store = store_by_id.get(match.get("store_id", ""), {})
        line = {
            "product_id": match["id"],
            "name": match.get("name"),
            "brand": match.get("brand"),
            "image": match.get("image"),
            "unit": match.get("unit"),
            "price": match.get("price"),
            "mrp": match.get("mrp"),
            "store_id": match.get("store_id"),
            "store_name": store.get("name"),
            "store_area": store.get("area"),
            "qty": q,
            "subtotal": q * (match.get("price") or 0),
            "query": {"name": it.get("name"), "brand": it.get("brand"), "raw": it.get("raw"), "quantity": q, "unit": it.get("unit")},
        }
        cart_items.append(line)
        total_estimated += line["subtotal"]

    scan_doc = {
        "id": f"parcha-{uuid.uuid4().hex[:10]}",
        "user_id": req.user_id,
        "image_url": req.image_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "note": (req.note or "").strip() or None,
        "extracted": extracted,
        "items": cart_items,
        "unmatched": unmatched,
        "total_estimated": total_estimated,
    }
    await db.parcha_scans.insert_one({**scan_doc})
    return {k: v for k, v in scan_doc.items() if k != "_id"}


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
