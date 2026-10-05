"""Backend tests for iteration 17 — Experts category (Sales & Marketing),
parcha-scans history endpoints, voice-cart and voice-search endpoints.
"""
import io
import math
import os
import struct
import wave

import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/") or os.environ.get("EXPO_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "EXPO_PUBLIC_BACKEND_URL must be set"
API = f"{BASE_URL}/api"


# ---------- helpers ----------
def _wav_bytes(seconds: float = 1.0, freq: int = 440, rate: int = 16000) -> bytes:
    """Generate a tiny PCM WAV sine wave so the file is >2048 bytes and well-formed."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        n = int(seconds * rate)
        for i in range(n):
            val = int(0.3 * 32767 * math.sin(2 * math.pi * freq * i / rate))
            w.writeframes(struct.pack("<h", val))
    return buf.getvalue()


# ---------- Agent categories & agents ----------
class TestExperts:
    def test_sales_marketing_category_present(self):
        r = requests.get(f"{API}/agent-categories", timeout=15)
        assert r.status_code == 200
        cats = r.json()
        ids = {c["id"] for c in cats}
        assert "acat-sales-marketing" in ids, f"Missing sales-marketing category. Got: {ids}"
        assert "acat-finance" in ids, "Finance category also expected"
        sm = next(c for c in cats if c["id"] == "acat-sales-marketing")
        assert sm["name"] == "Sales & Marketing Agencies"
        assert sm.get("agents_count", 0) >= 3

    def test_sales_marketing_agents_listed(self):
        r = requests.get(f"{API}/agents", params={"category_id": "acat-sales-marketing"}, timeout=15)
        assert r.status_code == 200
        agents = r.json()
        assert isinstance(agents, list)
        names = {a["name"] for a in agents}
        expected = {"Pulse Realty Marketing", "StoreyBoard Studio", "GroundUp Channel Partners"}
        assert expected.issubset(names), f"Missing agents. Got: {names}"
        for a in agents:
            assert "_id" not in a
            assert a["category_id"] == "acat-sales-marketing"


# ---------- Parcha scans ----------
class TestParchaScans:
    def test_list_parcha_scans_shape(self):
        r = requests.get(f"{API}/materials/parcha-scans", params={"limit": 5}, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        if data:
            d = data[0]
            for key in ("id", "created_at", "items_count", "unmatched_count", "total_estimated"):
                assert key in d, f"Missing key {key} in scan: {d.keys()}"
            assert "_id" not in d
            # list payload should be trimmed (no raw extracted)
            assert "extracted" not in d

    def test_get_single_scan_or_404(self):
        # Grab the latest scan id if available
        r = requests.get(f"{API}/materials/parcha-scans", params={"limit": 1}, timeout=15)
        assert r.status_code == 200
        lst = r.json()
        if not lst:
            # No scans in DB — assert 404 path
            r2 = requests.get(f"{API}/materials/parcha-scans/does-not-exist", timeout=10)
            assert r2.status_code == 404
            pytest.skip("No scans in DB — nothing to GET by id")
        sid = lst[0]["id"]
        r2 = requests.get(f"{API}/materials/parcha-scans/{sid}", timeout=15)
        assert r2.status_code == 200
        d = r2.json()
        assert d["id"] == sid
        assert "items" in d, "Full scan payload must include items array"
        assert isinstance(d["items"], list)
        assert "_id" not in d


# ---------- Voice cart ----------
class TestVoiceCart:
    def test_voice_cart_short_audio_400(self):
        """A clip <2048 bytes should return 400 'Recording too short'."""
        files = {"file": ("tiny.webm", b"x" * 100, "audio/webm")}
        r = requests.post(f"{API}/materials/voice-cart", files=files, timeout=20)
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text[:200]}"
        assert "short" in r.text.lower()

    def test_voice_cart_sine_wav_contract(self):
        """A real-ish WAV >2048 bytes: must not 500 and must return the documented keys."""
        wav = _wav_bytes(seconds=1.2)
        assert len(wav) > 2048
        files = {"file": ("sine.wav", wav, "audio/wav")}
        r = requests.post(f"{API}/materials/voice-cart", files=files, timeout=60)
        # Must not 500. 200 with documented keys expected (sine → likely no_speech)
        assert r.status_code == 200, f"Non-200: {r.status_code} {r.text[:300]}"
        data = r.json()
        for key in ("transcript", "translation", "items", "unmatched", "total_estimated"):
            assert key in data, f"Missing key {key} in voice-cart response: {data.keys()}"
        assert isinstance(data["items"], list)
        assert isinstance(data["unmatched"], list)


# ---------- Voice search ----------
class TestVoiceSearch:
    def test_voice_search_short_audio_400(self):
        files = {"file": ("tiny.webm", b"x" * 100, "audio/webm")}
        r = requests.post(f"{API}/explore/voice-search", files=files, timeout=20)
        assert r.status_code == 400
        assert "short" in r.text.lower()

    def test_voice_search_sine_wav_contract(self):
        wav = _wav_bytes(seconds=1.2)
        files = {"file": ("sine.wav", wav, "audio/wav")}
        r = requests.post(f"{API}/explore/voice-search", files=files, timeout=60)
        assert r.status_code == 200, f"Non-200: {r.status_code} {r.text[:300]}"
        data = r.json()
        for key in ("transcript", "filters", "summary"):
            assert key in data, f"Missing key {key} in voice-search response: {data.keys()}"
        assert isinstance(data["filters"], dict)
