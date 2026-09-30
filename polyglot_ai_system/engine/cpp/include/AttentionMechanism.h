// =============================================================================
// engine/cpp/include/AttentionMechanism.h
// Multi-head self-attention and KV-cache for the verbal communication engine
// Concentration and sustained attention modeled as attention architecture
// =============================================================================

#pragma once

#include "EngineCore.h"
#include <vector>
#include <cstdint>
#include <string>
#include <memory>
#include <mutex>
#include <atomic>

namespace engine {

// =============================================================================
// AttentionConfig
// =============================================================================

struct AttentionConfig {
    uint32_t  num_heads         = 16;
    uint32_t  head_dim          = 64;    ///< d_k per head
    uint32_t  model_dim         = 1024;  ///< d_model = num_heads * head_dim
    uint32_t  max_seq_len       = 8192;
    float     dropout_rate      = 0.1f;
    float     temperature       = 1.0f;
    bool      use_rotary_embed  = true;  ///< RoPE positional encoding
    bool      use_flash_attn    = true;  ///< Use Flash Attention kernel when available
    bool      causal_mask       = false; ///< True for decoder, false for encoder
};

// =============================================================================
// RotaryEmbedding — RoPE positional encoding
// =============================================================================

class RotaryEmbedding {
public:
    explicit RotaryEmbedding(uint32_t head_dim, uint32_t max_seq_len,
                              float base = 10000.0f);

    /// Applies RoPE in-place to a query or key tensor.
    /// Tensor layout: [seq_len, num_heads, head_dim]
    void apply(std::vector<float>& tensor,
               uint32_t seq_len, uint32_t num_heads, uint32_t head_dim,
               uint32_t offset = 0) const;

private:
    std::vector<float> cos_cache_; ///< cos(m * theta_i) [max_seq_len, head_dim/2]
    std::vector<float> sin_cache_; ///< sin(m * theta_i) [max_seq_len, head_dim/2]
    uint32_t           head_dim_;
    uint32_t           max_seq_len_;
};

// =============================================================================
// KVCache — efficient key-value cache for incremental attention
// =============================================================================

class KVCache {
public:
    KVCache(uint32_t num_heads, uint32_t head_dim, uint32_t max_seq_len);

    /// Appends a new key/value pair at the current position.
    void append(const std::vector<float>& key,   ///< [num_heads, head_dim]
                const std::vector<float>& value); ///< [num_heads, head_dim]

    /// Returns all cached keys up to the current sequence length.
    /// Shape: [seq_len, num_heads, head_dim]
    const std::vector<float>& keys()   const noexcept;
    const std::vector<float>& values() const noexcept;

    uint32_t seqLen()   const noexcept;
    uint32_t maxSeqLen() const noexcept;

    /// Resets the cache (e.g., new conversation turn).
    void reset();

    /// Removes entries older than `keep_last` tokens.
    void trim(uint32_t keep_last);

private:
    uint32_t          num_heads_;
    uint32_t          head_dim_;
    uint32_t          max_seq_len_;
    uint32_t          current_len_{0};
    std::vector<float> k_cache_; ///< [max_seq_len, num_heads, head_dim]
    std::vector<float> v_cache_; ///< [max_seq_len, num_heads, head_dim]
};

// =============================================================================
// MultiHeadAttention — core scaled dot-product multi-head attention
// =============================================================================

class MultiHeadAttention {
public:
    explicit MultiHeadAttention(const AttentionConfig& config);

    /**
     * @brief Computes multi-head attention.
     *
     * All tensors are row-major float32:
     *   Q, K, V: [seq_len, model_dim]
     *   output:  [seq_len, model_dim]
     *
     * @param query    Input query tensor.
     * @param key      Input key tensor.
     * @param value    Input value tensor.
     * @param seq_len  Number of tokens in the sequence.
     * @param mask     Optional causal/padding mask (size seq_len*seq_len; -inf blocks).
     * @returns        Attention output [seq_len, model_dim].
     */
    std::vector<float> forward(
        const std::vector<float>& query,
        const std::vector<float>& key,
        const std::vector<float>& value,
        uint32_t seq_len,
        const std::vector<float>* mask = nullptr) const;

    /**
     * @brief Incremental forward pass using KV cache.
     * Used during auto-regressive generation (one token at a time).
     *
     * @param query_token  Single token query [model_dim].
     * @param kv_cache     Running KV cache to read from and append to.
     * @param position     Current position in sequence (for RoPE).
     * @returns            Attention output [model_dim].
     */
    std::vector<float> forwardIncremental(
        const std::vector<float>& query_token,
        KVCache& kv_cache,
        uint32_t position) const;

    const AttentionConfig& config() const noexcept;

private:
    AttentionConfig config_;

    // Linear projection weights: [model_dim, model_dim] row-major
    std::vector<float> W_q_;
    std::vector<float> W_k_;
    std::vector<float> W_v_;
    std::vector<float> W_o_;

    std::unique_ptr<RotaryEmbedding> rope_;

    // Core computation helpers
    std::vector<float> projectQuery (const std::vector<float>& x, uint32_t seq_len) const;
    std::vector<float> projectKey   (const std::vector<float>& x, uint32_t seq_len) const;
    std::vector<float> projectValue (const std::vector<float>& x, uint32_t seq_len) const;
    std::vector<float> projectOutput(const std::vector<float>& x, uint32_t seq_len) const;

    std::vector<float> scaledDotProduct(
        const std::vector<float>& Q, const std::vector<float>& K,
        const std::vector<float>& V, uint32_t seq_len_q, uint32_t seq_len_k,
        const std::vector<float>* mask) const;

    void matmul(const float* A, const float* B, float* C,
                uint32_t M, uint32_t K, uint32_t N) const;
    void softmaxInPlace(float* row, uint32_t len) const;
};

// =============================================================================
// AttentionMechanism — the engine's sustained-attention subsystem
//
// Models "concentration and sustained attention" as a streaming multi-head
// attention architecture over the ongoing conversation context. Maintains
// a rolling KV cache, computes cross-utterance attention, and provides
// attended context vectors for downstream language understanding.
// =============================================================================

class AttentionMechanism {
public:
    explicit AttentionMechanism(const EngineConfig& config);

    /**
     * @brief Updates the attention state with a newly tokenized utterance.
     * The utterance's tokens are embedded and added to the rolling KV cache.
     *
     * @param utterance  Fully tokenized utterance from the input processor.
     */
    void updateWithUtterance(const TokenizedUtterance& utterance);

    /**
     * @brief Returns the current attended context vector.
     * This is a [model_dim] float vector summarizing what the engine
     * is "attending to" based on the full conversation context so far.
     */
    std::vector<float> getAttendedContext() const;

    /**
     * @brief Computes cross-attention between a query vector and the KV cache.
     * Used by the language understanding layer to attend to the full context.
     *
     * @param query  Query vector [model_dim].
     * @returns      Attended output vector [model_dim].
     */
    std::vector<float> attendTo(const std::vector<float>& query) const;

    /**
     * @brief Returns the current attention state for diagnostics/export.
     */
    AttentionState captureState() const;

    /**
     * @brief Resets the KV cache (e.g., new conversation).
     */
    void reset();

    /**
     * @brief Returns current sequence length in the KV cache.
     */
    uint32_t currentSeqLen() const noexcept;

    const AttentionConfig& config() const noexcept;

private:
    AttentionConfig    attn_config_;
    MultiHeadAttention mha_;
    KVCache            kv_cache_;
    mutable std::mutex mutex_;

    // Token embedding table (simplified: random init in production, replaced by loaded weights)
    std::unordered_map<std::string, std::vector<float>> token_embed_table_;

    /// Embeds a single token into [model_dim] float vector.
    std::vector<float> embedToken(const Token& token) const;

    /// Embeds an entire utterance into [seq_len, model_dim].
    std::vector<float> embedUtterance(const TokenizedUtterance& utterance) const;

    /// Current attended context (updated after each updateWithUtterance call).
    std::vector<float> attended_context_;
};

} // namespace engine
