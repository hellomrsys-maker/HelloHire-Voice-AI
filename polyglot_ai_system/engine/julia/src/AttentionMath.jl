# =============================================================================
# engine/julia/src/AttentionMath.jl
# Mathematical implementation of multi-head attention scoring,
# RoPE positional encoding, and KV-cache arithmetic in Julia.
# Used as the numerical reference implementation and for custom
# backward pass validation.
# =============================================================================

module AttentionMath

using LinearAlgebra
using Statistics
using Random

export scaled_dot_product_attention,
       multi_head_attention,
       rope_encode,
       causal_mask,
       softmax,
       softmax!,
       attention_entropy,
       compute_attention_pattern_entropy

# =============================================================================
# Softmax — numerically stable row-wise softmax
# =============================================================================

"""
    softmax(x::AbstractMatrix; dim::Int = 2) -> Matrix{Float32}

Numerically stable softmax over rows (dim=2) or columns (dim=1).
Subtracts the row/col maximum before exponentiation to prevent overflow.

# Arguments
- `x`: Input matrix of shape (M × N)
- `dim`: Dimension to apply softmax over (1 = columns, 2 = rows)

# Returns
- Matrix of the same shape with softmax applied

# Example
```julia
x = rand(Float32, 4, 8)
p = softmax(x, dim=2)
@assert all(≈(sum(p, dims=2), 1.0f0, atol=1e-5))
```
"""
function softmax(x::AbstractMatrix{T}; dim::Int = 2) where T <: AbstractFloat
    if dim == 2
        # Row-wise softmax
        max_vals = maximum(x, dims=2)
        shifted  = x .- max_vals
        exps     = exp.(shifted)
        return exps ./ sum(exps, dims=2)
    elseif dim == 1
        # Column-wise softmax
        max_vals = maximum(x, dims=1)
        shifted  = x .- max_vals
        exps     = exp.(shifted)
        return exps ./ sum(exps, dims=1)
    else
        throw(ArgumentError("dim must be 1 or 2, got $dim"))
    end
end

"""
    softmax!(x::AbstractMatrix; dim::Int = 2)

In-place numerically stable softmax.
"""
function softmax!(x::AbstractMatrix{T}; dim::Int = 2) where T <: AbstractFloat
    if dim == 2
        for i in axes(x, 1)
            row = view(x, i, :)
            max_val = maximum(row)
            row .= exp.(row .- max_val)
            row ./= sum(row)
        end
    elseif dim == 1
        for j in axes(x, 2)
            col = view(x, :, j)
            max_val = maximum(col)
            col .= exp.(col .- max_val)
            col ./= sum(col)
        end
    end
    return x
end

# =============================================================================
# Scaled Dot-Product Attention
# =============================================================================

"""
    scaled_dot_product_attention(
        Q::AbstractMatrix, K::AbstractMatrix, V::AbstractMatrix;
        mask::Union{Nothing, AbstractMatrix} = nothing,
        dropout_p::Float32 = 0.0f0,
        scale::Union{Nothing, Float32} = nothing,
        rng::AbstractRNG = Random.default_rng()
    ) -> Tuple{Matrix{Float32}, Matrix{Float32}}

Computes scaled dot-product attention:

    Attention(Q, K, V) = softmax(QKᵀ / √dₖ + mask) × V

# Arguments
- `Q`: Query matrix of shape (seq_len_q, d_k)
- `K`: Key matrix   of shape (seq_len_k, d_k)
- `V`: Value matrix of shape (seq_len_k, d_v)
- `mask`: Optional additive mask (shape seq_len_q × seq_len_k); use -Inf to block
- `dropout_p`: Attention dropout probability [0, 1)
- `scale`: Custom scale factor (default: 1/√d_k)
- `rng`: Random number generator for dropout

# Returns
- `output`: Attention-weighted values, shape (seq_len_q, d_v)
- `weights`: Attention weight matrix, shape (seq_len_q, seq_len_k)

# Example
```julia
Q = randn(Float32, 8, 64)
K = randn(Float32, 16, 64)
V = randn(Float32, 16, 64)
output, weights = scaled_dot_product_attention(Q, K, V)
@assert size(output)  == (8, 64)
@assert size(weights) == (8, 16)
```
"""
function scaled_dot_product_attention(
    Q::AbstractMatrix{T},
    K::AbstractMatrix{T},
    V::AbstractMatrix{T};
    mask::Union{Nothing, AbstractMatrix} = nothing,
    dropout_p::Float32 = 0.0f0,
    scale::Union{Nothing, Float32} = nothing,
    rng::AbstractRNG = Random.default_rng()
) where T <: AbstractFloat

    d_k = size(Q, 2)
    scale_factor = isnothing(scale) ? T(1.0 / sqrt(Float64(d_k))) : T(scale)

    # Compute raw attention scores: (seq_q × d_k) @ (d_k × seq_k) → (seq_q × seq_k)
    scores = Q * K' .* scale_factor

    # Apply optional additive mask
    if !isnothing(mask)
        @assert size(mask) == size(scores) "Mask shape $(size(mask)) must match scores shape $(size(scores))"
        scores .+= T.(mask)
    end

    # Softmax over keys for each query
    weights = softmax(scores, dim=2)

    # Apply attention dropout
    if dropout_p > 0.0f0
        drop_mask = rand(rng, T, size(weights)) .> T(dropout_p)
        weights = weights .* drop_mask ./ T(1.0 - dropout_p)
        # Re-normalize rows after dropout
        row_sums = sum(weights, dims=2)
        row_sums[row_sums .== 0] .= T(1.0)  # Avoid division by zero
        weights ./= row_sums
    end

    # Weighted sum of values: (seq_q × seq_k) @ (seq_k × d_v) → (seq_q × d_v)
    output = weights * V

    return output, weights
end

# =============================================================================
# Multi-Head Attention
# =============================================================================

"""
    multi_head_attention(
        Q::AbstractMatrix, K::AbstractMatrix, V::AbstractMatrix,
        W_q::AbstractMatrix, W_k::AbstractMatrix,
        W_v::AbstractMatrix, W_o::AbstractMatrix;
        num_heads::Int = 8,
        mask::Union{Nothing, AbstractMatrix} = nothing,
        dropout_p::Float32 = 0.0f0
    ) -> Matrix{Float32}

Computes full multi-head attention with projection matrices.

    MultiHead(Q, K, V) = Concat(head₁, ..., headₕ) × Wₒ
    headᵢ = Attention(Q × Wqᵢ, K × Wkᵢ, V × Wvᵢ)

# Arguments
- `Q`, `K`, `V`: Input tensors of shape (seq_len, d_model)
- `W_q`, `W_k`, `W_v`: Projection matrices of shape (d_model, d_model)
- `W_o`: Output projection matrix of shape (d_model, d_model)
- `num_heads`: Number of attention heads h (must divide d_model)
- `mask`: Optional attention mask
- `dropout_p`: Dropout probability

# Returns
- Output tensor of shape (seq_len, d_model)
"""
function multi_head_attention(
    Q::AbstractMatrix{T},
    K::AbstractMatrix{T},
    V::AbstractMatrix{T},
    W_q::AbstractMatrix{T},
    W_k::AbstractMatrix{T},
    W_v::AbstractMatrix{T},
    W_o::AbstractMatrix{T};
    num_heads::Int = 8,
    mask::Union{Nothing, AbstractMatrix} = nothing,
    dropout_p::Float32 = 0.0f0
) where T <: AbstractFloat

    seq_q, d_model = size(Q)
    seq_k          = size(K, 1)

    @assert d_model % num_heads == 0 "d_model ($d_model) must be divisible by num_heads ($num_heads)"
    d_head = d_model ÷ num_heads

    # Project to multi-head space: (seq, d_model) @ (d_model, d_model) → (seq, d_model)
    Q_proj = Q * W_q   # (seq_q, d_model)
    K_proj = K * W_k   # (seq_k, d_model)
    V_proj = V * W_v   # (seq_k, d_model)

    # Split into heads and compute attention for each head
    # Reshape: (seq, d_model) → (seq, num_heads, d_head)
    head_outputs = Vector{Matrix{T}}()

    for h in 1:num_heads
        col_start = (h - 1) * d_head + 1
        col_end   = h * d_head

        Qh = Q_proj[:, col_start:col_end]   # (seq_q, d_head)
        Kh = K_proj[:, col_start:col_end]   # (seq_k, d_head)
        Vh = V_proj[:, col_start:col_end]   # (seq_k, d_head)

        head_out, _ = scaled_dot_product_attention(Qh, Kh, Vh;
                        mask=mask, dropout_p=dropout_p)
        push!(head_outputs, head_out)
    end

    # Concatenate heads: (seq_q, d_model)
    concatenated = hcat(head_outputs...)   # (seq_q, d_model)

    # Output projection
    output = concatenated * W_o

    return output
end

# =============================================================================
# Rotary Positional Encoding (RoPE)
# =============================================================================

"""
    rope_precompute_freqs(head_dim::Int, max_seq_len::Int;
                           base::Float32 = 10000.0f0)
                        -> (cos_cache, sin_cache)

Precomputes the RoPE cosine and sine tables.

# Arguments
- `head_dim`: Dimension of each attention head (must be even)
- `max_seq_len`: Maximum sequence length
- `base`: RoPE base frequency (default: 10000.0)

# Returns
- `cos_cache`: Matrix of shape (max_seq_len, head_dim ÷ 2)
- `sin_cache`: Matrix of shape (max_seq_len, head_dim ÷ 2)
"""
function rope_precompute_freqs(
    head_dim::Int, max_seq_len::Int;
    base::Float32 = 10000.0f0
)
    @assert iseven(head_dim) "head_dim must be even for RoPE, got $head_dim"
    half_dim = head_dim ÷ 2

    # θᵢ = base^(-2i/d) for i ∈ [0, half_dim)
    thetas = [Float32(base)^(-2.0f0 * Float32(i) / Float32(head_dim))
              for i in 0:(half_dim - 1)]

    # cos and sin tables: [max_seq_len, half_dim]
    cos_cache = Matrix{Float32}(undef, max_seq_len, half_dim)
    sin_cache = Matrix{Float32}(undef, max_seq_len, half_dim)

    for pos in 1:max_seq_len
        for i in 1:half_dim
            angle = Float32(pos - 1) * thetas[i]
            cos_cache[pos, i] = cos(angle)
            sin_cache[pos, i] = sin(angle)
        end
    end

    return cos_cache, sin_cache
end

"""
    rope_encode(tensor::Array{Float32,3}, cos_cache, sin_cache; offset::Int = 0)
                -> Array{Float32,3}

Applies Rotary Positional Encoding to a tensor of shape (seq_len, num_heads, head_dim).

For each position m and dimension pair (i, i + half_dim):
    x'[i]             = x[i] * cos(m*θᵢ) - x[i + half_dim] * sin(m*θᵢ)
    x'[i + half_dim]  = x[i] * sin(m*θᵢ) + x[i + half_dim] * cos(m*θᵢ)

# Arguments
- `tensor`:    Input tensor of shape (seq_len, num_heads, head_dim)
- `cos_cache`: Precomputed cosine table (max_seq_len, half_dim)
- `sin_cache`: Precomputed sine table (max_seq_len, half_dim)
- `offset`:    Starting position offset (for incremental/cached generation)

# Returns
- Tensor with RoPE applied, same shape as input
"""
function rope_encode(
    tensor::Array{Float32, 3},
    cos_cache::Matrix{Float32},
    sin_cache::Matrix{Float32};
    offset::Int = 0
)
    seq_len, num_heads, head_dim = size(tensor)
    @assert iseven(head_dim) "head_dim must be even for RoPE"
    half_dim = head_dim ÷ 2

    result = similar(tensor)

    for pos in 1:seq_len
        abs_pos = pos + offset  # 1-based
        @assert abs_pos <= size(cos_cache, 1) "Position $abs_pos exceeds cos_cache length"

        for h in 1:num_heads
            for i in 1:half_dim
                x0 = tensor[pos, h, i]
                x1 = tensor[pos, h, i + half_dim]
                c  = cos_cache[abs_pos, i]
                s  = sin_cache[abs_pos, i]

                result[pos, h, i]           = x0 * c - x1 * s
                result[pos, h, i + half_dim] = x0 * s + x1 * c
            end
        end
    end

    return result
end

# =============================================================================
# Causal Mask
# =============================================================================

"""
    causal_mask(seq_len::Int; T::Type = Float32) -> Matrix

Creates a causal (lower-triangular) attention mask for autoregressive generation.
Positions above the diagonal are set to -Inf to prevent attending to future tokens.

# Example
```julia
mask = causal_mask(4)
# 4×4 matrix:
# 0    -Inf -Inf -Inf
# 0    0    -Inf -Inf
# 0    0    0    -Inf
# 0    0    0    0
```
"""
function causal_mask(seq_len::Int; T::Type = Float32) :: Matrix
    mask = fill(T(-Inf), seq_len, seq_len)
    for i in 1:seq_len
        for j in 1:i
            mask[i, j] = T(0.0)
        end
    end
    return mask
end

# =============================================================================
# Attention Entropy — measures concentration/diversity of attention
# Implements "concentration and sustained attention" diagnostic
# =============================================================================

"""
    attention_entropy(weights::AbstractMatrix) -> Vector{Float32}

Computes the entropy of each attention distribution (row).
Low entropy = highly concentrated attention (attending to few tokens).
High entropy = dispersed attention (attending to many tokens equally).

Entropy: H(p) = -∑ᵢ pᵢ log₂(pᵢ)

# Arguments
- `weights`: Attention weight matrix of shape (seq_q, seq_k)

# Returns
- Vector of per-query entropy values of length seq_q
"""
function attention_entropy(weights::AbstractMatrix{T}) :: Vector{Float32} where T
    eps = T(1e-9)
    entropies = Vector{Float32}(undef, size(weights, 1))

    for i in axes(weights, 1)
        row = view(weights, i, :)
        # Clamp to avoid log(0)
        p = max.(row, eps)
        # Normalize if not already
        p_norm = p ./ sum(p)
        h = -sum(p_norm .* log2.(p_norm))
        entropies[i] = Float32(h)
    end

    return entropies
end

"""
    compute_attention_pattern_entropy(weights_per_head::Vector{<:AbstractMatrix})
                                     -> NamedTuple

Computes attention entropy statistics across all heads.

# Returns
NamedTuple with fields:
- `per_head_mean`: Mean entropy per head (Vector)
- `per_head_max`:  Max entropy per head
- `global_mean`:   Mean entropy across all heads
- `global_std`:    Standard deviation of entropy across all heads
"""
function compute_attention_pattern_entropy(
    weights_per_head::Vector{<:AbstractMatrix}
) :: NamedTuple

    per_head_entropies = [attention_entropy(w) for w in weights_per_head]
    per_head_mean      = [mean(e) for e in per_head_entropies]
    per_head_max       = [maximum(e) for e in per_head_entropies]

    all_entropies = vcat(per_head_entropies...)
    return (
        per_head_mean = per_head_mean,
        per_head_max  = per_head_max,
        global_mean   = mean(all_entropies),
        global_std    = std(all_entropies),
    )
end

# =============================================================================
# Unit tests (inline, runnable with @testset)
# =============================================================================

"""
    run_attention_math_tests()

Runs inline unit tests for all AttentionMath functions.
"""
function run_attention_math_tests()
    using Test

    @testset "AttentionMath" begin

        @testset "softmax" begin
            x = Float32[1.0 2.0 3.0; 4.0 5.0 6.0]
            p = softmax(x, dim=2)
            @test size(p) == (2, 3)
            @test all(isapprox.(sum(p, dims=2), 1.0f0, atol=1e-5))
            @test all(p .>= 0.0f0)
            @test all(p .<= 1.0f0)
        end

        @testset "scaled_dot_product_attention" begin
            Q = randn(Float32, 4, 32)
            K = randn(Float32, 8, 32)
            V = randn(Float32, 8, 64)
            out, w = scaled_dot_product_attention(Q, K, V)
            @test size(out) == (4, 64)
            @test size(w)   == (4, 8)
            @test all(isapprox.(sum(w, dims=2), 1.0f0, atol=1e-4))
        end

        @testset "multi_head_attention" begin
            d_model = 64
            n_heads = 8
            seq_len = 6
            Q = randn(Float32, seq_len, d_model)
            K = randn(Float32, seq_len, d_model)
            V = randn(Float32, seq_len, d_model)
            W_q = randn(Float32, d_model, d_model) .* 0.02f0
            W_k = randn(Float32, d_model, d_model) .* 0.02f0
            W_v = randn(Float32, d_model, d_model) .* 0.02f0
            W_o = randn(Float32, d_model, d_model) .* 0.02f0
            out = multi_head_attention(Q, K, V, W_q, W_k, W_v, W_o; num_heads=n_heads)
            @test size(out) == (seq_len, d_model)
        end

        @testset "rope_precompute_and_encode" begin
            head_dim  = 32
            max_seq   = 128
            seq_len   = 8
            num_heads = 4
            cos_c, sin_c = rope_precompute_freqs(head_dim, max_seq)
            @test size(cos_c) == (max_seq, head_dim ÷ 2)
            @test size(sin_c) == (max_seq, head_dim ÷ 2)

            tensor = randn(Float32, seq_len, num_heads, head_dim)
            result = rope_encode(tensor, cos_c, sin_c)
            @test size(result) == size(tensor)
            # RoPE should preserve vector norms (rotation is norm-preserving)
            for pos in 1:seq_len, h in 1:num_heads
                orig_norm   = norm(tensor[pos, h, :])
                result_norm = norm(result[pos, h, :])
                @test isapprox(orig_norm, result_norm, atol=1e-4)
            end
        end

        @testset "causal_mask" begin
            mask = causal_mask(4)
            @test size(mask) == (4, 4)
            @test mask[1, 1] == 0.0f0
            @test isinf(mask[1, 2])
            @test mask[4, 4] == 0.0f0
            @test isinf(mask[4, 1]) == false  # Bottom-left should be 0
        end

        @testset "attention_entropy" begin
            # Uniform distribution → maximum entropy
            n = 8
            uniform = fill(Float32(1.0 / n), 4, n)
            ent = attention_entropy(uniform)
            @test length(ent) == 4
            @test all(isapprox.(ent, log2(Float32(n)), atol=0.01))

            # One-hot distribution → minimum entropy (≈ 0)
            onehot = zeros(Float32, 2, n)
            onehot[:, 1] .= 1.0f0
            ent2 = attention_entropy(onehot)
            @test all(ent2 .< 0.1f0)
        end

    end

    @info "AttentionMath tests completed"
end

end # module AttentionMath
