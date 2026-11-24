# Model card: Arterion EF Console

> Research prototype, not a medical device. Do not use for diagnosis or treatment decisions.

## Task
Left-ventricular ejection fraction (EF) estimation from an apical four-chamber echocardiogram video.

## Model
R(2+1)D-18 (Kinetics-pretrained, 31.3 M parameters) regressing EF from 32 frames sampled every 2nd frame at 112x112; the app averages up to three windows.

## Input and output
- **Input:** an echocardiogram video (AVI/MP4).
- **Output:** EF %, a normal / mildly / moderately / severely reduced band, the range across windows, windows used and frames read.

## Training and evaluation data
EchoNet-Dynamic (Ouyang et al., Nature 2020), Stanford University Dataset Research Use Agreement; test split of 1,277 videos.

## Results
- MAE 4.61 EF points, RMSE 6.25, R-squared 0.739 (every 2nd frame, mean of 3 windows).
- Single centre window: MAE 4.72.
- Previous release v1.0.0 (consecutive frames): MAE 5.13, R-squared 0.676.

Numbers in `training/artifacts/metrics.json` match the published weights.

## Limitations
- The spread between windows is a stability indicator, not a calibrated confidence interval.
- Single-centre training data; other scanners, views or poor image quality may give unreliable values.
- Project target R-squared 0.75 was just missed (0.739).

## Intended use
Research, teaching and prototyping. Not for diagnosis, triage or any clinical decision, and not validated for any clinical setting.

## Licence and data terms
Code: MIT. EchoNet-Dynamic is for non-commercial research use only; the weights are published with the same intent.
