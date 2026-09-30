// =============================================================================
// engine/cpp/include/VocalInputProcessor.h
// Speech input processing: VAD, ASR, text normalization, tokenization bridge
// =============================================================================

#pragma once

#include "EngineCore.h"
#include "TokenizerBridge.h"
#include <vector>
#include <string>
#include <memory>

namespace engine {

class VocalInputProcessor {
public:
    explicit VocalInputProcessor(const EngineConfig& config, TokenizerBridge& tokenizer);

    /**
     * @brief Normalizes and tokenizes a raw text string.
     * Steps: Unicode normalization → lowercasing → tokenization → annotation
     */
    TokenizedUtterance normalizeAndTokenize(const std::string& raw_text);

    /**
     * @brief Detects voice activity in an audio frame.
     * Uses energy-based VAD with adaptive threshold.
     * @returns true if speech energy above threshold.
     */
    bool hasVoiceActivity(const AudioFrame& frame) const;

    /**
     * @brief Converts a PCM audio frame to text transcript.
     * Production: calls Whisper or custom ASR model via CUDA kernel.
     * @returns Transcribed text.
     */
    std::string speechToText(const AudioFrame& frame);

    /**
     * @brief Detects the BCP-47 language code of a text string.
     * Uses n-gram language identification.
     * @returns {language_code, confidence}.
     */
    std::pair<std::string, float> detectLanguage(const std::string& text) const;

private:
    const EngineConfig& config_;
    TokenizerBridge&    tokenizer_;

    // VAD parameters
    float vad_energy_threshold_ = 0.01f;
    float vad_silence_threshold_ = 0.001f;

    // Unicode normalization helpers
    std::string unicodeNormalize(const std::string& text) const;
    std::string stripControlChars(const std::string& text) const;

    // Language identification n-gram model (trigram char-based)
    std::unordered_map<std::string,
        std::unordered_map<std::string, float>> lang_ngram_models_;
    void initLangModels();
};

// =============================================================================
// SpeechSynthesizer — text-to-speech synthesis
// =============================================================================

class SpeechSynthesizer {
public:
    explicit SpeechSynthesizer(const EngineConfig& config);

    /**
     * @brief Synthesizes speech from text.
     * Production: calls TTS neural model via CUDA.
     * Returns PCM AudioFrame.
     */
    AudioFrame synthesize(const std::string& text,
                          const std::string& language_code,
                          OutputModality modality) const;

private:
    const EngineConfig& config_;
    uint32_t sample_rate_ = 22050;
    uint8_t  channels_    = 1;

    // Generate a simple sinusoidal placeholder waveform for testing.
    // Production: replaced by neural TTS (e.g. VoiceFlow, VITS).
    AudioFrame generateSineWave(float frequency, float duration_sec) const;
};

// =============================================================================
// TokenizerBridge — FFI bridge to Rust tokenizer
// =============================================================================

class TokenizerBridge {
public:
    explicit TokenizerBridge(const EngineConfig& config);
    ~TokenizerBridge();

    /**
     * @brief Tokenizes raw text into a list of Token objects.
     * Calls the Rust tokenization library via C-linkage FFI.
     */
    std::vector<Token> tokenize(const std::string& text) const;

    /**
     * @brief Returns the vocabulary size.
     */
    size_t vocabSize() const noexcept;

    /**
     * @brief Converts a token ID to its surface form.
     */
    std::string idToToken(uint32_t id) const;

    /**
     * @brief Converts a surface form to its token ID. Returns 1 ([UNK]) if not found.
     */
    uint32_t tokenToId(const std::string& token) const;

private:
    const EngineConfig& config_;

    // Simple built-in tokenizer (whitespace + punctuation split)
    // In production, this calls the Rust tokenizer library via dlopen/JNI
    std::vector<std::string> splitTokens(const std::string& text) const;
};

// =============================================================================
// RecruitmentOrchestrator — coordinates subsystem instantiation
// =============================================================================

class RecruitmentOrchestrator {
public:
    explicit RecruitmentOrchestrator(const EngineConfig& config);

    std::unique_ptr<MemoryManager>          recruitMemoryManager(const EngineConfig& config);
    std::unique_ptr<TokenizerBridge>        recruitTokenizerBridge(const EngineConfig& config);
    std::unique_ptr<AttentionMechanism>     recruitAttentionMechanism(const EngineConfig& config);
    std::unique_ptr<VocalInputProcessor>    recruitVocalInputProcessor(
                                                const EngineConfig& config,
                                                TokenizerBridge& tokenizer);
    std::unique_ptr<LanguageUnderstanding>  recruitLanguageUnderstanding(
                                                const EngineConfig& config,
                                                AttentionMechanism& attention,
                                                MemoryManager& memory);
    std::unique_ptr<ResponseGenerator>     recruitResponseGenerator(
                                                const EngineConfig& config,
                                                LanguageUnderstanding& understanding,
                                                MemoryManager& memory);
    std::unique_ptr<SpeechSynthesizer>     recruitSpeechSynthesizer(const EngineConfig& config);

private:
    const EngineConfig& config_;
};

} // namespace engine
