import io

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.ef_estimation import model as m
from app.main import app

client = TestClient(app)


def _avi_bytes(n_frames=40, w=112, h=112, tmp_dir=None):
    import os
    import tempfile

    path = os.path.join(tempfile.mkdtemp(), "v.avi")
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MJPG"), 25, (w, h))
    rng = np.random.default_rng(0)
    for _ in range(n_frames):
        vw.write(rng.integers(0, 255, (h, w, 3), dtype=np.uint8))
    vw.release()
    return open(path, "rb").read()


def _upload(data: bytes, name: str):
    return client.post("/uploads", files={"file": (name, io.BytesIO(data))})


class FakeSession:
    """Stands in for the ONNX session so the pipeline can be tested without weights."""

    def __init__(self, value=0.6):
        self.value, self.calls = value, []

    def run(self, names, feed):
        clip = feed["clip"]
        assert clip.shape == (1, 3, 32, 112, 112) and clip.dtype == np.float32
        self.calls.append(clip)
        return [np.array([self.value], dtype=np.float32)]


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_upload_roundtrip_and_empty_rejected():
    r = _upload(b"abc", "a.avi")
    assert r.status_code == 200 and r.json()["file_url"].endswith(".avi")
    assert _upload(b"", "a.avi").status_code == 400


def test_predict_without_weights_returns_fallback(monkeypatch):
    monkeypatch.setattr(m, "_model_available", lambda: False)
    monkeypatch.setattr(m, "_session", None)
    url = _upload(_avi_bytes(), "v.avi").json()["file_url"]
    r = client.post("/ef-estimation/predict", json={"file_url": url})
    assert r.status_code == 200
    assert "weights not found" in r.json()["summary"]


def test_predict_rejects_non_video():
    url = _upload(b"this is not a video", "notes.txt").json()["file_url"]
    r = client.post("/ef-estimation/predict", json={"file_url": url})
    assert r.status_code == 422 and "detail" in r.json()


def test_predict_uses_model_and_classifies(monkeypatch):
    fake = FakeSession(0.6)
    monkeypatch.setattr(m, "_session", fake)
    url = _upload(_avi_bytes(60), "v.avi").json()["file_url"]
    j = client.post("/ef-estimation/predict", json={"file_url": url}).json()
    assert j["ejection_fraction"] == 60.0
    assert j["classification"] == "normal"
    assert j["clips_used"] == len(fake.calls) >= 1
    assert j["ef_range"] == [60.0, 60.0]


def test_short_video_still_predicts(monkeypatch):
    monkeypatch.setattr(m, "_session", FakeSession(0.4))
    url = _upload(_avi_bytes(10), "v.avi").json()["file_url"]
    j = client.post("/ef-estimation/predict", json={"file_url": url}).json()
    assert j["classification"] == "moderately_reduced"


def test_non_112_video_is_resized(monkeypatch):
    monkeypatch.setattr(m, "_session", FakeSession(0.5))
    url = _upload(_avi_bytes(40, w=200, h=150), "v.avi").json()["file_url"]
    assert client.post("/ef-estimation/predict", json={"file_url": url}).status_code == 200


def test_classification_bands():
    assert [m.classify_ef(x) for x in (70, 55, 54.9, 45, 44.9, 30, 29.9)] == [
        "normal", "normal", "mildly_reduced", "mildly_reduced",
        "moderately_reduced", "moderately_reduced", "severely_reduced"]
