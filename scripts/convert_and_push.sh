#!/usr/bin/env bash
# Conversion pipeline for MedGemma models to GGUF format and transfer to target device.
# Requires MediaPipe GenAI Converter and adb.
set -euo pipefail

MODEL_DIR="${1:-$HOME/models}"
CONVERTER="${CONVERTER_PATH:-mediapipe-genai-converter}"

echo "Starting MedGemma 4B INT4 quantization..."
if ! command -v "$CONVERTER" &>/dev/null; then
  echo "Notice: $CONVERTER not in PATH. Set CONVERTER_PATH or install via 'pip install mediapipe'."
fi

# Step 1: Convert model checkpoint to 4-bit quantized GGUF
"$CONVERTER" \
  --input "$MODEL_DIR/medgemma_4b" \
  --output "$MODEL_DIR/medgemma_4b_q4.gguf" \
  --quantization q4_0

# Step 2: Push to connected Android device
if command -v adb &>/dev/null; then
  echo "Deploying to connected Android device..."
  adb push "$MODEL_DIR/medgemma_4b_q4.gguf" /sdcard/DentAssist/
else
  echo "adb not detected; bundle model into application assets or iOS app sandbox."
fi
