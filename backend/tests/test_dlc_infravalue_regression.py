"""Backend regression: DLC/InfraValue UI removal must not alter backend payloads."""
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_BACKEND_URL") or "https://proptech-india-13.preview.emergentagent.com"
BASE_URL = BASE_URL.rstrip("/")


# properties endpoint untouched (listings still carry price_per_unit/verified)
class TestPropertiesPayloadIntact:
    def test_properties_list(self):
        r = requests.get(f"{BASE_URL}/api/properties", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and len(data) > 0
        p = data[0]
        for key in ("id", "title", "price", "area", "area_unit", "price_per_unit",
                    "verified", "images", "locality_name"):
            assert key in p, f"missing {key} in property payload"
        assert isinstance(p["price_per_unit"], (int, float))
        assert isinstance(p["verified"], bool)

    def test_property_detail_still_has_infravalue_and_govt(self):
        # UI removed but backend MUST still return these (per request).
        r = requests.get(f"{BASE_URL}/api/properties/p-06", timeout=15)
        assert r.status_code == 200
        p = r.json()
        assert "infravalue" in p, "backend removed infravalue (should remain)"
        assert "govt_value" in p, "backend removed govt_value (should remain)"
        iv = p["infravalue"]
        for k in ("low", "high", "confidence"):
            assert k in iv


# localities endpoint untouched
class TestLocalitiesPayloadIntact:
    def test_localities_list_has_dlc_and_range(self):
        r = requests.get(f"{BASE_URL}/api/localities", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0
        l = data[0]
        for key in ("govt_dlc_per_sq_yd", "estimated_range_low",
                    "estimated_range_high", "confidence"):
            assert key in l, f"missing {key} in locality payload"

    def test_locality_detail_price_history_series(self):
        # Price history must still have govt/est_low/est_high even though UI hides them
        r = requests.get(f"{BASE_URL}/api/localities/loc-jagatpura", timeout=15)
        assert r.status_code == 200
        l = r.json()
        ph = l.get("price_history") or []
        assert len(ph) > 0
        for key in ("year", "listing", "govt", "est_low", "est_high"):
            assert key in ph[0], f"price_history point missing {key}"


# compare endpoint still returns listing fields used by the UI table
class TestComparePayload:
    def test_compare_two_ids(self):
        r = requests.get(f"{BASE_URL}/api/compare?ids=p-06,p-07", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and len(data) == 2
        for p in data:
            for key in ("id", "title", "price", "area", "area_unit",
                        "price_per_unit", "type", "source", "verified",
                        "locality_name"):
                assert key in p, f"missing {key} in compare payload"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
