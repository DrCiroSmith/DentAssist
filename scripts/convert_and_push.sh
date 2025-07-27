#!/usr/bin/env bash
# Example pipeline converting MedGemma model to gguf and pushing to device
# Requires MediaPipe GenAI Converter and adb
set -euo pipefail

MODEL_DIR="${1:-~/models}"
CONVERTER="mediapipe-genai-converter" # TODO: path to converter

# Step 1: Convert model
$CONVERTER \
  --input "$MODEL_DIR/medgemma_4b" \
  --output "$MODEL_DIR/medgemma_4b_q4.gguf" \
  --quantization q4_0

# Step 2: Push to connected Android device
adb push "$MODEL_DIR/medgemma_4b_q4.gguf" /sdcard/DentAssist/

# For iOS, use ideviceinstaller or Xcode to bundle within app resources.
