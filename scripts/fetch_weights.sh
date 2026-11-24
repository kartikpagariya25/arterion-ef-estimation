#!/usr/bin/env bash
# Downloads trained ONNX weights from the latest GitHub Release into backend/app/ef_estimation/weights/
set -euo pipefail
REPO="kartikpagariya25/arterion-ef-estimation"
DEST="$(dirname "$0")/../backend/app/ef_estimation/weights"
mkdir -p "$DEST"
for f in ef_model.onnx; do
  echo "Downloading $f ..."
  curl -fL --retry 3 -o "$DEST/$f" "https://github.com/$REPO/releases/latest/download/$f"
done
echo "Done."
