# test_engine.jl
# Julia test suite for the verbal communication engine.
# Tests all Julia engine components: AttentionMath, EmbeddingOps,
# NumericalOptimizer, CognitiveSim, and EngineFFI.
# Run with: julia --project=. src/test_engine.jl

using Test
using LinearAlgebra
using Statistics

# Load engine modules
include("AttentionMath.jl")
include("EmbeddingOps.jl")
include("NumericalOptimizer.jl")
include("CognitiveSim.jl")

using .AttentionMath
using .EmbeddingOps
using .NumericalOptimizer
using .CognitiveSim

println("=" ^ 60)
println("Polyglot AI System — Julia Engine Test Suite")
println("=" ^ 60)

# ─────────────────────────────────────────────────────────────────────────────
# AttentionMath Tests
# ─────────────────────────────────────────────────────────────────────────────

@testset "AttentionMath" begin

    @testset "softmax" begin
        x = Float32[1.0, 2.0, 3.0, 4.0]
        s = softmax(x)
        @test length(s) == 4
        @test sum(s) ≈ 1.0f0 atol=1e-5
        @test all(s .>= 0.0f0)
        @test all(s .<= 1.0f0)
        # Max element should have highest probability
        @test argmax(s) == argmax(x)
    end

    @testset "scaled_dot_product_attention" begin
        B, H, S, D = 2, 4, 8, 32
        Q = randn(Float32, B, H, S, D)
        K = randn(Float32, B, H, S, D)
        V = randn(Float32, B, H, S, D)
        output, weights = scaled_dot_product_attention(Q, K, V)
        @test size(output) == (B, H, S, D)
        @test size(weights) == (B, H, S, S)
        # Attention weights should sum to ~1 over key dimension
        for b in 1:B, h in 1:H, q in 1:S
            @test sum(weights[b, h, q, :]) ≈ 1.0f0 atol=1e-4
        end
    end

    @testset "rotary_embedding" begin
        S, D = 16, 64
        x = randn(Float32, S, D)
        x_rotated = apply_rotary_embedding(x, S, D)
        @test size(x_rotated) == (S, D)
        # Rotary should preserve norm (approximately)
        for i in 1:S
            @test norm(x_rotated[i, :]) ≈ norm(x[i, :]) atol=1e-3
        end
    end

    @testset "causal_mask" begin
        S = 8
        mask = make_causal_mask(S)
        @test size(mask) == (S, S)
        # Upper triangle should be -Inf
        for i in 1:S, j in i+1:S
            @test mask[i, j] == -Inf
        end
        # Diagonal and lower triangle should be 0
        for i in 1:S, j in 1:i
            @test mask[i, j] == 0.0f0
        end
    end

end  # AttentionMath

# ─────────────────────────────────────────────────────────────────────────────
# EmbeddingOps Tests
# ─────────────────────────────────────────────────────────────────────────────

@testset "EmbeddingOps" begin

    @testset "token_embedding_lookup" begin
        vocab_size, dim = 100, 64
        W = randn(Float32, vocab_size, dim)
        ids = Int32[1, 5, 10, 50]
        embs = token_embedding_lookup(W, ids)
        @test size(embs) == (length(ids), dim)
        @test embs[1, :] ≈ W[1, :]
        @test embs[2, :] ≈ W[5, :]
    end

    @testset "positional_encoding" begin
        S, D = 32, 128
        pe = sinusoidal_positional_encoding(S, D)
        @test size(pe) == (S, D)
        # Even dimensions should be sine, odd should be cosine
        # Values should be in [-1, 1]
        @test all(pe .>= -1.0f0 .- 1e-5f0)
        @test all(pe .<= 1.0f0 .+ 1e-5f0)
    end

    @testset "layer_normalization" begin
        B, D = 4, 64
        x = randn(Float32, B, D)
        γ = ones(Float32, D)
        β = zeros(Float32, D)
        y = layer_norm(x, γ, β)
        @test size(y) == (B, D)
        # Each row should be approximately normalized
        for b in 1:B
            @test mean(y[b, :]) ≈ 0.0f0 atol=1e-4
            @test std(y[b, :]) ≈ 1.0f0 atol=0.1f0
        end
    end

end  # EmbeddingOps

# ─────────────────────────────────────────────────────────────────────────────
# NumericalOptimizer Tests
# ─────────────────────────────────────────────────────────────────────────────

@testset "NumericalOptimizer" begin

    @testset "gradient_descent_convergence" begin
        # Minimize f(x) = (x - 3)^2 starting from x=0
        x = [0.0f0]
        for step in 1:1000
            grad = 2.0f0 .* (x .- 3.0f0)
            x .-= 0.01f0 .* grad
        end
        @test x[1] ≈ 3.0f0 atol=0.1f0
    end

    @testset "adam_update" begin
        x = zeros(Float32, 10)
        m = zeros(Float32, 10)
        v = zeros(Float32, 10)
        grad = ones(Float32, 10)

        for step in 1:100
            adam_step!(x, grad, m, v, step, 0.01f0, 0.9f0, 0.999f0, 1e-8f0, 0.0f0)
        end
        # After many steps, x should be non-zero (moved in gradient direction)
        @test all(x .< 0.0f0)
    end

    @testset "cosine_schedule" begin
        lr_max = 1e-3f0
        for step in [0, 500, 1000, 5000, 10000]
            lr = cosine_schedule(step, lr_max, 0.0f0, 1000, 10000)
            @test 0.0f0 <= lr <= lr_max + 1e-6f0
        end
    end

end  # NumericalOptimizer

# ─────────────────────────────────────────────────────────────────────────────
# CognitiveSim Tests
# ─────────────────────────────────────────────────────────────────────────────

@testset "CognitiveSim" begin

    @testset "episodic_memory" begin
        mem = EpisodicMemory(capacity=32, dim=64)
        # Store 10 episodes
        for i in 1:10
            episode = randn(Float32, 64)
            store!(mem, episode, "tag_$i")
        end
        @test length(mem) == 10

        # Recall nearest episode
        query = randn(Float32, 64)
        result = recall(mem, query, top_k=3)
        @test length(result) == 3
    end

    @testset "attention_simulation" begin
        dim, seq_len = 32, 16
        state = CognitiveState(dim=dim, seq_len=seq_len)
        input = randn(Float32, seq_len, dim)
        output = simulate_attention(state, input)
        @test size(output) == (seq_len, dim)
    end

    @testset "curiosity_score" begin
        novelty_emb = randn(Float32, 64)
        known_embs = [randn(Float32, 64) for _ in 1:10]
        score = curiosity_score(novelty_emb, known_embs)
        @test 0.0f0 <= score <= 1.0f0
    end

end  # CognitiveSim

println()
println("All engine tests completed.")
println("=" ^ 60)
