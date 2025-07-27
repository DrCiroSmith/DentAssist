import 'dart:ffi' as ffi;
import 'dart:io';
import 'package:ffi/ffi.dart' as pkg_ffi;

// Native function signatures
typedef _NativeInitFunc = ffi.Pointer<ffi.Void> Function(ffi.Pointer<ffi.Int8>);
typedef _NativeInferFunc = ffi.Pointer<ffi.Int8> Function(
    ffi.Pointer<ffi.Void>, ffi.Pointer<ffi.Uint8>, ffi.IntPtr, ffi.Pointer<ffi.Int8>);
typedef _NativeFreeFunc = ffi.Void Function(ffi.Pointer<ffi.Void>);

// Dart-side signatures used by lookupFunction
typedef _InitFunc = ffi.Pointer<ffi.Void> Function(ffi.Pointer<ffi.Int8>);
typedef _InferFunc = ffi.Pointer<ffi.Int8> Function(
    ffi.Pointer<ffi.Void>, ffi.Pointer<ffi.Uint8>, int, ffi.Pointer<ffi.Int8>);
typedef _FreeFunc = void Function(ffi.Pointer<ffi.Void>);

class MlcLlmBindings {
  late final ffi.DynamicLibrary _lib;
  late final _InitFunc _init;
  late final _InferFunc _infer;
  late final _FreeFunc _free;

  MlcLlmBindings() {
    final path = Platform.isAndroid ? 'libmlc_llm.so' : 'mlc_llm';
    _lib = ffi.DynamicLibrary.open(path);
    _init = _lib.lookupFunction<_NativeInitFunc, _InitFunc>('mlc_llm_init');
    _infer = _lib.lookupFunction<_NativeInferFunc, _InferFunc>('mlc_llm_infer');
    _free = _lib.lookupFunction<_NativeFreeFunc, _FreeFunc>('mlc_llm_free');
  }

  ffi.Pointer<ffi.Void> init(String modelPath) {
    final ptr = modelPath.toNativeUtf8(allocator: pkg_ffi.malloc);
    final handle = _init(ptr.cast());
    pkg_ffi.malloc.free(ptr);
    return handle;
  }

  String infer(ffi.Pointer<ffi.Void> handle, List<int> imageBytes, String prompt) {
    final imgPtr = pkg_ffi.malloc.allocate<ffi.Uint8>(imageBytes.length);
    final imgList = imgPtr.asTypedList(imageBytes.length);
    imgList.setAll(0, imageBytes);
    final promptPtr = prompt.toNativeUtf8(allocator: pkg_ffi.malloc);
    final resultPtr = _infer(handle, imgPtr, imageBytes.length, promptPtr.cast());
    final result = resultPtr.cast<pkg_ffi.Utf8>().toDartString();
    pkg_ffi.malloc.free(imgPtr);
    pkg_ffi.malloc.free(promptPtr);
    return result;
  }

  void free(ffi.Pointer<ffi.Void> handle) {
    _free(handle);
  }
}
