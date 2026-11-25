import os
import tempfile

import cv2
import numpy as np

from ..common import InvalidInput, fetch_bytes

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")
MODEL_PATH = os.path.join(WEIGHTS_DIR, "ef_model.onnx")

CLIP_LENGTH = 32
FRAME_PERIOD = 2  # every 2nd frame, as in training; one window spans (32-1)*2+1 = 63 frames
FRAME_SIZE = 112
MAX_CLIPS = 3
KINETICS_MEAN = np.array([0.43216, 0.394666, 0.37645], dtype=np.float32)
KINETICS_STD = np.array([0.22803, 0.22145, 0.216989], dtype=np.float32)

_session = None


def _model_available() -> bool:
    return os.path.exists(MODEL_PATH)


def load_model():
    global _session
    if _session is None and _model_available():
        import onnxruntime as ort

        _session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
    return _session


def classify_ef(ef: float) -> str:
    if ef >= 55:
        return "normal"
    if ef >= 45:
        return "mildly_reduced"
    if ef >= 30:
        return "moderately_reduced"
    return "severely_reduced"


def _read_video(video_bytes: bytes) -> np.ndarray:
    """Decode to (T, 112, 112, 3) RGB uint8; raise InvalidInput if it is not a readable video."""
    fd, path = tempfile.mkstemp(suffix=".avi")
    with os.fdopen(fd, "wb") as f:
        f.write(video_bytes)
    cap = cv2.VideoCapture(path)
    frames = []
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if frame.shape[:2] != (FRAME_SIZE, FRAME_SIZE):
                frame = cv2.resize(frame, (FRAME_SIZE, FRAME_SIZE), interpolation=cv2.INTER_AREA)
            frames.append(frame)
    finally:
        cap.release()
        os.remove(path)
    if not frames:
        raise InvalidInput("This endpoint needs an echocardiogram video (AVI/MP4); no frames could be read.")
    return np.stack(frames)


def _clip_starts(n_frames: int) -> list:
    """Start indices of up to MAX_CLIPS windows spread across the video (same spacing as evaluation)."""
    span = (CLIP_LENGTH - 1) * FRAME_PERIOD + 1
    if n_frames <= span:
        return [0]
    return sorted({int(round(s)) for s in np.linspace(0, n_frames - span, MAX_CLIPS)})


def _make_clip(video: np.ndarray, start: int) -> np.ndarray:
    n = video.shape[0]
    idx = [min(start + i * FRAME_PERIOD, n - 1) for i in range(CLIP_LENGTH)]  # pad short videos with the last frame
    clip = (video[idx].astype(np.float32) / 255.0 - KINETICS_MEAN) / KINETICS_STD
    return clip.transpose(3, 0, 1, 2)[None, ...].astype(np.float32)


def predict(file_url: str) -> dict:
    video = _read_video(fetch_bytes(file_url))
    load_model()
    if _session is None:
        return {
            "ejection_fraction": 0.0,
            "classification": "unknown",
            "summary": "EF estimation model weights not found, so training has not been completed.",
            "clips_used": 0,
            "ef_range": [0.0, 0.0],
        }

    efs = [float(_session.run(["ef"], {"clip": _make_clip(video, s)})[0].reshape(-1)[0]) * 100
           for s in _clip_starts(video.shape[0])]
    ef = round(float(np.mean(efs)), 1)
    classification = classify_ef(ef)
    return {
        "ejection_fraction": ef,
        "classification": classification,
        "summary": f"Estimated EF {ef:.1f}%, {classification.replace('_', ' ')}.",
        "clips_used": len(efs),
        "ef_range": [round(min(efs), 1), round(max(efs), 1)],
        "frames": int(video.shape[0]),
    }
