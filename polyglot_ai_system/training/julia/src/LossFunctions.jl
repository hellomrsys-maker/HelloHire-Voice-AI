# =============================================================================
# training/julia/src/LossFunctions.jl
# Training loss functions: cross-entropy, Brier score, contrastive loss,
# creativity loss, and cognitive faculty-specific loss implementations.
# =============================================================================

module LossFunctions

using LinearAlgebra
using Statistics

export cross_entropy_loss, brier_score,
       contrastive_loss, triplet_loss,
       thinking_loss, creativity_loss,
       imagination_loss, metacognition_loss,
       kl_divergence, focal_loss

# =============================================================================
# Cross-Entropy Loss
# =============================================================================

"""
    cross_entropy_loss(logits::AbstractMatrix, targets::AbstractVector{<:Integer};
                        ignore_index::Int = -1, reduction::Symbol = :mean)
                      -> Float32

Numerically stable cross-entropy loss for language model training.

# Arguments
- `logits`:       [batch_size, vocab_size] raw logits (NOT softmax)
- `targets`:      [batch_size] integer target token IDs (0-based)
- `ignore_index`: Target ID to ignore (e.g., padding token)
- `reduction`:    `:mean` (default), `:sum`, or `:none`

# Returns
- Scalar loss (or vector if reduction = :none)

# Example
```julia
logits  = randn(Float32, 4, 1000)
targets = Int32[42, 73, 150, 8]
loss    = cross_entropy_loss(logits, targets)
```
"""
function cross_entropy_loss(
    logits::AbstractMatrix{T},
    targets::AbstractVector{<:Integer};
    ignore_index::Int = -1,
    reduction::Symbol = :mean,
) :: Union{Float32, Vector{Float32}} where T <: AbstractFloat

    batch_size, vocab_size = size(logits)
    @assert length(targets) == batch_size "targets length must match batch_size"

    losses = Vector{Float32}(undef, batch_size)

    for i in 1:batch_size
        t = Int(targets[i]) + 1  # Convert 0-based to 1-based Julia indexing

        if targets[i] == ignore_index || t < 1 || t > vocab_size
            losses[i] = 0.0f0
            continue
        end

        # Numerically stable: subtract max before exp
        row = @view logits[i, :]
        max_val = maximum(row)
        shifted = row .- max_val
        log_sum_exp = max_val + log(sum(exp.(shifted)))
        losses[i] = -(row[t] - log_sum_exp)
    end

    if reduction == :mean
        valid_count = count(i -> targets[i] != ignore_index, 1:batch_size)
        return valid_count > 0 ? sum(losses) / Float32(valid_count) : 0.0f0
    elseif reduction == :sum
        return Float32(sum(losses))
    elseif reduction == :none
        return losses
    else
        throw(ArgumentError("Unknown reduction: $reduction"))
    end
end

# =============================================================================
# KL Divergence
# =============================================================================

"""
    kl_divergence(p::AbstractVector, q::AbstractVector; eps::Float32 = 1e-9f0)
                 -> Float32

KL divergence KL(p || q) = ∑ p * log(p / q).
Both p and q must be valid probability distributions (sum to 1).
"""
function kl_divergence(
    p::AbstractVector{T},
    q::AbstractVector{T};
    eps::Float32 = 1e-9f0,
) :: Float32 where T <: AbstractFloat

    @assert length(p) == length(q) "p and q must have same length"
    kl = Float32(0.0)
    for i in eachindex(p)
        pi = Float32(p[i]) + eps
        qi = Float32(q[i]) + eps
        kl += pi * log(pi / qi)
    end
    return kl
end

# =============================================================================
# Focal Loss (for handling class imbalance in classification)
# =============================================================================

"""
    focal_loss(probs::AbstractVector, targets::AbstractVector{Bool};
                gamma::Float32 = 2.0f0, alpha::Float32 = 0.25f0)
             -> Float32

Focal loss for addressing class imbalance.
FL(p) = -α * (1-p)^γ * log(p) for positive examples
FL(p) = -(1-α) * p^γ * log(1-p) for negative examples
"""
function focal_loss(
    probs::AbstractVector{T},
    targets::AbstractVector{Bool};
    gamma::Float32 = 2.0f0,
    alpha::Float32 = 0.25f0,
    eps::Float32   = 1e-8f0,
) :: Float32 where T <: AbstractFloat

    @assert length(probs) == length(targets)
    loss = Float32(0.0)
    n = length(probs)

    for i in 1:n
        p = clamp(Float32(probs[i]), eps, 1.0f0 - eps)
        if targets[i]
            loss += -alpha * (1.0f0 - p)^gamma * log(p)
        else
            loss += -(1.0f0 - alpha) * p^gamma * log(1.0f0 - p)
        end
    end
    return loss / Float32(n)
end

# =============================================================================
# Brier Score (for calibration / metacognition training)
# =============================================================================

"""
    brier_score(predicted_probs::AbstractVector, outcomes::AbstractVector{Bool})
              -> Float32

Brier score: measures calibration of predicted probabilities.
BS = (1/N) * ∑(predicted_prob - outcome)²
Lower = better calibrated.
"""
function brier_score(
    predicted_probs::AbstractVector{T},
    outcomes::AbstractVector{Bool},
) :: Float32 where T <: AbstractFloat

    @assert length(predicted_probs) == length(outcomes)
    Float32(mean((Float32.(predicted_probs) .- Float32.(outcomes)) .^ 2))
end

# =============================================================================
# Contrastive Loss (for memory recall and similarity training)
# =============================================================================

"""
    contrastive_loss(embeddings_a::AbstractMatrix,
                      embeddings_b::AbstractMatrix,
                      labels::AbstractVector{Bool};
                      margin::Float32 = 1.0f0)
                   -> Float32

Contrastive loss for learning embeddings:
  - For similar pairs (label=true):  loss = d²
  - For dissimilar pairs (label=false): loss = max(0, margin - d)²

where d = L2 distance between embedding pairs.
"""
function contrastive_loss(
    embeddings_a::AbstractMatrix{T},
    embeddings_b::AbstractMatrix{T},
    labels::AbstractVector{Bool};
    margin::Float32 = 1.0f0,
) :: Float32 where T <: AbstractFloat

    @assert size(embeddings_a) == size(embeddings_b)
    @assert size(embeddings_a, 1) == length(labels)

    n = length(labels)
    total_loss = Float32(0.0)

    for i in 1:n
        d = Float32(norm(embeddings_a[i, :] .- embeddings_b[i, :]))
        if labels[i]
            total_loss += d^2
        else
            total_loss += max(0.0f0, margin - d)^2
        end
    end
    return total_loss / Float32(n)
end

# =============================================================================
# Triplet Loss (for memory retrieval training)
# =============================================================================

"""
    triplet_loss(anchor::AbstractMatrix, positive::AbstractMatrix,
                  negative::AbstractMatrix; margin::Float32 = 0.3f0)
              -> Float32

Triplet loss for learning embedding spaces:
L = max(0, d(anchor, positive) - d(anchor, negative) + margin)
"""
function triplet_loss(
    anchor::AbstractMatrix{T},
    positive::AbstractMatrix{T},
    negative::AbstractMatrix{T};
    margin::Float32 = 0.3f0,
) :: Float32 where T <: AbstractFloat

    @assert size(anchor) == size(positive) == size(negative)
    n = size(anchor, 1)
    total = Float32(0.0)

    for i in 1:n
        d_pos = Float32(norm(anchor[i, :] .- positive[i, :]))
        d_neg = Float32(norm(anchor[i, :] .- negative[i, :]))
        total += max(0.0f0, d_pos - d_neg + margin)
    end
    return total / Float32(n)
end

# =============================================================================
# Thinking loss (chain-of-thought supervision)
# =============================================================================

"""
    thinking_loss(final_logits::AbstractMatrix, final_targets::AbstractVector{<:Integer},
                   cot_logits::AbstractMatrix,  cot_targets::AbstractVector{<:Integer};
                   cot_weight::Float32 = 0.5f0)
              -> NamedTuple

Computes the full thinking/reasoning training loss:
  L_thinking = L_final + cot_weight × L_cot

# Arguments
- `final_logits`:   [batch, vocab] logits for final answer tokens
- `final_targets`:  [batch] ground-truth final answer token IDs
- `cot_logits`:     [batch * n_steps, vocab] logits for CoT step tokens
- `cot_targets`:    [batch * n_steps] supervision token IDs for CoT steps
- `cot_weight`:     Weight for the chain-of-thought loss component

# Returns
NamedTuple: (total, final, chain_of_thought)
"""
function thinking_loss(
    final_logits::AbstractMatrix{T},
    final_targets::AbstractVector{<:Integer},
    cot_logits::AbstractMatrix{T},
    cot_targets::AbstractVector{<:Integer};
    cot_weight::Float32 = 0.5f0,
) :: NamedTuple where T <: AbstractFloat

    l_final = cross_entropy_loss(final_logits, final_targets)
    l_cot   = cross_entropy_loss(cot_logits,   cot_targets)
    total   = l_final + cot_weight * l_cot

    return (total=total, final=l_final, chain_of_thought=l_cot)
end

# =============================================================================
# Creativity loss
# =============================================================================

"""
    creativity_loss(coherence_logits::AbstractMatrix,
                     coherence_targets::AbstractVector{<:Integer},
                     diversity_embeddings::AbstractMatrix;
                     div_weight::Float32 = 0.3f0,
                     orig_weight::Float32 = 0.3f0)
              -> NamedTuple

Computes creativity training loss:
L_creativity = L_coherence - div_weight × R_diversity - orig_weight × R_originality

# Arguments
- `coherence_logits`:     [batch, vocab] logits for coherence prediction
- `coherence_targets`:    [batch] coherence supervision targets
- `diversity_embeddings`: [batch, embed_dim] output embeddings for diversity reward
- `div_weight`:           Weight for diversity reward
- `orig_weight`:          Weight for originality reward

# Returns
NamedTuple: (total, coherence, diversity_reward, originality_reward)
"""
function creativity_loss(
    coherence_logits::AbstractMatrix{T},
    coherence_targets::AbstractVector{<:Integer},
    diversity_embeddings::AbstractMatrix{T};
    div_weight::Float32  = 0.3f0,
    orig_weight::Float32 = 0.3f0,
) :: NamedTuple where T <: AbstractFloat

    l_coherence = cross_entropy_loss(coherence_logits, coherence_targets)

    # Diversity reward: mean pairwise cosine distance (higher = more diverse)
    n = size(diversity_embeddings, 1)
    if n > 1
        norms = [Float32(norm(diversity_embeddings[i, :])) + 1e-9f0 for i in 1:n]
        norm_embs = diversity_embeddings ./ reshape(norms, n, 1)
        sim_matrix = Float32.(norm_embs * norm_embs')
        # Mean off-diagonal similarity
        off_diag_sim = (sum(sim_matrix) - tr(sim_matrix)) / Float32(n * (n - 1))
        r_diversity = 1.0f0 - off_diag_sim
    else
        r_diversity = 0.0f0
    end

    # Originality reward (placeholder — production: compare to training set)
    r_originality = 0.5f0

    total = max(0.05f0, l_coherence - div_weight * r_diversity - orig_weight * r_originality)

    return (total=total, coherence=l_coherence,
            diversity_reward=r_diversity, originality_reward=r_originality)
end

# =============================================================================
# Metacognition loss
# =============================================================================

"""
    metacognition_loss(confidence_preds::AbstractVector,
                        correctness_labels::AbstractVector{Bool};
                        error_logits::Union{Nothing, AbstractVector} = nothing,
                        error_labels::Union{Nothing, AbstractVector{Bool}} = nothing)
                     -> NamedTuple

Computes metacognition training loss:
L_meta = Brier_score(confidence, correctness) + CE(error_detection, is_error)
"""
function metacognition_loss(
    confidence_preds::AbstractVector{T},
    correctness_labels::AbstractVector{Bool};
    error_logits::Union{Nothing, AbstractVector} = nothing,
    error_labels::Union{Nothing, AbstractVector{Bool}} = nothing,
) :: NamedTuple where T <: AbstractFloat

    calib_loss = brier_score(confidence_preds, correctness_labels)

    error_detect_loss = 0.0f0
    if !isnothing(error_logits) && !isnothing(error_labels)
        error_probs = sigmoid.(Float32.(error_logits))
        error_detect_loss = focal_loss(error_probs, error_labels)
    end

    total = calib_loss + error_detect_loss

    return (total=total, calibration=calib_loss, error_detection=error_detect_loss)
end

# Sigmoid helper
sigmoid(x::Float32) = 1.0f0 / (1.0f0 + exp(-x))

# =============================================================================
# Tests
# =============================================================================

function run_loss_function_tests()
    using Test

    @testset "LossFunctions" begin

        @testset "cross_entropy_loss" begin
            logits  = Float32[2.0 1.0 0.5; 0.5 2.5 0.3; 1.0 0.5 3.0]  # 3×3
            targets = Int32[0, 1, 2]  # 0-based
            loss = cross_entropy_loss(logits, targets)
            @test loss > 0.0f0
            @test loss < 5.0f0  # Reasonable upper bound
            @test typeof(loss) == Float32
        end

        @testset "brier_score" begin
            perfect = Float32[1.0, 0.0, 1.0, 0.0]
            labels  = Bool[true, false, true, false]
            @test brier_score(perfect, labels) ≈ 0.0f0 atol=1e-6
            # Random predictions → Brier score ≈ 0.25
            random  = fill(0.5f0, 4)
            @test brier_score(random, labels) ≈ 0.25f0 atol=1e-5
        end

        @testset "kl_divergence" begin
            p = Float32[0.5, 0.3, 0.2]
            q = Float32[0.4, 0.4, 0.2]
            kl = kl_divergence(p, q)
            @test kl >= 0.0f0
            # KL(p||p) = 0
            @test kl_divergence(p, p) ≈ 0.0f0 atol=1e-5
        end

        @testset "contrastive_loss" begin
            a = Float32[1 0 0; 0 1 0]
            b = Float32[1 0 0; 0 0 1]
            labels = Bool[true, false]
            loss = contrastive_loss(a, b, labels)
            @test loss >= 0.0f0
        end

        @testset "thinking_loss" begin
            final_l  = randn(Float32, 4, 100)
            final_t  = Int32[10, 20, 30, 40]
            cot_l    = randn(Float32, 4, 100)
            cot_t    = Int32[5, 15, 25, 35]
            result   = thinking_loss(final_l, final_t, cot_l, cot_t)
            @test result.total > 0.0f0
            @test result.final > 0.0f0
            @test result.chain_of_thought > 0.0f0
        end

        @testset "metacognition_loss" begin
            confs  = Float32[0.9, 0.3, 0.8, 0.5]
            labels = Bool[true, false, true, false]
            result = metacognition_loss(confs, labels)
            @test result.total >= 0.0f0
            @test result.calibration >= 0.0f0
        end

    end

    @info "LossFunctions tests completed"
end

end # module LossFunctions
