"""
TeluguGrammarDynamics.jl - Mathematical Formulations & Dynamical Simulations for Telugu.
Provides nPVI (normalized Pairwise Variability Index) and Turn-Taking Entropy calculations.
"""
module TeluguGrammarDynamics

export compute_npvi, conversational_entropy, telugu_vowel_sonority

"""
    compute_npvi(durations::Vector{Float64})::Float64
Computes the normalized Pairwise Variability Index for Telugu syllabic mora durations.
Because Telugu is mora-timed with Ajanta open vowels, nPVI tends towards lower variance (35-45).
"""
function compute_npvi(durations::Vector{Float64})::Float64
    m = length(durations)
    if m < 2
        return 0.0
    end
    sum_diff = 0.0
    for k in 1:(m - 1)
        dk = durations[k]
        dk1 = durations[k + 1]
        mean_d = (dk + dk1) / 2.0
        if mean_d > 1e-6
            sum_diff += abs(dk - dk1) / mean_d
        end
    end
    return (100.0 / (m - 1)) * sum_diff
end

"""
    conversational_entropy(transition_matrix::Matrix{Float64})::Float64
Calculates Shannon entropy of turn-taking transitions across conversational dyads.
"""
function conversational_entropy(transition_matrix::Matrix{Float64})::Float64
    ent = 0.0
    for p in transition_matrix
        if p > 1e-9
            ent -= p * log2(p)
        end
    end
    return ent
end

"""
    telugu_vowel_sonority(vowel_length::Symbol)::Float64
Returns the intrinsic acoustic sonority coefficient for short vs long Telugu vowels.
"""
function telugu_vowel_sonority(vowel_length::Symbol)::Float64
    if vowel_length == :long
        return 1.45
    elseif vowel_length == :short
        return 1.00
    else
        return 0.70
    end
end

end # module
