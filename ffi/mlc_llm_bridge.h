#pragma once
#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Opaque handle to model instance
typedef void* MedGemmaHandle;

// Initializes runtime and loads GGUF model
MedGemmaHandle mlc_llm_init(const char* model_path);

// Runs inference given image bytes and prompt
// Returns newly allocated C string (caller owns)
char* mlc_llm_infer(MedGemmaHandle handle,
                    const uint8_t* image_bytes,
                    size_t image_len,
                    const char* prompt);

void mlc_llm_free(MedGemmaHandle handle);

#ifdef __cplusplus
}
#endif
