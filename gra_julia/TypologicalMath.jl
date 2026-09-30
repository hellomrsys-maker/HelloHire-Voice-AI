"""
TypologicalMath.jl - Mathematical Foundations of Comparative Grammar Typology.

Implements mathematical formalisms for:
1. Greenbergian Syntactic Word Order Harmony: H_Greenberg in [0, 1].
2. Morphological Synthesis & Fusion Indices (Greenberg 1960).
3. Mahalanobis / Weighted Multi-Dimensional Typological Distance across 8 Diagnostic Pillars.
4. Boas-Jakobson Obligatory Information Entropy: H_BJ = - sum_i p_i * log2(p_i).
5. Cross-Lingual L1->L2 Negative Transfer Friction Metric.
"""

module TypologicalMath

using LinearAlgebra
using Statistics

export index_of_synthesis, index_of_fusion
export greenberg_harmony_metric, typological_distance
export boas_jakobson_entropy, cross_lingual_friction_score

"""
    index_of_synthesis(num_morphemes::Int, num_words::Int) -> Float64

Computes Greenberg's Index of Synthesis (M/W ratio):
I_s = N_morphemes / N_words.
Typical ranges:
- Isolating (e.g. Vietnamese, Mandarin): 1.00 - 1.20
- Synthetic Fusional (e.g. Latin, Russian): 2.00 - 2.80
- Synthetic Agglutinative (e.g. Turkish, Swahili): 2.50 - 3.80
- Polysynthetic (e.g. Greenlandic, Mohawk): 4.00 - 8.00+
"""
function index_of_synthesis(num_morphemes::Int, num_words::Int)::Float64
    if num_words <= 0
        return 1.0
    end
    return Float64(num_morphemes) / Float64(num_words)
end

"""
    index_of_fusion(num_fusional_morphemes::Int, num_morpheme_boundaries::Int) -> Float64

Evaluates Greenberg's Index of Fusion (Degree of morphemic portmanteau blending vs transparent segmentation):
I_f = N_fusional / (N_boundaries + 1e-8).
- Agglutinative (pure transparency): I_f -> 0.0
- Fusional (high portmanteau syncretism): I_f -> 1.0
"""
function index_of_fusion(num_fusional_morphemes::Int, num_morpheme_boundaries::Int)::Float64
    if num_morpheme_boundaries <= 0
        return 0.0
    end
    return clamp(Float64(num_fusional_morphemes) / Float64(num_morpheme_boundaries), 0.0, 1.0)
end

"""
    greenberg_harmony_metric(vo_order::Int, adpos_order::Int, rel_order::Int, gen_order::Int) -> Float64

Measures cross-categorial branching harmony under Greenberg's Universal 3 and 4:
Parameters (1 = Head-Initial / Right-Branching, -1 = Head-Final / Left-Branching):
- vo_order: VO (+1) vs OV (-1)
- adpos_order: Preposition (+1) vs Postposition (-1)
- rel_order: Noun-Relative (+1) vs Relative-Noun (-1)
- gen_order: Noun-Genitive (+1) vs Genitive-Noun (-1)

Returns consistency index in [0, 1], where 1.0 represents perfect harmonic alignment.
"""
function greenberg_harmony_metric(
    vo_order::Int,
    adpos_order::Int,
    rel_order::Int,
    gen_order::Int
)::Float64
    vectors = [Float64(vo_order), Float64(adpos_order), Float64(rel_order), Float64(gen_order)]
    mean_dir = mean(vectors) # in [-1, 1]
    # Variance measures disharmony
    var_dir = var(vectors)
    # Harmony = 1 - var / 2 (max possible variance of {-1, 1} is 1.33)
    return clamp(1.0 - (var_dir / 1.3333), 0.0, 1.0)
end

"""
    typological_distance(vec_a::Vector{Float64}, vec_b::Vector{Float64}, weights::Vector{Float64}) -> Float64

Calculates weighted Euclidean distance between two language feature vectors across the 8 diagnostic pillars:
D_typ(L_1, L_2) = sqrt( sum_i w_i * (L_1,i - L_2,i)^2 )
"""
function typological_distance(
    vec_a::Vector{Float64},
    vec_b::Vector{Float64},
    weights::Vector{Float64} = ones(Float64, length(vec_a))
)::Float64
    n = min(length(vec_a), length(vec_b), length(weights))
    if n == 0
        return 0.0
    end

    sum_sq = 0.0
    sum_w = 0.0
    for i in 1:n
        w = weights[i]
        sum_sq += w * (vec_a[i] - vec_b[i])^2
        sum_w += w
    end

    if sum_w <= 0.0
        return 0.0
    end
    return sqrt(sum_sq / sum_w)
end

"""
    boas_jakobson_entropy(obligatory_categories::Vector{Bool}) -> Float64

Computes Shannon information entropy over the active obligatory categories enforced by a grammar
(e.g., tense, dual number, gender, evidentiality, spatial shape, honorific level).
H_BJ = - sum_i p_i * log2(p_i)
"""
function boas_jakobson_entropy(obligatory_categories::Vector{Bool})::Float64
    k = count(obligatory_categories)
    total = length(obligatory_categories)
    if k == 0 || total == 0
        return 0.0
    end

    p_active = Float64(k) / Float64(total)
    p_inactive = 1.0 - p_active

    h = 0.0
    if p_active > 0.0
        h -= p_active * log2(p_active)
    end
    if p_inactive > 0.0
        h -= p_inactive * log2(p_inactive)
    end
    return h
end

"""
    cross_lingual_friction_score(
        l1_synthesis::Float64,
        l2_synthesis::Float64,
        head_dir_match::Bool,
        align_match::Bool
    ) -> Float64

Estimates second language acquisition (SLA) processing friction:
High friction occurs when synthesis types diverge widely (e.g. Isolating to Polysynthetic)
or head directionality flips (e.g. English SVO Prepositions to Turkish SOV Postpositions).
"""
function cross_lingual_friction_score(
    l1_synthesis::Float64,
    l2_synthesis::Float64,
    head_dir_match::Bool,
    align_match::Bool
)::Float64
    synthesis_delta = abs(l1_synthesis - l2_synthesis) / 4.0 # normalized
    dir_penalty = head_dir_match ? 0.0 : 0.40
    align_penalty = align_match ? 0.0 : 0.35

    friction = (0.25 * synthesis_delta) + dir_penalty + align_penalty
    return clamp(friction, 0.0, 1.0)
end

end # module TypologicalMath
