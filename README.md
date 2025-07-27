# DentAssist

DentAssist is a cross-platform clinical companion for dentists built with Flutter. It runs fully offline using MedGemma 4B quantized with MediaPipe GenAI Converter and executed via the MLC-LLM runtime.

## Setup

1. Install Flutter 3.22 and Dart 3.
2. Clone this repository and run `flutter pub get`.
3. Build for Android or iOS using standard Flutter commands:
   ```bash
   flutter build apk   # Android 14 (arm64)
   flutter build ios   # iOS 17 (arm64)
   ```

### Quantization & Model Conversion

Use `scripts/convert_and_push.sh` to convert the MedGemma checkpoint into the `gguf` format:

```bash
./scripts/convert_and_push.sh /path/to/models
```

This script expects MediaPipe GenAI Converter to be installed and `adb` available to push the model to a connected Android device. Adjust the script for iOS deployments.

### HIPAA Checklist (Offline Mode)

- **No network access** when the in-app "Offline Mode" toggle is enabled.
- Patient data stored using AES‑256 via `sqflite`/`sqlcipher`.
- PHI can be removed with a long‑press action → “Secure Wipe.”
- Include the AMA & ADA clinical decision support disclaimer in the app UI.

## Repository Structure

```
ffi/                 # Native bridge headers and C++ implementation
lib/                 # Flutter sources
  main.dart          # Entry point with Navigator 2.0
  widgets/ChatScreen.dart
  services/          # Modular service layer (TODO)
android/             # Android specific files (NDK setup TODO)
ios/                 # iOS specific files (Metal config TODO)
scripts/             # Utility scripts
```

## Testing

Run unit tests with:

```bash
flutter test
```

## TODO

- Integrate real MLC‑LLM runtime calls in `ffi/mlc_llm_bridge.cpp`.
- Implement multimodal query flow and service layer.
- Add CI configuration and expand test coverage to ≥80%.
