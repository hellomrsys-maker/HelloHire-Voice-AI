"""
SocialEquilibrium.jl — Non-linear Social Equilibrium and Affect Dynamics (ECSE Julia Layer)

Models the coupled differential dynamics between candidate warmth W(t)
and interviewer rapport R(t) under mutual alignment:
  dW/dt = alpha * (R - W) + gamma_w * S_cand
  dR/dt = beta  * (W - R) + gamma_r * S_inter
"""

module SocialEquilibrium

export SocialState, step_social_dynamics, simulate_conversation_equilibrium

struct SocialState
    warmth::Float64
    rapport::Float64
    valence::Float64
end

function step_social_dynamics(
    state::SocialState,
    candidate_signal::Float64,
    interviewer_signal::Float64,
    dt::Float64 = 0.1,
    alpha::Float64 = 0.35,
    beta::Float64 = 0.25
)::SocialState
    # Coupled evolution
    dW = alpha * (state.rapport - state.warmth) + 0.3 * candidate_signal
    dR = beta  * (state.warmth - state.rapport) + 0.2 * interviewer_signal

    new_w = clamp(state.warmth + dW * dt, 0.0, 1.0)
    new_r = clamp(state.rapport + dR * dt, 0.0, 1.0)
    new_v = clamp(0.6 * new_w + 0.4 * new_r, 0.0, 1.0)

    return SocialState(new_w, new_r, new_v)
end

function simulate_conversation_equilibrium(turns::Vector{Float64})::Vector{SocialState}
    states = Vector{SocialState}()
    curr = SocialState(0.5, 0.5, 0.5)
    push!(states, curr)

    for s in turns
        curr = step_social_dynamics(curr, s, 0.6)
        push!(states, curr)
    end
    return states
end

end # module
