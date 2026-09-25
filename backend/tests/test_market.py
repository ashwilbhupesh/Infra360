"""Tests for the new InfraLocal Market (construction ecosystem) endpoints.

Only new endpoints tested here; existing 25 tests live in backend_test.py.
Base URL uses EXPO_PUBLIC_BACKEND_URL from /app/frontend/.env.
"""
import os
import pytest
import requests
from dotenv import load_dotenv

# Load frontend env to pick up EXPO_PUBLIC_BACKEND_URL (public preview URL)
load_dotenv("/app/frontend/.env")

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL")
assert BASE_URL, "EXPO_PUBLIC_BACKEND_URL must be set in /app/frontend/.env"
BASE_URL = BASE_URL.rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _assert_no_underscore_id(obj):
    """Recursively verify `_id` is never present anywhere in the payload."""
    if isinstance(obj, dict):
        assert "_id" not in obj, f"_id leaked in dict: keys={list(obj.keys())}"
        for v in obj.values():
            _assert_no_underscore_id(v)
    elif isinstance(obj, list):
        for item in obj:
            _assert_no_underscore_id(item)


# ---------- Groups ----------
class TestMarketGroups:
    def test_groups_returns_6_with_categories(self, api_client):
        r = api_client.get(f"{API}/market/groups")
        assert r.status_code == 200, r.text
        groups = r.json()
        assert isinstance(groups, list)
        assert len(groups) == 6, f"expected 6 groups, got {len(groups)}"

        names = {g["name"] for g in groups}
        assert names == {"Design", "Build", "Materials", "Interiors", "Move In", "Maintenance"}

        for g in groups:
            for field in ("id", "name", "subtitle", "icon", "categories"):
                assert field in g, f"group missing field {field}: {g}"
            assert isinstance(g["categories"], list)
            for c in g["categories"]:
                assert "suppliers_count" in c
                assert isinstance(c["suppliers_count"], int)

        # No _id leaked anywhere in the payload
        _assert_no_underscore_id(groups)

    def test_counts_positive_for_cement_contractors_architects(self, api_client):
        r = api_client.get(f"{API}/market/groups")
        assert r.status_code == 200
        groups = r.json()
        cat_by_id = {}
        for g in groups:
            for c in g["categories"]:
                cat_by_id[c["id"]] = c
        for cat_id in ("cat-cement", "cat-contractors", "cat-architects"):
            assert cat_id in cat_by_id, f"missing category {cat_id}"
            assert cat_by_id[cat_id]["suppliers_count"] > 0, (
                f"{cat_id} suppliers_count not > 0: {cat_by_id[cat_id]}"
            )


# ---------- Categories ----------
class TestMarketCategories:
    def test_all_categories(self, api_client):
        r = api_client.get(f"{API}/market/categories")
        assert r.status_code == 200, r.text
        cats = r.json()
        assert isinstance(cats, list)
        assert len(cats) == 24, f"expected 24 categories, got {len(cats)}"
        for c in cats:
            for field in ("id", "group_id", "name", "image"):
                assert field in c, f"category missing {field}: {c}"
        _assert_no_underscore_id(cats)

    def test_categories_filtered_by_group_materials(self, api_client):
        r = api_client.get(f"{API}/market/categories", params={"group_id": "grp-materials"})
        assert r.status_code == 200, r.text
        cats = r.json()
        assert len(cats) == 9, f"expected 9 materials categories, got {len(cats)}"
        for c in cats:
            assert c["group_id"] == "grp-materials", c


# ---------- Suppliers list ----------
class TestSuppliersList:
    def test_suppliers_shape_and_no_id(self, api_client):
        r = api_client.get(f"{API}/market/suppliers")
        assert r.status_code == 200, r.text
        suppliers = r.json()
        assert isinstance(suppliers, list)
        # spec: ~26 suppliers
        assert 24 <= len(suppliers) <= 30, f"unexpected supplier count: {len(suppliers)}"
        for s in suppliers:
            for field in ("rating", "reviews", "verified", "featured", "offerings"):
                assert field in s, f"supplier missing field {field}: {s.get('id')}"
            assert isinstance(s["offerings"], list)
            assert isinstance(s["rating"], (int, float))
            assert isinstance(s["reviews"], int)
            assert isinstance(s["verified"], bool)
            assert isinstance(s["featured"], bool)
        _assert_no_underscore_id(suppliers)

    def test_filter_by_category_cement(self, api_client):
        r = api_client.get(f"{API}/market/suppliers", params={"category_id": "cat-cement"})
        assert r.status_code == 200
        arr = r.json()
        assert len(arr) == 2, f"expected 2 cement suppliers, got {len(arr)}"
        for s in arr:
            assert s["category_id"] == "cat-cement"

    def test_filter_by_group_materials(self, api_client):
        r = api_client.get(f"{API}/market/suppliers", params={"group_id": "grp-materials"})
        assert r.status_code == 200
        arr = r.json()
        assert len(arr) >= 8, f"expected >= 8 materials suppliers, got {len(arr)}"
        # Fetch materials category ids
        cats_r = api_client.get(f"{API}/market/categories", params={"group_id": "grp-materials"})
        material_cat_ids = {c["id"] for c in cats_r.json()}
        for s in arr:
            assert s["category_id"] in material_cat_ids, (
                f"supplier {s['id']} has category_id={s['category_id']} not in materials"
            )

    def test_featured_only(self, api_client):
        r = api_client.get(f"{API}/market/suppliers", params={"featured_only": "true"})
        assert r.status_code == 200
        arr = r.json()
        assert len(arr) > 0, "expected at least one featured supplier"
        for s in arr:
            assert s["featured"] is True, s

    def test_verified_only(self, api_client):
        r = api_client.get(f"{API}/market/suppliers", params={"verified_only": "true"})
        assert r.status_code == 200
        arr = r.json()
        assert len(arr) > 0
        for s in arr:
            assert s["verified"] is True, s

    def test_search_q_cement(self, api_client):
        r = api_client.get(f"{API}/market/suppliers", params={"q": "cement"})
        assert r.status_code == 200
        arr = r.json()
        assert len(arr) > 0, "expected matches for 'cement'"
        for s in arr:
            hay = " ".join(
                [s.get("name", ""), s.get("tagline", "")] + list(s.get("offerings", []))
            ).lower()
            assert "cement" in hay, f"supplier {s['id']} does not match 'cement': {hay}"

    def test_filter_by_city_jaipur(self, api_client):
        r = api_client.get(f"{API}/market/suppliers", params={"city": "Jaipur"})
        assert r.status_code == 200
        arr = r.json()
        assert len(arr) > 0
        for s in arr:
            assert s["city"] == "Jaipur"


# ---------- Supplier detail ----------
class TestSupplierDetail:
    def test_supplier_detail_with_category(self, api_client):
        r = api_client.get(f"{API}/market/suppliers/sup-01")
        assert r.status_code == 200, r.text
        s = r.json()
        assert s["id"] == "sup-01"
        assert "category" in s and isinstance(s["category"], dict)
        assert s["category"]["name"] == "Architects", s["category"]
        _assert_no_underscore_id(s)

    def test_supplier_not_found(self, api_client):
        r = api_client.get(f"{API}/market/suppliers/does-not-exist")
        assert r.status_code == 404, r.text


# ---------- Quote requests ----------
class TestQuoteRequests:
    def test_create_quote_and_persist(self, api_client):
        payload = {
            "supplier_id": "sup-06",
            "name": "TEST_ User",
            "mobile": "9876543210",
            "message": "Need turnkey villa quote",
        }
        r = api_client.post(f"{API}/market/quote-requests", json=payload)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "id" in body and body["id"].startswith("qr-"), body
        assert body.get("status") == "New", body

        # Persistence check via mongo (best-effort). If MONGO_URL not reachable,
        # fall back to trusting the API response.
        try:
            from pymongo import MongoClient
            from dotenv import load_dotenv as _ld

            _ld("/app/backend/.env")
            mongo_url = os.environ.get("MONGO_URL")
            db_name = os.environ.get("DB_NAME")
            if mongo_url and db_name:
                client = MongoClient(mongo_url, serverSelectionTimeoutMS=2000)
                found = client[db_name].quote_requests.find_one({"id": body["id"]})
                assert found is not None, f"quote {body['id']} not persisted in db"
                assert found["supplier_id"] == "sup-06"
                assert found["mobile"] == "9876543210"
                # cleanup TEST_ data
                client[db_name].quote_requests.delete_one({"id": body["id"]})
        except ImportError:
            pass

    def test_create_quote_invalid_supplier(self, api_client):
        payload = {
            "supplier_id": "sup-does-not-exist",
            "name": "TEST_ Ghost",
            "mobile": "9000000000",
            "message": "should 404",
        }
        r = api_client.post(f"{API}/market/quote-requests", json=payload)
        assert r.status_code == 404, r.text
