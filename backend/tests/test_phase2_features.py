"""Phase-2 feature regression tests for InfraJagat:
- Featured listings & lead-based pricing
- Agent subscription tiers + analytics
- Verification request + admin review
- Saved-search alerts (CRUD + matches)
- Locality compare
- Home-loan EMI quote
- AI-backed InfraValue (with heuristic fallback + cache)
"""
import os
import pytest
import requests

BASE_URL = os.environ["EXPO_PUBLIC_BACKEND_URL"].rstrip("/")
ADMIN_TOKEN = "infrajagat-admin"


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def test_user(api):
    """Create or reuse a test user via OTP onboarding."""
    r = api.post(f"{BASE_URL}/api/auth/onboard", json={
        "name": "TEST_Phase2",
        "mobile": "9999900050",
        "area": "Jagatpura",
        "otp": "0000",
    })
    assert r.status_code == 200, r.text
    return r.json()["user"]["id"]


# -------- Promote / Featured --------
class TestPromote:
    def test_plans(self, api):
        r = api.get(f"{BASE_URL}/api/promote/plans")
        assert r.status_code == 200
        plans = r.json()["plans"]
        assert len(plans) == 3
        for p in plans:
            assert set(["id", "name", "days", "price"]).issubset(p.keys())

    def test_promote_property(self, api, test_user):
        r = api.post(f"{BASE_URL}/api/properties/p-10/promote", json={
            "plan_id": "plan-14",
            "user_id": test_user,
            "payment_method": "upi",
            "payment_ref": "mock-ref-123",
        })
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["featured_until"]
        assert body["tier"] in ("basic", "spotlight", "headline")
        # verify property shows as featured
        p = api.get(f"{BASE_URL}/api/properties/p-10").json()
        assert p.get("featured") is True

    def test_featured_properties_first(self, api):
        r = api.get(f"{BASE_URL}/api/properties", params={"limit": 60})
        assert r.status_code == 200
        items = r.json()
        assert len(items) > 0
        # first results should include featured
        top5 = items[:5]
        assert any(p.get("featured") for p in top5)
        # seeded featured IDs exist
        seeded = {"p-02", "p-07", "p-10", "p-15", "p-20", "b-01", "b-03", "r-02"}
        all_ids = {p["id"] for p in items}
        assert seeded & all_ids  # at least some overlap


# -------- Leads --------
class TestLeads:
    def test_create_lead(self, api, test_user):
        r = api.post(f"{BASE_URL}/api/properties/p-02/leads", json={
            "user_id": test_user,
            "name": "TEST_Lead",
            "mobile": "9999900050",
            "channel": "whatsapp",
            "message": "Interested",
        })
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["cost"] == 25
        assert body["channel"] == "whatsapp"

    def test_lead_other_channels_cost(self, api, test_user):
        for ch, cost in [("call", 35), ("visit", 75)]:
            r = api.post(f"{BASE_URL}/api/properties/p-02/leads", json={
                "user_id": test_user, "name": "TEST", "mobile": "9999900050",
                "channel": ch, "message": "x"
            })
            assert r.status_code == 200
            assert r.json()["cost"] == cost

    def test_admin_lead_list(self, api):
        r = api.get(f"{BASE_URL}/api/properties/p-02/leads", params={"admin_token": ADMIN_TOKEN})
        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 3
        assert data["total_cost"] >= 25 + 35 + 75

    def test_admin_lead_forbidden(self, api):
        r = api.get(f"{BASE_URL}/api/properties/p-02/leads", params={"admin_token": "wrong"})
        assert r.status_code == 403


# -------- Verification --------
class TestVerification:
    @pytest.fixture(scope="class")
    def verification_id(self, api, test_user):
        r = api.post(f"{BASE_URL}/api/properties/p-07/verification-request", json={
            "user_id": test_user,
            "docs": [
                {"type": "patta", "url": "/mock/patta.jpg"},
                {"type": "sale_deed", "url": "/mock/sale.jpg"},
            ],
            "note": "TEST verification",
        })
        assert r.status_code == 200, r.text
        return r.json()["id"]

    def test_admin_list(self, api, verification_id):
        r = api.get(f"{BASE_URL}/api/verification-requests", params={"admin_token": ADMIN_TOKEN})
        assert r.status_code == 200
        ids = [d["id"] for d in r.json()]
        assert verification_id in ids

    def test_admin_list_forbidden(self, api):
        r = api.get(f"{BASE_URL}/api/verification-requests")
        assert r.status_code == 403

    def test_approve_flips_verified(self, api, verification_id):
        r = api.post(
            f"{BASE_URL}/api/verification-requests/{verification_id}/review",
            json={"decision": "approve", "admin_token": ADMIN_TOKEN, "reason": "ok"},
        )
        assert r.status_code == 200, r.text
        p = api.get(f"{BASE_URL}/api/properties/p-07").json()
        assert p.get("verified") is True


# -------- Subscription tiers + Analytics --------
class TestSubscriptionsAnalytics:
    def test_tiers(self, api):
        r = api.get(f"{BASE_URL}/api/agent-subscription-tiers")
        assert r.status_code == 200
        tiers = r.json()["tiers"]
        names = [t["name"] for t in tiers]
        for n in ("Gold", "Silver", "Bronze", "Unverified"):
            assert n in names
        for t in tiers:
            assert "perks" in t and isinstance(t["perks"], list)
            assert "monthly_price" in t and "annual_price" in t

    def test_agent_analytics(self, api):
        # Get an agent id
        agents = api.get(f"{BASE_URL}/api/agents").json()
        aid = agents[0]["id"] if isinstance(agents, list) else agents["agents"][0]["id"]
        r = api.get(f"{BASE_URL}/api/agents/{aid}/analytics")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["tier"] in ("Gold", "Silver", "Bronze", "Unverified")
        m = body["metrics"]
        for k in ("views_30d", "leads_30d", "conversion_pct", "profile_rank_city"):
            assert k in m
        assert len(body["trend_14d"]) == 14


# -------- Saved searches --------
class TestSavedSearches:
    @pytest.fixture(scope="class")
    def sid(self, api, test_user):
        r = api.post(f"{BASE_URL}/api/saved-searches", json={
            "user_id": test_user,
            "name": "TEST_3BHK_Jagatpura",
            "params": {"locality_id": "loc-jagatpura", "bedrooms": 3},
            "notify": True,
        })
        assert r.status_code == 200, r.text
        body = r.json()
        assert "last_match_count" in body
        return body["id"]

    def test_list(self, api, test_user, sid):
        r = api.get(f"{BASE_URL}/api/saved-searches", params={"user_id": test_user})
        assert r.status_code == 200
        assert any(d["id"] == sid for d in r.json())

    def test_matches(self, api, test_user, sid):
        r = api.get(f"{BASE_URL}/api/saved-searches/{sid}/matches", params={"user_id": test_user})
        assert r.status_code == 200
        body = r.json()
        assert "results" in body and "count" in body

    def test_delete(self, api, test_user, sid):
        r = api.delete(f"{BASE_URL}/api/saved-searches/{sid}", params={"user_id": test_user})
        assert r.status_code == 200
        # verify gone
        r2 = api.get(f"{BASE_URL}/api/saved-searches", params={"user_id": test_user})
        assert not any(d["id"] == sid for d in r2.json())


# -------- Locality compare --------
class TestLocalityCompare:
    def test_compare_two(self, api):
        r = api.get(f"{BASE_URL}/api/compare/localities",
                    params={"ids": "loc-jagatpura,loc-vaishali-nagar"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        for d in data:
            assert "lifestyle" in d
            assert "properties_count" in d
            assert "featured_count" in d


# -------- EMI --------
class TestEMI:
    def test_emi_basic(self, api):
        r = api.post(f"{BASE_URL}/api/finance/emi", json={
            "price": 7500000,
            "down_payment_pct": 20,
            "annual_rate_pct": 8.75,
            "tenure_years": 20,
            "monthly_income": 120000,
        })
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["emi"] > 0
        assert len(body["bank_offers"]) == 4
        assert body["eligibility"]["note"] is not None

    def test_emi_invalid(self, api):
        r = api.post(f"{BASE_URL}/api/finance/emi", json={"price": 0})
        assert r.status_code == 400


# -------- AI Valuation --------
class TestAIValuation:
    def test_ai_valuation_p02(self, api):
        r = api.get(f"{BASE_URL}/api/properties/p-02/ai-valuation", timeout=60)
        assert r.status_code == 200, r.text
        body = r.json()
        for k in ("fair_value_low", "fair_value_high", "confidence", "key_factors", "risks"):
            assert k in body
        assert body["fair_value_low"] <= body["fair_value_high"]

    def test_ai_valuation_cached(self, api):
        # Second call should be fast (cached)
        import time
        t0 = time.time()
        r = api.get(f"{BASE_URL}/api/properties/p-02/ai-valuation", timeout=30)
        dt = time.time() - t0
        assert r.status_code == 200
        assert dt < 5.0, f"cached call too slow: {dt}s"
