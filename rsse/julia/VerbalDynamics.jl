"""
VerbalDynamics.jl - Mathematical Modeling of Interview Verbal Communication & Dialogue Latency

Implements:
1. Turn-Taking Latency Continuous Markov Model (Candidate response pause vs. cognitive hesitation)
2. Conversational Acoustic Boundary Entropy
3. Vocalic Energy Dispersion & Acoustic Stress Trajectory
4. STAR Structural Completeness Scoring Function
"""

module VerbalDynamics

using LinearAlgebra
using Statistics

export TurnTakingLatencyModel, ConversationalEntropy, calculate_turn_latency_score
export compute_conversational_entropy, model_vocalic_energy_decay, evaluate_star_mathematics

"""
    TurnTakingLatencyModel

Models candidate latency between interviewer question and candidate answer:
- Optimal cognitive hesitation: 0.8s to 2.2s (thoughtful synthesis)
- Extreme latency > 4.0s: cognitive block / disfluency
- Immediate latency < 0.3s: unconsidered or rehearsed response
"""
struct TurnTakingLatencyModel
    optimal_min::Float64
    optimal_max::Float64
    decay_rate::Float64

    function TurnTakingLatencyModel()
        new(0.8, 2.2, 0.45)
    end
end

function calculate_turn_latency_score(model::TurnTakingLatencyModel, latency_seconds::Float64)::Float64
    if latency_seconds >= model.optimal_min && latency_seconds <= model.optimal_max
        return 1.0
    elseif latency_seconds < model.optimal_min
        return clamp(0.5 + (latency_seconds / model.optimal_min) * 0.5, 0.2, 1.0)
    else
        excess = latency_seconds - model.optimal_max
        return clamp(exp(-model.decay_rate * excess), 0.1, 1.0)
    end
end

"""
    compute_conversational_entropy(phoneme_durations::Vector{Float64}) -> Float64

Computes Shannon entropy of vocalic duration intervals to measure conversational fluency:
H = - sum(p_i * log2(p_i))
Lower entropy in syllable-timed speech; higher controlled entropy in expressive stress-timed delivery.
"""
function compute_conversational_entropy(phoneme_durations::Vector{Float64})::Float64
    n = length(phoneme_durations)
    if n < 2
        return 0.0
    end
    total = sum(phoneme_durations)
    if total <= 0.0
        return 0.0
    end
    probs = phoneme_durations ./ total
    entropy = 0.0
    for p in probs
        if p > 1e-9
            entropy -= p * log2(p)
        end
    end
    return round(entropy, digits=4)
end

"""
    model_vocalic_energy_decay(base_energy::Float64, turns::Int, stress_factor::Float64) -> Vector{Float64}

Simulates vocalic acoustic energy retention over multi-turn challenging interviews.
E(t) = E_0 * (1 - alpha * (1 - exp(-beta * t)))
"""
function model_vocalic_energy_decay(base_energy::Float64, turns::Int, stress_factor::Float64)::Vector{Float64}
    energies = zeros(Float64, turns)
    alpha = 0.35 * clamp(stress_factor, 0.0, 2.0)
    beta = 0.15
    for t in 1:turns
        decay = 1.0 - alpha * (1.0 - exp(-beta * Float64(t)))
        energies[t] = round(base_energy * decay, digits=4)
    end
    return energies
end

"""
    evaluate_star_mathematics(s::Float64, t::Float64, a::Float64, r::Float64) -> Float64

Computes geometric mean weighted STAR completeness:
C_STAR = (S^w_s * T^w_t * A^w_a * R^w_r)
where Action and Result carry highest weights for leadership and technical roles.
"""
function evaluate_star_mathematics(s::Float64, t::Float64, a::Float64, r::Float64)::Float64
    w_s = 0.15
    w_t = 0.15
    w_a = 0.40
    w_r = 0.30
    
    score = (s^w_s) * (t^w_t) * (a^w_a) * (r^w_r)
    return round(clamp(score, 0.0, 1.0), digits=4)
end

end # module VerbalDynamics
