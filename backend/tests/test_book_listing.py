# Tests for the new "Book" listing_type (b-01..b-06) feature in Explore
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "https://proptech-india-13.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# --- 1. listing_type=Book returns exactly 6 book properties, no _id leak ---
class TestBookListing:
    def test_book_list_count_and_ids(self, api):
        r = api.get(f"{BASE_URL}/api/properties", params={"listing_type": "Book"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 6, f"Expected 6 Book props, got {len(data)}"
        ids = sorted(p["id"] for p in data)
        assert ids == ["b-01", "b-02", "b-03", "b-04", "b-05", "b-06"]
        for p in data:
            assert p["listing_type"] == "Book"
            assert "_id" not in p, "MongoDB _id leaked in response"

    def test_book_titles_contain_expected_tokens(self, api):
        r = api.get(f"{BASE_URL}/api/properties", params={"listing_type": "Book"})
        titles = " | ".join(p["title"] for p in r.json())
        for token in ["Pre-Launch", "Under Construction", "Book @", "New Launch", "Plotted Township"]:
            assert token in titles, f"Missing token '{token}' in titles: {titles}"


# --- 2. listing_type=Book&type=Villa -> 2 villas (b-02, b-06) ---
class TestBookVillaFilter:
    def test_book_villa_filter(self, api):
        r = api.get(f"{BASE_URL}/api/properties", params={"listing_type": "Book", "type": "Villa"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        ids = sorted(p["id"] for p in data)
        assert ids == ["b-02", "b-06"]
        for p in data:
            assert p["type"] == "Villa"
            assert p["listing_type"] == "Book"
        titles = " ".join(p["title"] for p in data)
        assert "Mahima Elanza" in titles
        assert "Royal Palms Villas" in titles


# --- 3. listing_type=Buy still 30 items, no b-* or r-* ---
class TestBuyRegression:
    def test_buy_still_30(self, api):
        r = api.get(f"{BASE_URL}/api/properties", params={"listing_type": "Buy"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 30, f"Expected 30 Buy props, got {len(data)}"
        for p in data:
            pid = p["id"]
            assert not pid.startswith("b-"), f"Book id {pid} leaked into Buy"
            assert not pid.startswith("r-"), f"Rent id {pid} leaked into Buy"
            assert p["listing_type"] == "Buy"


# --- 4. listing_type=Rent still 6 items with r-01..r-06 ---
class TestRentRegression:
    def test_rent_still_6(self, api):
        r = api.get(f"{BASE_URL}/api/properties", params={"listing_type": "Rent"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 6
        ids = sorted(p["id"] for p in data)
        assert ids == ["r-01", "r-02", "r-03", "r-04", "r-05", "r-06"]
        for p in data:
            assert p["listing_type"] == "Rent"


# --- 5. GET /api/properties/b-01 ---
class TestBookDetail:
    def test_b01_detail(self, api):
        r = api.get(f"{BASE_URL}/api/properties/b-01")
        assert r.status_code == 200
        p = r.json()
        assert p["id"] == "b-01"
        assert p["listing_type"] == "Book"
        assert "_id" not in p
        # expect enrichments
        assert "infravalue" in p, f"Missing infravalue in b-01: {list(p.keys())}"
        assert "govt_value" in p, f"Missing govt_value in b-01: {list(p.keys())}"
        assert "lister" in p, f"Missing lister in b-01: {list(p.keys())}"
        # source="Developer" for b-* => lister type Developer
        assert p["lister"].get("type") == "Developer", f"Expected lister type Developer, got {p['lister']}"


# --- 6. GET /api/properties/b-01/similar ---
class TestBookSimilar:
    def test_b01_similar(self, api):
        r = api.get(f"{BASE_URL}/api/properties/b-01/similar")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0, "similar should return at least one item"
        ids = [p["id"] for p in data]
        for p in data:
            assert p["listing_type"] == "Book", f"Non-Book in similar: {p['id']}={p['listing_type']}"
            assert p["type"] == "Apartment", f"Non-Apartment in similar: {p['id']}={p['type']}"
            assert p["id"] != "b-01"
            assert not p["id"].startswith("p-"), f"Buy prop leaked: {p['id']}"
            assert not p["id"].startswith("r-"), f"Rent prop leaked: {p['id']}"
        assert "b-03" in ids, f"Expected b-03 in similar, got {ids}"
