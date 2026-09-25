"""Tests for NEW endpoints added on top of InfraLocal + Market:
- Heatmap
- Agent categories/agents/enquiries
- Property `lister` field
- Property compare
- Supplier reviews
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # fallback: read frontend .env
    from pathlib import Path
    envp = Path("/app/frontend/.env")
    if envp.exists():
        for line in envp.read_text().splitlines():
            if line.startswith("EXPO_PUBLIC_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


# ---------------- Heatmap ----------------
class TestHeatmap:
    def test_heatmap_shape(self, s):
        r = s.get(f"{API}/heatmap", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert isinstance(data, dict)
        for k in ("min", "max", "points"):
            assert k in data, f"missing key {k}"
        pts = data["points"]
        assert isinstance(pts, list)
        assert len(pts) == 7, f"expected 7 points, got {len(pts)}"
        keys = {"id", "name", "lat", "lng", "median_price_per_sq_yd",
                "govt_dlc_per_sq_yd", "intensity"}
        for p in pts:
            assert "_id" not in p
            assert keys.issubset(p.keys()), f"missing: {keys - p.keys()}"
            assert 0.0 <= float(p["intensity"]) <= 1.0
        intensities = [p["intensity"] for p in pts]
        assert min(intensities) == 0
        assert max(intensities) == 1.0


# ---------------- Agent categories ----------------
class TestAgentCategories:
    def test_seven_categories(self, s):
        r = s.get(f"{API}/agent-categories", timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 7
        expected = {
            "Property Brokers", "Land Aggregators", "JDA / Land-Use Liaison",
            "Registry & Stamp Duty", "Property Lawyers", "Home Loan Advisors",
            "RERA Consultants"
        }
        names = {c["name"] for c in data}
        assert expected.issubset(names), f"missing: {expected - names}"
        for c in data:
            assert "_id" not in c
            assert isinstance(c.get("agents_count"), int)
            assert c["agents_count"] > 0


# ---------------- Agents ----------------
class TestAgents:
    def test_list_all_13(self, s):
        r = s.get(f"{API}/agents", timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 13
        required = {"id", "category_id", "name", "area", "rating", "verified",
                    "phone", "whatsapp", "image", "coverage", "specialties"}
        for a in data:
            assert "_id" not in a
            assert required.issubset(a.keys()), f"missing keys: {required - a.keys()}"
            assert isinstance(a["coverage"], list)
            assert isinstance(a["specialties"], list)

    def test_filter_by_category_broker(self, s):
        r = s.get(f"{API}/agents", params={"category_id": "acat-broker"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 3
        assert all(a["category_id"] == "acat-broker" for a in data)

    def test_verified_only(self, s):
        r = s.get(f"{API}/agents", params={"verified_only": "true"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0
        assert all(a["verified"] is True for a in data)

    def test_featured_only(self, s):
        r = s.get(f"{API}/agents", params={"featured_only": "true"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0
        assert all(a.get("featured") is True for a in data)

    def test_search_plot(self, s):
        r = s.get(f"{API}/agents", params={"q": "plot"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        names = {a["name"] for a in data}
        assert names & {"Vikram Singh Rathore", "Ashok Sharma"}, f"got: {names}"

    def test_area_filter(self, s):
        r = s.get(f"{API}/agents", params={"area": "Ajmer Road"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        names = {a["name"] for a in data}
        assert "Ashok Sharma" in names, f"got: {names}"

    def test_get_agent_ag01(self, s):
        r = s.get(f"{API}/agents/ag-01", timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == "ag-01"
        assert "_id" not in data
        assert isinstance(data.get("category"), dict)
        assert data["category"]["name"] == "Property Brokers"
        # recent_listings should be present since acat-broker
        assert "recent_listings" in data
        assert isinstance(data["recent_listings"], list)
        assert 0 <= len(data["recent_listings"]) <= 6

    def test_get_agent_404(self, s):
        r = s.get(f"{API}/agents/nope", timeout=30)
        assert r.status_code == 404


# ---------------- Agent enquiries ----------------
class TestAgentEnquiries:
    created_ids = []

    def test_create_enquiry(self, s):
        payload = {
            "agent_id": "ag-01",
            "name": "TEST Buyer",
            "mobile": "9876543210",
            "message": "Looking for a 3 BHK",
        }
        r = s.post(f"{API}/agents/ag-01/enquiries", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["id"].startswith("aen-")
        assert data["status"] == "New"
        TestAgentEnquiries.created_ids.append(data["id"])

    def test_short_mobile_400(self, s):
        payload = {"agent_id": "ag-01", "name": "TEST Buyer", "mobile": "12"}
        r = s.post(f"{API}/agents/ag-01/enquiries", json=payload, timeout=30)
        assert r.status_code == 400

    def test_missing_agent_404(self, s):
        payload = {"agent_id": "does-not-exist", "name": "TEST Buyer",
                   "mobile": "9876543210"}
        r = s.post(f"{API}/agents/does-not-exist/enquiries", json=payload, timeout=30)
        assert r.status_code == 404


# ---------------- Property `lister` ----------------
class TestPropertyLister:
    def test_owner_lister(self, s):
        r = s.get(f"{API}/properties/p-01", timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "lister" in data
        lister = data["lister"]
        for k in ("type", "name", "phone", "whatsapp"):
            assert k in lister, f"missing lister.{k}"
        assert lister["type"] == "Owner"
        assert lister.get("agent_id") is None

    def test_broker_lister(self, s):
        r = s.get(f"{API}/properties/p-03", timeout=30)
        assert r.status_code == 200
        data = r.json()
        lister = data["lister"]
        assert lister["type"] == "Broker"
        assert lister.get("agent_id", "").startswith("ag-")
        assert "verified" in lister
        assert isinstance(lister["verified"], bool)
        assert "rera_id" in lister


# ---------------- Compare ----------------
class TestCompare:
    def test_compare_three(self, s):
        r = s.get(f"{API}/compare", params={"ids": "p-01,p-03,p-06"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 3
        got_ids = [d["id"] for d in data]
        assert got_ids == ["p-01", "p-03", "p-06"]
        for d in data:
            assert "infravalue" in d
            iv = d["infravalue"]
            for k in ("low", "high", "confidence"):
                assert k in iv
            assert "govt_value" in d
            assert "lister" in d

    def test_compare_all_invalid(self, s):
        r = s.get(f"{API}/compare", params={"ids": "xxx,yyy"}, timeout=30)
        assert r.status_code == 200
        assert r.json() == []

    def test_compare_mixed(self, s):
        r = s.get(f"{API}/compare", params={"ids": "p-01,nope"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["id"] == "p-01"


# ---------------- Supplier reviews ----------------
class TestSupplierReviews:
    created_ids = []

    def test_list_reviews_initial(self, s):
        r = s.get(f"{API}/market/suppliers/sup-06/reviews", timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_create_review(self, s):
        payload = {"user_id": "test", "name": "TEST User", "rating": 4,
                   "text": "Very reliable"}
        r = s.post(f"{API}/market/suppliers/sup-06/reviews", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["id"].startswith("rev-")
        assert data["rating"] == 4
        assert data["name"] == "TEST User"
        assert "_id" not in data
        TestSupplierReviews.created_ids.append(data["id"])
        # Persistence check
        r2 = s.get(f"{API}/market/suppliers/sup-06/reviews", timeout=30)
        ids = {rv["id"] for rv in r2.json()}
        assert data["id"] in ids

    def test_rating_zero_400(self, s):
        payload = {"name": "TEST User", "rating": 0}
        r = s.post(f"{API}/market/suppliers/sup-06/reviews", json=payload, timeout=30)
        assert r.status_code == 400

    def test_rating_six_400(self, s):
        payload = {"name": "TEST User", "rating": 6}
        r = s.post(f"{API}/market/suppliers/sup-06/reviews", json=payload, timeout=30)
        assert r.status_code == 400

    def test_missing_supplier_404(self, s):
        payload = {"name": "TEST User", "rating": 4}
        r = s.post(f"{API}/market/suppliers/does-not-exist/reviews",
                   json=payload, timeout=30)
        assert r.status_code == 404


# ---------------- Cleanup ----------------
def test_zz_cleanup():
    """Cleanup TEST_ enquiries and reviews via direct Mongo."""
    import asyncio
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ.get("MONGO_URL") or open("/app/backend/.env").read().split("MONGO_URL=")[1].split("\n")[0].strip()
    db_name = os.environ.get("DB_NAME") or open("/app/backend/.env").read().split("DB_NAME=")[1].split("\n")[0].strip()

    async def _clean():
        c = AsyncIOMotorClient(mongo_url)
        d = c[db_name]
        await d.agent_enquiries.delete_many({"name": {"$regex": "^TEST"}})
        await d.supplier_reviews.delete_many({"name": {"$regex": "^TEST"}})
        c.close()

    asyncio.get_event_loop().run_until_complete(_clean())
