# Persian Grammar Dynamics (Julia 1.10+)
# Mathematical and statistical simulation of SOV information structure,
# Ezafe attachment entropy, and Ta'arof honorific dynamics.

module PersianGrammarDynamics

export SOVDynamicsState, simulate_ezafe_decay, calculate_shannon_entropy

struct SOVDynamicsState
    head_finality_ratio::Float64
    ezafe_density::Float64
    dom_adherence::Float64
    taarof_index::Float64
end

"""
Simulates the statistical decay of modifier attachment certainty as Ezafe chains lengthen.
"""
function simulate_ezafe_decay(chain_length::Int)::Vector{Float64}
    decay_curve = zeros(Float64, chain_length)
    decay_constant = 0.15
    for i in 1:chain_length
        decay_curve[i] = exp(-decay_constant * (i - 1))
    end
    return decay_curve
end

"""
Calculates the Shannon information entropy of Persian morphological distributions.
"""
function calculate_shannon_entropy(probabilities::Vector{Float64})::Float64
    entropy = 0.0
    for p in probabilities
        if p > 0.0
            entropy -= p * log2(p)
        end
    end
    return entropy
end

end # module
