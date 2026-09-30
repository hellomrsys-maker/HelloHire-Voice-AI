"""
Amharic Grammar Dynamics Simulation (Julia).
Differential-equation linguistic drift, Markov register transitions, and
information-theoretic entropy. Language: Amharic (am).
"""

module AmharicGrammarDynamics

using LinearAlgebra
using Statistics

export simulate_lexical_drift, compute_register_transition_matrix, evaluate_entropy_spectrum

function simulate_lexical_drift(initial_frequencies::Vector{Float64}, alpha::Float64, beta::Float64, steps::Int)
    dim = length(initial_frequencies)
    history = zeros(Float64, steps, dim)
    history[1, :] = initial_frequencies
    dt = 0.01
    for t in 2:steps
        noise = randn(dim) * sqrt(dt)
        drift = -alpha .* history[t-1, :] .* dt
        new_val = history[t-1, :] .+ drift .+ (beta .* noise)
        history[t, :] = max.(new_val, 1e-6)
        history[t, :] ./= sum(history[t, :])
    end
    return history
end

function compute_register_transition_matrix(transition_matrix::Matrix{Float64})
    eig = eigen(transition_matrix')
    idx = argmin(abs.(eig.values .- 1.0))
    stationary = real(eig.vectors[:, idx])
    return stationary ./ sum(stationary)
end

function evaluate_entropy_spectrum(distribution::Vector{Float64})::Float64
    valid_p = filter(p -> p > 0.0, distribution)
    return -sum(valid_p .* log2.(valid_p))
end

end # module AmharicGrammarDynamics
