// =============================================================================
// engine/cpp/src/AttentionMechanism.cpp
// Full implementation of multi-head attention, KV cache, RoPE, and the
// AttentionMechanism (sustained concentration) subsystem
// =============================================================================

#include "AttentionMechanism.h"

#include <cmath>
#include <algorithm>
#include <numeric>
#include <cassert>
#include <random>
#include <sstream>
#include <stdexcept>

namespace engine {

// =============================================================================
// RotaryEmbedding
// =============================================================================

RotaryEmbedding::RotaryEmbedding(uint32_t head_dim, uint32_t max_seq_len, float base)
    : head_dim_(head_dim)
    , max_seq_len_(max_seq_len)
{
    // Precompute cos/sin tables: shape [max_seq_len, head_dim/2]
    const uint32_t half_dim = head_dim / 2;
    cos_cache_.resize(max_seq_len * half_dim);
    sin_cache_.resize(max_seq_len * half_dim);

    for (uint32_t pos = 0; pos < max_seq_len; ++pos) {
        for (uint32_t i = 0; i < half_dim; ++i) {
            // theta_i = base^(-2i/d)
            float theta = std::pow(base, -2.0f * static_cast<float>(i) /
                                         static_cast<float>(head_dim));
            float angle = static_cast<float>(pos) * theta;
            cos_cache_[pos * half_dim + i] = std::cos(angle);
            sin_cache_[pos * half_dim + i] = std::sin(angle);
        }
    }
}

void RotaryEmbedding::apply(std::vector<float>& tensor,
                             uint32_t seq_len, uint32_t num_heads,
                             uint32_t head_dim, uint32_t offset) const
{
    assert(tensor.size() == seq_len * num_heads * head_dim);
    const uint32_t half_dim = head_dim / 2;

    for (uint32_t pos = 0; pos < seq_len; ++pos) {
        const uint32_t abs_pos = pos + offset;
        assert(abs_pos < max_seq_len_);

        for (uint32_t h = 0; h < num_heads; ++h) {
            float* head_ptr = tensor.data() + (pos * num_heads + h) * head_dim;

            for (uint32_t i = 0; i < half_dim; ++i) {
                const float cos_val = cos_cache_[abs_pos * half_dim + i];
                const float sin_val = sin_cache_[abs_pos * half_dim + i];

                const float x0 = head_ptr[i];
                const float x1 = head_ptr[i + half_dim];

                // Rotate pairs: (x0, x1) → (x0*cos - x1*sin, x0*sin + x1*cos)
                head_ptr[i]           = x0 * cos_val - x1 * sin_val;
                head_ptr[i + half_dim] = x0 * sin_val + x1 * cos_val;
            }
        }
    }
}

// =============================================================================
// KVCache
// =============================================================================

KVCache::KVCache(uint32_t num_heads, uint32_t head_dim, uint32_t max_seq_len)
    : num_heads_(num_heads)
    , head_dim_(head_dim)
    , max_seq_len_(max_seq_len)
    , current_len_(0)
{
    k_cache_.resize(max_seq_len * num_heads * head_dim, 0.0f);
    v_cache_.resize(max_seq_len * num_heads * head_dim, 0.0f);
}

void KVCache::append(const std::vector<float>& key, const std::vector<float>& value) {
    assert(key.size()   == num_heads_ * head_dim_);
    assert(value.size() == num_heads_ * head_dim_);

    if (current_len_ >= max_seq_len_) {
        // Sliding window: shift left by 1 to make room for the new token
        const size_t stride = num_heads_ * head_dim_;
        std::memmove(k_cache_.data(), k_cache_.data() + stride,
                     (max_seq_len_ - 1) * stride * sizeof(float));
        std::memmove(v_cache_.data(), v_cache_.data() + stride,
                     (max_seq_len_ - 1) * stride * sizeof(float));
        current_len_ = max_seq_len_ - 1;
    }

    const size_t offset = current_len_ * num_heads_ * head_dim_;
    std::copy(key.begin(),   key.end(),   k_cache_.begin() + static_cast<ptrdiff_t>(offset));
    std::copy(value.begin(), value.end(), v_cache_.begin() + static_cast<ptrdiff_t>(offset));
    ++current_len_;
}

const std::vector<float>& KVCache::keys()   const noexcept { return k_cache_; }
const std::vector<float>& KVCache::values() const noexcept { return v_cache_; }
uint32_t KVCache::seqLen()    const noexcept { return current_len_; }
uint32_t KVCache::maxSeqLen() const noexcept { return max_seq_len_; }

void KVCache::reset() {
    current_len_ = 0;
    std::fill(k_cache_.begin(), k_cache_.end(), 0.0f);
    std::fill(v_cache_.begin(), v_cache_.end(), 0.0f);
}

void KVCache::trim(uint32_t keep_last) {
    if (keep_last >= current_len_) return;
    const uint32_t remove = current_len_ - keep_last;
    const size_t stride   = num_heads_ * head_dim_;
    std::memmove(k_cache_.data(), k_cache_.data() + remove * stride,
                 keep_last * stride * sizeof(float));
    std::memmove(v_cache_.data(), v_cache_.data() + remove * stride,
                 keep_last * stride * sizeof(float));
    current_len_ = keep_last;
}

// =============================================================================
// MultiHeadAttention — helpers
// =============================================================================

MultiHeadAttention::MultiHeadAttention(const AttentionConfig& config)
    : config_(config)
    , kv_cache_stub_(0, 0, 0) // Placeholder; only used via forwardIncremental
{
    const uint32_t D = config_.model_dim;
    std::mt19937 rng(42);
    std::normal_distribution<float> dist(0.0f, 0.02f);

    // Initialize projection matrices with Xavier-like init
    auto init = [&](std::vector<float>& w, size_t rows, size_t cols) {
        w.resize(rows * cols);
        float scale = std::sqrt(2.0f / static_cast<float>(rows + cols));
        std::normal_distribution<float> d(0.0f, scale);
        for (auto& x : w) x = d(rng);
    };

    init(W_q_, D, D);
    init(W_k_, D, D);
    init(W_v_, D, D);
    init(W_o_, D, D);

    if (config_.use_rotary_embed) {
        rope_ = std::make_unique<RotaryEmbedding>(
            config_.head_dim, config_.max_seq_len);
    }
}

void MultiHeadAttention::matmul(const float* A, const float* B, float* C,
                                  uint32_t M, uint32_t K, uint32_t N) const
{
    // Naive row-major matmul: C[M,N] = A[M,K] @ B[K,N]
    // In production this is replaced by BLAS/cuBLAS call
    for (uint32_t m = 0; m < M; ++m) {
        for (uint32_t n = 0; n < N; ++n) {
            float acc = 0.0f;
            for (uint32_t k = 0; k < K; ++k) {
                acc += A[m * K + k] * B[k * N + n];
            }
            C[m * N + n] = acc;
        }
    }
}

void MultiHeadAttention::softmaxInPlace(float* row, uint32_t len) const {
    float max_val = *std::max_element(row, row + len);
    float sum = 0.0f;
    for (uint32_t i = 0; i < len; ++i) {
        row[i] = std::exp(row[i] - max_val);
        sum += row[i];
    }
    for (uint32_t i = 0; i < len; ++i) row[i] /= sum;
}

std::vector<float> MultiHeadAttention::projectQuery(
    const std::vector<float>& x, uint32_t seq_len) const
{
    const uint32_t D = config_.model_dim;
    std::vector<float> out(seq_len * D);
    matmul(x.data(), W_q_.data(), out.data(), seq_len, D, D);
    return out;
}

std::vector<float> MultiHeadAttention::projectKey(
    const std::vector<float>& x, uint32_t seq_len) const
{
    const uint32_t D = config_.model_dim;
    std::vector<float> out(seq_len * D);
    matmul(x.data(), W_k_.data(), out.data(), seq_len, D, D);
    return out;
}

std::vector<float> MultiHeadAttention::projectValue(
    const std::vector<float>& x, uint32_t seq_len) const
{
    const uint32_t D = config_.model_dim;
    std::vector<float> out(seq_len * D);
    matmul(x.data(), W_v_.data(), out.data(), seq_len, D, D);
    return out;
}

std::vector<float> MultiHeadAttention::projectOutput(
    const std::vector<float>& x, uint32_t seq_len) const
{
    const uint32_t D = config_.model_dim;
    std::vector<float> out(seq_len * D);
    matmul(x.data(), W_o_.data(), out.data(), seq_len, D, D);
    return out;
}

std::vector<float> MultiHeadAttention::scaledDotProduct(
    const std::vector<float>& Q,
    const std::vector<float>& K,
    const std::vector<float>& V,
    uint32_t seq_len_q, uint32_t seq_len_k,
    const std::vector<float>* mask) const
{
    const uint32_t H  = config_.num_heads;
    const uint32_t Dh = config_.head_dim;
    const float scale = 1.0f / std::sqrt(static_cast<float>(Dh));

    std::vector<float> output(seq_len_q * H * Dh, 0.0f);

    for (uint32_t h = 0; h < H; ++h) {
        // Compute attention scores: Sq x Sk
        std::vector<float> scores(seq_len_q * seq_len_k);

        for (uint32_t qi = 0; qi < seq_len_q; ++qi) {
            for (uint32_t ki = 0; ki < seq_len_k; ++ki) {
                float dot = 0.0f;
                for (uint32_t d = 0; d < Dh; ++d) {
                    dot += Q[(qi * H + h) * Dh + d] * K[(ki * H + h) * Dh + d];
                }
                float score = dot * scale;
                if (mask) score += (*mask)[qi * seq_len_k + ki];
                scores[qi * seq_len_k + ki] = score;
            }
        }

        // Softmax over keys for each query
        for (uint32_t qi = 0; qi < seq_len_q; ++qi) {
            softmaxInPlace(scores.data() + qi * seq_len_k, seq_len_k);
        }

        // Weighted sum of values
        for (uint32_t qi = 0; qi < seq_len_q; ++qi) {
            for (uint32_t d = 0; d < Dh; ++d) {
                float acc = 0.0f;
                for (uint32_t ki = 0; ki < seq_len_k; ++ki) {
                    acc += scores[qi * seq_len_k + ki] *
                           V[(ki * H + h) * Dh + d];
                }
                output[(qi * H + h) * Dh + d] = acc;
            }
        }
    }

    return output;
}

std::vector<float> MultiHeadAttention::forward(
    const std::vector<float>& query,
    const std::vector<float>& key,
    const std::vector<float>& value,
    uint32_t seq_len,
    const std::vector<float>* mask) const
{
    const uint32_t D = config_.model_dim;
    assert(query.size() == seq_len * D);
    assert(key.size()   == seq_len * D);
    assert(value.size() == seq_len * D);

    // Project to Q, K, V
    auto Q = projectQuery(query, seq_len);
    auto K = projectKey  (key,   seq_len);
    auto V = projectValue(value, seq_len);

    // Apply RoPE to Q and K
    if (config_.use_rotary_embed && rope_) {
        rope_->apply(Q, seq_len, config_.num_heads, config_.head_dim);
        rope_->apply(K, seq_len, config_.num_heads, config_.head_dim);
    }

    // Scaled dot-product attention
    auto attended = scaledDotProduct(Q, K, V, seq_len, seq_len, mask);

    // Reshape [seq_len, H, Dh] → [seq_len, D] (they are the same)
    // Project output
    return projectOutput(attended, seq_len);
}

std::vector<float> MultiHeadAttention::forwardIncremental(
    const std::vector<float>& query_token,
    KVCache& kv_cache,
    uint32_t position) const
{
    const uint32_t D  = config_.model_dim;
    const uint32_t H  = config_.num_heads;
    const uint32_t Dh = config_.head_dim;

    assert(query_token.size() == D);

    // Project query (shape [1, D])
    auto Q = projectQuery(query_token, 1);
    auto K = projectKey  (query_token, 1);
    auto V = projectValue(query_token, 1);

    // Apply RoPE at current position
    if (config_.use_rotary_embed && rope_) {
        rope_->apply(Q, 1, H, Dh, position);
        rope_->apply(K, 1, H, Dh, position);
    }

    // Append to KV cache
    kv_cache.append(K, V);

    // Attend over full KV cache
    uint32_t cache_len = kv_cache.seqLen();
    // KV cache stores flat: [seq_len, H*Dh] need [seq_len, H, Dh]
    const auto& K_full = kv_cache.keys();
    const auto& V_full = kv_cache.values();

    // Compute scores for this single query against all cached K
    const float scale = 1.0f / std::sqrt(static_cast<float>(Dh));
    std::vector<float> output(H * Dh, 0.0f);

    for (uint32_t h = 0; h < H; ++h) {
        std::vector<float> scores(cache_len);
        for (uint32_t ki = 0; ki < cache_len; ++ki) {
            float dot = 0.0f;
            for (uint32_t d = 0; d < Dh; ++d) {
                dot += Q[h * Dh + d] * K_full[(ki * H + h) * Dh + d];
            }
            scores[ki] = dot * scale;
        }
        softmaxInPlace(scores.data(), cache_len);

        for (uint32_t d = 0; d < Dh; ++d) {
            float acc = 0.0f;
            for (uint32_t ki = 0; ki < cache_len; ++ki) {
                acc += scores[ki] * V_full[(ki * H + h) * Dh + d];
            }
            output[h * Dh + d] = acc;
        }
    }

    // Project output (reshape to [1, D])
    return projectOutput(output, 1);
}

const AttentionConfig& MultiHeadAttention::config() const noexcept {
    return config_;
}

// =============================================================================
// AttentionMechanism — the engine's sustained attention subsystem
// =============================================================================

AttentionMechanism::AttentionMechanism(const EngineConfig& config)
    : attn_config_{
        .num_heads         = config.attention_heads,
        .head_dim          = config.attention_dim / config.attention_heads,
        .model_dim         = config.attention_dim,
        .max_seq_len       = config.max_sequence_length,
        .dropout_rate      = config.attention_dropout,
        .temperature       = 1.0f,
        .use_rotary_embed  = true,
        .use_flash_attn    = config.enable_gpu,
        .causal_mask       = false
    }
    , mha_     (attn_config_)
    , kv_cache_(config.attention_heads,
                config.attention_dim / config.attention_heads,
                config.max_sequence_length)
{
    // Initialize attended context to zero
    attended_context_.assign(config.attention_dim, 0.0f);

    // Initialize a simple token embedding table with random init
    // In production this is loaded from the model weights file
    std::mt19937 rng(1337);
    std::normal_distribution<float> dist(0.0f, 0.02f);
    // Pre-allocate embeddings for common tokens
    auto make_embed = [&]() {
        std::vector<float> e(config.attention_dim);
        for (auto& v : e) v = dist(rng);
        return e;
    };
    for (const char* tok : {"[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]",
                             "hi", "hello", "hey", "i", "am", "my", "name",
                             "is", "the", "a", "an", ".", ",", "?", "!"}) {
        token_embed_table_[tok] = make_embed();
    }
}

std::vector<float> AttentionMechanism::embedToken(const Token& token) const {
    auto it = token_embed_table_.find(token.normalized);
    if (it != token_embed_table_.end()) return it->second;

    // Unknown token: hash-based deterministic embedding (production: nearest-neighbor lookup)
    std::vector<float> embed(attn_config_.model_dim, 0.0f);
    std::hash<std::string> hasher;
    std::mt19937 rng(static_cast<uint32_t>(hasher(token.normalized)));
    std::normal_distribution<float> dist(0.0f, 0.02f);
    for (auto& v : embed) v = dist(rng);
    return embed;
}

std::vector<float> AttentionMechanism::embedUtterance(
    const TokenizedUtterance& utterance) const
{
    if (utterance.tokens.empty()) {
        return std::vector<float>(attn_config_.model_dim, 0.0f);
    }
    std::vector<float> result;
    result.reserve(utterance.tokens.size() * attn_config_.model_dim);
    for (const auto& tok : utterance.tokens) {
        auto embed = embedToken(tok);
        result.insert(result.end(), embed.begin(), embed.end());
    }
    return result;
}

void AttentionMechanism::updateWithUtterance(const TokenizedUtterance& utterance) {
    std::lock_guard lock(mutex_);

    if (utterance.tokens.empty()) return;

    const uint32_t seq_len = static_cast<uint32_t>(utterance.tokens.size());
    const uint32_t D       = attn_config_.model_dim;
    const uint32_t H       = attn_config_.num_heads;
    const uint32_t Dh      = attn_config_.head_dim;

    // Embed the utterance
    auto embedded = embedUtterance(utterance);  // [seq_len, D]

    // For each token, do incremental attention update
    for (uint32_t t = 0; t < seq_len; ++t) {
        const uint32_t pos = kv_cache_.seqLen(); // position before append
        std::vector<float> token_vec(embedded.begin() + t * D,
                                     embedded.begin() + (t + 1) * D);

        // Compute incremental attention output for this token
        auto out = mha_.forwardIncremental(token_vec, kv_cache_, pos);

        // The last token's attention output becomes the new attended context
        if (t == seq_len - 1) {
            attended_context_ = out;
        }
    }
}

std::vector<float> AttentionMechanism::getAttendedContext() const {
    std::lock_guard lock(mutex_);
    return attended_context_;
}

std::vector<float> AttentionMechanism::attendTo(
    const std::vector<float>& query) const
{
    std::lock_guard lock(mutex_);

    if (kv_cache_.seqLen() == 0 || query.empty()) {
        return std::vector<float>(attn_config_.model_dim, 0.0f);
    }

    uint32_t pos = kv_cache_.seqLen();
    // Forward incremental without modifying cache (create a scratch copy)
    KVCache scratch_cache(attn_config_.num_heads, attn_config_.head_dim,
                           attn_config_.max_seq_len);
    // Copy current KV cache contents into scratch
    for (uint32_t i = 0; i < kv_cache_.seqLen(); ++i) {
        const uint32_t stride = attn_config_.num_heads * attn_config_.head_dim;
        std::vector<float> k(kv_cache_.keys().begin()   + i * stride,
                             kv_cache_.keys().begin()   + (i + 1) * stride);
        std::vector<float> v(kv_cache_.values().begin() + i * stride,
                             kv_cache_.values().begin() + (i + 1) * stride);
        scratch_cache.append(k, v);
    }

    return mha_.forwardIncremental(query, scratch_cache, pos);
}

AttentionState AttentionMechanism::captureState() const {
    std::lock_guard lock(mutex_);
    AttentionState state;
    state.query_vector   = attended_context_;
    state.key_cache      = kv_cache_.keys();
    state.value_cache    = kv_cache_.values();
    state.head_count     = attn_config_.num_heads;
    state.sequence_length = kv_cache_.seqLen();
    state.temperature    = attn_config_.temperature;
    return state;
}

void AttentionMechanism::reset() {
    std::lock_guard lock(mutex_);
    kv_cache_.reset();
    std::fill(attended_context_.begin(), attended_context_.end(), 0.0f);
}

uint32_t AttentionMechanism::currentSeqLen() const noexcept {
    return kv_cache_.seqLen();
}

const AttentionConfig& AttentionMechanism::config() const noexcept {
    return attn_config_;
}

} // namespace engine
