# Downloads trained ONNX weights from the latest GitHub Release into backend/app/ef_estimation/weights/
$ErrorActionPreference = "Stop"
$repo = "kartikpagariya25/arterion-ef-estimation"
$dest = Join-Path $PSScriptRoot "..\backend\app\ef_estimation\weights"
New-Item -ItemType Directory -Force $dest | Out-Null
foreach ($f in "ef_model.onnx") {
  Write-Host "Downloading $f ..."
  Invoke-WebRequest "https://github.com/$repo/releases/latest/download/$f" -OutFile (Join-Path $dest $f)
}
Write-Host "Done."
