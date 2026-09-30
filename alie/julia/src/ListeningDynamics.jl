"""
ListeningDynamics.jl — Mathematical Dynamics of Active Listening Attention (ALIE Julia Layer)

Models:
1. Attention Allocation ODE — how focus distributes between content recall and new input
2. Co-reference State Tracking — entity activation memory as a decaying exponential field
3. Comprehension Confidence Trajectory — Bayesian update of understanding certainty across turns
"""

module ListeningDynamics

using LinearAlgebra
using Statistics

export AttentionAllocationModel, simulate_attention_trajectory
export CoReferenceField, simulate_entity_decay
export ComprehensionBayesTracker, update_comprehension

"""
    AttentionAllocationModel

Models candidate attention split between:
  - α(t): processing new information from interviewer
  - β(t): integrating with prior knowledge (recall)
  Constraint: α(t) + β(t) = 1

  dα/dt = -λ_α * α(t) + κ * Stimulus(t)
  dβ/dt = -λ_β * β(t) + ρ * β(t-1)
"""
struct AttentionAllocationModel
    lambda_alpha::Float64   # New-info attention decay (e.g., 0.12)
    lambda_beta::Float64    # Recall integration decay (e.g., 0.08)
    kappa::Float64          # Stimulus amplification gain (e.g., 0.45)
    rho::Float64            # Memory reinforcement factor (e.g., 0.30)
end

function AttentionAllocationModel()
    AttentionAllocationModel(0.12, 0.08, 0.45, 0.30)
end

function simulate_attention_trajectory(
    model::AttentionAllocationModel,
    n_turns::Int,
    stimulus_fn::Function,  # s(t) in [0,1]: interviewer question complexity
)::Vector{Float64}
    alphas = zeros(n_turns)
    alphas[1] = 0.50  # Initial balanced attention

    for i in 2:n_turns
        t = Float64(i)
        s = stimulus_fn(t)
        d_alpha = -model.lambda_alpha * alphas[i-1] + model.kappa * s
        alphas[i] = clamp(alphas[i-1] + d_alpha * 0.1, 0.05, 0.95)
    end
    return alphas
end

"""
    CoReferenceField

Entity activation follows exponential decay:
  A_e(t) = A_e(t_mention) * exp(-decay * (t - t_mention))
"""
struct CoReferenceField
    decay_rate::Float64   # How fast entity salience decays per turn (e.g., 0.18)
    threshold::Float64    # Minimum salience to count as active (e.g., 0.20)
end

CoReferenceField() = CoReferenceField(0.18, 0.20)

function simulate_entity_decay(
    field::CoReferenceField,
    mention_turn::Int,
    eval_turn::Int,
    initial_salience::Float64 = 1.0
)::Float64
    dt = max(0, eval_turn - mention_turn)
    salience = initial_salience * exp(-field.decay_rate * dt)
    return salience >= field.threshold ? salience : 0.0
end

"""
    ComprehensionBayesTracker

Maintains running Bayesian estimate of how well the candidate
understands the conversation context:
  P(understand | evidence) ∝ P(evidence | understand) * P(understand_prior)
"""
mutable struct ComprehensionBayesTracker
    prior::Float64
    likelihood_hit::Float64   # P(signal | understood)   = 0.92
    likelihood_miss::Float64  # P(signal | not understood) = 0.20

    ComprehensionBayesTracker() = new(0.70, 0.92, 0.20)
end

function update_comprehension(tracker::ComprehensionBayesTracker, signal::Bool)::Float64
    p = tracker.prior
    if signal
        posterior = (tracker.likelihood_hit * p) /
                    (tracker.likelihood_hit * p + tracker.likelihood_miss * (1.0 - p))
    else
        posterior = ((1.0 - tracker.likelihood_hit) * p) /
                    ((1.0 - tracker.likelihood_hit) * p + (1.0 - tracker.likelihood_miss) * (1.0 - p))
    end
    tracker.prior = clamp(posterior, 0.05, 0.99)
    return tracker.prior
end

end # module ListeningDynamics
