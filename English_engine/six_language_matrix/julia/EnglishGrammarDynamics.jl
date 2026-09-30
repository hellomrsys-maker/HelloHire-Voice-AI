"""
English Grammar Dynamics Simulation (Julia).
Differential equation systems modeling linguistic drift,
Markovian state transitions between communicative registers,
and information-theoretic entropy calculations.
"""

module EnglishGrammarDynamics

using LinearAlgebra
using Statistics

export simulate_lexical_drift, compute_register_transition_matrix, evaluate_entropy_spectrum

"""
Simulates continuous-time linguistic drift over time horizon T with drift rate beta.
dx/dt = -alpha * x + beta * noise
"""
function simulate_lexical_drift(initial_frequencies::Vector{Float64}, alpha::Float64, beta::Float64, steps::Int)
    dim = length(initial_frequencies)
    history = zeros(Float64, steps, dim)
    history[1, :] = initial_frequencies

    dt = 0.01
    for t in 2:steps
        noise = randn(dim) * sqrt(dt)
        drift = -alpha .* history[t-1, :] .* dt
        diffusion = beta .* noise
        new_val = history[t-1, :] .+ drift .+ diffusion
        history[t, :] = max.(new_val, 1e-6)
        history[t, :] ./= sum(history[t, :]) # Renormalize to probability simplex
    end

    return history
end

"""
Computes the stationary distribution of register transitions (Academic, Professional, Conversational).
"""
function compute_register_transition_matrix(transition_matrix::Matrix{Float64})
    # Compute left eigenvector corresponding to eigenvalue 1.0
    eigen_decomp = eigen(transition_matrix')
    idx = argmin(abs.(eigen_decomp.values .- 1.0))
    stationary = real(eigen_decomp.vectors[:, idx])
    return stationary ./ sum(stationary)
end

"""
Calculates the Shannon entropy spectrum of n-gram distribution.
"""
function evaluate_entropy_spectrum(distribution::Vector{Float64})::Float64
    valid_p = filter(p -> p > 0.0, distribution)
    return -sum(valid_p .* log2.(valid_p))
end

end # module EnglishGrammarDynamics
