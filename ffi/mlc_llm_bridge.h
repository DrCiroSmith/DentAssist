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

// Result of a deterministic route-table air-gap inspection.
// destination_zero_gateway is 1 when the only/default route has
// Destination == 0x00000000 (air-gapped, no active default gateway).
// interface_count is the number of parsed route-table entries.
typedef struct {
    int destination_zero_gateway;
    int interface_count;
} DentAssistRouteTableResult;

// Primary DentAssist C ABI Symbols
MedGemmaHandle dentassist_model_init(const char* model_path, int num_threads, int gpu_layers);

char* dentassist_infer_multimodal(MedGemmaHandle handle,
                                  const uint8_t* image_bytes,
                                  size_t image_len,
                                  const char* prompt,
                                  TokenCallback token_cb,
                                  void* user_data);

void dentassist_free(MedGemmaHandle handle);

// ---- Real air-gap route inspection (POSIX /proc/net/route) ----
// Testable pure parser: feeds /proc/net/route file content directly.
DentAssistRouteTableResult dentassist_check_route_table(const char* proc_net_route_content);

// System-level verification: parses /proc/net/route and probes
// getifaddrs() non-loopback IFF_UP interfaces to confirm zero active
// default gateway when air-gapped. Returns 1 when air-gap verified.
int dentassist_is_offline_verified(void);

// ---- Real volatile memory zeroization (3-pass + compiler barrier) ----
// Sanitizes len bytes at ptr: zeros, 0xFF, xorshift64* CSPRNG pass,
// final zero pass. Uses volatile uint8_t* and a compiler memory barrier
// so the passes cannot be optimized away. Callable from Dart FFI.
void dentassist_secure_wipe_buffer(void* ptr, size_t len);

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
