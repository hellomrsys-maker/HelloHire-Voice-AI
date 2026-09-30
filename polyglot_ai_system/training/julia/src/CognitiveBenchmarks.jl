# CognitiveBenchmarks.jl
# Evaluation benchmarks for all cognitive faculties trained in the AI system.
# Covers: reasoning depth, attention quality, memory recall, creativity,
# imagination, metacognition, and associative reasoning.
# All benchmarks return normalized scores in [0, 1].

module CognitiveBenchmarks

using Statistics
using LinearAlgebra
using Printf
using Logging

export BenchmarkSuite, run_benchmarks, BenchmarkResult, BenchmarkReport
export ThinkingBenchmark, AttentionBenchmark, MemoryBenchmark
export CreativityBenchmark, ImaginationBenchmark, MetacognitionBenchmark
export AssociativeBenchmark, CuriosityBenchmark

# ─────────────────────────────────────────────────────────────────────────────
# Result types
# ─────────────────────────────────────────────────────────────────────────────

"""Single benchmark result."""
struct BenchmarkResult
    name::String
    faculty::Symbol
    score::Float32         # normalized [0, 1]
    raw_value::Float64
    unit::String
    passed::Bool
    threshold::Float32
    elapsed_ms::Float64
    metadata::Dict{String,Any}
end

function BenchmarkResult(;
    name, faculty, score, raw_value=Float64(score), unit="%",
    threshold=0.7f0, elapsed_ms=0.0, metadata=Dict{String,Any}()
)
    BenchmarkResult(name, faculty, Float32(score), raw_value, unit,
                    Float32(score) >= threshold, Float32(threshold), elapsed_ms, metadata)
end

"""
Aggregated report from a full benchmark suite run.
"""
struct BenchmarkReport
    results::Vector{BenchmarkResult}
    overall_score::Float32
    passed::Bool
    faculty_scores::Dict{Symbol, Float32}
    elapsed_total_ms::Float64
end

function BenchmarkReport(results::Vector{BenchmarkResult}, elapsed_ms::Float64)
    scores = [r.score for r in results]
    overall = isempty(scores) ? 0.0f0 : mean(scores)
    passed = all(r.passed for r in results)

    # Per-faculty aggregation
    faculty_groups = Dict{Symbol, Vector{Float32}}()
    for r in results
        push!(get!(faculty_groups, r.faculty, Float32[]), r.score)
    end
    faculty_scores = Dict(f => mean(ss) for (f, ss) in faculty_groups)

    BenchmarkReport(results, Float32(overall), passed, faculty_scores, elapsed_ms)
end

function Base.show(io::IO, rpt::BenchmarkReport)
    println(io, "=== Cognitive Benchmark Report ===")
    @printf(io, "Overall score: %.3f | Passed: %s\n", rpt.overall_score, rpt.passed ? "YES" : "NO")
    println(io, "\nPer-faculty scores:")
    for (faculty, score) in sort(collect(rpt.faculty_scores); by=first)
        @printf(io, "  %-25s %.3f\n", faculty, score)
    end
    println(io, "\nDetailed results:")
    for r in rpt.results
        status = r.passed ? "✓" : "✗"
        @printf(io, "  [%s] %-35s %.3f %s\n", status, r.name, r.score, r.unit)
    end
    @printf(io, "\nTotal elapsed: %.1f ms\n", rpt.elapsed_total_ms)
end

# ─────────────────────────────────────────────────────────────────────────────
# Abstract benchmark type
# ─────────────────────────────────────────────────────────────────────────────

abstract type AbstractBenchmark end

"""Run a benchmark and return a BenchmarkResult."""
function run(bm::AbstractBenchmark, model_outputs::Dict{String,Any})::BenchmarkResult
    error("run not implemented for $(typeof(bm))")
end

# ─────────────────────────────────────────────────────────────────────────────
# Thinking / Reasoning Benchmark
# ─────────────────────────────────────────────────────────────────────────────

"""
Evaluates multi-step reasoning quality using chain-of-thought traces.
Scores:
  - Chain length (number of distinct reasoning steps)
  - Step coherence (dot product similarity between consecutive hidden states)
  - Answer accuracy on logical deduction probes
"""
struct ThinkingBenchmark <: AbstractBenchmark
    min_chain_length::Int
    coherence_threshold::Float32
    threshold::Float32
end

ThinkingBenchmark(; min_chain_length=3, coherence_threshold=0.7f0, threshold=0.7f0) =
    ThinkingBenchmark(min_chain_length, coherence_threshold, threshold)

function run(bm::ThinkingBenchmark, outputs::Dict{String,Any})::BenchmarkResult
    t0 = time_ns()
    chain = get(outputs, "reasoning_chain", Vector{Vector{Float32}}())
    probe_answers = get(outputs, "probe_answers", Float32[])
    probe_labels  = get(outputs, "probe_labels",  Float32[])

    # Score 1: chain length
    chain_len = length(chain)
    len_score = min(Float32(chain_len) / Float32(bm.min_chain_length), 1.0f0)

    # Score 2: coherence between consecutive steps
    coherence_scores = Float32[]
    for i in 1:length(chain)-1
        h1, h2 = chain[i], chain[i+1]
        norm1, norm2 = norm(h1), norm(h2)
        if norm1 > 1e-8f0 && norm2 > 1e-8f0
            push!(coherence_scores, dot(h1, h2) / (norm1 * norm2))
        end
    end
    coherence = isempty(coherence_scores) ? 0.5f0 : mean(coherence_scores)
    coh_score = clamp(coherence, 0.0f0, 1.0f0)

    # Score 3: logical probe accuracy
    acc_score = if !isempty(probe_answers) && length(probe_answers) == length(probe_labels)
        correct = sum(round.(probe_answers) .== probe_labels)
        Float32(correct) / Float32(length(probe_labels))
    else
        0.5f0
    end

    overall = 0.3f0 * len_score + 0.35f0 * coh_score + 0.35f0 * acc_score
    elapsed = (time_ns() - t0) / 1e6

    BenchmarkResult(
        name="thinking_reasoning",
        faculty=:thinking,
        score=overall,
        unit="score",
        threshold=bm.threshold,
        elapsed_ms=elapsed,
        metadata=Dict("chain_len"=>chain_len, "coherence"=>coherence, "probe_acc"=>acc_score)
    )
end

# ─────────────────────────────────────────────────────────────────────────────
# Attention Benchmark
# ─────────────────────────────────────────────────────────────────────────────

"""
Measures the quality of attention patterns:
  - Entropy of attention distributions (lower entropy → sharper focus)
  - Coverage: fraction of tokens that received ≥1% attention
  - Cross-head diversity: mean pairwise cosine distance between heads
"""
struct AttentionBenchmark <: AbstractBenchmark
    num_heads::Int
    seq_len::Int
    threshold::Float32
end

AttentionBenchmark(; num_heads=8, seq_len=512, threshold=0.65f0) =
    AttentionBenchmark(num_heads, seq_len, threshold)

function run(bm::AttentionBenchmark, outputs::Dict{String,Any})::BenchmarkResult
    t0 = time_ns()
    # attn_weights: [num_heads × seq_len × seq_len]
    attn = get(outputs, "attention_weights", nothing)

    if isnothing(attn) || ndims(attn) < 3
        return BenchmarkResult(name="attention_quality", faculty=:attention,
                               score=0.0f0, threshold=bm.threshold)
    end

    H, S1, S2 = size(attn, 1), size(attn, 2), size(attn, 3)

    # Entropy: for each head, mean entropy of its seq attention rows
    entropies = Float32[]
    for h in 1:H
        for s in 1:S1
            row = attn[h, s, :]
            row = max.(row, 1e-9f0)
            row = row ./ sum(row)
            push!(entropies, -sum(row .* log2.(row)))
        end
    end
    mean_entropy = mean(entropies)
    max_entropy = log2(Float32(S2))
    # Normalized: lower entropy is better for sharp attention → invert
    entropy_score = clamp(1.0f0 - mean_entropy / max_entropy, 0.0f0, 1.0f0)

    # Coverage: fraction of tokens attended to above threshold
    coverage_scores = Float32[]
    for h in 1:H
        row = vec(mean(attn[h, :, :], dims=1))
        covered = sum(row .>= 0.01f0)
        push!(coverage_scores, Float32(covered) / Float32(S2))
    end
    coverage = mean(coverage_scores)

    # Head diversity: mean pairwise cosine distance between head mean attention vectors
    head_vecs = [vec(mean(attn[h, :, :], dims=1)) for h in 1:H]
    div_scores = Float32[]
    for i in 1:H, j in i+1:H
        v1, v2 = head_vecs[i], head_vecs[j]
        n1, n2 = norm(v1), norm(v2)
        if n1 > 1e-8f0 && n2 > 1e-8f0
            push!(div_scores, 1.0f0 - dot(v1, v2) / (n1 * n2))
        end
    end
    diversity = isempty(div_scores) ? 0.5f0 : mean(div_scores)

    overall = 0.4f0 * entropy_score + 0.3f0 * coverage + 0.3f0 * diversity
    elapsed = (time_ns() - t0) / 1e6

    BenchmarkResult(
        name="attention_quality",
        faculty=:attention,
        score=overall,
        unit="score",
        threshold=bm.threshold,
        elapsed_ms=elapsed,
        metadata=Dict("entropy_score"=>entropy_score, "coverage"=>coverage, "diversity"=>diversity)
    )
end

# ─────────────────────────────────────────────────────────────────────────────
# Memory Benchmark (episodic + semantic)
# ─────────────────────────────────────────────────────────────────────────────

"""
Evaluates memory recall quality:
  - Episodic recall: hit rate on recently seen token sequences
  - Semantic recall: embedding nearest-neighbor accuracy on concept probes
  - Retention decay: exponential fit of recall accuracy over time
"""
struct MemoryBenchmark <: AbstractBenchmark
    episodic_window::Int   # tokens in episodic window
    threshold::Float32
end

MemoryBenchmark(; episodic_window=128, threshold=0.65f0) =
    MemoryBenchmark(episodic_window, threshold)

function run(bm::MemoryBenchmark, outputs::Dict{String,Any})::BenchmarkResult
    t0 = time_ns()

    episodic_hits    = get(outputs, "episodic_hits", 0)
    episodic_probes  = get(outputs, "episodic_probes", 1)
    semantic_hits    = get(outputs, "semantic_hits", 0)
    semantic_probes  = get(outputs, "semantic_probes", 1)
    retention_curve  = get(outputs, "retention_curve", Float32[1.0f0])

    episodic_score = Float32(episodic_hits) / Float32(max(episodic_probes, 1))
    semantic_score = Float32(semantic_hits) / Float32(max(semantic_probes, 1))

    # Retention: area under retention curve (trapezoidal)
    n = length(retention_curve)
    auc = n > 1 ? sum(0.5f0 .* (retention_curve[1:end-1] .+ retention_curve[2:end])) / Float32(n-1)
                : retention_curve[1]
    retention_score = clamp(Float32(auc), 0.0f0, 1.0f0)

    overall = 0.35f0 * episodic_score + 0.35f0 * semantic_score + 0.30f0 * retention_score
    elapsed = (time_ns() - t0) / 1e6

    BenchmarkResult(
        name="memory_recall",
        faculty=:memory,
        score=overall,
        threshold=bm.threshold,
        elapsed_ms=elapsed,
        metadata=Dict("episodic"=>episodic_score, "semantic"=>semantic_score, "retention"=>retention_score)
    )
end

# ─────────────────────────────────────────────────────────────────────────────
# Creativity Benchmark
# ─────────────────────────────────────────────────────────────────────────────

"""
Measures divergent thinking via:
  - Semantic diversity: mean pairwise cosine distance between generated embeddings
  - Lexical novelty: OOV rate vs baseline distribution
  - Surprise score: negative log-probability of generated tokens relative to greedy
"""
struct CreativityBenchmark <: AbstractBenchmark
    threshold::Float32
end

CreativityBenchmark(; threshold=0.6f0) = CreativityBenchmark(threshold)

function run(bm::CreativityBenchmark, outputs::Dict{String,Any})::BenchmarkResult
    t0 = time_ns()

    embeddings      = get(outputs, "generated_embeddings", nothing)  # [n_samples × dim]
    lexical_novelty = get(outputs, "lexical_novelty", 0.5f0)
    surprise_score  = get(outputs, "surprise_score", 0.5f0)

    semantic_diversity = if !isnothing(embeddings) && size(embeddings, 1) > 1
        n = size(embeddings, 1)
        pairs = Float32[]
        for i in 1:n, j in i+1:n
            v1, v2 = embeddings[i, :], embeddings[j, :]
            n1, n2 = norm(v1), norm(v2)
            if n1 > 1e-8f0 && n2 > 1e-8f0
                push!(pairs, 1.0f0 - dot(v1, v2) / (n1 * n2))
            end
        end
        isempty(pairs) ? 0.5f0 : mean(pairs)
    else
        0.5f0
    end

    overall = 0.4f0 * semantic_diversity +
              0.3f0 * Float32(lexical_novelty) +
              0.3f0 * Float32(surprise_score)
    elapsed = (time_ns() - t0) / 1e6

    BenchmarkResult(
        name="creativity_divergent",
        faculty=:creativity,
        score=overall,
        threshold=bm.threshold,
        elapsed_ms=elapsed,
        metadata=Dict("diversity"=>semantic_diversity, "novelty"=>lexical_novelty)
    )
end

# ─────────────────────────────────────────────────────────────────────────────
# Imagination Benchmark
# ─────────────────────────────────────────────────────────────────────────────

"""
Evaluates generative synthesis quality (conditional generation):
  - Prompt coherence: cosine similarity of generated embedding to prompt embedding
  - Completion fluency: perplexity of generated text under a reference LM
  - Interpolation smoothness: linearity of semantic interpolation in latent space
"""
struct ImaginationBenchmark <: AbstractBenchmark
    threshold::Float32
end

ImaginationBenchmark(; threshold=0.65f0) = ImaginationBenchmark(threshold)

function run(bm::ImaginationBenchmark, outputs::Dict{String,Any})::BenchmarkResult
    t0 = time_ns()

    prompt_emb    = get(outputs, "prompt_embedding",    nothing)
    generated_emb = get(outputs, "generated_embedding", nothing)
    fluency_ppl   = get(outputs, "fluency_perplexity",  100.0f0)
    interp_curve  = get(outputs, "interpolation_curve", Float32[])

    coherence = if !isnothing(prompt_emb) && !isnothing(generated_emb)
        n1, n2 = norm(prompt_emb), norm(generated_emb)
        if n1 > 1e-8f0 && n2 > 1e-8f0
            clamp(dot(prompt_emb, generated_emb) / (n1 * n2), -1.0f0, 1.0f0)
        else
            0.5f0
        end
    else
        0.5f0
    end

    # Fluency: lower perplexity is better; normalize to [0,1] with exponential decay
    fluency = exp(-Float32(fluency_ppl) / 100.0f0)

    # Smoothness of latent interpolation: measure linearity deviation
    smoothness = if length(interp_curve) > 2
        # Expected: linear ramp from 0 to 1
        n = length(interp_curve)
        ideal = range(0.0f0, 1.0f0, length=n)
        deviation = mean((interp_curve .- ideal).^2)
        clamp(1.0f0 - Float32(deviation), 0.0f0, 1.0f0)
    else
        0.5f0
    end

    overall = 0.35f0 * (coherence * 0.5f0 + 0.5f0) +  # shift cosine to [0,1]
              0.35f0 * fluency +
              0.3f0  * smoothness
    elapsed = (time_ns() - t0) / 1e6

    BenchmarkResult(
        name="imagination_synthesis",
        faculty=:imagination,
        score=overall,
        threshold=bm.threshold,
        elapsed_ms=elapsed,
        metadata=Dict("coherence"=>coherence, "fluency"=>fluency, "smoothness"=>smoothness)
    )
end

# ─────────────────────────────────────────────────────────────────────────────
# Metacognition Benchmark
# ─────────────────────────────────────────────────────────────────────────────

"""
Evaluates self-monitoring ability:
  - Calibration: how well confidence scores match actual accuracy
  - Uncertainty detection: F1 for detecting when the model should abstain
  - Self-correction rate: fraction of errors corrected on second-pass review
"""
struct MetacognitionBenchmark <: AbstractBenchmark
    threshold::Float32
end

MetacognitionBenchmark(; threshold=0.6f0) = MetacognitionBenchmark(threshold)

function run(bm::MetacognitionBenchmark, outputs::Dict{String,Any})::BenchmarkResult
    t0 = time_ns()

    confidences   = get(outputs, "confidences",   Float32[])
    accuracies    = get(outputs, "accuracies",    Float32[])
    abstain_pred  = get(outputs, "abstain_pred",  Float32[])
    abstain_true  = get(outputs, "abstain_true",  Float32[])
    correction_rate = get(outputs, "correction_rate", 0.5f0)

    # Expected Calibration Error (ECE) → calibration score
    calibration = if length(confidences) == length(accuracies) && !isempty(confidences)
        ece = mean(abs.(confidences .- accuracies))
        clamp(1.0f0 - ece, 0.0f0, 1.0f0)
    else
        0.5f0
    end

    # Uncertainty F1
    uncertainty_f1 = if length(abstain_pred) == length(abstain_true) && !isempty(abstain_pred)
        tp = sum((abstain_pred .>= 0.5f0) .& (abstain_true .>= 0.5f0))
        fp = sum((abstain_pred .>= 0.5f0) .& (abstain_true .< 0.5f0))
        fn = sum((abstain_pred .< 0.5f0)  .& (abstain_true .>= 0.5f0))
        prec = tp / (tp + fp + 1e-8f0)
        rec  = tp / (tp + fn + 1e-8f0)
        2 * prec * rec / (prec + rec + 1e-8f0)
    else
        0.5f0
    end

    overall = 0.4f0 * calibration + 0.3f0 * uncertainty_f1 + 0.3f0 * Float32(correction_rate)
    elapsed = (time_ns() - t0) / 1e6

    BenchmarkResult(
        name="metacognition",
        faculty=:metacognition,
        score=overall,
        threshold=bm.threshold,
        elapsed_ms=elapsed,
        metadata=Dict("calibration"=>calibration, "uncertainty_f1"=>uncertainty_f1)
    )
end

# ─────────────────────────────────────────────────────────────────────────────
# Associative Reasoning Benchmark
# ─────────────────────────────────────────────────────────────────────────────

"""
Measures associative graph traversal quality:
  - Hit@k accuracy on concept-pair analogies (A:B :: C:?)
  - Graph path coherence score
"""
struct AssociativeBenchmark <: AbstractBenchmark
    k::Int
    threshold::Float32
end

AssociativeBenchmark(; k=5, threshold=0.65f0) = AssociativeBenchmark(k, threshold)

function run(bm::AssociativeBenchmark, outputs::Dict{String,Any})::BenchmarkResult
    t0 = time_ns()

    analogy_hits   = get(outputs, "analogy_hits_at_k",   0)
    analogy_probes = get(outputs, "analogy_probes",       1)
    path_scores    = get(outputs, "path_coherence_scores", Float32[])

    hit_at_k = Float32(analogy_hits) / Float32(max(analogy_probes, 1))
    path_coherence = isempty(path_scores) ? 0.5f0 : mean(path_scores)

    overall = 0.6f0 * hit_at_k + 0.4f0 * Float32(path_coherence)
    elapsed = (time_ns() - t0) / 1e6

    BenchmarkResult(
        name="associative_reasoning",
        faculty=:associative,
        score=overall,
        threshold=bm.threshold,
        elapsed_ms=elapsed,
        metadata=Dict("hit_at_k"=>hit_at_k, "path_coherence"=>path_coherence)
    )
end

# ─────────────────────────────────────────────────────────────────────────────
# Curiosity-Driven Exploration Benchmark
# ─────────────────────────────────────────────────────────────────────────────

"""
Measures curiosity-driven behavior:
  - Novel token usage rate in open-ended generation
  - Entropy of topic distribution across multiple generations
  - Self-information seeking score (mutual information with latent query embedding)
"""
struct CuriosityBenchmark <: AbstractBenchmark
    threshold::Float32
end

CuriosityBenchmark(; threshold=0.6f0) = CuriosityBenchmark(threshold)

function run(bm::CuriosityBenchmark, outputs::Dict{String,Any})::BenchmarkResult
    t0 = time_ns()

    novel_token_rate = get(outputs, "novel_token_rate",  0.5f0)
    topic_entropy    = get(outputs, "topic_entropy",     1.0f0)
    max_topic_entropy = get(outputs, "max_topic_entropy", 4.0f0)
    mi_score         = get(outputs, "query_mi_score",    0.5f0)

    novelty_score = clamp(Float32(novel_token_rate), 0.0f0, 1.0f0)
    entropy_score = clamp(Float32(topic_entropy) / Float32(max_topic_entropy), 0.0f0, 1.0f0)

    overall = 0.35f0 * novelty_score + 0.35f0 * entropy_score + 0.3f0 * Float32(mi_score)
    elapsed = (time_ns() - t0) / 1e6

    BenchmarkResult(
        name="curiosity_exploration",
        faculty=:curiosity,
        score=overall,
        threshold=bm.threshold,
        elapsed_ms=elapsed,
        metadata=Dict("novelty"=>novelty_score, "entropy_score"=>entropy_score)
    )
end

# ─────────────────────────────────────────────────────────────────────────────
# BenchmarkSuite — runs all benchmarks
# ─────────────────────────────────────────────────────────────────────────────

"""
A suite of all cognitive benchmarks. Run all and produce a BenchmarkReport.
"""
struct BenchmarkSuite
    benchmarks::Vector{AbstractBenchmark}
end

function BenchmarkSuite()
    BenchmarkSuite([
        ThinkingBenchmark(),
        AttentionBenchmark(),
        MemoryBenchmark(),
        CreativityBenchmark(),
        ImaginationBenchmark(),
        MetacognitionBenchmark(),
        AssociativeBenchmark(),
        CuriosityBenchmark(),
    ])
end

"""
Run all benchmarks in the suite against `model_outputs`.
`model_outputs` is a Dict mapping benchmark-expected keys to their values.
Returns a full BenchmarkReport.
"""
function run_benchmarks(suite::BenchmarkSuite, model_outputs::Dict{String,Any})::BenchmarkReport
    t0 = time_ns()
    results = BenchmarkResult[]
    for bm in suite.benchmarks
        try
            result = run(bm, model_outputs)
            push!(results, result)
            status = result.passed ? "PASS" : "FAIL"
            @info "[$status] $(result.name): $(round(result.score, digits=3))"
        catch e
            @warn "Benchmark $(typeof(bm)) threw: $e"
        end
    end
    elapsed_ms = (time_ns() - t0) / 1e6
    BenchmarkReport(results, elapsed_ms)
end

end # module CognitiveBenchmarks
