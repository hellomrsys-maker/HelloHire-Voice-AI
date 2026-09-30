# test_training.jl
# Julia test suite for the AI training system.
# Tests LossFunctions, TrainingOptimizer, CognitiveBenchmarks, and TrainingFFI.
# Run with: julia --project=. src/test_training.jl

using Test
using LinearAlgebra
using Statistics

include("LossFunctions.jl")
include("TrainingOptimizer.jl")
include("CognitiveBenchmarks.jl")
include("TrainingFFI.jl")

using .LossFunctions
using .TrainingOptimizer
using .CognitiveBenchmarks
using .TrainingFFI

println("=" ^ 60)
println("Polyglot AI System — Julia Training Test Suite")
println("=" ^ 60)

# ─────────────────────────────────────────────────────────────────────────────
# LossFunctions Tests
# ─────────────────────────────────────────────────────────────────────────────

@testset "LossFunctions" begin

    @testset "cross_entropy" begin
        vocab_size = 10
        logits = randn(Float32, vocab_size)
        target = zeros(Float32, vocab_size)
        target[3] = 1.0f0  # one-hot target
        loss = cross_entropy_loss(logits, target)
        @test loss >= 0.0f0
        @test isfinite(loss)
    end

    @testset "cross_entropy_perfect" begin
        vocab_size = 5
        logits = Float32[-100, -100, 100, -100, -100]  # strongly predict class 3
        target = Float32[0, 0, 1, 0, 0]
        loss = cross_entropy_loss(logits, target)
        @test loss ≈ 0.0f0 atol=0.01f0
    end

    @testset "kl_divergence" begin
        P = Float32[0.3, 0.4, 0.3]
        Q = Float32[0.3, 0.4, 0.3]
        kl = kl_divergence(P, Q)
        @test kl ≈ 0.0f0 atol=1e-5f0
    end

    @testset "contrastive_loss" begin
        dim = 16
        anchor   = normalize(randn(Float32, dim))
        positive = normalize(randn(Float32, dim))
        negative = normalize(randn(Float32, dim))
        loss = contrastive_loss(anchor, positive, negative; margin=1.0f0)
        @test loss >= 0.0f0
        @test isfinite(loss)
    end

    @testset "memory_consolidation_loss" begin
        dim, n_episodes = 32, 8
        current_emb = randn(Float32, dim)
        stored_embs = [randn(Float32, dim) for _ in 1:n_episodes]
        loss = memory_consolidation_loss(current_emb, stored_embs)
        @test isfinite(loss)
        @test loss >= 0.0f0
    end

    @testset "creativity_diversity_loss" begin
        n_samples, dim = 5, 16
        samples = [randn(Float32, dim) for _ in 1:n_samples]
        loss = creativity_diversity_loss(samples)
        @test isfinite(loss)
    end

    @testset "label_smoothed_cross_entropy" begin
        vocab_size = 20
        logits = randn(Float32, vocab_size)
        target_idx = 5
        loss_smooth = label_smoothed_cross_entropy(logits, target_idx, 0.1f0, vocab_size)
        loss_exact  = label_smoothed_cross_entropy(logits, target_idx, 0.0f0, vocab_size)
        @test loss_smooth >= 0.0f0
        @test loss_exact  >= 0.0f0
        # Smoothed loss is typically higher for correct predictions
    end

end  # LossFunctions

# ─────────────────────────────────────────────────────────────────────────────
# TrainingOptimizer Tests
# ─────────────────────────────────────────────────────────────────────────────

@testset "TrainingOptimizer" begin

    @testset "AdamW convergence" begin
        # Minimize f(x) = ||x||^2 from a random starting point
        x = randn(Float32, 10) * 5.0f0
        opt = AdamWOptimizer(lr=0.01f0)
        for step in 1:500
            grad = 2.0f0 .* x  # gradient of ||x||^2
            step!(opt, x, grad)
        end
        @test norm(x) < 0.5f0
    end

    @testset "Lion convergence" begin
        x = randn(Float32, 10) * 3.0f0
        opt = LionOptimizer(lr=0.001f0, weight_decay=0.0f0)
        for _ in 1:1000
            grad = 2.0f0 .* x
            step!(opt, x, grad)
        end
        @test norm(x) < 1.0f0
    end

    @testset "WarmupCosineSchedule" begin
        sched = WarmupCosineSchedule(1e-3f0; warmup_steps=100, total_steps=1000)
        # At step 0, lr should be near 0
        @test sched(0) ≈ 0.0f0 atol=1e-5f0
        # At step 100 (end of warmup), lr should be near lr_max
        @test sched(100) ≈ 1e-3f0 atol=1e-5f0
        # At step 1000, lr should be near lr_min (0)
        @test sched(1000) <= 1e-5f0
        # All values should be non-negative
        for s in 0:100:1000
            @test sched(s) >= 0.0f0
        end
    end

    @testset "GradientClipper" begin
        clipper = GradientClipper(1.0f0)
        grads = [randn(Float32, 20) .* 10.0f0 for _ in 1:5]
        original_norm = sqrt(sum(sum(g .^ 2) for g in grads))
        pre_clip_norm = clip_gradients!(clipper, grads)
        post_clip_norm = sqrt(sum(sum(g .^ 2) for g in grads))
        # Pre-clip norm should equal original
        @test pre_clip_norm ≈ original_norm atol=1e-3f0
        # Post-clip norm should be ≤ max_norm
        @test post_clip_norm <= 1.0f0 + 1e-4f0
    end

    @testset "OneCycleSchedule monotonicity" begin
        sched = OneCycleSchedule(1e-2f0; total_steps=1000)
        # Should increase then decrease
        values = [sched(s) for s in 0:10:1000]
        @test maximum(values) >= sched(0)
        @test all(v -> v >= 0.0f0, values)
    end

end  # TrainingOptimizer

# ─────────────────────────────────────────────────────────────────────────────
# CognitiveBenchmarks Tests
# ─────────────────────────────────────────────────────────────────────────────

@testset "CognitiveBenchmarks" begin

    @testset "ThinkingBenchmark" begin
        bm = ThinkingBenchmark()
        outputs = Dict{String,Any}(
            "reasoning_chain" => [randn(Float32, 64) for _ in 1:5],
            "probe_answers"   => Float32[1.0, 0.0, 1.0, 1.0],
            "probe_labels"    => Float32[1.0, 0.0, 1.0, 1.0],
        )
        result = CognitiveBenchmarks.run(bm, outputs)
        @test 0.0f0 <= result.score <= 1.0f0
        @test result.faculty == :thinking
    end

    @testset "AttentionBenchmark" begin
        bm = AttentionBenchmark(num_heads=4, seq_len=16)
        attn = abs.(randn(Float32, 4, 16, 16))
        # Normalize rows
        for h in 1:4, s in 1:16
            attn[h, s, :] ./= sum(attn[h, s, :])
        end
        outputs = Dict{String,Any}("attention_weights" => attn)
        result = CognitiveBenchmarks.run(bm, outputs)
        @test 0.0f0 <= result.score <= 1.0f0
    end

    @testset "MemoryBenchmark" begin
        bm = MemoryBenchmark()
        outputs = Dict{String,Any}(
            "episodic_hits"   => 8,
            "episodic_probes" => 10,
            "semantic_hits"   => 7,
            "semantic_probes" => 10,
            "retention_curve" => Float32[1.0, 0.9, 0.8, 0.75, 0.7],
        )
        result = CognitiveBenchmarks.run(bm, outputs)
        @test 0.0f0 <= result.score <= 1.0f0
        @test result.faculty == :memory
    end

    @testset "BenchmarkSuite" begin
        suite = BenchmarkSuite()
        @test length(suite.benchmarks) == 8

        # Run with mostly-empty outputs — should not throw
        outputs = Dict{String,Any}()
        report = run_benchmarks(suite, outputs)
        @test 0.0f0 <= report.overall_score <= 1.0f0
        @test length(report.results) == 8
    end

end  # CognitiveBenchmarks

# ─────────────────────────────────────────────────────────────────────────────
# TrainingFFI Tests
# ─────────────────────────────────────────────────────────────────────────────

@testset "TrainingFFI" begin

    @testset "init" begin
        result = init_julia_training_ffi(verbose=false)
        @test result == true
    end

    @testset "ffi_compute_loss" begin
        vocab_size = 100
        logits = randn(Float32, vocab_size)
        target = zeros(Float32, vocab_size)
        target[42] = 1.0f0
        loss = ffi_compute_loss(logits, target)
        @test isfinite(loss)
        @test loss >= 0.0f0
    end

    @testset "ffi_layer_statistics" begin
        weights = randn(Float32, 128)
        stats = ffi_layer_statistics(weights)
        @test length(stats) == 5  # mean, std, min, max, l2_norm
        @test stats[1] ≈ mean(weights) atol=1e-5f0
        @test stats[5] ≈ norm(weights) atol=1e-4f0
    end

    @testset "ffi_gradient_statistics" begin
        grads = randn(Float32, 64)
        stats = ffi_gradient_statistics(grads)
        @test length(stats) == 5
        @test 0.0f0 <= stats[5] <= 1.0f0  # percentage zeros
    end

    @testset "ffi_cosine_similarity_batch" begin
        A = randn(Float32, 4, 32)
        similarities = ffi_cosine_similarity_batch(A)
        n = size(A, 1)
        @test length(similarities) == n * (n - 1) ÷ 2
        @test all(-1.0f0 - 1e-5f0 .<= similarities .<= 1.0f0 + 1e-5f0)
    end

end  # TrainingFFI

println()
println("All training tests completed.")
println("=" ^ 60)
