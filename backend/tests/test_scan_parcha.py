"""Backend tests for the Parcha scanner (NEW feature) + Materials catalog sanity."""
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "https://proptech-india-13.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# --- Materials catalog sanity ---------------------------------------------
class TestMaterialsCatalog:
    def test_products_cement_returns_brands(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/materials/products", params={"q": "cement"}, timeout=20)
        assert r.status_code == 200, r.text
        items = r.json()
        assert isinstance(items, list) and len(items) > 0, "Expected cement products"
        brands = {(it.get("brand") or "").lower() for it in items}
        print("Brands found:", brands)
        # at least one of the expected brands must be present
        expected = {"ultratech", "ambuja", "shree"}
        assert any(b for b in brands if any(e in b for e in expected)), f"No expected cement brand in {brands}"


# --- Scan Parcha pipeline sanity ------------------------------------------
class TestScanParcha:
    def test_scan_parcha_returns_shape(self, api_client):
        # Use picsum (reliably reachable) — LLM may return empty items for an irrelevant image,
        # pass criterion per prompt is "no crash + correct shape".
        payload = {
            "image_url": "https://picsum.photos/seed/parcha-test/400/600.jpg"
        }
        r = api_client.post(f"{BASE_URL}/api/materials/scan-parcha", json=payload, timeout=90)
        assert r.status_code == 200, r.text
        data = r.json()
        print("scan-parcha keys:", list(data.keys()))
        # must have all 4 keys
        for k in ["items", "unmatched", "total_estimated", "extracted"]:
            assert k in data, f"Missing key {k} in response"
        assert isinstance(data["items"], list)
        assert isinstance(data["unmatched"], list)
        assert isinstance(data["extracted"], list)
        assert isinstance(data["total_estimated"], (int, float))
