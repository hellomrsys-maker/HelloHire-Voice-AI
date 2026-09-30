/**
 * @file typology_engine.cpp
 * @brief Implementation of Universal Comparative Grammar Typology Engine Core.
 */

#include "../include/typology_engine.hpp"
#include <cstring>
#include <algorithm>
#include <sstream>

namespace solorock::typology {

TypologyEngine::TypologyEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {}

TypologicalProfile TypologyEngine::analyze_sample(
    const std::string& text,
    LanguageFamily family_hint
) {
    TypologicalProfile profile;
    profile.family = family_hint;

    // Set canonical structural parameters based on family
    switch (family_hint) {
        case LanguageFamily::SinoTibetan:
            profile.morph_type = MorphologicalType::Isolating;
            profile.alignment = GrammaticalAlignment::NominativeAccusative;
            profile.directionality = HeadDirectionality::HeadInitial;
            profile.synthesis_index = 1.05f;
            profile.greenberg_harmony = 0.92f;
            profile.pillar_scores = {0.95f, 0.92f, 0.88f, 0.90f, 0.98f, 0.90f, 0.88f, 0.82f};
            profile.diagnostic_summary = "Typology [Sino-Tibetan]: Isolating, Tone, Measure Classifiers, Aspect Particles, Rigid SVO.";
            break;

        case LanguageFamily::AfroAsiatic:
            profile.morph_type = MorphologicalType::Fusional;
            profile.alignment = GrammaticalAlignment::NominativeAccusative;
            profile.directionality = HeadDirectionality::HeadInitial;
            profile.synthesis_index = 2.40f;
            profile.greenberg_harmony = 0.85f;
            profile.pillar_scores = {0.92f, 0.86f, 0.90f, 0.95f, 0.88f, 0.85f, 0.84f, 0.86f};
            profile.diagnostic_summary = "Typology [Afro-Asiatic]: Templatic Root-and-Pattern, Broken Plurals, Dual Number, VSO/SVO.";
            break;

        case LanguageFamily::Austronesian:
            profile.morph_type = MorphologicalType::Agglutinative;
            profile.alignment = GrammaticalAlignment::SymmetricalVoice;
            profile.directionality = HeadDirectionality::HeadInitial;
            profile.synthesis_index = 1.85f;
            profile.greenberg_harmony = 0.82f;
            profile.pillar_scores = {0.88f, 0.80f, 0.96f, 0.97f, 0.86f, 0.85f, 0.80f, 0.84f};
            profile.diagnostic_summary = "Typology [Austronesian]: Symmetrical Voice, Pivot Alignment, Inclusive/Exclusive 1PL, Reduplication.";
            break;

        case LanguageFamily::NigerCongo:
            profile.morph_type = MorphologicalType::Agglutinative;
            profile.alignment = GrammaticalAlignment::NominativeAccusative;
            profile.directionality = HeadDirectionality::HeadInitial;
            profile.synthesis_index = 2.65f;
            profile.greenberg_harmony = 0.88f;
            profile.pillar_scores = {0.94f, 0.99f, 0.90f, 0.94f, 0.90f, 0.88f, 0.82f, 0.85f};
            profile.diagnostic_summary = "Typology [Niger-Congo]: 10-22 Noun Classes, Prefixing Alliterative Concord, Tonal Grammar.";
            break;

        case LanguageFamily::JaponicKoreanic:
            profile.morph_type = MorphologicalType::Agglutinative;
            profile.alignment = GrammaticalAlignment::NominativeAccusative;
            profile.directionality = HeadDirectionality::HeadFinal;
            profile.synthesis_index = 2.85f;
            profile.greenberg_harmony = 0.98f;
            profile.pillar_scores = {0.92f, 0.78f, 0.98f, 0.96f, 0.99f, 0.92f, 0.99f, 0.85f};
            profile.diagnostic_summary = "Typology [Japonic/Koreanic]: Strict SOV, Postpositional Particles, Left-Branching, Keigo Honorifics.";
            break;

        case LanguageFamily::Dravidian:
            profile.morph_type = MorphologicalType::Agglutinative;
            profile.alignment = GrammaticalAlignment::NominativeAccusative;
            profile.directionality = HeadDirectionality::HeadFinal;
            profile.synthesis_index = 3.10f;
            profile.greenberg_harmony = 0.96f;
            profile.pillar_scores = {0.96f, 0.82f, 0.95f, 0.94f, 0.98f, 0.88f, 0.85f, 0.82f};
            profile.diagnostic_summary = "Typology [Dravidian]: Retroflex Phonology, Dative Subjects, Suffix-Only Agglutination, Strict SOV.";
            break;

        case LanguageFamily::Uralic:
            profile.morph_type = MorphologicalType::Agglutinative;
            profile.alignment = GrammaticalAlignment::NominativeAccusative;
            profile.directionality = HeadDirectionality::HeadFinal;
            profile.synthesis_index = 3.40f;
            profile.greenberg_harmony = 0.90f;
            profile.pillar_scores = {0.94f, 1.00f, 0.98f, 0.92f, 0.92f, 0.94f, 0.80f, 0.84f};
            profile.diagnostic_summary = "Typology [Uralic]: 15-27 Spatial Cases, Triadic Local Locatives, Vowel Harmony, Zero Gender, Negative Verb.";
            break;

        case LanguageFamily::Turkic:
            profile.morph_type = MorphologicalType::Agglutinative;
            profile.alignment = GrammaticalAlignment::NominativeAccusative;
            profile.directionality = HeadDirectionality::HeadFinal;
            profile.synthesis_index = 3.60f;
            profile.greenberg_harmony = 0.99f;
            profile.pillar_scores = {0.98f, 1.00f, 0.95f, 0.96f, 0.99f, 0.94f, 0.88f, 0.88f};
            profile.diagnostic_summary = "Typology [Turkic]: Pure Transparent Agglutination, 2/4-Way Vowel Harmony, Evidentiality, SOV Postpositions.";
            break;

        case LanguageFamily::NativeAmericanIsolates:
            profile.morph_type = MorphologicalType::Polysynthetic;
            profile.alignment = GrammaticalAlignment::ErgativeAbsolutive;
            profile.directionality = HeadDirectionality::HeadFinal;
            profile.synthesis_index = 4.85f;
            profile.greenberg_harmony = 0.75f;
            profile.pillar_scores = {0.90f, 0.92f, 0.96f, 0.98f, 0.85f, 0.84f, 0.82f, 0.85f};
            profile.diagnostic_summary = "Typology [Polysynthetic/Isolates]: Sentence-Words, Ergative-Absolutive, Handling Stems, Obviation.";
            break;

        case LanguageFamily::CreolesPidgins:
            profile.morph_type = MorphologicalType::Isolating;
            profile.alignment = GrammaticalAlignment::NominativeAccusative;
            profile.directionality = HeadDirectionality::HeadInitial;
            profile.synthesis_index = 1.08f;
            profile.greenberg_harmony = 0.95f;
            profile.pillar_scores = {0.85f, 0.90f, 0.84f, 0.92f, 0.96f, 0.90f, 0.80f, 0.88f};
            profile.diagnostic_summary = "Typology [Creoles/Pidgins]: Radical Analytic Regularization, Pre-Verbal TMA Particles, SVO.";
            break;

        case LanguageFamily::IndoEuropean:
        default:
            profile.morph_type = MorphologicalType::Fusional;
            profile.alignment = GrammaticalAlignment::NominativeAccusative;
            profile.directionality = HeadDirectionality::HeadInitial;
            profile.synthesis_index = 2.15f;
            profile.greenberg_harmony = 0.78f;
            profile.pillar_scores = {0.88f, 0.85f, 0.86f, 0.90f, 0.88f, 0.86f, 0.84f, 0.85f};
            profile.diagnostic_summary = "Typology [Indo-European]: Fusional Portmanteau Endings, Grammatical Gender, Case Syncretism, Ablaut.";
            break;
    }

    // Predict L1 transfer friction assuming English (Indo-European) L1
    profile.l1_transfer_frictions = predict_friction(LanguageFamily::IndoEuropean, family_hint);

    // Synchronize to shared physical memory
    sync_to_amsv(profile);

    return profile;
}

void TypologyEngine::sync_to_amsv(const TypologicalProfile& profile) {
    if (!amsv_) return;

    // Pack typological feature vector directly into amsv_->linguistic_embedding (floats 0..15):
    amsv_->linguistic_embedding[0] = static_cast<float>(profile.family);
    amsv_->linguistic_embedding[1] = static_cast<float>(profile.morph_type);
    amsv_->linguistic_embedding[2] = static_cast<float>(profile.alignment);
    amsv_->linguistic_embedding[3] = static_cast<float>(profile.directionality);
    amsv_->linguistic_embedding[4] = profile.synthesis_index;
    amsv_->linguistic_embedding[5] = profile.greenberg_harmony;

    for (size_t i = 0; i < 8; ++i) {
        amsv_->linguistic_embedding[6 + i] = profile.pillar_scores[i];
    }

    // Offset 14: L1-L2 friction penalty index
    amsv_->linguistic_embedding[14] = profile.l1_transfer_frictions.empty() ? 0.0f : 0.75f;
    // Offset 15: Heartbeat update counter / Valid flag
    amsv_->linguistic_embedding[15] = 1.0f;

    // If summary exists, write to AMSV error_diagnostic_buffer
    if (!profile.diagnostic_summary.empty()) {
        size_t len = std::min(profile.diagnostic_summary.size(), sizeof(amsv_->error_diagnostic_buffer) - 1);
        std::memcpy(amsv_->error_diagnostic_buffer, profile.diagnostic_summary.c_str(), len);
        amsv_->error_diagnostic_buffer[len] = '\0';
    }
}

std::vector<std::string> TypologyEngine::predict_friction(LanguageFamily l1, LanguageFamily l2) {
    std::vector<std::string> frictions;

    if (l1 == LanguageFamily::IndoEuropean && l2 == LanguageFamily::Turkic) {
        frictions.push_back("Delayed Semantic Resolution: Head-final SOV forces memory hold before predicate resolves.");
        frictions.push_back("Evidentiality Obligation: Mandatory epistemic distinction between direct (-di) and indirect (-mis) past.");
        frictions.push_back("2-Way and 4-Way Vowel Harmony: Cognitive latency computing harmonic vowel shifts across suffix chains.");
        frictions.push_back("Differential Object Marking: Definite direct objects require accusative case, indefinite remain unmarked.");
    } else if (l1 == LanguageFamily::IndoEuropean && l2 == LanguageFamily::SinoTibetan) {
        frictions.push_back("Aspect vs Tense Paradigm: Erroneously applying perfective 'le' as an English simple past marker.");
        frictions.push_back("Classifier Selection: Nouns require sortal classifiers matching physical/geometric prototypes.");
        frictions.push_back("Tonal Minimal Pairs: Disassociating pitch from sentence intonation into lexical phonemic roots.");
    } else if (l1 == LanguageFamily::IndoEuropean && l2 == LanguageFamily::Austronesian) {
        frictions.push_back("Passive Voice Fallacy: Treating Patient Focus as passive rather than the default topical pivot.");
        frictions.push_back("Inclusive vs Exclusive 1PL: Confusing 'kita' (inclusive) with 'kami' (exclusive).");
    } else if (l1 == LanguageFamily::IndoEuropean && l2 == LanguageFamily::JaponicKoreanic) {
        frictions.push_back("Topic vs Subject Split: Conflating informational frame (wa/eun) with grammatical agent (ga/i).");
        frictions.push_back("Honorific Social Deixis: Obligatory calculation of in-group/out-group and hierarchical rank.");
    } else {
        frictions.push_back("Divergent morphological synthesis and head-directionality parameters.");
    }

    return frictions;
}

} // namespace solorock::typology
