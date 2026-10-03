"""Backend tests for the new Materials shopping endpoints + regression on existing APIs."""
import os
import pytest
import requests

BASE_URL = os.environ["EXPO_PUBLIC_BACKEND_URL"].rstrip("/")

EXPECTED_CATS = [
    "Cement & steel",
    "Electricals & lighting",
    "Bathware",
    "Tiling & adhesives",
    "Paints & finishes",
    "Electrical appliances",
    "Water proofing",
    # seed uses "CPVC, PVC & GI fittings"
    "CPVC, PVC & GI fittings",
    "Hardware & locks",
    "Plywood & laminates",
]


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------------- Categories ----------------
class TestMaterialsCategories:
    def test_list_categories(self, api):
        r = api.get(f"{BASE_URL}/api/materials/categories", timeout=20)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 10, f"Expected 10 categories, got {len(data)}"
        # Order by `order` field (1..10)
        orders = [c.get("order") for c in data]
        assert orders == sorted(orders), f"Not ordered by `order`: {orders}"
        names = [c["name"] for c in data]
        assert names == EXPECTED_CATS, f"Mismatch names: {names}"
        for c in data:
            assert c.get("stores_count", 0) >= 1, f"{c['id']} has 0 stores"
            assert "image" in c and c["image"]


# ---------------- Stores in category ----------------
class TestStoresInCategory:
    def test_cement_steel_stores(self, api):
        r = api.get(f"{BASE_URL}/api/materials/categories/mat-cement-steel/stores", timeout=20)
        assert r.status_code == 200
        stores = r.json()
        assert isinstance(stores, list)
        assert len(stores) >= 3, f"Expected >=3 stores, got {len(stores)}"
        # Featured first
        feats = [bool(s.get("featured", False)) for s in stores]
        assert feats == sorted(feats, reverse=True), f"Featured not first: {feats}"
        for s in stores:
            assert "products" in s and isinstance(s["products"], list)
            assert len(s["products"]) > 0, f"Store {s['id']} has no products"
            assert s.get("products_count") == len(s["products"])
            for p in s["products"]:
                assert p["category_id"] == "mat-cement-steel"
                assert p["store_id"] == s["id"]


# ---------------- Store detail ----------------
class TestStoreDetail:
    def test_steel_syndicate(self, api):
        r = api.get(f"{BASE_URL}/api/materials/stores/mst-steelsynd", timeout=20)
        assert r.status_code == 200
        s = r.json()
        assert s["id"] == "mst-steelsynd"
        assert "catalogue" in s and isinstance(s["catalogue"], list)
        assert len(s["catalogue"]) >= 1
        for section in s["catalogue"]:
            assert "category" in section and "products" in section
            for p in section["products"]:
                assert p["store_id"] == "mst-steelsynd"
        assert s.get("products_count", 0) > 0

    def test_store_not_found(self, api):
        r = api.get(f"{BASE_URL}/api/materials/stores/mst-does-not-exist", timeout=20)
        assert r.status_code == 404


# ---------------- Product search ----------------
class TestProductSearch:
    def test_search_cement(self, api):
        r = api.get(f"{BASE_URL}/api/materials/products?q=cement", timeout=20)
        assert r.status_code == 200
        prods = r.json()
        assert isinstance(prods, list)
        assert len(prods) > 0
        for p in prods:
            assert "cement" in (p.get("name", "") + p.get("brand", "")).lower()
            assert "store" in p and p["store"] is not None
            assert "name" in p["store"]


# ---------------- Cart enquiry ----------------
class TestCartEnquiry:
    def test_create_enquiry_success(self, api):
        payload = {
            "name": "TEST User",
            "mobile": "9876543210",
            "items": [
                {"product_id": "p-mat-001", "store_id": "mst-balaji", "qty": 10},
                {"product_id": "p-mat-005", "store_id": "mst-steelsynd", "qty": 100},
            ],
        }
        r = api.post(f"{BASE_URL}/api/materials/cart-enquiry", json=payload, timeout=20)
        assert r.status_code == 200, r.text
        doc = r.json()
        assert doc["status"] == "New"
        # Expected totals: 10*385 + 100*62 = 3850 + 6200 = 10050
        assert doc["total"] == 10050, f"Total mismatch: {doc['total']}"
        assert len(doc["per_store"]) == 2
        subtotals = {bucket["store"]["id"]: bucket["subtotal"] for bucket in doc["per_store"]}
        assert subtotals["mst-balaji"] == 3850
        assert subtotals["mst-steelsynd"] == 6200

    def test_empty_items_400(self, api):
        payload = {"name": "x", "mobile": "9876543210", "items": []}
        r = api.post(f"{BASE_URL}/api/materials/cart-enquiry", json=payload, timeout=20)
        assert r.status_code == 400

    def test_invalid_mobile_400(self, api):
        payload = {
            "name": "x", "mobile": "12345",
            "items": [{"product_id": "p-mat-001", "store_id": "mst-balaji", "qty": 1}],
        }
        r = api.post(f"{BASE_URL}/api/materials/cart-enquiry", json=payload, timeout=20)
        assert r.status_code == 400


# ---------------- User activity ----------------
class TestUserActivity:
    def test_materials_orders_field(self, api):
        # create a user first
        r = api.post(
            f"{BASE_URL}/api/auth/onboard",
            json={"name": "TEST Activity", "mobile": "9999900001"},
            timeout=20,
        )
        assert r.status_code == 200, r.text
        uid = r.json()["user"]["id"]

        r2 = api.get(f"{BASE_URL}/api/user/{uid}/activity", timeout=20)
        assert r2.status_code == 200
        data = r2.json()
        assert "materials_orders" in data
        assert isinstance(data["materials_orders"], list)

    def test_materials_order_links_user(self, api):
        r = api.post(
            f"{BASE_URL}/api/auth/onboard",
            json={"name": "TEST Mat Order", "mobile": "9999900002"},
            timeout=20,
        )
        uid = r.json()["user"]["id"]
        payload = {
            "user_id": uid,
            "name": "TEST Mat Order",
            "mobile": "9999900002",
            "items": [{"product_id": "p-mat-001", "store_id": "mst-balaji", "qty": 2}],
        }
        rc = api.post(f"{BASE_URL}/api/materials/cart-enquiry", json=payload, timeout=20)
        assert rc.status_code == 200
        ra = api.get(f"{BASE_URL}/api/user/{uid}/activity", timeout=20)
        assert ra.status_code == 200
        orders = ra.json()["materials_orders"]
        assert len(orders) >= 1
        assert orders[0]["mobile"] == "9999900002"


# ---------------- Regression: existing APIs still work ----------------
class TestRegression:
    def test_market_groups(self, api):
        r = api.get(f"{BASE_URL}/api/market/groups", timeout=20)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) > 0

    def test_market_suppliers(self, api):
        r = api.get(f"{BASE_URL}/api/market/suppliers?featured_only=true", timeout=20)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_properties(self, api):
        r = api.get(f"{BASE_URL}/api/properties?limit=5", timeout=20)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_agents(self, api):
        r = api.get(f"{BASE_URL}/api/agents?limit=5", timeout=20)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
