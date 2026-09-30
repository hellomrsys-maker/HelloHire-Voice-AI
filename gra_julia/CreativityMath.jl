"""
CreativityMath.jl - Mathematical Modeling of Language Creativity, Rhetorical Distance & Syntactic Entropy.

Implements:
1. Conceptual Divergence Entropy (Shannon semantic information).
2. Metaphorical Tension / Associative Leap Cosine Distance.
3. Syntactic Tree Depth & Structural Branching Complexity.
4. Classical Readability Metrics (Flesch-Kincaid, Automated Readability Index ARI).
5. Metric Stress Periodicity & Rhythm Regularity Index (nPVI for poetic meter).
"""

module CreativityMath

using LinearAlgebra
using Statistics

export shannon_creativity_entropy, metaphorical_tension, compute_flesch_kincaid, compute_ari
export syntactic_tree_complexity, normalized_pairwise_variability_index

"""
    shannon_creativity_entropy(probabilities::Vector{Float64}) -> Float64

Computes information-theoretic entropy of creative vocabulary dispersion:
H = - sum_i p_i * log2(p_i)
"""
function shannon_creativity_entropy(probabilities::Vector{Float64})::Float64
    H = 0.0
    for p in probabilities
        if p > 1e-12
            H -= p * log2(p)
        end
    end
    return H
end

"""
    metaphorical_tension(tenor::Vector{Float64}, vehicle::Vector{Float64}) -> Float64

Computes cognitive tension in metaphorical mappings:
T = 1.0 - (u · v) / (||u|| * ||v||)
High tension (0.7 - 0.9) represents a profound associative leap;
Excessive tension (> 0.95) degenerates into semantic incoherence.
"""
function metaphorical_tension(tenor::Vector{Float64}, vehicle::Vector{Float64})::Float64
    norm_t = norm(tenor)
    norm_v = norm(vehicle)
    if norm_t < 1e-8 || norm_v < 1e-8
        return 1.0
    end
    cosine_sim = dot(tenor, vehicle) / (norm_t * norm_v)
    return clamp(1.0 - cosine_sim, 0.0, 1.0)
end

"""
    syntactic_tree_complexity(node_counts_by_depth::Vector{Int}) -> Float64

Evaluates structural complexity of X-Bar phrase marker:
C = sum_{d=1}^D (d^1.5 * N_d) / sum(N_d)
"""
function syntactic_tree_complexity(node_counts_by_depth::Vector{Int})::Float64
    total_nodes = sum(node_counts_by_depth)
    if total_nodes == 0
        return 0.0
    end

    weighted_sum = 0.0
    for (d, count) in enumerate(node_counts_by_depth)
        weighted_sum += (Float64(d)^1.5) * Float64(count)
    end
    return weighted_sum / Float64(total_nodes)
end

"""
    compute_flesch_kincaid(total_words::Int, total_sentences::Int, total_syllables::Int) -> Float64

Computes Flesch-Kincaid Grade Level (FKGL):
FKGL = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
"""
function compute_flesch_kincaid(total_words::Int, total_sentences::Int, total_syllables::Int)::Float64
    if total_words == 0 || total_sentences == 0
        return 0.0
    end
    asl = Float64(total_words) / Float64(total_sentences) # Average Sentence Length
    asw = Float64(total_syllables) / Float64(total_words)  # Average Syllables per Word
    fkgl = 0.39 * asl + 11.8 * asw - 15.59
    return max(0.0, fkgl)
end

"""
    compute_ari(total_chars::Int, total_words::Int, total_sentences::Int) -> Float64

Computes Automated Readability Index (ARI):
ARI = 4.71 * (chars / words) + 0.5 * (words / sentences) - 21.43
"""
function compute_ari(total_chars::Int, total_words::Int, total_sentences::Int)::Float64
    if total_words == 0 || total_sentences == 0
        return 0.0
    end
    cpw = Float64(total_chars) / Float64(total_words)
    wps = Float64(total_words) / Float64(total_sentences)
    ari = 4.71 * cpw + 0.5 * wps - 21.43
    return max(0.0, ari)
end

"""
    normalized_pairwise_variability_index(syllable_durations::Vector{Float64}) -> Float64

Computes normalized Pairwise Variability Index (nPVI) for metric rhythm:
nPVI = (100 / (m - 1)) * sum_{k=1}^{m-1} | (d_k - d_{k+1}) / ((d_k + d_{k+1}) / 2) |
"""
function normalized_pairwise_variability_index(durations::Vector{Float64})::Float64
    m = length(durations)
    if m < 2
        return 0.0
    end

    total_diff = 0.0
    for k in 1:(m - 1)
        mean_d = (durations[k] + durations[k + 1]) / 2.0
        if mean_d > 1e-6
            total_diff += abs(durations[k] - durations[k + 1]) / mean_d
        end
    end
    return (100.0 / (Float64(m) - 1.0)) * total_diff
end

end # module CreativityMath
