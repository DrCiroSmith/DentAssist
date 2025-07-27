#include "mlc_llm_bridge.h"
#include <string>
#include <iostream>

extern "C" {

struct DummyModel {
  std::string path;
};

MedGemmaHandle mlc_llm_init(const char* model_path) {
  // TODO: integrate with MLC-LLM runtime
  DummyModel* model = new DummyModel();
  model->path = model_path ? model_path : "";
  return reinterpret_cast<MedGemmaHandle>(model);
}

char* mlc_llm_infer(MedGemmaHandle handle,
                    const uint8_t* image_bytes,
                    size_t image_len,
                    const char* prompt) {
  // TODO: call into MedGemma with image + prompt
  std::string reply = "Model response placeholder";
  char* result = static_cast<char*>(malloc(reply.size() + 1));
  memcpy(result, reply.c_str(), reply.size() + 1);
  return result;
}

void mlc_llm_free(MedGemmaHandle handle) {
  DummyModel* model = reinterpret_cast<DummyModel*>(handle);
  delete model;
}

} // extern "C"
