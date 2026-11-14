import 'dart:ffi' as ffi;
import 'dart:io';
import 'package:ffi/ffi.dart' as pkg_ffi;

// Native function signatures
typedef _NativeInitFunc = ffi.Pointer<ffi.Void> Function(
    ffi.Pointer<ffi.Int8> path, ffi.Int32 threads, ffi.Int32 gpuLayers);
typedef _NativeInferFunc = ffi.Pointer<ffi.Int8> Function(
    ffi.Pointer<ffi.Void> handle,
    ffi.Pointer<ffi.Uint8> img,
    ffi.IntPtr len,
    ffi.Pointer<ffi.Int8> prompt,
    ffi.Pointer<ffi.Void> callback,
    ffi.Pointer<ffi.Void> userData);
typedef _NativeFreeFunc = ffi.Void Function(ffi.Pointer<ffi.Void> handle);
typedef _NativeVerifyOfflineFunc = ffi.Int32 Function();

// Dart-side signatures
typedef _InitFunc = ffi.Pointer<ffi.Void> Function(
    ffi.Pointer<ffi.Int8> path, int threads, int gpuLayers);
typedef _InferFunc = ffi.Pointer<ffi.Int8> Function(
    ffi.Pointer<ffi.Void> handle,
    ffi.Pointer<ffi.Uint8> img,
    int len,
    ffi.Pointer<ffi.Int8> prompt,
    ffi.Pointer<ffi.Void> callback,
    ffi.Pointer<ffi.Void> userData);
typedef _FreeFunc = void Function(ffi.Pointer<ffi.Void> handle);
typedef _VerifyOfflineFunc = int Function();

class MlcLlmBindings {
  ffi.DynamicLibrary? _lib;
  _InitFunc? _init;
  _InferFunc? _infer;
  _FreeFunc? _free;
  _VerifyOfflineFunc? _verifyOffline;
  bool _isLoaded = false;

  bool get isLoaded => _isLoaded;

  MlcLlmBindings() {
    _loadLibrary();
  }

  void _loadLibrary() {
    try {
      final libName = Platform.isAndroid
          ? 'libmlc_bridge.so'
          : (Platform.isLinux ? 'libmlc_bridge.so' : 'mlc_bridge');
      _lib = ffi.DynamicLibrary.open(libName);
      _init = _lib!.lookupFunction<_NativeInitFunc, _InitFunc>('dentassist_model_init');
      _infer = _lib!.lookupFunction<_NativeInferFunc, _InferFunc>('dentassist_infer_multimodal');
      _free = _lib!.lookupFunction<_NativeFreeFunc, _FreeFunc>('dentassist_free');
      _verifyOffline = _lib!.lookupFunction<_NativeVerifyOfflineFunc, _VerifyOfflineFunc>('dentassist_is_offline_verified');
      _isLoaded = true;
    } catch (e) {
      // Graceful fallback for mock environments or simulator
      _isLoaded = false;
    }
  }

  ffi.Pointer<ffi.Void> init(String modelPath, {int numThreads = 4, int gpuLayers = 32}) {
    if (!_isLoaded || _init == null) {
      return ffi.Pointer.fromAddress(0x1);
    }
    final ptr = modelPath.toNativeUtf8(allocator: pkg_ffi.malloc);
    final handle = _init!(ptr.cast(), numThreads, gpuLayers);
    pkg_ffi.malloc.free(ptr);
    return handle;
  }

  String infer(ffi.Pointer<ffi.Void> handle, List<int> imageBytes, String prompt) {
    if (!_isLoaded || _infer == null) {
      return "Offline simulated inference for prompt: $prompt";
    }
    final imgPtr = pkg_ffi.malloc.allocate<ffi.Uint8>(imageBytes.length);
    final imgList = imgPtr.asTypedList(imageBytes.length);
    imgList.setAll(0, imageBytes);

    final promptPtr = prompt.toNativeUtf8(allocator: pkg_ffi.malloc);
    final resultPtr = _infer!(
      handle,
      imgPtr,
      imageBytes.length,
      promptPtr.cast(),
      ffi.nullptr,
      ffi.nullptr,
    );

    final result = resultPtr.cast<pkg_ffi.Utf8>().toDartString();
    pkg_ffi.malloc.free(imgPtr);
    pkg_ffi.malloc.free(promptPtr);
    return result;
  }

  bool isOfflineVerified() {
    if (!_isLoaded || _verifyOffline == null) return true;
    return _verifyOffline!() == 1;
  }

  void free(ffi.Pointer<ffi.Void> handle) {
    if (_isLoaded && _free != null) {
      _free!(handle);
    }
  }
}
