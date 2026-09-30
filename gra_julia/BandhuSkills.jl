"""
BandhuSkills.jl - Mathematical Modeling of Grammar Skills & Historical Dynamics
Provides quantitative formulations for:
1. Speech Rhythm Typology: Normalized Pairwise Variability Index (nPVI) and vocalic %V
2. Listening Segmentation Entropy: Transition probability distributions across continuous acoustic streams
3. Book-Scale Reference Decay: Long-horizon exponential decay of pronoun-antecedent binding
4. Multi-Tier Editorial Progression Dynamics
"""

module BandhuSkills

using LinearAlgebra
using Statistics

export compute_npvi, compute_rpvi, classify_rhythm_class,
       segmentation_entropy, pronoun_reference_salience,
       editorial_stage_markov_step

"""
    compute_npvi(durations::Vector{Float64}) -> Float64

Computes the Normalized Pairwise Variability Index (nPVI) for vocalic intervals:
nPVI = 100 / (m - 1) * sum_{k=1}^{m-1} |(d_k - d_{k+1}) / ((d_k + d_{k+1}) / 2)|
Stress-timed languages (English, German) exhibit high nPVI (> 60).
Syllable-timed languages (Spanish, French) exhibit low nPVI (< 45).
"""
function compute_npvi(durations::Vector{Float64})::Float64
    m = length(durations)
    if m < 2
        return 0.0
    end
    acc = 0.0
    for k in 1:(m - 1)
        dk = durations[k]
        dk1 = durations[k + 1]
        mean_d = (dk + dk1) / 2.0
        if mean_d > 1e-6
            acc += abs(dk - dk1) / mean_d
        end
    end
    return (100.0 / (m - 1)) * acc
end

"""
    compute_rpvi(durations::Vector{Float64}) -> Float64

Computes the raw Pairwise Variability Index (rPVI) for consonantal intervals:
rPVI = 1 / (m - 1) * sum_{k=1}^{m-1} |d_k - d_{k+1}|
"""
function compute_rpvi(durations::Vector{Float64})::Float64
    m = length(durations)
    if m < 2
        return 0.0
    end
    acc = 0.0
    for k in 1:(m - 1)
        acc += abs(durations[k] - durations[k + 1])
    end
    return acc / (m - 1)
end

"""
    classify_rhythm_class(npvi::Float64, pct_v::Float64) -> Symbol

Classifies rhythm timing:
- :StressTimed (e.g., English, German, Russian)
- :SyllableTimed (e.g., Spanish, French, Italian)
- :MoraTimed (e.g., Japanese)
"""
function classify_rhythm_class(npvi::Float64, pct_v::Float64)::Symbol
    if npvi >= 55.0 && pct_v <= 45.0
        return :StressTimed
    elseif npvi < 50.0 && pct_v > 42.0
        return :SyllableTimed
    else
        return :MoraTimed
    end
end

"""
    segmentation_entropy(transition_probs::Vector{Float64}) -> Float64

Computes Shannon entropy across phonetic boundary transition probabilities:
H = - sum p * log2(p)
High entropy indicates boundary ambiguity where grammatical priors must resolve segmentation.
"""
function segmentation_entropy(transition_probs::Vector{Float64})::Float64
    total = sum(transition_probs)
    if total <= 1e-9
        return 0.0
    end
    probs = transition_probs ./ total
    h = 0.0
    for p in probs
        if p > 1e-9
            h -= p * log2(p)
        end
    end
    return h
end

"""
    pronoun_reference_salience(distance_in_sentences::Int, lambda_decay::Float64 = 0.35) -> Float64

Models the cognitive activation salience of a nominal antecedent over sentence distance:
S(d) = exp(- lambda * d)
When S(d) falls below 0.15, reference decay occurs and an overt noun phrase is mandatory.
"""
function pronoun_reference_salience(distance_in_sentences::Int, lambda_decay::Float64 = 0.35)::Float64
    if distance_in_sentences < 0
        return 1.0
    end
    return exp(-lambda_decay * distance_in_sentences)
end

"""
    editorial_stage_markov_step(state::Vector{Float64}, P::Matrix{Float64}) -> Vector{Float64}

Propagates manuscript error distributions across the 5-stage editing pipeline:
Stages: [1: Draft, 2: Structural, 3: Line, 4: Copy, 5: Proofread]
"""
function editorial_stage_markov_step(state::Vector{Float64}, P::Matrix{Float64})::Vector{Float64}
    return P' * state
end

end # module
