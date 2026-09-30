# VerbalTurnDynamics.jl - Engine B Sub-Core B6 (Julia)
# Spoken & Verbal Communication Engine: Markov turn-taking transitions,
# conversational latency distributions, and communicative stress modeling.

module VerbalTurnDynamics

export model_turn_transitions, compute_dialogue_entropy, VerbalDynamicsReport

struct VerbalDynamicsReport
    turn_entropy::Float64
    latency_decay_rate::Float64
    equilibrium_state_probability::Float64
    dialogue_stability_index::Float64
end

"""
    compute_dialogue_entropy(turn_latencies::Vector{Float64}) -> Float64

Computes entropy over conversational response latencies.
"""
function compute_dialogue_entropy(latencies::Vector{Float64})::Float64
    if isempty(latencies)
        return 0.0
    end
    mean_lat = sum(latencies) / length(latencies)
    variance = sum((x - mean_lat)^2 for x in latencies) / max(1, length(latencies) - 1)
    return 0.5 * log(2.0 * π * ℯ * (variance + 1e-6))
end

"""
    model_turn_transitions(turn_count::Int, avg_wpm::Float64) -> VerbalDynamicsReport

Models interviewer-candidate state dynamics via transition equilibrium.
"""
function model_turn_transitions(turn_count::Int, avg_wpm::Float64)::VerbalDynamicsReport
    rate_factor = clamp(avg_wpm / 140.0, 0.5, 1.5)
    decay_rate = 0.08 * rate_factor
    turn_entropy = 1.25 * log(1.0 + turn_count)
    equilibrium_prob = 1.0 / (1.0 + exp(-decay_rate * turn_count))
    stability = clamp(1.0 - abs(rate_factor - 1.0) * 0.5, 0.0, 1.0)

    return VerbalDynamicsReport(
        round(turn_entropy, digits=4),
        round(decay_rate, digits=4),
        round(equilibrium_prob, digits=4),
        round(stability, digits=4)
    )
end

end # module VerbalTurnDynamics
