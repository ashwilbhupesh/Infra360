"""Tests for new backend behavior:
- POST /api/auth/onboard now accepts and upserts `profession`
- GET /api/properties/{pid}/similar returns similar properties by type/price/locality
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "EXPO_PUBLIC_BACKEND_URL must be set"

API = f"{BASE_URL}/api"

TEST_MOBILE_1 = "9998887771"  # will be upserted multiple times
TEST_MOBILE_2 = "9998887772"  # new user without profession


@pytest.fixture(scope="module")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    yield s
    # Cleanup: remove test users via direct mongo access
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        if mongo_url and db_name:
            async def _cleanup():
                client = AsyncIOMotorClient(mongo_url)
                await client[db_name].users.delete_many(
                    {"mobile": {"$in": [TEST_MOBILE_1, TEST_MOBILE_2]}}
                )
                client.close()
            asyncio.get_event_loop().run_until_complete(_cleanup())
    except Exception as e:
        print(f"cleanup skipped: {e}")


# -------- Onboard profession tests --------
class TestOnboardProfession:
    def test_1_onboard_with_profession_investor(self, api_client):
        r = api_client.post(f"{API}/auth/onboard", json={
            "name": "TEST Rahul",
            "mobile": TEST_MOBILE_1,
            "area": "Jaipur",
            "profession": "Investor",
        })
        assert r.status_code == 200, r.text
        data = r.json()
        assert "user" in data
        user = data["user"]
        assert user["mobile"] == TEST_MOBILE_1
        assert user["profession"] == "Investor"
        assert user.get("name") == "TEST Rahul"
        assert "_id" not in user

    def test_2_onboard_upsert_changes_profession_to_broker(self, api_client):
        r = api_client.post(f"{API}/auth/onboard", json={
            "name": "TEST Rahul",
            "mobile": TEST_MOBILE_1,
            "area": "Jaipur",
            "profession": "Broker",
        })
        assert r.status_code == 200, r.text
        user = r.json()["user"]
        assert user["profession"] == "Broker"
        assert "_id" not in user

    def test_3_onboard_without_profession_keeps_existing(self, api_client):
        r = api_client.post(f"{API}/auth/onboard", json={
            "name": "TEST Rahul",
            "mobile": TEST_MOBILE_1,
            "area": "Jaipur",
        })
        assert r.status_code == 200, r.text
        user = r.json()["user"]
        assert user["profession"] == "Broker", (
            f"Expected profession to remain Broker, got {user.get('profession')}"
        )

        # Also verify via /auth/me
        uid = user["id"]
        r2 = api_client.get(f"{API}/auth/me", params={"user_id": uid})
        assert r2.status_code == 200
        me = r2.json()
        assert me["profession"] == "Broker"

    def test_4_onboard_new_user_no_profession_is_null(self, api_client):
        r = api_client.post(f"{API}/auth/onboard", json={
            "name": "TEST NoProf",
            "mobile": TEST_MOBILE_2,
            "area": "Jaipur",
        })
        assert r.status_code == 200, r.text
        user = r.json()["user"]
        assert user.get("profession") is None
        uid = user["id"]

        r2 = api_client.get(f"{API}/auth/me", params={"user_id": uid})
        assert r2.status_code == 200
        me = r2.json()
        assert me.get("profession") is None
        assert "_id" not in me


# -------- Similar properties tests --------
class TestSimilarProperties:
    def _fetch_property(self, api_client, pid):
        r = api_client.get(f"{API}/properties/{pid}")
        assert r.status_code == 200, f"cannot load {pid}: {r.text}"
        return r.json()

    def test_5_similar_p06_apartments(self, api_client):
        base = self._fetch_property(api_client, "p-06")
        assert base["type"].lower().startswith("apartment") or base["type"] == "Apartment", \
            f"p-06 not Apartment: {base['type']}"
        base_price = base["price"]
        base_loc = base["locality_id"]
        base_loc_name = base.get("locality_name")

        r = api_client.get(f"{API}/properties/p-06/similar")
        assert r.status_code == 200, r.text
        items = r.json()
        assert isinstance(items, list)
        assert len(items) <= 6
        assert len(items) > 0, "expected at least one similar apartment"

        lo, hi = base_price * 0.6, base_price * 1.6
        for it in items:
            assert "_id" not in it
            assert it["id"] != "p-06"
            assert it["type"] == base["type"], f"non-matching type in similar: {it['type']}"
            assert lo <= it["price"] <= hi, f"price {it['price']} out of [{lo},{hi}]"
            # required fields
            for f in ["id", "title", "type", "price", "area", "images", "locality_name"]:
                assert f in it, f"missing field {f}"

        # Same-locality first
        same_loc_indices = [i for i, it in enumerate(items) if it["locality_id"] == base_loc]
        other_indices = [i for i, it in enumerate(items) if it["locality_id"] != base_loc]
        if same_loc_indices and other_indices:
            assert max(same_loc_indices) < min(other_indices), (
                f"Same-locality ({base_loc_name}) items should appear before others"
            )

    def test_6_similar_limit_param(self, api_client):
        r = api_client.get(f"{API}/properties/p-06/similar", params={"limit": 3})
        assert r.status_code == 200
        items = r.json()
        assert len(items) <= 3

    def test_7_similar_unknown_property_404(self, api_client):
        r = api_client.get(f"{API}/properties/xxx/similar")
        assert r.status_code == 404

    def test_8_similar_p01_plots(self, api_client):
        base = self._fetch_property(api_client, "p-01")
        base_type = base["type"]
        base_loc = base["locality_id"]
        base_loc_name = base.get("locality_name")

        r = api_client.get(f"{API}/properties/p-01/similar")
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) > 0

        for it in items:
            assert "_id" not in it
            assert it["id"] != "p-01"
            assert it["type"] == base_type, f"expected type {base_type}, got {it['type']}"
            for f in ["id", "title", "type", "price", "area", "images", "locality_name"]:
                assert f in it, f"missing field {f}"

        # same locality first
        same_loc_indices = [i for i, it in enumerate(items) if it["locality_id"] == base_loc]
        other_indices = [i for i, it in enumerate(items) if it["locality_id"] != base_loc]
        if same_loc_indices and other_indices:
            assert max(same_loc_indices) < min(other_indices), (
                f"Same-locality ({base_loc_name}) plots should appear before others"
            )
