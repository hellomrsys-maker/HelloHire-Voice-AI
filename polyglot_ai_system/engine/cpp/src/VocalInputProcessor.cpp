// =============================================================================
// engine/cpp/src/VocalInputProcessor.cpp
// Full implementation of speech processing, tokenizer bridge, synthesizer,
// and recruitment orchestrator
// =============================================================================

#include "VocalInputProcessor.h"
#include "MemoryManager.h"
#include "AttentionMechanism.h"
#include "LanguageUnderstanding.h"
#include "ResponseGenerator.h"

#include <algorithm>
#include <sstream>
#include <cctype>
#include <cmath>
#include <cassert>
#include <numeric>

namespace engine {

// =============================================================================
// TokenizerBridge
// =============================================================================

TokenizerBridge::TokenizerBridge(const EngineConfig& config)
    : config_(config)
{}

TokenizerBridge::~TokenizerBridge() = default;

std::vector<std::string> TokenizerBridge::splitTokens(const std::string& text) const {
    // Whitespace + punctuation tokenizer (BPE-lite baseline)
    // Production: calls Rust tokenizer via dlopen("librust_tokenizer.so")
    std::vector<std::string> tokens;
    std::string current;

    for (size_t i = 0; i < text.size(); ++i) {
        char c = text[i];
        if (std::isspace(c)) {
            if (!current.empty()) { tokens.push_back(current); current.clear(); }
        } else if (std::ispunct(c) && c != '\'' && c != '-') {
            if (!current.empty()) { tokens.push_back(current); current.clear(); }
            tokens.push_back(std::string(1, c));
        } else {
            current += c;
        }
    }
    if (!current.empty()) tokens.push_back(current);
    return tokens;
}

std::vector<Token> TokenizerBridge::tokenize(const std::string& text) const {
    auto surface_tokens = splitTokens(text);
    std::vector<Token> tokens;
    tokens.reserve(surface_tokens.size());

    uint32_t char_pos = 0;
    for (uint32_t i = 0; i < static_cast<uint32_t>(surface_tokens.size()); ++i) {
        const auto& surf = surface_tokens[i];

        // Lowercase normalized form
        std::string norm = surf;
        std::transform(norm.begin(), norm.end(), norm.begin(), ::tolower);

        // Detect special tokens
        bool is_special = (surf == "[CLS]" || surf == "[SEP]" || surf == "[PAD]" ||
                           surf == "[UNK]" || surf == "[MASK]");

        // Find char position in original text
        size_t found = text.find(surf, char_pos);
        uint32_t cs = (found != std::string::npos) ? static_cast<uint32_t>(found) : char_pos;
        uint32_t ce = cs + static_cast<uint32_t>(surf.size());
        char_pos = ce;

        tokens.push_back(Token{
            .surface    = surf,
            .normalized = norm,
            .lemma      = norm,    // Will be overridden by morphological analysis
            .pos_tag    = "",      // Will be filled by LanguageUnderstanding
            .dep_label  = "",
            .position   = i,
            .char_start = cs,
            .char_end   = ce,
            .confidence = 1.0f,
            .is_special = is_special
        });
    }
    return tokens;
}

size_t TokenizerBridge::vocabSize() const noexcept {
    // Production: return actual vocab size from loaded Rust tokenizer
    return 50257; // GPT-2 vocab size as baseline
}

std::string TokenizerBridge::idToToken(uint32_t id) const {
    // Production: lookup in vocab table loaded from Rust side
    return "[tok_" + std::to_string(id) + "]";
}

uint32_t TokenizerBridge::tokenToId(const std::string& token) const {
    // Production: reverse lookup in vocab table
    std::hash<std::string> h;
    return static_cast<uint32_t>(h(token) % 50257);
}

// =============================================================================
// VocalInputProcessor
// =============================================================================

VocalInputProcessor::VocalInputProcessor(const EngineConfig& config,
                                           TokenizerBridge& tokenizer)
    : config_(config)
    , tokenizer_(tokenizer)
{
    initLangModels();
}

void VocalInputProcessor::initLangModels() {
    // Simplified trigram-based language identification priors
    // Production: load trained model weights from binary file
    lang_ngram_models_["en"]["the"] = 0.052f;
    lang_ngram_models_["en"]["and"] = 0.028f;
    lang_ngram_models_["en"]["ing"] = 0.015f;
    lang_ngram_models_["fr"]["les"] = 0.040f;
    lang_ngram_models_["fr"]["est"] = 0.025f;
    lang_ngram_models_["fr"]["qui"] = 0.020f;
    lang_ngram_models_["de"]["der"] = 0.045f;
    lang_ngram_models_["de"]["und"] = 0.030f;
    lang_ngram_models_["es"]["que"] = 0.038f;
    lang_ngram_models_["es"]["los"] = 0.028f;
    lang_ngram_models_["ja"]["は"]   = 0.050f;
    lang_ngram_models_["ja"]["の"]   = 0.055f;
}

std::string VocalInputProcessor::unicodeNormalize(const std::string& text) const {
    // NFC normalization (simplified: in production use ICU or utf8proc)
    // For ASCII-range text this is a no-op
    std::string result;
    result.reserve(text.size());
    for (unsigned char c : text) {
        result += static_cast<char>(c);
    }
    return result;
}

std::string VocalInputProcessor::stripControlChars(const std::string& text) const {
    std::string result;
    result.reserve(text.size());
    for (unsigned char c : text) {
        if (c >= 0x20 || c == '\n' || c == '\t') {
            result += static_cast<char>(c);
        }
    }
    return result;
}

TokenizedUtterance VocalInputProcessor::normalizeAndTokenize(const std::string& raw_text) {
    // Step 1: Strip control characters
    std::string clean = stripControlChars(raw_text);

    // Step 2: Unicode normalization
    std::string normalized = unicodeNormalize(clean);

    // Step 3: Trim leading/trailing whitespace
    size_t start = normalized.find_first_not_of(" \t\n\r");
    size_t end   = normalized.find_last_not_of(" \t\n\r");
    if (start == std::string::npos) normalized = "";
    else normalized = normalized.substr(start, end - start + 1);

    // Step 4: Language detection
    auto [lang_code, lang_conf] = detectLanguage(normalized);

    // Step 5: Tokenize via Rust tokenizer bridge
    auto tokens = tokenizer_.tokenize(normalized);

    return TokenizedUtterance{
        .raw_text        = raw_text,
        .tokens          = std::move(tokens),
        .language_code   = lang_code,
        .lang_confidence = lang_conf
    };
}

bool VocalInputProcessor::hasVoiceActivity(const AudioFrame& frame) const {
    if (frame.samples.empty()) return false;

    // Compute root mean square energy
    double energy_sum = 0.0;
    for (int16_t sample : frame.samples) {
        double normalized = static_cast<double>(sample) / 32768.0;
        energy_sum += normalized * normalized;
    }
    double rms = std::sqrt(energy_sum / frame.samples.size());
    return rms > vad_energy_threshold_;
}

std::string VocalInputProcessor::speechToText(const AudioFrame& frame) {
    // Production: invoke Whisper ASR via CUDA kernel through FFI
    // The CUDA kernel (engine/cuda/kernels/asr_kernel.cu) handles this path.
    // For the baseline without GPU, we return a dummy transcript.
    (void)frame;
    return "[ASR_TRANSCRIPT: speech-to-text not yet connected to CUDA ASR kernel]";
}

std::pair<std::string, float> VocalInputProcessor::detectLanguage(
    const std::string& text) const
{
    if (text.empty()) return {"en", 1.0f};

    // Lowercase text for matching
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    std::unordered_map<std::string, float> lang_scores;
    for (const auto& [lang, ngrams] : lang_ngram_models_) {
        float score = 0.0f;
        for (const auto& [ngram, weight] : ngrams) {
            size_t pos = 0;
            while ((pos = lower.find(ngram, pos)) != std::string::npos) {
                score += weight;
                ++pos;
            }
        }
        lang_scores[lang] = score;
    }

    // Find highest scoring language
    auto best = std::max_element(
        lang_scores.begin(), lang_scores.end(),
        [](const auto& a, const auto& b) { return a.second < b.second; });

    if (best == lang_scores.end() || best->second == 0.0f) {
        return {"en", 0.6f}; // Default to English
    }

    // Compute softmax-normalized confidence
    float total = 0.0f;
    for (const auto& [_, s] : lang_scores) total += s;
    float conf = (total > 0.0f) ? best->second / total : 0.6f;

    return {best->first, conf};
}

// =============================================================================
// SpeechSynthesizer
// =============================================================================

SpeechSynthesizer::SpeechSynthesizer(const EngineConfig& config)
    : config_(config)
{}

AudioFrame SpeechSynthesizer::generateSineWave(float frequency, float duration_sec) const {
    const uint32_t num_samples = static_cast<uint32_t>(sample_rate_ * duration_sec);
    AudioFrame frame;
    frame.sample_rate = sample_rate_;
    frame.channels    = channels_;
    frame.timestamp   = std::chrono::milliseconds(0);
    frame.samples.resize(num_samples);

    for (uint32_t i = 0; i < num_samples; ++i) {
        float t = static_cast<float>(i) / static_cast<float>(sample_rate_);
        float sample = 0.3f * std::sin(2.0f * 3.14159265f * frequency * t);
        frame.samples[i] = static_cast<int16_t>(sample * 32767.0f);
    }
    return frame;
}

AudioFrame SpeechSynthesizer::synthesize(const std::string& text,
                                           const std::string& language_code,
                                           OutputModality modality) const
{
    // Production: invoke VITS/FastSpeech2 neural TTS via CUDA kernel
    // The kernel is in engine/cuda/kernels/tts_kernel.cu
    // For now: generate a 440Hz tone (A4) for the duration proportional to text length

    (void)language_code;
    (void)modality;

    const float duration = std::max(0.5f, std::min(5.0f,
        static_cast<float>(text.size()) * 0.05f));
    return generateSineWave(440.0f, duration);
}

// =============================================================================
// RecruitmentOrchestrator
// =============================================================================

RecruitmentOrchestrator::RecruitmentOrchestrator(const EngineConfig& config)
    : config_(config)
{}

std::unique_ptr<MemoryManager> RecruitmentOrchestrator::recruitMemoryManager(
    const EngineConfig& config)
{
    return std::make_unique<MemoryManager>(config);
}

std::unique_ptr<TokenizerBridge> RecruitmentOrchestrator::recruitTokenizerBridge(
    const EngineConfig& config)
{
    return std::make_unique<TokenizerBridge>(config);
}

std::unique_ptr<AttentionMechanism> RecruitmentOrchestrator::recruitAttentionMechanism(
    const EngineConfig& config)
{
    return std::make_unique<AttentionMechanism>(config);
}

std::unique_ptr<VocalInputProcessor> RecruitmentOrchestrator::recruitVocalInputProcessor(
    const EngineConfig& config, TokenizerBridge& tokenizer)
{
    return std::make_unique<VocalInputProcessor>(config, tokenizer);
}

std::unique_ptr<LanguageUnderstanding> RecruitmentOrchestrator::recruitLanguageUnderstanding(
    const EngineConfig& config,
    AttentionMechanism& attention,
    MemoryManager& memory)
{
    return std::make_unique<LanguageUnderstanding>(config, attention, memory);
}

std::unique_ptr<ResponseGenerator> RecruitmentOrchestrator::recruitResponseGenerator(
    const EngineConfig& config,
    LanguageUnderstanding& understanding,
    MemoryManager& memory)
{
    return std::make_unique<ResponseGenerator>(config, understanding, memory);
}

std::unique_ptr<SpeechSynthesizer> RecruitmentOrchestrator::recruitSpeechSynthesizer(
    const EngineConfig& config)
{
    return std::make_unique<SpeechSynthesizer>(config);
}

} // namespace engine
