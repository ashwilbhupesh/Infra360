"""Tests for the NEW enrichment behaviour: lifestyle scores on localities and tier on agents."""
import os
import math
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL") or os.environ.get("EXPO_BACKEND_URL")
if not BASE_URL:
    # Fallback: read from frontend/.env
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("EXPO_PUBLIC_BACKEND_URL="):
                BASE_URL = line.strip().split("=", 1)[1]
                break
BASE_URL = BASE_URL.rstrip("/")


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------- Localities: lifestyle enrichment ----------

class TestLocalityLifestyle:
    def test_list_localities_have_lifestyle(self, api):
        r = api.get(f"{BASE_URL}/api/localities", timeout=20)
        assert r.status_code == 200, r.text
        data = r.json()
        assert isinstance(data, list) and len(data) > 0
        for loc in data:
            assert "_id" not in loc, f"leaking _id in {loc.get('id')}"
            assert "lifestyle" in loc, f"missing lifestyle in {loc.get('id')}"
            ls = loc["lifestyle"]
            for k in ("walkability", "schools", "hospitals", "connectivity", "safety", "overall"):
                assert k in ls, f"missing {k} in {loc.get('id')}"
                assert isinstance(ls[k], int), f"{k} not int in {loc.get('id')} (got {type(ls[k]).__name__})"
                assert 0 <= ls[k] <= 100, f"{k} out of range in {loc.get('id')}"
            expected_overall = round((ls["walkability"] + ls["schools"] + ls["hospitals"] + ls["connectivity"] + ls["safety"]) / 5)
            assert ls["overall"] == expected_overall, f"overall wrong for {loc.get('id')}: got {ls['overall']}, expected {expected_overall}"

    def test_jagatpura_lifestyle_values(self, api):
        r = api.get(f"{BASE_URL}/api/localities/loc-jagatpura", timeout=20)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "_id" not in data
        ls = data["lifestyle"]
        assert ls["walkability"] == 76
        assert ls["schools"] == 88
        assert ls["hospitals"] == 78
        assert ls["connectivity"] == 85
        assert ls["safety"] == 82
        assert ls["overall"] == 82
        assert "notes" in ls and isinstance(ls["notes"], str)
        assert "schools" in ls["notes"].lower()

    def test_sirsi_road_lifestyle_values(self, api):
        r = api.get(f"{BASE_URL}/api/localities/loc-sirsi-road", timeout=20)
        assert r.status_code == 200, r.text
        ls = r.json()["lifestyle"]
        assert ls["walkability"] == 55
        assert ls["schools"] == 58
        assert ls["hospitals"] == 52
        # overall = round((55+58+52+74+65)/5) = round(60.8) = 61
        assert ls["overall"] == 61

    def test_nonexistent_locality_404(self, api):
        r = api.get(f"{BASE_URL}/api/localities/loc-nonexistent", timeout=20)
        assert r.status_code == 404


# ---------- Agents: tier enrichment ----------

VALID_TIERS = {"Gold", "Silver", "Bronze", "Unverified"}


class TestAgentTiers:
    def test_list_agents_have_tier(self, api):
        r = api.get(f"{BASE_URL}/api/agents", timeout=20)
        assert r.status_code == 200, r.text
        agents = r.json()
        assert isinstance(agents, list) and len(agents) > 0
        for ag in agents:
            assert "_id" not in ag, f"leaking _id in {ag.get('id')}"
            assert "tier" in ag, f"missing tier in {ag.get('id')}"
            assert ag["tier"] in VALID_TIERS, f"invalid tier for {ag.get('id')}: {ag['tier']}"

    def test_ag01_ashok_gold(self, api):
        r = api.get(f"{BASE_URL}/api/agents/ag-01", timeout=20)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "_id" not in data
        assert data["tier"] == "Gold", data

    def test_ag03_rohit_unverified(self, api):
        r = api.get(f"{BASE_URL}/api/agents/ag-03", timeout=20)
        assert r.status_code == 200, r.text
        assert r.json()["tier"] == "Unverified"

    def test_ag06_manish_silver(self, api):
        r = api.get(f"{BASE_URL}/api/agents/ag-06", timeout=20)
        assert r.status_code == 200, r.text
        assert r.json()["tier"] == "Silver"

    def test_ag13_karan_bronze(self, api):
        r = api.get(f"{BASE_URL}/api/agents/ag-13", timeout=20)
        assert r.status_code == 200, r.text
        assert r.json()["tier"] == "Bronze"
