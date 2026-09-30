"""
ScenarioDynamics.jl - Mathematical Modeling of Interview Scenario Progression and Competency Dynamics

Implements:
1. Continuous-Time Markov Chain (CTMC) & Markov Decision Process (MDP) for scenario state transitions.
2. Bayesian updating / Kalman filtering of multi-dimensional candidate competency vectors.
3. Stress accumulation dynamical system with emotional damping.
4. Transition probability matrix parameterization based on real-time AMSV state vector.
"""

module ScenarioDynamics

using LinearAlgebra
using Statistics

export InterviewPhase, PhaseWarmup, PhaseCore, PhaseDepth, PhaseStress, PhaseSynthesis, PhaseConcluded
export ScenarioState, TransitionMatrix, update_competency_bayesian, simulate_stress_trajectory, compute_transition_probabilities

@enum InterviewPhase begin
    PhaseWarmup = 1
    PhaseCore = 2
    PhaseDepth = 3
    PhaseStress = 4
    PhaseSynthesis = 5
    PhaseConcluded = 6
end

"""
    ScenarioState

Represents the continuous state of the recruitment scenario simulation.
- `phase`: Current interview phase (1-6)
- `stress_level`: Accumulated cognitive and physiological stress [0.0, 1.0]
- `competency_estimates`: 8-element vector of estimated candidate capabilities
- `covariance_matrix`: 8x8 uncertainty covariance of competency estimates
"""
mutable struct ScenarioState
    phase::InterviewPhase
    stress_level::Float64
    competency_estimates::Vector{Float64}
    covariance_matrix::Matrix{Float64}
    turn_counter::Int
    register_compliance::Float64

    function ScenarioState()
        new(
            PhaseWarmup,
            0.15,
            fill(0.5, 8),
            Matrix{Float64}(I, 8, 8) * 0.25,
            0,
            1.0
        )
    end
end

"""
    compute_transition_probabilities(state::ScenarioState, stress_multiplier::Float64) -> Vector{Float64}

Computes transition probabilities from current phase to all possible phases:
P(s_{t+1} | s_t, c_t, σ_t)
"""
function compute_transition_probabilities(state::ScenarioState, stress_multiplier::Float64)::Vector{Float64}
    probs = zeros(Float64, 6)
    curr = Int(state.phase)
    
    if curr == 6 # Concluded
        probs[6] = 1.0
        return probs
    end

    # Baseline forward transition probability based on turn count and capability
    mean_competency = mean(state.competency_estimates)
    emotional_reg = state.competency_estimates[8] # 8th capability is emotional regulation

    # Forward progression rate lambda
    # High competency accelerates exploration; low emotional regulation triggers stress early
    turn_factor = min(1.0, Float64(state.turn_counter) / 3.0)
    forward_prob = clamp(0.35 * turn_factor + 0.35 * mean_competency + 0.30 * state.register_compliance, 0.1, 0.95)

    probs[curr] = 1.0 - forward_prob
    probs[curr + 1] = forward_prob

    return probs
end

"""
    simulate_stress_trajectory(current_stress::Float64, probe_severity::Float64, emotional_reg::Float64; dt::Float64=0.1) -> Float64

Simulates continuous-time stress response:
dσ/dt = -γ σ + α · ProbeSeverity - β · EmotionalRegulation
"""
function simulate_stress_trajectory(
    current_stress::Float64,
    probe_severity::Float64,
    emotional_reg::Float64;
    dt::Float64 = 0.1
)::Float64
    gamma = 0.25  # Natural stress decay rate
    alpha = 0.60  # Probe impact gain
    beta = 0.45   # Emotional regulation damping factor

    d_stress = -gamma * current_stress + alpha * probe_severity - beta * emotional_reg
    new_stress = current_stress + d_stress * dt
    return clamp(new_stress, 0.0, 1.0)
end

"""
    update_competency_bayesian(state::ScenarioState, observation::Vector{Float64}, observation_noise_cov::Matrix{Float64})

Performs Kalman / Bayesian state estimation update on 8-dimensional competency vector:
K = P H^T (H P H^T + R)^{-1}
c = c + K (y - H c)
P = (I - K H) P
"""
function update_competency_bayesian(
    state::ScenarioState,
    observation::Vector{Float64},
    observation_noise_cov::Matrix{Float64}
)
    H = Matrix{Float64}(I, 8, 8) # Identity observation matrix
    P = state.covariance_matrix
    R = observation_noise_cov

    # Innovation covariance S = H P H^T + R
    S = H * P * H' + R
    # Kalman gain K = P H^T S^{-1}
    K = P * H' * inv(S)

    # Innovation residual y - H c
    residual = observation - (H * state.competency_estimates)

    # Updated state estimate
    state.competency_estimates = state.competency_estimates + K * residual
    # Bound to [0.0, 1.0]
    state.competency_estimates = clamp.(state.competency_estimates, 0.0, 1.0)

    # Updated covariance P = (I - K H) P
    state.covariance_matrix = (Matrix{Float64}(I, 8, 8) - K * H) * P
    return state.competency_estimates
end

end # module ScenarioDynamics
