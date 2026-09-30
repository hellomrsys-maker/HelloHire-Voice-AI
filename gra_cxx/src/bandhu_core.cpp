/**
 * @file bandhu_core.cpp
 * @brief BandhuPrime Dedicated AI Engine Core Implementation (C++20).
 */

#include "../include/bandhu_core.hpp"
#include <algorithm>
#include <cctype>
#include <sstream>

namespace solorock::bandhu {

namespace {

std::string toLower(std::string_view sv) {
    std::string s(sv);
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });
    return s;
}

bool containsSubstr(std::string_view str, std::string_view sub) {
    return str.find(sub) != std::string_view::npos;
}

} // anonymous namespace

BandhuSkillResult BandhuCoreEngine::evaluateWriting(std::string_view text) {
    BandhuSkillResult res;
    res.skill = SkillType::Writing;
    res.era = classifyEra(text);

    if (text.empty()) {
        res.structural_score = 0.0f;
        res.fatal_errors = 1;
        res.diagnostic_notes.push_back("Empty text stream.");
        return res;
    }

    // 1. Terminal punctuation validation
    char last_char = text.back();
    while (!text.empty() && std::isspace(static_cast<unsigned char>(text.back()))) {
        text.remove_suffix(1);
    }
    if (!text.empty()) {
        last_char = text.back();
        bool valid_end = (last_char == '.' || last_char == '?' || last_char == '!' || last_char == ';');
        if (!valid_end) {
            res.clarity_errors++;
            res.structural_score -= 0.25f;
            res.diagnostic_notes.push_back("Missing terminal punctuation glyph.");
        }
    }

    // 2. Initial Capitalization check
    size_t first_idx = 0;
    while (first_idx < text.size() && std::isspace(static_cast<unsigned char>(text[first_idx]))) {
        first_idx++;
    }
    if (first_idx < text.size() && std::isalpha(static_cast<unsigned char>(text[first_idx]))) {
        if (!std::isupper(static_cast<unsigned char>(text[first_idx]))) {
            res.register_errors++;
            res.register_score -= 0.20f;
            res.diagnostic_notes.push_back("Sentence onset lacks capitalization.");
        }
    }

    // 3. Finite verb presence heuristic
    std::string lower = toLower(text);
    static const std::vector<std::string> verbs = {
        "is", "are", "was", "were", "has", "have", "had", "do", "does", "did",
        "will", "would", "can", "could", "shall", "should", "may", "might", "must",
        "walk", "run", "write", "publish", "read", "examine", "analyze", "conclude"
    };
    bool found_verb = false;
    for (const auto& v : verbs) {
        if (containsSubstr(lower, v)) {
            found_verb = true;
            break;
        }
    }
    if (!found_verb) {
        res.fatal_errors++;
        res.structural_score -= 0.45f;
        res.diagnostic_notes.push_back("Potential sentence fragment: no finite verb detected.");
    }

    res.structural_score = std::clamp(res.structural_score, 0.0f, 1.0f);
    res.register_score = std::clamp(res.register_score, 0.0f, 1.0f);
    res.recommended_stage = EditingStage::CopyEdit;
    return res;
}

BandhuSkillResult BandhuCoreEngine::evaluateEmail(std::string_view text) {
    BandhuSkillResult res;
    res.skill = SkillType::Emailing;
    res.era = classifyEra(text);

    std::string lower = toLower(text);

    // Salutation validation
    bool has_salutation = containsSubstr(lower, "dear ") || containsSubstr(lower, "sehr geehrte")
                       || containsSubstr(lower, "estimado") || containsSubstr(lower, "cher ")
                       || containsSubstr(lower, "hello") || containsSubstr(lower, "hi ");
    if (!has_salutation) {
        res.register_errors++;
        res.register_score -= 0.25f;
        res.diagnostic_notes.push_back("Email lacks conventional salutation greeting.");
    }

    // Modal politeness check
    bool has_polite_modal = containsSubstr(lower, "could you") || containsSubstr(lower, "would you")
                         || containsSubstr(lower, "would it be possible") || containsSubstr(lower, "könnten sie")
                         || containsSubstr(lower, "pourriez-vous");
    bool has_abrupt_imp = containsSubstr(lower, "send me") || containsSubstr(lower, "do this now")
                       || containsSubstr(lower, "give me");
    if (has_abrupt_imp && !has_polite_modal) {
        res.register_errors++;
        res.register_score -= 0.35f;
        res.diagnostic_notes.push_back("Direct imperative detected without modal politeness mitigation.");
    }

    // Sign-off validation
    bool has_signoff = containsSubstr(lower, "best regards") || containsSubstr(lower, "sincerely")
                    || containsSubstr(lower, "mit freundlichen grüßen") || containsSubstr(lower, "cordialement")
                    || containsSubstr(lower, "warm regards");
    if (!has_signoff) {
        res.register_errors++;
        res.register_score -= 0.20f;
        res.diagnostic_notes.push_back("Email lacks recognized formal sign-off formula.");
    }

    res.structural_score = std::clamp(res.structural_score, 0.0f, 1.0f);
    res.register_score = std::clamp(res.register_score, 0.0f, 1.0f);
    res.recommended_stage = EditingStage::CopyEdit;
    return res;
}

BandhuSkillResult BandhuCoreEngine::evaluateReviewing(std::string_view text) {
    BandhuSkillResult res;
    res.skill = SkillType::Reviewing;
    res.era = classifyEra(text);

    std::string lower = toLower(text);

    // Hedged language verification
    bool has_hedging = containsSubstr(lower, "suggest") || containsSubstr(lower, "might consider")
                    || containsSubstr(lower, "could benefit") || containsSubstr(lower, "recommend")
                    || containsSubstr(lower, "appears to");
    if (!has_hedging) {
        res.style_preferences++;
        res.register_score -= 0.15f;
        res.diagnostic_notes.push_back("Editorial critique lacks conventional modal hedging.");
    }

    // Specific location anchoring verification
    bool has_anchor = containsSubstr(lower, "line ") || containsSubstr(lower, "page ")
                   || containsSubstr(lower, "section ") || containsSubstr(lower, "paragraph ")
                   || containsSubstr(lower, "p. ");
    if (!has_anchor) {
        res.clarity_errors++;
        res.structural_score -= 0.30f;
        res.diagnostic_notes.push_back("Review critique unanchored: missing line/page/section coordinates.");
    }

    res.structural_score = std::clamp(res.structural_score, 0.0f, 1.0f);
    res.register_score = std::clamp(res.register_score, 0.0f, 1.0f);
    res.recommended_stage = EditingStage::LineEdit;
    return res;
}

BandhuSkillResult BandhuCoreEngine::evaluateBookWriting(std::string_view text) {
    BandhuSkillResult res;
    res.skill = SkillType::BookWriting;
    res.era = classifyEra(text);

    std::string lower = toLower(text);

    // Tense lock verification (Past vs Present markers)
    static const std::vector<std::string> past_verbs = {"was", "were", "walked", "said", "looked", "saw"};
    static const std::vector<std::string> pres_verbs = {"is", "are", "walks", "says", "looks", "sees"};

    uint32_t past_hits = 0;
    uint32_t pres_hits = 0;

    for (const auto& v : past_verbs) {
        if (containsSubstr(lower, v)) past_hits++;
    }
    for (const auto& v : pres_verbs) {
        if (containsSubstr(lower, v)) pres_hits++;
    }

    if (past_hits > 0 && pres_hits > 0) {
        res.clarity_errors++;
        res.consistency_score -= 0.30f;
        res.diagnostic_notes.push_back("Tense collision: unmotivated shift between past and present narration.");
        res.recommended_stage = EditingStage::CopyEdit;
    }

    res.consistency_score = std::clamp(res.consistency_score, 0.0f, 1.0f);
    return res;
}

HistoricalEra BandhuCoreEngine::classifyEra(std::string_view text) {
    std::string lower = toLower(text);

    // Ancient indicators
    if (containsSubstr(lower, "panini") || containsSubstr(lower, "aṣṭādhyāyī")
        || containsSubstr(lower, "sanskrit") || containsSubstr(lower, "hieroglyph")
        || containsSubstr(lower, "cuneiform") || containsSubstr(lower, "sumerian")
        || containsSubstr(lower, "akkadian") || containsSubstr(lower, "sibawayh")
        || containsSubstr(lower, "kataba") || containsSubstr(lower, "gallia")) {
        return HistoricalEra::Ancient;
    }

    // Digital indicators
    if (containsSubstr(lower, "brb") || containsSubstr(lower, "lol") || containsSubstr(lower, "yyds")
        || containsSubstr(lower, "tbh") || containsSubstr(lower, "imo") || containsSubstr(lower, "nsdd")
        || containsSubstr(lower, "kaomoji") || containsSubstr(lower, "【重要】")) {
        return HistoricalEra::Digital;
    }

    // Historical indicators
    if (containsSubstr(lower, "thou ") || containsSubstr(lower, "thee ") || containsSubstr(lower, "hath ")
        || containsSubstr(lower, "doth ")) {
        return HistoricalEra::Historical;
    }

    return HistoricalEra::Modern;
}

void BandhuCoreEngine::syncToAMSV(const BandhuSkillResult& result, solorock::amsv::AtomicStateVector* amsv) {
    if (!amsv) return;

    // Pack into maio_global_state_alpha:
    // Bits 0-15: Skill ID
    // Bits 16-31: Era ID
    // Bits 32-47: Structural Score Q16
    // Bits 48-63: Register Score Q16
    uint16_t skill_id = static_cast<uint16_t>(result.skill);
    uint16_t era_id = static_cast<uint16_t>(result.era);
    uint16_t struct_q16 = static_cast<uint16_t>(result.structural_score * 65535.0f);
    uint16_t reg_q16 = static_cast<uint16_t>(result.register_score * 65535.0f);

    uint64_t packed = static_cast<uint64_t>(skill_id) |
                      (static_cast<uint64_t>(era_id) << 16) |
                      (static_cast<uint64_t>(struct_q16) << 32) |
                      (static_cast<uint64_t>(reg_q16) << 48);

    amsv->maio_global_state_alpha.store(packed);
}

} // namespace solorock::bandhu
