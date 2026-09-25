"""InfraLocal backend API tests"""
import os
import io
import pytest
import requests
from dotenv import load_dotenv

load_dotenv("/app/frontend/.env")
BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


# ---- Health ----
def test_health(s):
    r = s.get(f"{API}/health", timeout=30)
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"


# ---- Localities ----
def test_localities_list(s):
    r = s.get(f"{API}/localities", timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 7
    keys = {"id", "name", "median_price_per_sq_yd", "govt_dlc_per_sq_yd", "yoy_change_pct"}
    for loc in data:
        assert keys.issubset(loc.keys()), f"Missing keys in {loc}"
        assert "_id" not in loc


def test_locality_detail_jagatpura(s):
    r = s.get(f"{API}/localities/loc-jagatpura", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d["id"] == "loc-jagatpura"
    assert "price_history" in d and len(d["price_history"]) == 6
    ph0 = d["price_history"][0]
    for k in ("year", "listing", "govt", "est_low", "est_high"):
        assert k in ph0
    assert isinstance(d.get("infrastructure"), list)
    assert isinstance(d.get("news"), list)
    assert isinstance(d.get("properties_count"), int) and d["properties_count"] >= 1
    assert "_id" not in d


def test_locality_not_found(s):
    r = s.get(f"{API}/localities/loc-not-real", timeout=30)
    assert r.status_code == 404


# ---- Properties ----
def test_properties_list(s):
    r = s.get(f"{API}/properties?limit=100", timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # 30 seeded, some tests may create extras - ensure at least 30
    demo = [p for p in data if p.get("is_demo") is True]
    assert len(demo) == 30, f"Expected 30 demo properties, got {len(demo)}"
    for p in data:
        assert "_id" not in p
        assert "id" in p


def test_properties_filter_type(s):
    r = s.get(f"{API}/properties", params={"type": "Residential Plot"}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(p["type"] == "Residential Plot" for p in data)


def test_properties_filter_locality(s):
    r = s.get(f"{API}/properties", params={"locality_id": "loc-ajmer-road"}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(p["locality_id"] == "loc-ajmer-road" for p in data)


def test_properties_verified_only(s):
    r = s.get(f"{API}/properties", params={"verified_only": "true"}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(p["verified"] is True for p in data)


def test_properties_price_range(s):
    r = s.get(f"{API}/properties", params={"min_price": 5000000, "max_price": 15000000}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(5000000 <= p["price"] <= 15000000 for p in data)


def test_property_detail_p06(s):
    r = s.get(f"{API}/properties/p-06", timeout=30)
    assert r.status_code == 200
    p = r.json()
    assert p["id"] == "p-06"
    assert "_id" not in p
    assert "infravalue" in p
    iv = p["infravalue"]
    for k in ("low", "high", "confidence"):
        assert k in iv
    assert iv["low"] <= iv["high"]
    assert "govt_value" in p and isinstance(p["govt_value"], int)
    assert p.get("locality", {}).get("id") == "loc-jagatpura"


def test_property_not_found(s):
    r = s.get(f"{API}/properties/p-does-not-exist", timeout=30)
    assert r.status_code == 404


# ---- Auth ----
@pytest.fixture(scope="module")
def user(s):
    payload = {"name": "TEST User", "mobile": "9998887771", "area": "Jagatpura"}
    r = s.post(f"{API}/auth/onboard", json=payload, timeout=30)
    assert r.status_code == 200, r.text
    u = r.json()["user"]
    assert u["mobile"] == payload["mobile"]
    assert "id" in u and "created_at" in u
    return u


def test_onboard_upsert_same_mobile(s, user):
    payload = {"name": "TEST User Updated", "mobile": user["mobile"], "area": "Vaishali"}
    r = s.post(f"{API}/auth/onboard", json=payload, timeout=30)
    assert r.status_code == 200
    u2 = r.json()["user"]
    assert u2["id"] == user["id"], "upsert should return same id"


def test_onboard_invalid_mobile(s):
    r = s.post(f"{API}/auth/onboard", json={"name": "X", "mobile": "123"}, timeout=30)
    assert r.status_code == 400


def test_onboard_missing_mobile(s):
    r = s.post(f"{API}/auth/onboard", json={"name": "X", "mobile": ""}, timeout=30)
    assert r.status_code == 400


def test_auth_me(s, user):
    r = s.get(f"{API}/auth/me", params={"user_id": user["id"]}, timeout=30)
    assert r.status_code == 200
    assert r.json()["id"] == user["id"]


def test_auth_me_not_found(s):
    r = s.get(f"{API}/auth/me", params={"user_id": "no-such-user"}, timeout=30)
    assert r.status_code == 404


# ---- Create Property ----
def test_create_property(s, user):
    payload = {
        "title": "TEST 3 BHK Test Apt",
        "type": "Apartment",
        "price": 6500000,
        "area": 1200,
        "area_unit": "sq ft",
        "lat": 26.83,
        "lng": 75.85,
        "locality_id": "loc-jagatpura",
        "bedrooms": 3,
        "facing": "East",
        "source": "Owner",
        "owner_user_id": user["id"],
        "description": "Test property",
    }
    r = s.post(f"{API}/properties", json=payload, timeout=30)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["id"].startswith("p-user-")
    assert d["verified"] is False
    assert d["verification_status"] == "Verification Pending"
    assert d["locality_name"] == "Jagatpura"
    assert "_id" not in d
    # Persistence check
    g = s.get(f"{API}/properties/{d['id']}", timeout=30)
    assert g.status_code == 200
    assert g.json()["id"] == d["id"]


def test_create_property_bad_locality(s):
    payload = {
        "title": "x", "type": "Apartment", "price": 1000, "area": 100,
        "area_unit": "sq ft", "lat": 0, "lng": 0, "locality_id": "loc-fake",
    }
    r = s.post(f"{API}/properties", json=payload, timeout=30)
    assert r.status_code == 400


# ---- Saved ----
def test_saved_toggle_and_list(s, user):
    body = {"user_id": user["id"], "property_id": "p-06"}
    r1 = s.post(f"{API}/saved/toggle", json=body, timeout=30)
    assert r1.status_code == 200
    assert r1.json()["saved"] is True

    r_list = s.get(f"{API}/saved", params={"user_id": user["id"]}, timeout=30)
    assert r_list.status_code == 200
    lst = r_list.json()
    assert any(p["id"] == "p-06" for p in lst)

    r2 = s.post(f"{API}/saved/toggle", json=body, timeout=30)
    assert r2.status_code == 200
    assert r2.json()["saved"] is False

    r_list2 = s.get(f"{API}/saved", params={"user_id": user["id"]}, timeout=30)
    assert not any(p["id"] == "p-06" for p in r_list2.json())


# ---- Follows ----
def test_follow_toggle_and_list(s, user):
    body = {"user_id": user["id"], "locality_id": "loc-jagatpura"}
    r1 = s.post(f"{API}/follows/toggle", json=body, timeout=30)
    assert r1.status_code == 200
    assert r1.json()["following"] is True

    r_list = s.get(f"{API}/follows", params={"user_id": user["id"]}, timeout=30)
    assert r_list.status_code == 200
    lst = r_list.json()
    assert any(l["id"] == "loc-jagatpura" for l in lst)

    r2 = s.post(f"{API}/follows/toggle", json=body, timeout=30)
    assert r2.json()["following"] is False


# ---- Infrastructure ----
def test_infrastructure_list(s):
    r = s.get(f"{API}/infrastructure", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert len(d) == 7


def test_infrastructure_filter_jagatpura(s):
    r = s.get(f"{API}/infrastructure", params={"locality_id": "loc-jagatpura"}, timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert len(d) > 0
    assert all("loc-jagatpura" in x["locality_ids"] for x in d)


# ---- News ----
def test_news_list_sorted(s):
    r = s.get(f"{API}/news", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert len(d) >= 7
    dates = [n["date"] for n in d]
    assert dates == sorted(dates, reverse=True), "News should be sorted date desc"


def test_news_filter_category(s):
    r = s.get(f"{API}/news", params={"category": "Infrastructure"}, timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert len(d) > 0
    assert all(n["category"] == "Infrastructure" for n in d)


# ---- Upload ----
def test_upload_and_fetch(s):
    # 1x1 PNG bytes
    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?"
        b"\x00\x05\xfe\x02\xfe\xa2\xcd\x0e\x0e\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("test.png", io.BytesIO(png), "image/png")}
    # Remove content-type header for multipart
    up = requests.post(f"{API}/upload", files=files, timeout=60)
    if up.status_code >= 500:
        pytest.skip(f"Object storage unavailable: {up.status_code} {up.text[:200]}")
    assert up.status_code == 200, up.text
    j = up.json()
    assert "storage_path" in j and "url" in j
    # Fetch
    r = requests.get(f"{BASE_URL}{j['url']}", timeout=60)
    assert r.status_code == 200
    assert r.content == png or len(r.content) > 0
