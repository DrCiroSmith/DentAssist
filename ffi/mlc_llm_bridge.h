#pragma once
#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Opaque handle to MedGemma runtime instance
typedef void* MedGemmaHandle;

// Streaming token callback function signature
typedef void (*TokenCallback)(const char* token, void* user_data);

// Primary DentAssist C ABI Symbols
MedGemmaHandle dentassist_model_init(const char* model_path, int num_threads, int gpu_layers);

char* dentassist_infer_multimodal(MedGemmaHandle handle,
                                  const uint8_t* image_bytes,
                                  size_t image_len,
                                  const char* prompt,
                                  TokenCallback token_cb,
                                  void* user_data);

void dentassist_free(MedGemmaHandle handle);

int dentassist_is_offline_verified(void);

// Backwards-compatible legacy aliases
MedGemmaHandle mlc_llm_init(const char* model_path);

char* mlc_llm_infer(MedGemmaHandle handle,
                    const uint8_t* image_bytes,
                    size_t image_len,
                    const char* prompt);

void mlc_llm_free(MedGemmaHandle handle);

#ifdef __cplusplus
}
#endif
