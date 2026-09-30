"""
LinguisticMath.jl - Mathematical Modeling of Language Typology, Diachronic Evolution & SLA Dynamics.

Implements:
1. Zipf-Mandelbrot Lexical Frequency Law: P(r) = C / (r + beta)^alpha.
2. Syntactic Dependency Tree Branching Entropy.
3. Diachronic Phonological Distance & Grimm's Law Consonant Mutation Matrix.
4. Second Language Acquisition (SLA) Processability Theory & Cognitive Load Dynamics.
5. 7-Point Universal Correctness Framework Composite Metric & Subordination Ratios (Part 10 of Guide).
"""

module LinguisticMath

using LinearAlgebra
using Statistics

export zipf_mandelbrot_probability, syntactic_branching_entropy
export phonological_mutation_distance, compute_sla_processability_index
export cognitive_load_capacity
export subordination_index, hedging_ratio, universal_checklist_composite

"""
    zipf_mandelbrot_probability(rank::Int, alpha::Float64=1.05, beta::Float64=2.7) -> Float64

Computes word probability at given frequency rank under Mandelbrot's generalized formula.
"""
function zipf_mandelbrot_probability(rank::Int, alpha::Float64=1.05, beta::Float64=2.7)::Float64
    if rank <= 0
        return 0.0
    end
    return 1.0 / ((Float64(rank) + beta)^alpha)
end

"""
    syntactic_branching_entropy(branching_factors::Vector{Int}) -> Float64

Evaluates Shannon entropy over constituent branching factors (e.g. unary, binary, ternary nodes).
H = - sum_i p_i * log2(p_i)
"""
function syntactic_branching_entropy(branching_factors::Vector{Int})::Float64
    total = sum(branching_factors)
    if total == 0
        return 0.0
    end

    H = 0.0
    for count in branching_factors
        if count > 0
            p = Float64(count) / Float64(total)
            H -= p * log2(p)
        end
    end
    return H
end

"""
    subordination_index(num_subordinate::Int, num_coordinate::Int) -> Float64

Computes Clausal Subordination Ratio:
I_sub = N_sub / (N_sub + N_coord + 1e-8)
High ratio (> 0.6) reflects academic / complex prose maturity (Part 4 of Guide).
"""
function subordination_index(num_subordinate::Int, num_coordinate::Int)::Float64
    denom = Float64(num_subordinate + num_coordinate)
    if denom == 0.0
        return 0.0
    end
    return Float64(num_subordinate) / denom
end

"""
    hedging_ratio(num_hedges::Int, num_assertions::Int) -> Float64

Evaluates academic epistemic stance balance:
H = N_hedges / (N_hedges + N_assertions + 1e-8)
Target range in academic discourse: 0.15 - 0.35.
"""
function hedging_ratio(num_hedges::Int, num_assertions::Int)::Float64
    total = Float64(num_hedges + num_assertions)
    if total == 0.0
        return 0.0
    end
    return Float64(num_hedges) / total
end

"""
    universal_checklist_composite(scores::Vector{Float64}, weights::Vector{Float64}=Float64[]) -> Float64

Computes weighted composite score over the 7-Point Universal Correctness Framework:
Scores for dimensions [A, B, C, D, E, F, G].
"""
function universal_checklist_composite(scores::Vector{Float64}, weights::Vector{Float64}=Float64[])::Float64
    if length(scores) != 7
        throw(ArgumentError("Checklist requires exactly 7 dimension scores [A..G]"))
    end
    w = isempty(weights) ? fill(1.0 / 7.0, 7) : weights ./ sum(weights)
    return dot(scores, w)
end

"""
    phonological_mutation_distance(proto_features::Vector{Float64}, daughter_features::Vector{Float64}) -> Float64

Calculates diachronic phonetic drift distance between ancestral and daughter language segments.
D = sqrt( sum( (proto - daughter)^2 ) ) / sqrt(dim)
"""
function phonological_mutation_distance(proto_features::Vector{Float64}, daughter_features::Vector{Float64})::Float64
    dim = min(length(proto_features), length(daughter_features))
    if dim == 0
        return 0.0
    end

    sum_sq = 0.0
    for i in 1:dim
        diff = proto_features[i] - daughter_features[i]
        sum_sq += diff * diff
    end
    return sqrt(sum_sq) / sqrt(Float64(dim))
end

"""
    compute_sla_processability_index(stage::Int, target_difficulty::Float64) -> Float64

Models Pienemann Processability Theory (Stages 1 to 6):
1: Lemma Access
2: Category Procedure (Past tense -ed, plural -s)
3: Phrasal Procedure (NP agreement)
4: S-Procedure (Subject-Verb inversion)
5: Subordinate Clause Procedure (Embedded word order)
6: Pragmatic Systemic Reorganization

Returns production probability P(success) under current processing constraints.
"""
function compute_sla_processability_index(stage::Int, target_difficulty::Float64)::Float64
    clamped_stage = clamp(stage, 1, 6)
    z = (Float64(clamped_stage) * 0.8) - target_difficulty
    return 1.0 / (1.0 + exp(-z))
end

"""
    cognitive_load_capacity(intrinsic::Float64, extraneous::Float64, germane::Float64) -> Tuple{Float64, Bool}

Calculates Sweller cognitive load ratio:
Total = Intrinsic + Extraneous + Germane.
Returns (TotalLoad, IsOverloaded) where capacity threshold is 1.0 (working memory saturation).
"""
function cognitive_load_capacity(intrinsic::Float64, extraneous::Float64, germane::Float64)::Tuple{Float64, Bool}
    total = intrinsic + extraneous + germane
    is_overloaded = total > 1.0
    return (total, is_overloaded)
end

end # module LinguisticMath
