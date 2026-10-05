"""Phase-3 Fix+Feature tests: finance category agents + locality search sanity."""
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    BASE_URL = "https://proptech-india-13.preview.emergentagent.com"


@pytest.fixture
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ------- Finance Advisors category -------
class TestFinanceCategory:
    def test_agent_categories_includes_finance(self, client):
        r = client.get(f"{BASE_URL}/api/agent-categories")
        assert r.status_code == 200
        cats = r.json()
        ids = [c["id"] for c in cats]
        assert "acat-finance" in ids, f"acat-finance missing from {ids}"
        fin = next(c for c in cats if c["id"] == "acat-finance")
        assert fin["name"] == "Finance & Investment Advisors"
        assert fin.get("agents_count", 0) >= 3

    def test_finance_category_returns_3_agents(self, client):
        r = client.get(f"{BASE_URL}/api/agents", params={"category_id": "acat-finance"})
        assert r.status_code == 200
        agents = r.json()
        assert len(agents) == 3
        names = {a["name"] for a in agents}
        assert "CA Nikhil Mehta" in names
        assert "Riya Khandelwal" in names
        assert "Suresh Kabra" in names

    def test_finance_agents_have_required_fields(self, client):
        r = client.get(f"{BASE_URL}/api/agents", params={"category_id": "acat-finance"})
        agents = r.json()
        for a in agents:
            assert "id" in a and a["id"].startswith("ag-")
            assert a.get("category_id") == "acat-finance"
            assert "specialization" in a or "name" in a
            assert "_id" not in a  # no mongo ObjectId leakage


# ------- Localities (used by /location-picker search) -------
class TestLocalitiesSearch:
    def test_localities_list_ok(self, client):
        r = client.get(f"{BASE_URL}/api/localities")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and len(data) > 0

    def test_search_vaishali(self, client):
        r = client.get(f"{BASE_URL}/api/localities")
        data = r.json()
        matches = [l for l in data if "vaishali" in l["name"].lower() or "vaishali" in l.get("city", "").lower()]
        assert len(matches) >= 1, "Vaishali search should return at least one locality"


# ------- Regression: core endpoints still 200 -------
class TestRegressionBasics:
    @pytest.mark.parametrize("path", [
        "/api/properties",
        "/api/news",
        "/api/agent-categories",
        "/api/market/categories",
        "/api/promote/plans",
        "/api/agent-subscription-tiers",
    ])
    def test_endpoint_200(self, client, path):
        r = client.get(f"{BASE_URL}{path}")
        assert r.status_code == 200, f"{path} -> {r.status_code}"
