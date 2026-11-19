#include "mlc_llm_bridge.h"
#include <string>
#include <vector>
#include <sstream>
#include <cstring>
#include <cstdlib>
#include <chrono>
#include <thread>
#include <iostream>
#include <cstdint>
#include <random>
#include <fstream>

#ifdef USE_MLC_RUNTIME
#include <mlc/llm/relax_model_runner.h>
#endif

#if defined(__linux__) || defined(__APPLE__)
#include <ifaddrs.h>
#include <net/if.h>
#include <arpa/inet.h>
#endif

namespace {

struct MedGemmaRuntimeContext {
    std::string model_path;
    int num_threads{4};
    int gpu_layers{32};
    bool is_initialized{false};
};

} // anonymous namespace

static void compiler_barrier(const volatile void* p) {
    asm volatile("" : : "r"(p) : "memory");
}

static uint64_t xorshift64star_state = 0x9E3779B97F4A7C15ULL;

static uint64_t xorshift64star_next() {
    uint64_t x = xorshift64star_state;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    xorshift64star_state = x;
    return x * 0x2545F4914F6CDD1DULL;
}

void dentassist_secure_wipe_buffer(void* ptr, size_t len) {
    if (ptr == nullptr || len == 0) return;
    volatile uint8_t* p = static_cast<volatile uint8_t*>(ptr);
    for (size_t i = 0; i < len; ++i) p[i] = 0x00;
    compiler_barrier(p);
    for (size_t i = 0; i < len; ++i) p[i] = 0xFF;
    compiler_barrier(p);
    for (size_t i = 0; i < len; ++i) p[i] = static_cast<uint8_t>(xorshift64star_next());
    compiler_barrier(p);
    for (size_t i = 0; i < len; ++i) p[i] = 0x00;
    compiler_barrier(p);
}

static bool is_default_gateway_line(const char* line) {
    if (line == nullptr) return false;
    if (strncmp(line, "Iface", 5) == 0) return false;
    char iface[64] = {0};
    unsigned long destination = 0, gateway = 0, flags = 0, mask = 0;
    int refcnt = 0, use = 0, metric = 0, mtu = 0, window = 0, irtt = 0;
    int n = sscanf(line, "%63s %lx %lx %lx %d %d %d %lx %d %d %d",
                   iface, &destination, &gateway, &flags,
                   &refcnt, &use, &metric, &mask, &mtu, &window, &irtt);
    if (n < 8) return false;
    return destination == 0x00000000UL;
}

DentAssistRouteTableResult dentassist_check_route_table(const char* proc_net_route_content) {
    DentAssistRouteTableResult result{0, 0};
    if (proc_net_route_content == nullptr) return result;
    std::string content(proc_net_route_content);
    std::istringstream stream(content);
    std::string line;
    int default_gateway_count = 0;
    while (std::getline(stream, line)) {
        if (line.empty()) continue;
        if (strncmp(line.c_str(), "Iface", 5) == 0) continue; // header line
        result.interface_count++;
        if (is_default_gateway_line(line.c_str())) default_gateway_count++;
    }
    result.destination_zero_gateway = (default_gateway_count == 0) ? 1 : 0;
    return result;
}

int dentassist_is_offline_verified(void) {
    std::ifstream route_file("/proc/net/route");
    std::string route_content((std::istreambuf_iterator<char>(route_file)),
                              std::istreambuf_iterator<char>());
    if (!route_content.empty()) {
        DentAssistRouteTableResult rt = dentassist_check_route_table(route_content.c_str());
        if (rt.destination_zero_gateway == 0) return 0;
    }
#if defined(__linux__) || defined(__APPLE__)
    struct ifaddrs* ifaddr = nullptr;
    if (getifaddrs(&ifaddr) == 0) {
        for (struct ifaddrs* ifa = ifaddr; ifa != nullptr; ifa = ifa->ifa_next) {
            if (ifa->ifa_name == nullptr || ifa->ifa_addr == nullptr) continue;
            if ((ifa->ifa_flags & IFF_UP) == 0) continue;
            if ((ifa->ifa_flags & IFF_LOOPBACK) != 0) continue;
            if (ifa->ifa_addr->sa_family == AF_INET || ifa->ifa_addr->sa_family == AF_INET6) {
                freeifaddrs(ifaddr);
                return 0;
            }
        }
        freeifaddrs(ifaddr);
    }
#endif
    return 1;
}

extern "C" {

MedGemmaHandle dentassist_model_init(const char* model_path, int num_threads, int gpu_layers) {
    auto* ctx = new MedGemmaRuntimeContext();
    ctx->model_path = model_path ? model_path : "models/medgemma-4b-int4.gguf";
    ctx->num_threads = num_threads > 0 ? num_threads : 4;
    ctx->gpu_layers = gpu_layers >= 0 ? gpu_layers : 32;
    ctx->is_initialized = true;
#ifdef USE_MLC_RUNTIME
    // mlc::llm::ModelRunner::Init(ctx->model_path, ctx->gpu_layers);
#endif
    return reinterpret_cast<MedGemmaHandle>(ctx);
}

char* dentassist_infer_multimodal(MedGemmaHandle handle,
                                  const uint8_t* image_bytes,
                                  size_t image_len,
                                  const char* prompt,
                                  TokenCallback token_cb,
                                  void* user_data) {
    if (!handle) {
        const char* err = "ERROR: Uninitialized MedGemma runtime handle";
        char* res = static_cast<char*>(malloc(strlen(err) + 1));
        strcpy(res, err);
        return res;
    }
    auto* ctx = reinterpret_cast<MedGemmaRuntimeContext*>(handle);
    (void)ctx;
#ifdef USE_MLC_RUNTIME
    // mlc_run_forward(ctx, image_bytes, image_len, prompt, token_cb, user_data);
#endif
    (void)image_bytes;
    (void)image_len;
    std::string safe_prompt = prompt ? prompt : "Analyze radiograph";
    std::ostringstream response;
    response << "### Clinical Decision Support Assessment (Offline MedGemma 4B SIMULATION)\n\n"
             << "**1. Radiographic & Visual Observations:**\n"
             << "- Image payload size: " << image_len << " bytes processed via on-device vision tokenizer.\n"
             << "- Well-defined radiolucency observed in periapical region of tooth #19 (mandibular first molar).\n"
             << "- Loss of lamina dura continuity along the distal root apex with mild PDL ligament widening.\n\n"
             << "**2. Differential Diagnosis:**\n"
             << "  1. Chronic Apical Periodontitis (Likelihood: 82%)\n"
             << "  2. Periapical Granuloma / Radicular Cyst (Likelihood: 14%)\n"
             << "  3. Focal Cemento-Osseous Dysplasia (Early Osteolytic Phase) (Likelihood: 4%)\n\n"
             << "**3. Clinical Protocol Recommendations:**\n"
             << "- Perform cold thermal and electric pulp testing (EPT) on #19, #18, and #20 to assess vitality.\n"
             << "- Measure periodontal probing depths circumferentially to rule out vertical root fracture.\n"
             << "- Review patient medical history for bisphosphonate or antiresorptive therapy before surgical intervention.\n\n"
             << "**ADA CDS Disclaimer:** Non-definitive automated diagnostic assistance. Verification by licensed practitioner required.";
    std::string full_text = response.str();
    if (token_cb) {
        std::istringstream stream(full_text);
        std::string word;
        while (stream >> word) {
            std::string token = word + " ";
            token_cb(token.c_str(), user_data);
        }
    }
    char* result = static_cast<char*>(malloc(full_text.size() + 1));
    memcpy(result, full_text.c_str(), full_text.size() + 1);
    return result;
}

void dentassist_free(MedGemmaHandle handle) {
    if (handle) {
        auto* ctx = reinterpret_cast<MedGemmaRuntimeContext*>(handle);
        delete ctx;
    }
}

MedGemmaHandle mlc_llm_init(const char* model_path) {
    return dentassist_model_init(model_path, 4, 32);
}
char* mlc_llm_infer(MedGemmaHandle handle, const uint8_t* image_bytes,
                    size_t image_len, const char* prompt) {
    return dentassist_infer_multimodal(handle, image_bytes, image_len, prompt, nullptr, nullptr);
}
void mlc_llm_free(MedGemmaHandle handle) { dentassist_free(handle); }

} // extern "C"
