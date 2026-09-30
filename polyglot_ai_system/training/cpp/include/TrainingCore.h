// =============================================================================
// training/cpp/include/TrainingCore.h
// AI Training System — Core C++ Header
// Covers: thinking ability, deep reasoning, attention mechanisms,
//         recall/memory, creativity, imagination, and all cognitive faculties.
// =============================================================================

#pragma once

#include <cstdint>
#include <memory>
#include <string>
#include <vector>
#include <unordered_map>
#include <functional>
#include <atomic>
#include <mutex>
#include <shared_mutex>
#include <optional>
#include <span>
#include <chrono>

namespace training {

// =============================================================================
// Forward declarations
// =============================================================================

class CognitiveModel;
class ThinkingEngine;
class MemoryTrainer;
class CreativityTrainer;
class ImaginationModule;
class MetacognitionTrainer;
class TrainingDataManager;
class CheckpointManager;
class LossComputer;

// =============================================================================
// Training phase enumeration
// =============================================================================

enum class TrainingPhase : uint8_t {
    UNSTARTED           = 0,
    WARMUP              = 1,
    THINKING_TRAINING   = 2,
    ATTENTION_TRAINING  = 3,
    MEMORY_TRAINING     = 4,
    CREATIVITY_TRAINING = 5,
    IMAGINATION_TRAINING = 6,
    METACOGNITION_TRAINING = 7,
    INTEGRATION         = 8,
    EVALUATION          = 9,
    COMPLETE            = 10,
};

// =============================================================================
// Cognitive capability descriptors
// =============================================================================

enum class CognitiveFaculty : uint32_t {
    THINKING       = 1 << 0,  ///< Deep reasoning chains
    ATTENTION      = 1 << 1,  ///< Sustained concentration mechanisms
    EPISODIC_MEMORY= 1 << 2,  ///< Recall of specific past events
    SEMANTIC_MEMORY= 1 << 3,  ///< General world knowledge recall
    CREATIVITY     = 1 << 4,  ///< Divergent thinking
    IMAGINATION    = 1 << 5,  ///< Generative synthesis
    ASSOCIATION    = 1 << 6,  ///< Associative reasoning
    METACOGNITION  = 1 << 7,  ///< Self-monitoring of reasoning quality
    CURIOSITY      = 1 << 8,  ///< Curiosity-driven exploration
    ALL            = 0xFFFFFFFF
};

inline CognitiveFaculty operator|(CognitiveFaculty a, CognitiveFaculty b) {
    return static_cast<CognitiveFaculty>(
        static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}
inline bool has_faculty(CognitiveFaculty set, CognitiveFaculty query) {
    return (static_cast<uint32_t>(set) & static_cast<uint32_t>(query)) != 0;
}

// =============================================================================
// Training configuration
// =============================================================================

struct TrainingConfig {
    // Run identity
    std::string  run_id;
    std::string  experiment_name;

    // Cognitive capabilities to train
    CognitiveFaculty  faculties_to_train = CognitiveFaculty::ALL;

    // Training loop hyperparameters
    uint32_t  num_epochs           = 100;
    uint32_t  batch_size           = 32;
    float     learning_rate        = 3e-4f;
    float     lr_warmup_fraction   = 0.1f;
    float     weight_decay         = 0.01f;
    float     gradient_clip_norm   = 1.0f;
    uint32_t  eval_every_steps     = 500;
    uint32_t  checkpoint_every_steps = 1000;
    uint32_t  max_steps            = 100000;

    // Model architecture
    uint32_t  model_dim      = 1024;
    uint32_t  num_heads      = 16;
    uint32_t  num_layers     = 24;
    uint32_t  ffn_dim        = 4096;
    uint32_t  max_seq_length = 8192;
    float     dropout        = 0.1f;

    // Memory training
    uint32_t  episodic_memory_size = 131072;
    uint32_t  semantic_memory_size = 2097152;
    uint32_t  working_memory_size  = 4096;

    // Creativity training
    float     creativity_temperature  = 0.8f;
    uint32_t  diversity_penalty_steps = 100;
    float     originality_weight      = 0.3f;

    // Reasoning depth training
    uint32_t  min_reasoning_steps = 1;
    uint32_t  max_reasoning_steps = 32;
    float     chain_of_thought_supervision_weight = 0.5f;

    // Computation
    uint32_t  num_workers  = 8;
    bool      use_gpu      = true;
    int       gpu_device   = 0;
    bool      use_mixed_precision = true;

    // Paths
    std::string  data_dir          = "data/";
    std::string  checkpoint_dir    = "checkpoints/";
    std::string  experiment_dir    = "experiments/";
    std::string  engine_config_path = "language_engines/English_engine.training.yaml";
};

// =============================================================================
// Training metrics
// =============================================================================

struct TrainingMetrics {
    uint64_t  global_step;
    uint32_t  epoch;
    float     loss;
    float     thinking_loss;
    float     attention_loss;
    float     memory_loss;
    float     creativity_loss;
    float     imagination_loss;
    float     metacognition_loss;
    float     learning_rate;
    float     gradient_norm;
    double    tokens_per_second;
    std::chrono::milliseconds step_time;
};

// =============================================================================
// TrainingCore — main training system class
// =============================================================================

/**
 * @brief TrainingCore — coordinates the full AI training pipeline.
 *
 * Implements training across all cognitive faculties:
 *   1. Thinking ability and deep reasoning chains
 *   2. Concentration and sustained attention mechanisms
 *   3. Functioning recall (episodic + semantic memory)
 *   4. Creativity and divergent thinking
 *   5. Imagination and generative synthesis
 *   6. Associative reasoning (emergent from 1-5)
 *   7. Metacognition (emergent from 1-5)
 *   8. Curiosity-driven exploration (emergent from 4-5)
 *
 * Training begins ONLY after the verbal communication engine is verified
 * as operational (enforced by the build system).
 */
class TrainingCore {
public:
    explicit TrainingCore(TrainingConfig config);
    TrainingCore(const TrainingCore&)            = delete;
    TrainingCore& operator=(const TrainingCore&) = delete;
    TrainingCore(TrainingCore&&)            noexcept;
    TrainingCore& operator=(TrainingCore&&) noexcept;
    ~TrainingCore();

    // -------------------------------------------------------------------------
    // Training pipeline
    // -------------------------------------------------------------------------

    /**
     * @brief Runs the complete training pipeline.
     * Trains all requested cognitive faculties in the configured order.
     * Saves checkpoints and logs metrics at regular intervals.
     */
    void train();

    /**
     * @brief Runs a single training step.
     * Returns the metrics for this step.
     */
    TrainingMetrics step();

    /**
     * @brief Evaluates the model on the held-out evaluation set.
     * Returns a metrics snapshot.
     */
    TrainingMetrics evaluate();

    /**
     * @brief Saves a training checkpoint.
     * @param tag  Optional tag (e.g., "best", "latest", "epoch_10")
     */
    void saveCheckpoint(const std::string& tag = "latest");

    /**
     * @brief Loads a training checkpoint.
     * @param checkpoint_path  Path to the checkpoint directory or file.
     */
    void loadCheckpoint(const std::string& checkpoint_path);

    // -------------------------------------------------------------------------
    // Status
    // -------------------------------------------------------------------------

    TrainingPhase   currentPhase()  const noexcept;
    TrainingMetrics lastMetrics()   const;
    uint64_t        globalStep()    const noexcept;
    bool            isTraining()    const noexcept;

    /**
     * @brief Gracefully stops training after the current step completes.
     */
    void requestStop();

    const TrainingConfig& config() const noexcept;

    // -------------------------------------------------------------------------
    // Subsystem accessors
    // -------------------------------------------------------------------------

    CognitiveModel&    model()        noexcept;
    ThinkingEngine&    thinking()     noexcept;
    MemoryTrainer&     memory()       noexcept;
    CreativityTrainer& creativity()   noexcept;
    ImaginationModule& imagination()  noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};

// =============================================================================
// C-linkage exports for FFI
// =============================================================================

extern "C" {

struct TrainingHandle;

TrainingHandle* training_create(const char* config_json);
int             training_start(TrainingHandle* handle);
int             training_step(TrainingHandle* handle, float* out_loss);
int             training_save_checkpoint(TrainingHandle* handle, const char* tag);
void            training_request_stop(TrainingHandle* handle);
void            training_destroy(TrainingHandle* handle);

} // extern "C"

} // namespace training
