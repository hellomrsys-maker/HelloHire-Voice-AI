#pragma once

#include <string>
#include <vector>
#include <cstdint>
#include <algorithm>
#include <cmath>

namespace solorock::cdie {

struct CrossDomainMetrics {
    float cross_domain_transfer_index;
    uint8_t transfer_grade;
    bool has_cross_domain_bridge;
    float manifold_distance;
};

class CrossDomainIdeaEngine {
public:
    explicit CrossDomainIdeaEngine(uint8_t* amsv_buffer = nullptr);
    CrossDomainMetrics evaluate(const std::string& text);

private:
    uint8_t* amsv_buffer_;
};

extern "C" {
    int cdie_cpp_evaluate(const char* text_ptr, CrossDomainMetrics* out, uint8_t* amsv_buf);
}

} // namespace solorock::cdie
