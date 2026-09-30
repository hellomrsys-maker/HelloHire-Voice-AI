# =============================================================================
# engine/julia/src/EmbeddingOps.jl
# Embedding arithmetic, cosine similarity, distance metrics,
# nearest-neighbor search, and interpolation for the engine.
# =============================================================================

module EmbeddingOps

using LinearAlgebra
using Statistics
using Random

export cosine_similarity, cosine_similarity_matrix,
       l2_normalize, l2_distance,
       nearest_neighbors, approximate_nearest_neighbors,
       embedding_mean, embedding_interpolate,
       analogy_vector, embedding_centroid,
       rank_by_similarity

# =============================================================================
# Normalization
# =============================================================================

"""
    l2_normalize(v::AbstractVector) -> Vector{Float32}

L2-normalizes a vector to unit norm. Returns a zero vector if norm is ~0.
"""
function l2_normalize(v::AbstractVector{T}) :: Vector{Float32} where T
    n = norm(v)
    if n < Float32(1e-9)
        return zeros(Float32, length(v))
    end
    return Float32.(v) ./ Float32(n)
end

"""
    l2_normalize(M::AbstractMatrix; dims::Int = 1) -> Matrix{Float32}

L2-normalizes each column (dims=1) or row (dims=2) of a matrix.
"""
function l2_normalize(M::AbstractMatrix{T}; dims::Int = 1) :: Matrix{Float32} where T
    norms = sqrt.(sum(M .^ 2, dims=dims))
    norms[norms .< 1e-9] .= 1.0
    return Float32.(M) ./ Float32.(norms)
end

# =============================================================================
# Cosine Similarity
# =============================================================================

"""
    cosine_similarity(a::AbstractVector, b::AbstractVector) -> Float32

Computes cosine similarity between two vectors.
Handles zero-norm vectors gracefully (returns 0.0).
"""
function cosine_similarity(a::AbstractVector, b::AbstractVector) :: Float32
    na = Float32(norm(a))
    nb = Float32(norm(b))
    if na < 1e-9f0 || nb < 1e-9f0
        return 0.0f0
    end
    return Float32(dot(a, b)) / (na * nb)
end

"""
    cosine_similarity_matrix(A::AbstractMatrix, B::AbstractMatrix) -> Matrix{Float32}

Computes pairwise cosine similarities between rows of A and rows of B.

# Arguments
- `A`: Matrix of shape (m, d)
- `B`: Matrix of shape (n, d)

# Returns
- Matrix of shape (m, n) where entry [i, j] = cosine_sim(A[i,:], B[j,:])
"""
function cosine_similarity_matrix(
    A::AbstractMatrix{T},
    B::AbstractMatrix{T}
) :: Matrix{Float32} where T

    # L2-normalize rows
    A_norm = l2_normalize(A, dims=2)  # (m, d)
    B_norm = l2_normalize(B, dims=2)  # (n, d)

    # Cosine similarity = dot product of normalized vectors
    return Float32.(A_norm * B_norm')
end

# =============================================================================
# Distance Metrics
# =============================================================================

"""
    l2_distance(a::AbstractVector, b::AbstractVector) -> Float32

Euclidean (L2) distance between two vectors.
"""
function l2_distance(a::AbstractVector, b::AbstractVector) :: Float32
    Float32(norm(Float32.(a) .- Float32.(b)))
end

"""
    pairwise_l2_distances(A::AbstractMatrix, B::AbstractMatrix) -> Matrix{Float32}

Computes pairwise L2 distances between rows of A and rows of B.
Uses the identity: ‖a - b‖² = ‖a‖² - 2aᵀb + ‖b‖²
"""
function pairwise_l2_distances(
    A::AbstractMatrix{T},
    B::AbstractMatrix{T}
) :: Matrix{Float32} where T

    A_f = Float32.(A)
    B_f = Float32.(B)

    # ‖a‖² for each row of A: (m,)
    A_sq = sum(A_f .^ 2, dims=2)  # (m, 1)
    # ‖b‖² for each row of B: (n,)
    B_sq = sum(B_f .^ 2, dims=2)  # (n, 1)

    # Cross term: A @ Bᵀ → (m, n)
    cross = A_f * B_f'

    # D²[i,j] = ‖aᵢ‖² - 2aᵢᵀbⱼ + ‖bⱼ‖²
    D_sq = A_sq .- 2.0f0 .* cross .+ B_sq'

    # Clamp negatives (numerical precision issues)
    D_sq = max.(D_sq, 0.0f0)

    return sqrt.(D_sq)
end

# =============================================================================
# Nearest Neighbor Search
# =============================================================================

"""
    nearest_neighbors(query::AbstractVector, bank::AbstractMatrix;
                       k::Int = 5, metric::Symbol = :cosine)
                    -> Vector{Tuple{Int, Float32}}

Exact nearest-neighbor search. Returns top-k (index, score) pairs.

# Arguments
- `query`: Query vector of shape (d,)
- `bank`:  Embedding bank of shape (n, d) — each row is an embedding
- `k`:     Number of neighbors to return
- `metric`: `:cosine` (higher = more similar) or `:l2` (lower = closer)

# Returns
- Vector of (index, score) pairs, sorted by score (descending for cosine, ascending for l2)
"""
function nearest_neighbors(
    query::AbstractVector,
    bank::AbstractMatrix;
    k::Int = 5,
    metric::Symbol = :cosine
) :: Vector{Tuple{Int, Float32}}

    n = size(bank, 1)
    k = min(k, n)

    if metric == :cosine
        scores = [cosine_similarity(query, bank[i, :]) for i in 1:n]
        sorted_idx = sortperm(scores, rev=true)[1:k]
        return [(idx, scores[idx]) for idx in sorted_idx]

    elseif metric == :l2
        distances = [l2_distance(query, bank[i, :]) for i in 1:n]
        sorted_idx = sortperm(distances)[1:k]
        return [(idx, distances[idx]) for idx in sorted_idx]

    else
        throw(ArgumentError("Unknown metric: $metric. Use :cosine or :l2"))
    end
end

# =============================================================================
# Embedding Arithmetic
# =============================================================================

"""
    embedding_mean(embeddings::AbstractMatrix) -> Vector{Float32}

Computes the mean of a set of embeddings.
Input: (n, d) matrix of n embeddings of dimension d.
"""
function embedding_mean(embeddings::AbstractMatrix{T}) :: Vector{Float32} where T
    Float32.(mean(embeddings, dims=1)[1, :])
end

"""
    embedding_interpolate(a::AbstractVector, b::AbstractVector;
                           t::Float32 = 0.5f0) -> Vector{Float32}

Spherical linear interpolation (SLERP) between two embedding vectors.

# Arguments
- `a`, `b`: Unit vectors to interpolate between
- `t`:      Interpolation parameter [0, 1]; t=0 → a, t=1 → b

# Returns
- Interpolated unit vector
"""
function embedding_interpolate(
    a::AbstractVector{T},
    b::AbstractVector{T};
    t::Float32 = 0.5f0
) :: Vector{Float32} where T

    a_f = Float32.(a)
    b_f = Float32.(b)
    a_n = l2_normalize(a_f)
    b_n = l2_normalize(b_f)

    # Compute angle between vectors
    cos_theta = clamp(dot(a_n, b_n), -1.0f0, 1.0f0)
    theta = acos(cos_theta)

    if abs(theta) < 1e-6f0
        # Vectors are nearly identical — linear interpolation
        return l2_normalize((1.0f0 - t) .* a_n .+ t .* b_n)
    end

    # SLERP: sin((1-t)*θ)/sin(θ) * a + sin(t*θ)/sin(θ) * b
    sin_theta = sin(theta)
    wa = sin((1.0f0 - t) * theta) / sin_theta
    wb = sin(t * theta) / sin_theta

    return l2_normalize(wa .* a_n .+ wb .* b_n)
end

"""
    analogy_vector(a::AbstractVector, b::AbstractVector, c::AbstractVector)
                  -> Vector{Float32}

Computes word analogy: "a is to b as c is to ?"
Returns the normalized vector: normalize(b - a + c)

# Example
```julia
# "king" - "man" + "woman" ≈ "queen"
result = analogy_vector(man_emb, king_emb, woman_emb)
```
"""
function analogy_vector(
    a::AbstractVector,
    b::AbstractVector,
    c::AbstractVector
) :: Vector{Float32}
    l2_normalize(Float32.(b) .- Float32.(a) .+ Float32.(c))
end

"""
    embedding_centroid(embeddings::AbstractMatrix;
                        weights::Union{Nothing, AbstractVector} = nothing)
                      -> Vector{Float32}

Computes the (optionally weighted) centroid of a set of embeddings.
"""
function embedding_centroid(
    embeddings::AbstractMatrix{T};
    weights::Union{Nothing, AbstractVector} = nothing
) :: Vector{Float32} where T

    if isnothing(weights)
        return embedding_mean(embeddings)
    else
        @assert length(weights) == size(embeddings, 1) "weights length must match embedding count"
        w = Float32.(weights) ./ sum(Float32.(weights))
        return Float32.(w' * embeddings)[1, :]
    end
end

"""
    rank_by_similarity(query::AbstractVector, candidates::AbstractMatrix,
                        labels::AbstractVector{<:AbstractString})
                      -> Vector{NamedTuple}

Ranks candidate embeddings by cosine similarity to a query.

# Returns
Vector of (label, similarity) NamedTuples, sorted by similarity descending.
"""
function rank_by_similarity(
    query::AbstractVector,
    candidates::AbstractMatrix,
    labels::AbstractVector{<:AbstractString}
) :: Vector{NamedTuple}

    @assert size(candidates, 1) == length(labels) "candidates rows must match labels length"
    sims = [cosine_similarity(query, candidates[i, :]) for i in 1:size(candidates, 1)]
    sorted_idx = sortperm(sims, rev=true)

    return [(label = labels[sorted_idx[i]], similarity = sims[sorted_idx[i]])
            for i in 1:length(sorted_idx)]
end

# =============================================================================
# Tests
# =============================================================================

function run_embedding_ops_tests()
    using Test

    @testset "EmbeddingOps" begin

        @testset "l2_normalize" begin
            v = [3.0f0, 4.0f0]
            n = l2_normalize(v)
            @test isapprox(norm(n), 1.0f0, atol=1e-6)
            @test isapprox(n[1], 0.6f0, atol=1e-6)
            @test isapprox(n[2], 0.8f0, atol=1e-6)

            # Zero vector
            z = l2_normalize([0.0f0, 0.0f0, 0.0f0])
            @test all(z .== 0.0f0)
        end

        @testset "cosine_similarity" begin
            a = [1.0f0, 0.0f0]
            b = [0.0f0, 1.0f0]
            @test isapprox(cosine_similarity(a, b), 0.0f0, atol=1e-6)

            @test isapprox(cosine_similarity(a, a), 1.0f0, atol=1e-6)
            @test isapprox(cosine_similarity(a, -a), -1.0f0, atol=1e-6)
        end

        @testset "cosine_similarity_matrix" begin
            A = Float32[1 0; 0 1; 1 1]  # 3 × 2
            B = Float32[1 0; 0 1]        # 2 × 2
            S = cosine_similarity_matrix(A, B)
            @test size(S) == (3, 2)
            # Row 1 (1,0) vs col 1 (1,0): sim = 1.0
            @test isapprox(S[1, 1], 1.0f0, atol=1e-5)
            # Row 2 (0,1) vs col 1 (1,0): sim = 0.0
            @test isapprox(S[2, 1], 0.0f0, atol=1e-5)
        end

        @testset "nearest_neighbors" begin
            bank = Float32[1 0 0; 0 1 0; 0 0 1; 1 1 0]  # 4 × 3
            query = Float32[1, 0, 0]
            neighbors = nearest_neighbors(query, bank, k=2)
            @test length(neighbors) == 2
            @test neighbors[1][1] == 1  # Exact match (row 1)
        end

        @testset "embedding_interpolate" begin
            a = [1.0f0, 0.0f0]
            b = [0.0f0, 1.0f0]
            mid = embedding_interpolate(a, b, t=0.5f0)
            # Result should be ≈ 45-degree direction
            @test isapprox(norm(mid), 1.0f0, atol=1e-5)
            @test isapprox(mid[1], mid[2], atol=1e-5)
        end

        @testset "analogy_vector" begin
            # Simple: b - a + c
            a = [1.0f0, 0.0f0]
            b = [1.0f0, 1.0f0]
            c = [0.0f0, 0.0f0]
            result = analogy_vector(a, b, c)
            @test length(result) == 2
            @test isapprox(norm(result), 1.0f0, atol=1e-5)
        end

    end

    @info "EmbeddingOps tests completed"
end

end # module EmbeddingOps
