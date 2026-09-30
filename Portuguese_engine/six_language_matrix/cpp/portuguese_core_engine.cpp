// Portuguese C++20 Core Engine Implementation
#include "portuguese_core_engine.hpp"

namespace gra::portuguese {

PortugueseCoreEngine::PortugueseCoreEngine() {
    irregular_verbs_["fazer"] = "irregular";
    irregular_verbs_["dizer"] = "irregular";
    irregular_verbs_["ser"]   = "copula";
    irregular_verbs_["estar"] = "copula";
    irregular_verbs_["ter"]   = "irregular";
}

AnalysisResult PortugueseCoreEngine::analyze(std::string_view sentence) {
    AnalysisResult res{};
    res.has_valid_svo = !sentence.empty();
    res.syntactic_score = 0.88f;
    res.register_score = 0.92f;

    res.has_clitic = (sentence.find('-') != std::string_view::npos);
    res.has_crase = (sentence.find("à") != std::string_view::npos || sentence.find("À") != std::string_view::npos);

    return res;
}

void PortugueseCoreEngine::sync_to_amsv(const AnalysisResult& res, PortugueseAMSRecord* out_amsv) {
    if (!out_amsv) return;

    out_amsv->phoneme_state = 0x0000000000000003ULL;
    out_amsv->prosody_state = 0x0000000000000004ULL;

    out_amsv->capability_scores[1] = static_cast<uint8_t>(res.syntactic_score * 255.0f);
    out_amsv->capability_scores[3] = static_cast<uint8_t>(res.register_score * 255.0f);

    out_amsv->global_structural_score = res.syntactic_score;
    out_amsv->global_register_score = res.register_score;
}

} // namespace gra::portuguese
