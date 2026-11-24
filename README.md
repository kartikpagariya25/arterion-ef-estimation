# Arterion EF Console

Estimates **left-ventricular ejection fraction (EF)** from an apical four-chamber echocardiogram video and shows it on a clinical gauge with the normal / mildly / moderately / severely reduced bands.

![Screenshot](docs/screenshot.jpg)

> **Research prototype — not a medical device.** Do not use for diagnosis or treatment decisions.

Part of the [Arterion](https://github.com/kartikpagariya25/Arterion) project.

## How it works

An **R(2+1)D-18** video network (Kinetics-pretrained, 31.3 M parameters) regresses EF from a 32-frame, 112×112 clip built from **every 2nd frame** (a window spans 63 frames, roughly one full heartbeat). At inference the backend scores up to **three windows** spread across the video and reports their mean; the spread between windows is shown as a stability indicator (it is not a calibrated confidence interval). Videos are resized to 112×112; short videos are padded with their last frame.

EF bands: ≥ 55 % normal · 45–54 % mildly reduced · 30–44 % moderately reduced · < 30 % severely reduced.

## Results (EchoNet-Dynamic test split, 1,277 videos)

| MAE | RMSE | R² |
|---|---|---|
| **4.61 EF points** | 6.25 | **0.739** |

Same protocol as the app: every 2nd frame, mean of 3 windows (single centre window: MAE 4.72). The previous release (v1.0.0, consecutive frames, centre window) scored MAE 5.13 / R² 0.676; this model was fine-tuned from it. These are single-centre results. The project's aim was R² ≥ 0.75 / MAE ≤ 5: MAE is met, R² is just short. `training/artifacts/metrics.json` always matches the published weights.

## Run it

```bash
./scripts/fetch_weights.sh        # or .\scripts\fetch_weights.ps1  (GitHub Release)
docker compose up --build
# site: http://localhost:8080     API docs: http://localhost:8000/docs
```

Without Docker: `cd backend && pip install -r requirements-dev.txt && uvicorn app.main:app --port 8000`, then serve `frontend/`. The site talks to `window.API_BASE` (`frontend/js/config.js`). No sample videos are bundled: EchoNet-Dynamic's terms do not allow redistributing its data. Note that browsers cannot play `.avi` files, so the page shows "preview not available" for them while the analysis still runs.

### API

| Endpoint | Body | Returns |
|---|---|---|
| `POST /uploads` | multipart `file` | `{file_url}` |
| `POST /ef-estimation/predict` | `{file_url}` (video) | `ejection_fraction`, `classification`, `ef_range`, `clips_used`, `frames`, `summary` |

Non-video files return 422 with a readable `detail`; empty uploads 400; files over 200 MB 413.

Tests: `cd backend && pytest tests`.

## Training

`training/src`: `dataset.py` → `train.py` (MSE, AMP, early stopping on MAE) → `evaluate.py` → `export_onnx.py` (parity-checked) → `infer.py`.

## Data and licences

Code: MIT. Trained on [EchoNet-Dynamic](https://echonet.github.io/dynamic/) (Ouyang et al., *Nature* 2020), released under the Stanford University Dataset Research Use Agreement — **non-commercial research use only**. The trained weights are published under the same research-use intent; do not use them commercially or clinically.
