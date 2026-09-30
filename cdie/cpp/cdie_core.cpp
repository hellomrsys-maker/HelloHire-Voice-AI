#include "cdie_core.hpp"
#include <cstring>

namespace solorock::cdie {

CrossDomainIdeaEngine::CrossDomainIdeaEngine(uint8_t* amsv_buffer)
    : amsv_buffer_(amsv_buffer) {}

static std::string lower_str(const std::string& s) {
    std::string r = s;
    std::transform(r.begin(), r.end(), r.begin(), ::tolower);
    return r;
}

CrossDomainMetrics CrossDomainIdeaEngine::evaluate(const std::string& text) {
    CrossDomainMetrics m{};
    std::string l = lower_str(text);

    const std::vector<const char*> connectors = {
        "like a", "similar to how", "just as", "akin to", "analogous to", "much like", "draws inspiration from"
    };
    const std::vector<const char*> bio_terms = {
        "dna", "rna", "cellular", "evolution", "immune", "t-cell", "antigen", "metabolism"
    };
    const std::vector<const char*> tech_terms = {
        "latency", "cache", "throughput", "concurrency", "distributed", "microservices", "database"
    };

    int conn_hits = 0;
    for (const auto* c : connectors) {
        if (l.find(c) != std::string::npos) ++conn_hits;
    }

    int bio_hits = 0;
    for (const auto* b : bio_terms) {
        if (l.find(b) != std::string::npos) ++bio_hits;
    }

    int tech_hits = 0;
    for (const auto* t : tech_terms) {
        if (l.find(t) != std::string::npos) ++tech_hits;
    }

    m.has_cross_domain_bridge = (bio_hits > 0 && tech_hits > 0 && conn_hits > 0);
    m.manifold_distance = (bio_hits > 0 && tech_hits > 0) ? 0.85f : 0.25f;

    float score = 0.20f;
    if (m.has_cross_domain_bridge) {
        score = std::min(1.0f, 0.55f + conn_hits * 0.20f + 0.15f);
    } else if (bio_hits > 0 && tech_hits > 0) {
        score = 0.50f;
    } else if (conn_hits > 0) {
        score = 0.35f;
    }

    m.cross_domain_transfer_index = score;
    if (score >= 0.75f) m.transfer_grade = 1;
    else if (score >= 0.55f) m.transfer_grade = 2;
    else if (score >= 0.35f) m.transfer_grade = 3;
    else m.transfer_grade = 4;

    return m;
}

extern "C" {
int cdie_cpp_evaluate(const char* text_ptr, CrossDomainMetrics* out, uint8_t* amsv_buf) {
    if (!text_ptr || !out) return -1;
    CrossDomainIdeaEngine engine(amsv_buf);
    *out = engine.evaluate(text_ptr);
    return 0;
}
}

} // namespace solorock::cdie
