#include "../ffi/mlc_llm_bridge.h"
#include <iostream>
#include <cassert>
#include <cstring>
#include <vector>
#include <string>
#include <cstdint>

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

    // ---------------------------------------------------------------
    // TEST 2: dentassist_check_route_table - deterministic pure parser
    // ---------------------------------------------------------------
    std::cout << "[TEST] 2a. Route table: air-gapped content (no default gateway)..." << std::endl;
    const char* airgapped_route =
        "Iface\tDestination\tGateway\tFlags\tRefCnt\tUse\tMetric\tMask\tMTU\tWindow\tIRTT\n"
        "eth0\t00123456\t00000000\t0001\t0\t0\t0\t00ffffff\t0\t0\t0\n"
        "eth0\t0000a8c0\t00000000\t0001\t0\t0\t0\t0000ffff\t0\t0\t0\n";
    DentAssistRouteTableResult rt_air = dentassist_check_route_table(airgapped_route);
    assert(rt_air.interface_count == 2 && "Should parse 2 route entries");
    assert(rt_air.destination_zero_gateway == 1 && "Air-gapped: zero default gateways");
    std::cout << "  -> interfaces=" << rt_air.interface_count
              << " destination_zero_gateway=" << rt_air.destination_zero_gateway << " OK" << std::endl;

    std::cout << "[TEST] 2b. Route table: online content (active default gateway)..." << std::endl;
    const char* online_route =
        "Iface\tDestination\tGateway\tFlags\tRefCnt\tUse\tMetric\tMask\tMTU\tWindow\tIRTT\n"
        "eth0\t00000000\t01234567\t0003\t0\t0\t0\t00000000\t0\t0\t0\n"
        "eth0\t00123456\t00000000\t0001\t0\t0\t0\t00ffffff\t0\t0\t0\n";
    DentAssistRouteTableResult rt_on = dentassist_check_route_table(online_route);
    assert(rt_on.interface_count == 2 && "Should parse 2 route entries");
    assert(rt_on.destination_zero_gateway == 0 && "Online: active default gateway present");
    std::cout << "  -> interfaces=" << rt_on.interface_count
              << " destination_zero_gateway=" << rt_on.destination_zero_gateway << " OK" << std::endl;

    // Null-content safety
    DentAssistRouteTableResult rt_null = dentassist_check_route_table(nullptr);
    assert(rt_null.interface_count == 0 && rt_null.destination_zero_gateway == 0 &&
           "Null content must yield empty result");
    std::cout << "[TEST] 2c. Route table: null-content safety OK" << std::endl;

    // ---------------------------------------------------------------
    // TEST 3: dentassist_secure_wipe_buffer - byte-level zeroization
    // ---------------------------------------------------------------
    std::cout << "[TEST] 3. Secure wipe: byte-level zeroization across buffer..." << std::endl;
    const size_t wipe_len = 256;
    uint8_t wipe_buf[wipe_len];
    for (size_t i = 0; i < wipe_len; ++i) wipe_buf[i] = static_cast<uint8_t>(0xA5 + (i % 7));
    dentassist_secure_wipe_buffer(wipe_buf, wipe_len);
    bool all_zero = true;
    for (size_t i = 0; i < wipe_len; ++i) {
        if (wipe_buf[i] != 0x00) { all_zero = false; break; }
    }
    assert(all_zero && "Buffer must be fully zeroed after secure wipe");
    std::cout << "  -> all bytes zero after 3-pass wipe: OK" << std::endl;

    // Edge cases: null ptr and zero len must not crash
    dentassist_secure_wipe_buffer(nullptr, 1024);
    dentassist_secure_wipe_buffer(wipe_buf, 0);
    std::cout << "[TEST] 3b. Secure wipe: null/zero edge cases OK" << std::endl;

    // ---------------------------------------------------------------
    // TEST 4: dentassist_is_offline_verified (system-level)
    // ---------------------------------------------------------------
    std::cout << "[TEST] 4. System air-gap verification (dentassist_is_offline_verified)..." << std::endl;
    int is_offline = dentassist_is_offline_verified();
    std::cout << "  -> system is_offline_verified=" << is_offline << std::endl;
    assert((is_offline == 0 || is_offline == 1) && "Must return 0 or 1");

    // ---------------------------------------------------------------
    // TEST 5: Multimodal inference with streaming callback
    // ---------------------------------------------------------------
    std::cout << "[TEST] 5. Running multimodal inference with streaming callback..." << std::endl;
    std::vector<std::string> streamed_tokens;
    const uint8_t mock_image[] = {0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A}; // PNG magic
    const char* prompt = "Periapical lesion tooth #19";

    char* full_response = dentassist_infer_multimodal(
        handle, mock_image, sizeof(mock_image), prompt,
        test_token_collector, &streamed_tokens);

    assert(full_response != nullptr && "Inference result should not be null");
    assert(strlen(full_response) > 50 && "Response must contain substantive clinical text");
    assert(!streamed_tokens.empty() && "Streamed tokens should have been delivered");
    std::cout << "  -> Received " << streamed_tokens.size() << " streaming tokens" << std::endl;
    std::cout << "  -> Full response length: " << strlen(full_response) << " chars" << std::endl;
    std::cout << "  -> Sample output: " << std::string(full_response).substr(0, 80) << "..." << std::endl;
    free(full_response);

    // ---------------------------------------------------------------
    // TEST 6: Legacy alias mlc_llm_infer
    // ---------------------------------------------------------------
    std::cout << "[TEST] 6. Testing legacy alias mlc_llm_infer..." << std::endl;
    char* legacy_resp = mlc_llm_infer(handle, mock_image, sizeof(mock_image), "Vitality test");
    assert(legacy_resp != nullptr);
    free(legacy_resp);
    std::cout << "  -> Legacy alias: OK" << std::endl;

    // ---------------------------------------------------------------
    // TEST 7: Release model memory
    // ---------------------------------------------------------------
    std::cout << "[TEST] 7. Releasing model memory..." << std::endl;
    dentassist_free(handle);
    std::cout << "  -> Deallocation SUCCESS" << std::endl;

    std::cout << "\nALL C++ FFI BRIDGE TESTS PASSED" << std::endl;
    return 0;
}
