"""Tests for iteration 7 backend changes:
- listing_type on properties (Buy/Rent), 6 rentals seeded
- filter by listing_type + type/locality
- GET /properties/{pid}/similar honours listing_type
- Onboard preserves profession when omitted (regression)
- GET /user/{uid}/activity aggregates saved/follows/my_listings/quote_requests/agent_enquiries
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "EXPO_PUBLIC_BACKEND_URL must be set"
API = f"{BASE_URL}/api"

TEST_MOBILE_PROFESSION = "9998887779"
TEST_MOBILE_ACTIVITY = "9998887780"


@pytest.fixture(scope="module")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    yield s
    # Cleanup TEST users at the end (uses mongo directly since no delete endpoint exists)
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        if mongo_url and db_name:
            async def _cleanup():
                client = AsyncIOMotorClient(mongo_url)
                db = client[db_name]
                users = await db.users.find(
                    {"mobile": {"$in": [TEST_MOBILE_PROFESSION, TEST_MOBILE_ACTIVITY]}}
                ).to_list(10)
                uids = [u["id"] for u in users]
                await db.users.delete_many({"id": {"$in": uids}})
                await db.saved.delete_many({"user_id": {"$in": uids}})
                await db.follows.delete_many({"user_id": {"$in": uids}})
                await db.saved_properties.delete_many({"user_id": {"$in": uids}})
                await db.followed_localities.delete_many({"user_id": {"$in": uids}})
                await db.quote_requests.delete_many({"user_id": {"$in": uids}})
                await db.agent_enquiries.delete_many({"user_id": {"$in": uids}})
                client.close()
            asyncio.get_event_loop().run_until_complete(_cleanup())
    except Exception as e:
        print(f"cleanup skipped: {e}")


# ---------------- Listing type on /properties ----------------
class TestListingTypeListing:
    def test_1_all_properties_have_listing_type(self, api_client):
        r = api_client.get(f"{API}/properties", params={"limit": 500})
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) >= 36, f"expected >=36, got {len(items)}"
        for p in items:
            assert "listing_type" in p, f"missing listing_type on {p.get('id')}"
            assert p["listing_type"] in ("Buy", "Rent")
            assert "_id" not in p

    def test_2_filter_buy(self, api_client):
        r = api_client.get(f"{API}/properties", params={"listing_type": "Buy", "limit": 500})
        assert r.status_code == 200
        items = r.json()
        assert len(items) == 30, f"expected 30 Buy items, got {len(items)}"
        for p in items:
            assert p["listing_type"] == "Buy"
            assert not p["id"].startswith("r-"), f"unexpected rental id in Buy: {p['id']}"

    def test_3_filter_rent(self, api_client):
        r = api_client.get(f"{API}/properties", params={"listing_type": "Rent", "limit": 500})
        assert r.status_code == 200
        items = r.json()
        assert len(items) == 6, f"expected 6 Rent items, got {len(items)}"
        rent_keywords = ("for rent", "on rent", "rental")
        for p in items:
            assert p["listing_type"] == "Rent"
            assert p["id"].startswith("r-"), f"unexpected id in Rent: {p['id']}"
            assert 10000 <= p["price"] < 200000, f"price out of monthly range: {p['price']}"
        # at least one has rent keyword in title
        titles_lower = [p["title"].lower() for p in items]
        assert any(any(k in t for k in rent_keywords) for t in titles_lower), \
            f"no title has rent keyword: {titles_lower}"

    def test_4_filter_rent_apartments(self, api_client):
        r = api_client.get(f"{API}/properties", params={"listing_type": "Rent", "type": "Apartment", "limit": 500})
        assert r.status_code == 200
        items = r.json()
        ids = sorted([p["id"] for p in items])
        assert ids == ["r-01", "r-02", "r-05", "r-06"], f"got {ids}"
        for p in items:
            assert p["listing_type"] == "Rent"
            assert p["type"] == "Apartment"

    def test_5_filter_rent_by_locality(self, api_client):
        r = api_client.get(f"{API}/properties", params={"listing_type": "Rent", "locality_id": "loc-mansarovar", "limit": 500})
        assert r.status_code == 200
        items = r.json()
        ids = sorted([p["id"] for p in items])
        assert ids == ["r-03", "r-06"], f"got {ids}"


# ---------------- Single rental fetch ----------------
class TestRentalDetail:
    def test_6_get_r01(self, api_client):
        r = api_client.get(f"{API}/properties/r-01")
        assert r.status_code == 200
        p = r.json()
        assert "_id" not in p
        assert p["id"] == "r-01"
        assert p["listing_type"] == "Rent"
        for f in ["title", "type", "price", "area", "area_unit", "locality_id", "locality_name", "images"]:
            assert f in p, f"missing {f}"
        assert "lister" in p and isinstance(p["lister"], dict)
        assert "infravalue" in p
        assert "govt_value" in p
        assert p["infravalue"]["low"] <= p["infravalue"]["high"]


# ---------------- Similar honours listing_type ----------------
class TestSimilarListingType:
    def test_7_rental_similar_only_rent_and_same_type(self, api_client):
        base = api_client.get(f"{API}/properties/r-01").json()
        assert base["type"] == "Apartment"
        r = api_client.get(f"{API}/properties/r-01/similar")
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) > 0, "expected at least one similar rental"
        for it in items:
            assert "_id" not in it
            assert it["id"] != "r-01"
            assert it["listing_type"] == "Rent", f"mixed listing_type in similar: {it['id']} -> {it['listing_type']}"
            assert it["type"] == "Apartment", f"wrong type: {it['type']}"
            assert not it["id"].startswith("p-"), f"Buy property leaked into rental similar: {it['id']}"

    def test_8_buy_similar_only_buy(self, api_client):
        r = api_client.get(f"{API}/properties/p-06/similar")
        assert r.status_code == 200
        items = r.json()
        assert len(items) > 0
        for it in items:
            assert it["listing_type"] == "Buy", f"mixed listing_type: {it['id']} -> {it['listing_type']}"
            assert not it["id"].startswith("r-"), f"Rent leaked into Buy similar: {it['id']}"


# ---------------- Onboard preserves profession ----------------
class TestOnboardProfessionPreserved:
    def test_9_profession_preserved_on_subsequent_onboard(self, api_client):
        # create with profession Broker
        r = api_client.post(f"{API}/auth/onboard", json={
            "name": "TEST U",
            "mobile": TEST_MOBILE_PROFESSION,
            "area": "Jaipur",
            "profession": "Broker",
        })
        assert r.status_code == 200, r.text
        u = r.json()["user"]
        assert u["profession"] == "Broker"
        assert "_id" not in u
        uid = u["id"]

        # onboard again WITHOUT profession
        r2 = api_client.post(f"{API}/auth/onboard", json={
            "name": "TEST U",
            "mobile": TEST_MOBILE_PROFESSION,
            "area": "Jaipur",
        })
        assert r2.status_code == 200, r2.text
        u2 = r2.json()["user"]
        assert u2["profession"] == "Broker", f"expected Broker, got {u2.get('profession')}"

        # also verify via /auth/me
        r3 = api_client.get(f"{API}/auth/me", params={"user_id": uid})
        assert r3.status_code == 200
        assert r3.json()["profession"] == "Broker"


# ---------------- User activity endpoint ----------------
class TestUserActivity:
    @pytest.fixture(scope="class")
    def activity_user(self, api_client):
        r = api_client.post(f"{API}/auth/onboard", json={
            "name": "TEST Activity",
            "mobile": TEST_MOBILE_ACTIVITY,
            "area": "Jaipur",
            "profession": "Investor",
        })
        assert r.status_code == 200, r.text
        return r.json()["user"]

    def test_10_seed_activity(self, api_client, activity_user):
        uid = activity_user["id"]

        # Save 2 properties
        for pid in ["p-01", "p-06"]:
            rr = api_client.post(f"{API}/saved/toggle", json={"user_id": uid, "property_id": pid})
            assert rr.status_code == 200, rr.text

        # Follow 1 locality
        rr = api_client.post(f"{API}/follows/toggle", json={"user_id": uid, "locality_id": "loc-mansarovar"})
        assert rr.status_code == 200, rr.text

        # Grab first agent + first supplier
        agents = api_client.get(f"{API}/agents").json()
        assert isinstance(agents, list) and len(agents) > 0
        agent_id = agents[0]["id"]
        suppliers = api_client.get(f"{API}/market/suppliers").json()
        assert isinstance(suppliers, list) and len(suppliers) > 0
        supplier_id = suppliers[0]["id"]

        # Agent enquiry
        r_ae = api_client.post(f"{API}/agents/{agent_id}/enquiries", json={
            "agent_id": agent_id,
            "user_id": uid,
            "name": "TEST Activity",
            "mobile": "9998887780",
            "message": "TEST enquiry",
        })
        assert r_ae.status_code == 200, r_ae.text

        # Supplier quote
        r_qr = api_client.post(f"{API}/market/quote-requests", json={
            "user_id": uid,
            "supplier_id": supplier_id,
            "name": "TEST Activity",
            "mobile": TEST_MOBILE_ACTIVITY,
            "message": "TEST quote",
        })
        assert r_qr.status_code == 200, r_qr.text

    def test_11_activity_response_shape(self, api_client, activity_user):
        uid = activity_user["id"]
        r = api_client.get(f"{API}/user/{uid}/activity")
        assert r.status_code == 200, r.text
        data = r.json()

        # Required keys
        for k in ["saved", "follows", "my_listings", "quote_requests", "agent_enquiries"]:
            assert k in data, f"missing key {k}"
            assert isinstance(data[k], list), f"{k} not a list"

        # Saved should have 2 items
        assert len(data["saved"]) == 2, f"expected 2 saved, got {len(data['saved'])}"
        # Follows should have 1 item
        assert len(data["follows"]) == 1, f"expected 1 follow, got {len(data['follows'])}"

        # No _id anywhere
        def check_no_id(obj, path=""):
            if isinstance(obj, dict):
                assert "_id" not in obj, f"_id leaked at {path}: keys={list(obj.keys())}"
                for k, v in obj.items():
                    check_no_id(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    check_no_id(v, f"{path}[{i}]")
        check_no_id(data)

        # agent enquiries should have >=1 with agent object
        assert len(data["agent_enquiries"]) >= 1, "expected >=1 agent enquiry"
        for ae in data["agent_enquiries"]:
            assert "agent" in ae and isinstance(ae["agent"], dict), f"missing agent: {ae}"
            for f in ["name", "firm", "image"]:
                assert f in ae["agent"], f"agent missing {f}: {ae['agent']}"

        # quote requests should have >=1 with supplier object
        assert len(data["quote_requests"]) >= 1, "expected >=1 quote request"
        for qr in data["quote_requests"]:
            assert "supplier" in qr and isinstance(qr["supplier"], dict), f"missing supplier: {qr}"
            for f in ["name", "image"]:
                assert f in qr["supplier"], f"supplier missing {f}: {qr['supplier']}"

    def test_12_activity_nonexistent_user_404(self, api_client):
        r = api_client.get(f"{API}/user/nonexistent-user-xyz/activity")
        assert r.status_code == 404
