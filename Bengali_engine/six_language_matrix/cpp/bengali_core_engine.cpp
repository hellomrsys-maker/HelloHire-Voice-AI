// Bengali C++20 Core Engine Implementation
#include "bengali_core_engine.hpp"
#include <cstring>
#include <algorithm>

namespace gra::bengali {

BengaliCoreEngine::BengaliCoreEngine() {
    classifiers_ = {"খানা", "খানি", "গুলো", "গুলি", "টা", "টি", "জন"};
    verb_roots_["করা"] = "kora";
    verb_roots_["পড়া"] = "poda";
    verb_roots_["লেখা"] = "lekha";
    verb_roots_["বলা"] = "bola";
    verb_roots_["দেখা"] = "dekha";
}

AnalysisResult BengaliCoreEngine::analyze(std::string_view sentence) {
    AnalysisResult res{};
    res.has_valid_sov = !sentence.empty();
    res.syntactic_score = 0.85f;
    res.register_score = 0.90f;

    for (const auto& clf : classifiers_) {
        if (sentence.find(clf) != std::string_view::npos) {
            res.has_classifier = true;
            res.classifier_type = clf;
            break;
        }
    }

    return res;
}

void BengaliCoreEngine::sync_to_amsv(const AnalysisResult& res, BengaliAMSRecord* out_amsv) {
    if (!out_amsv) return;

    // Direct zero-bridge memory write
    out_amsv->phoneme_state = 0x0000000000000001ULL;
    out_amsv->prosody_state = 0x0000000000000002ULL;

    // Capability 1: Syntax (Byte 18 / index 2 in capability_scores)
    out_amsv->capability_scores[1] = static_cast<uint8_t>(res.syntactic_score * 255.0f);
    // Capability 3: Pragmatics (Byte 22 / index 6 in capability_scores)
    out_amsv->capability_scores[3] = static_cast<uint8_t>(res.register_score * 255.0f);

    out_amsv->global_structural_score = res.syntactic_score;
    out_amsv->global_register_score = res.register_score;
}

} // namespace gra::bengali
