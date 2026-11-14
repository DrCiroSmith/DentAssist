#include "../ffi/mlc_llm_bridge.h"
#include <iostream>
#include <cassert>
#include <cstring>
#include <vector>
#include <string>

// Token callback aggregator for testing
static void test_token_collector(const char* token, void* user_data) {
    auto* tokens = reinterpret_cast<std::vector<std::string>*>(user_data);
    if (token && tokens) {
        tokens->push_back(token);
    }
}

int main() {
    std::cout << "[TEST] 1. Initializing DentAssist MedGemma C++ FFI Bridge..." << std::endl;
    MedGemmaHandle handle = dentassist_model_init("models/medgemma-4b-int4.gguf", 4, 32);
    assert(handle != nullptr && "Handle should be valid pointer");
    std::cout << "  -> Initialization SUCCESS (handle=" << handle << ")" << std::endl;

    std::cout << "[TEST] 2. Verifying air-gapped offline status..." << std::endl;
    int is_offline = dentassist_is_offline_verified();
    assert(is_offline == 1 && "Must confirm air-gapped status");
    std::cout << "  -> Air-gap verified: OK" << std::endl;

    std::cout << "[TEST] 3. Running multimodal inference with streaming callback..." << std::endl;
    std::vector<std::string> streamed_tokens;
    const uint8_t mock_image[] = {0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A}; // PNG magic
    const char* prompt = "Periapical lesion tooth #19";

    char* full_response = dentassist_infer_multimodal(
        handle,
        mock_image,
        sizeof(mock_image),
        prompt,
        test_token_collector,
        &streamed_tokens
    );

    assert(full_response != nullptr && "Inference result should not be null");
    assert(strlen(full_response) > 50 && "Response must contain substantive clinical text");
    assert(!streamed_tokens.empty() && "Streamed tokens should have been delivered");
    std::cout << "  -> Received " << streamed_tokens.size() << " streaming tokens" << std::endl;
    std::cout << "  -> Full response length: " << strlen(full_response) << " chars" << std::endl;
    std::cout << "  -> Sample output: " << std::string(full_response).substr(0, 80) << "..." << std::endl;

    free(full_response);

    std::cout << "[TEST] 4. Testing legacy alias mlc_llm_infer..." << std::endl;
    char* legacy_resp = mlc_llm_infer(handle, mock_image, sizeof(mock_image), "Vitality test");
    assert(legacy_resp != nullptr);
    free(legacy_resp);
    std::cout << "  -> Legacy alias: OK" << std::endl;

    std::cout << "[TEST] 5. Releasing model memory..." << std::endl;
    dentassist_free(handle);
    std::cout << "  -> Deallocation SUCCESS" << std::endl;

    std::cout << "\n✅ ALL C++ FFI BRIDGE TESTS PASSED (100% SUCCESS)\n" << std::endl;
    return 0;
}
