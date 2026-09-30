// =============================================================================
// engine/cpp/include/EngineCore.h
// Verbal Communication Engine — Core C++ Header
// Production-grade, recruitment-driven architecture
// =============================================================================

#pragma once

#include <cstdint>
#include <cstddef>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <functional>
#include <atomic>
#include <mutex>
#include <shared_mutex>
#include <optional>
#include <variant>
#include <span>
#include <chrono>

namespace engine {

// =============================================================================
// Forward declarations
// =============================================================================

class VocalInputProcessor;
class LanguageUnderstanding;
class ResponseGenerator;
class SpeechSynthesizer;
class MemoryManager;
class AttentionMechanism;
class RecruitmentOrchestrator;
class TokenizerBridge;

// =============================================================================
// Core enumerations
// =============================================================================

enum class EngineStatus : uint8_t {
    UNINITIALIZED = 0,
    RECRUITING    = 1,
    OPERATIONAL   = 2,
    PROCESSING    = 3,
    SUSPENDED     = 4,
    ERROR_STATE   = 5,
    SHUTDOWN      = 6
};

enum class InputModality : uint8_t {
    TEXT        = 0,
    SPEECH_PCM  = 1,
    SPEECH_OPUS = 2,
    IMAGE_TEXT  = 3,
    HANDWRITING = 4
};

enum class OutputModality : uint8_t {
    TEXT          = 0,
    SPEECH_PCM    = 1,
    SPEECH_OPUS   = 2,
    STRUCTURED    = 3
};

enum class ReasoningDepth : uint8_t {
    SHALLOW  = 0,   // fast, single-pass
    MODERATE = 1,   // 2–4 reasoning steps
    DEEP     = 2,   // full chain-of-thought
    EXTENDED = 3    // recursive multi-hypothesis
};

enum class RegisterType : uint8_t {
    FORMAL         = 0,
    NEUTRAL        = 1,
    INFORMAL       = 2,
    TECHNICAL      = 3,
    CREATIVE       = 4,
    CHILD_DIRECTED = 5
};

// =============================================================================
// Core data structures
// =============================================================================

/// Raw audio frame: 16-bit PCM, mono or stereo.
struct AudioFrame {
    std::vector<int16_t> samples;
    uint32_t             sample_rate;   ///< Hz, e.g. 16000 or 44100
    uint8_t              channels;      ///< 1 = mono, 2 = stereo
    std::chrono::milliseconds timestamp;
};

/// A normalized language token with full linguistic annotation.
struct Token {
    std::string  surface;          ///< Original surface form
    std::string  normalized;       ///< Lowercase/normalized form
    std::string  lemma;            ///< Dictionary base form
    std::string  pos_tag;          ///< Universal Dependencies POS tag
    std::string  dep_label;        ///< Dependency relation label
    uint32_t     position;         ///< Token index in sentence
    uint32_t     char_start;       ///< Character offset start
    uint32_t     char_end;         ///< Character offset end (exclusive)
    float        confidence;       ///< Tokenizer confidence [0,1]
    bool         is_special;       ///< True for [CLS], [SEP], etc.
};

/// A complete tokenized utterance.
struct TokenizedUtterance {
    std::string          raw_text;
    std::vector<Token>   tokens;
    std::string          language_code;  ///< BCP-47 language tag
    float                lang_confidence;
};

/// Semantic intent extracted from an utterance.
struct Intent {
    std::string               name;           ///< e.g. "greet_and_identify"
    float                     confidence;     ///< [0,1]
    std::unordered_map<std::string, std::string> slots;  ///< slot name → value
};

/// A complete meaning frame for an utterance.
struct MeaningFrame {
    Intent                  primary_intent;
    std::vector<Intent>     secondary_intents;
    std::string             literal_meaning;
    std::string             natural_meaning;
    RegisterType            detected_register;
    float                   sentiment;        ///< [-1,1]
    float                   certainty;        ///< [0,1]
};

/// A planned response before surface realization.
struct ResponsePlan {
    std::string          communicative_goal;
    std::vector<std::string> content_slots;
    RegisterType         target_register;
    ReasoningDepth       depth;
    std::string          language_code;
    float                creativity_level;   ///< [0,1]
};

/// Fully realized response ready for output.
struct EngineResponse {
    std::string   text;
    AudioFrame    speech;                ///< Only populated if speech requested
    OutputModality modality;
    float         confidence;
    std::string   reasoning_trace;      ///< Chain-of-thought trace (optional)
    std::chrono::milliseconds latency;
};

/// Attention state: a compressed representation of what the engine is
/// "attending to" at a given moment across the input context.
struct AttentionState {
    std::vector<float>  query_vector;    ///< current query embedding
    std::vector<float>  key_cache;       ///< cached key vectors (flattened)
    std::vector<float>  value_cache;     ///< cached value vectors (flattened)
    uint32_t            head_count;
    uint32_t            sequence_length;
    float               temperature;    ///< attention temperature
};

/// Memory entry for episodic or semantic memory systems.
struct MemoryEntry {
    uint64_t     id;
    std::string  content;
    std::string  memory_type;    ///< "episodic" | "semantic" | "working"
    float        salience;       ///< [0,1] importance weight
    std::chrono::system_clock::time_point created_at;
    std::chrono::system_clock::time_point last_accessed;
    uint32_t     access_count;
    bool         approved;
};

// =============================================================================
// Engine configuration
// =============================================================================

struct EngineConfig {
    // Identity
    std::string  engine_id;
    std::string  engine_version;

    // Modalities
    InputModality  default_input_modality   = InputModality::TEXT;
    OutputModality default_output_modality  = OutputModality::TEXT;

    // Language
    std::string  default_language           = "en";
    std::vector<std::string> supported_languages;

    // Performance
    uint32_t  thread_pool_size    = 8;
    uint32_t  max_batch_size      = 64;
    uint32_t  max_sequence_length = 8192;
    bool      enable_gpu          = true;
    int       gpu_device_id       = 0;

    // Memory
    size_t   working_memory_bytes  = 1ULL << 30;  ///< 1 GB
    size_t   episodic_memory_slots = 65536;
    size_t   semantic_memory_slots = 1048576;

    // Attention
    uint32_t  attention_heads     = 16;
    uint32_t  attention_dim       = 1024;
    float     attention_dropout   = 0.1f;

    // Reasoning
    ReasoningDepth default_reasoning_depth = ReasoningDepth::MODERATE;
    uint32_t       max_reasoning_steps     = 32;

    // Safety
    bool  enable_safety_filter  = true;
    bool  enable_privacy_guard  = true;
    float safety_threshold      = 0.85f;
};

// =============================================================================
// Core EngineCore class
// =============================================================================

/**
 * @brief EngineCore — The central class for the Verbal Communication Engine.
 *
 * Implements a recruitment-driven architecture: the engine is instantiated and
 * then progressively recruits/activates subsystems as their functional requirements
 * are identified. Once all required subsystems are recruited, the engine is
 * declared operational.
 *
 * Thread safety: All public methods are thread-safe. Internal state is protected
 * by reader-writer locks for maximum read concurrency.
 */
class EngineCore {
public:
    // -------------------------------------------------------------------------
    // Construction & lifecycle
    // -------------------------------------------------------------------------

    /**
     * @brief Constructs an engine with the given configuration.
     * @param config  Full engine configuration. Caller retains ownership.
     */
    explicit EngineCore(EngineConfig config);

    /// Non-copyable
    EngineCore(const EngineCore&)            = delete;
    EngineCore& operator=(const EngineCore&) = delete;

    /// Movable
    EngineCore(EngineCore&&)            noexcept;
    EngineCore& operator=(EngineCore&&) noexcept;

    ~EngineCore();

    // -------------------------------------------------------------------------
    // Recruitment-driven initialization
    // -------------------------------------------------------------------------

    /**
     * @brief Recruits and activates all engine subsystems in dependency order.
     *
     * Recruitment order:
     *   1. MemoryManager         — working, episodic, semantic stores
     *   2. TokenizerBridge       — Rust tokenizer via FFI
     *   3. AttentionMechanism    — attention heads and KV cache
     *   4. VocalInputProcessor   — speech-to-text + text normalization
     *   5. LanguageUnderstanding — intent, semantics, pragmatics
     *   6. ResponseGenerator     — planning, realization, creativity
     *   7. SpeechSynthesizer     — text-to-speech synthesis
     *
     * @throws std::runtime_error if any subsystem fails to recruit.
     * @returns true if all subsystems are operational.
     */
    bool recruitAllSubsystems();

    /**
     * @brief Recruits a single named subsystem.
     * @param subsystem_name  One of: "memory", "tokenizer", "attention",
     *                        "input", "understanding", "generator", "synthesizer"
     */
    bool recruitSubsystem(std::string_view subsystem_name);

    /**
     * @brief Returns true if all required subsystems are recruited and ready.
     */
    bool isOperational() const noexcept;

    // -------------------------------------------------------------------------
    // Core processing pipeline
    // -------------------------------------------------------------------------

    /**
     * @brief Processes a text input through the full engine pipeline.
     *
     * Pipeline:
     *   text input → normalization → tokenization → language detection →
     *   morphology → syntax → semantics → pragmatics → intent extraction →
     *   response planning → word selection → grammar realization → output
     *
     * @param input       Raw input text.
     * @param modality    Requested output modality.
     * @param depth       Reasoning depth for this request.
     * @returns           Fully realized EngineResponse.
     */
    EngineResponse processText(
        std::string_view  input,
        OutputModality    modality = OutputModality::TEXT,
        ReasoningDepth    depth    = ReasoningDepth::MODERATE
    );

    /**
     * @brief Processes an audio frame through the full engine pipeline.
     *
     * Pipeline:
     *   audio → voice activity detection → speech-to-text → processText
     *
     * @param frame   Raw PCM audio frame.
     * @param depth   Reasoning depth.
     * @returns       Fully realized EngineResponse.
     */
    EngineResponse processAudio(
        const AudioFrame& frame,
        ReasoningDepth    depth = ReasoningDepth::MODERATE
    );

    // -------------------------------------------------------------------------
    // Subsystem accessors (for testing and inter-language FFI)
    // -------------------------------------------------------------------------

    MemoryManager&          memory()       noexcept;
    const MemoryManager&    memory() const noexcept;
    AttentionMechanism&     attention()    noexcept;
    LanguageUnderstanding&  understanding() noexcept;
    ResponseGenerator&      generator()   noexcept;

    // -------------------------------------------------------------------------
    // Status and diagnostics
    // -------------------------------------------------------------------------

    EngineStatus        status()    const noexcept;
    const EngineConfig& config()    const noexcept;
    std::string         statusReport() const;

    /**
     * @brief Returns a JSON-serialized engine health dump.
     * Includes per-subsystem status, memory usage, and latency stats.
     */
    std::string healthDump() const;

    // -------------------------------------------------------------------------
    // Shutdown
    // -------------------------------------------------------------------------

    /**
     * @brief Gracefully shuts down all subsystems and releases resources.
     */
    void shutdown();

private:
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};

// =============================================================================
// EngineFactory — creates and configures EngineCore instances
// =============================================================================

class EngineFactory {
public:
    /**
     * @brief Creates a default production-ready engine.
     * Loads configuration from the YAML engine training file.
     *
     * @param training_file_path  Path to the canonical engine training YAML.
     * @returns Fully configured EngineCore, already recruited.
     */
    static std::unique_ptr<EngineCore> createFromTrainingFile(
        std::string_view training_file_path
    );

    /**
     * @brief Creates an engine from an explicit EngineConfig.
     */
    static std::unique_ptr<EngineCore> createFromConfig(EngineConfig config);
};

// =============================================================================
// C-linkage exports for FFI (Python/Java/Julia/Rust)
// =============================================================================

extern "C" {

/// Opaque handle to an EngineCore instance for FFI consumers.
struct EngineHandle;

/// Creates an engine from config JSON string. Returns heap-allocated handle.
EngineHandle* engine_create(const char* config_json);

/// Recruits all subsystems. Returns 1 on success, 0 on failure.
int engine_recruit(EngineHandle* handle);

/// Processes text input. Writes result into out_buf (caller allocates out_buf_size bytes).
/// Returns number of bytes written, or -1 on error.
int engine_process_text(EngineHandle* handle,
                        const char* input, size_t input_len,
                        char* out_buf, size_t out_buf_size);

/// Returns 1 if engine is operational, 0 otherwise.
int engine_is_operational(EngineHandle* handle);

/// Returns a null-terminated JSON health dump string. Caller must free with engine_free_string().
char* engine_health_dump(EngineHandle* handle);

/// Frees a string allocated by engine_*.
void engine_free_string(char* str);

/// Destroys the engine handle and releases all resources.
void engine_destroy(EngineHandle* handle);

} // extern "C"

} // namespace engine
