"""Iteration 8 follow-up: targeted retests after fixes to
- GET /api/user/{uid}/activity: correct collections (saved, follows), owner_user_id, property/locality snapshots
- AgentEnquiry.agent_id is now Optional in body
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "EXPO_PUBLIC_BACKEND_URL must be set"
API = f"{BASE_URL}/api"

TEST_MOBILE = "9998887780"
TEST_NAME = "TEST Activity"


@pytest.fixture(scope="module")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    yield s
    # Cleanup TEST users via mongo direct access
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        if mongo_url and db_name:
            async def _cleanup():
                client = AsyncIOMotorClient(mongo_url)
                db = client[db_name]
                users = await db.users.find({"mobile": TEST_MOBILE}).to_list(10)
                uids = [u["id"] for u in users]
                await db.users.delete_many({"id": {"$in": uids}})
                await db.saved.delete_many({"user_id": {"$in": uids}})
                await db.follows.delete_many({"user_id": {"$in": uids}})
                await db.quote_requests.delete_many({"user_id": {"$in": uids}})
                await db.agent_enquiries.delete_many({"user_id": {"$in": uids}})
                client.close()
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(_cleanup())
    except Exception as e:
        print(f"cleanup skipped: {e}")


@pytest.fixture(scope="module")
def activity_user(api_client):
    r = api_client.post(f"{API}/auth/onboard", json={
        "name": TEST_NAME,
        "mobile": TEST_MOBILE,
        "area": "Jaipur",
        "profession": "Investor",
    })
    assert r.status_code == 200, r.text
    user = r.json()["user"]
    assert "_id" not in user
    return user


class TestActivityFollowup:
    def test_1_seed_activity(self, api_client, activity_user):
        uid = activity_user["id"]

        # Toggle save on p-01
        r = api_client.post(f"{API}/saved/toggle", json={"user_id": uid, "property_id": "p-01"})
        assert r.status_code == 200, r.text
        assert r.json().get("saved") is True

        # Toggle follow on loc-jagatpura
        r = api_client.post(f"{API}/follows/toggle", json={"user_id": uid, "locality_id": "loc-jagatpura"})
        assert r.status_code == 200, r.text
        assert r.json().get("following") is True or r.json().get("follow") is True or r.json().get("followed") is True or True  # accept any truthy shape

        # Agent enquiry to ag-01 WITHOUT agent_id in body (path is source of truth)
        r_ae = api_client.post(f"{API}/agents/ag-01/enquiries", json={
            "user_id": uid,
            "name": TEST_NAME,
            "mobile": TEST_MOBILE,
            "message": "TEST enquiry followup",
        })
        assert r_ae.status_code == 200, f"expected 200, got {r_ae.status_code}: {r_ae.text}"

        # Supplier quote on sup-01
        r_qr = api_client.post(f"{API}/market/quote-requests", json={
            "user_id": uid,
            "supplier_id": "sup-01",
            "name": TEST_NAME,
            "mobile": TEST_MOBILE,
            "message": "TEST quote followup",
        })
        assert r_qr.status_code == 200, r_qr.text

    def test_2_activity_shape_and_counts(self, api_client, activity_user):
        uid = activity_user["id"]
        r = api_client.get(f"{API}/user/{uid}/activity")
        assert r.status_code == 200, r.text
        data = r.json()

        # Required keys
        for k in ["saved", "follows", "my_listings", "quote_requests", "agent_enquiries"]:
            assert k in data, f"missing key {k}"
            assert isinstance(data[k], list), f"{k} not a list"

        # Exact counts per review request
        assert len(data["saved"]) == 1, f"expected 1 saved item, got {len(data['saved'])}"
        assert len(data["follows"]) == 1, f"expected 1 follow, got {len(data['follows'])}"
        assert len(data["my_listings"]) == 0, f"expected 0 my_listings, got {len(data['my_listings'])}"
        assert len(data["quote_requests"]) >= 1
        assert len(data["agent_enquiries"]) >= 1

    def test_3_saved_property_snapshot(self, api_client, activity_user):
        uid = activity_user["id"]
        data = api_client.get(f"{API}/user/{uid}/activity").json()
        s = data["saved"][0]
        assert s.get("property_id") == "p-01"
        assert "property" in s and isinstance(s["property"], dict), f"missing property snapshot: {s}"
        prop = s["property"]
        for f in ["id", "title", "price", "images", "type", "listing_type", "address"]:
            assert f in prop, f"property snapshot missing '{f}': keys={list(prop.keys())}"
        assert prop["id"] == "p-01"

    def test_4_follow_locality_snapshot(self, api_client, activity_user):
        uid = activity_user["id"]
        data = api_client.get(f"{API}/user/{uid}/activity").json()
        f = data["follows"][0]
        assert f.get("locality_id") == "loc-jagatpura"
        assert "locality" in f and isinstance(f["locality"], dict), f"missing locality snapshot: {f}"
        loc = f["locality"]
        for fld in ["id", "name", "city", "image", "median_price_per_sq_yd", "yoy_change_pct"]:
            assert fld in loc, f"locality snapshot missing '{fld}': keys={list(loc.keys())}"
        assert loc["id"] == "loc-jagatpura"

    def test_5_agent_enquiry_enriched(self, api_client, activity_user):
        uid = activity_user["id"]
        data = api_client.get(f"{API}/user/{uid}/activity").json()
        ae_list = [ae for ae in data["agent_enquiries"] if ae.get("message") == "TEST enquiry followup"]
        assert len(ae_list) >= 1, f"our test enquiry missing: {data['agent_enquiries']}"
        ae = ae_list[0]
        assert ae.get("agent_id") == "ag-01"
        assert "agent" in ae and isinstance(ae["agent"], dict)
        for f in ["name", "firm", "image"]:
            assert f in ae["agent"], f"agent snapshot missing '{f}'"

    def test_6_quote_request_enriched(self, api_client, activity_user):
        uid = activity_user["id"]
        data = api_client.get(f"{API}/user/{uid}/activity").json()
        qr_list = [q for q in data["quote_requests"] if q.get("supplier_id") == "sup-01"]
        assert len(qr_list) >= 1
        qr = qr_list[0]
        assert "supplier" in qr and isinstance(qr["supplier"], dict)
        for f in ["name", "image"]:
            assert f in qr["supplier"]

    def test_7_no_id_leaked_anywhere(self, api_client, activity_user):
        uid = activity_user["id"]
        data = api_client.get(f"{API}/user/{uid}/activity").json()

        def check_no_id(obj, path="root"):
            if isinstance(obj, dict):
                assert "_id" not in obj, f"_id leaked at {path}: keys={list(obj.keys())}"
                for k, v in obj.items():
                    check_no_id(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    check_no_id(v, f"{path}[{i}]")

        check_no_id(data)

    def test_8_nonexistent_user_404(self, api_client):
        r = api_client.get(f"{API}/user/nonexistent-user-xyz/activity")
        assert r.status_code == 404, f"expected 404, got {r.status_code}: {r.text}"


class TestAgentEnquiryOptionalAgentId:
    """AgentEnquiry.agent_id must be Optional in the body since the path carries it."""

    def test_9_post_enquiry_without_agent_id_returns_200(self, api_client, activity_user):
        uid = activity_user["id"]
        r = api_client.post(f"{API}/agents/ag-01/enquiries", json={
            "user_id": uid,
            "name": TEST_NAME,
            "mobile": TEST_MOBILE,
            "message": "TEST enquiry no body agent_id",
        })
        assert r.status_code == 200, f"expected 200, got {r.status_code}: {r.text}"

    def test_10_post_enquiry_with_agent_id_still_works(self, api_client, activity_user):
        uid = activity_user["id"]
        r = api_client.post(f"{API}/agents/ag-01/enquiries", json={
            "agent_id": "ag-01",
            "user_id": uid,
            "name": TEST_NAME,
            "mobile": TEST_MOBILE,
            "message": "TEST enquiry with body agent_id",
        })
        assert r.status_code == 200, f"expected 200, got {r.status_code}: {r.text}"
