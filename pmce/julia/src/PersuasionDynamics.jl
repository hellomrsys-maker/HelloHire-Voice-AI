"""
PersuasionDynamics.jl — Dynamical Vector Attraction Model for Persuasion (PMCE Julia Layer)

Models the state trajectory of interviewer conviction C(t) driven by
Logos L(t) and Ethos E(t) under resistance damping R:
  dC/dt = (1 - C) * (alpha * L + beta * E) - gamma * R * C
"""

module PersuasionDynamics

export ConvictionState, step_conviction, simulate_persuasion_arc

struct ConvictionState
    conviction::Float64
    skepticism::Float64
    momentum::Float64
end

function step_conviction(
    s::ConvictionState,
    logos::Float64,
    ethos::Float64,
    dt::Float64 = 0.1,
    alpha::Float64 = 0.45,
    beta::Float64 = 0.35,
    gamma::Float64 = 0.15
)::ConvictionState
    drive = alpha * logos + beta * ethos
    dC = (1.0 - s.conviction) * drive - gamma * s.skepticism * s.conviction

    new_c = clamp(s.conviction + dC * dt, 0.0, 1.0)
    new_sk = clamp(s.skepticism - 0.2 * drive * dt, 0.0, 1.0)
    new_m = clamp(dC / dt, -1.0, 1.0)

    return ConvictionState(new_c, new_sk, new_m)
end

function simulate_persuasion_arc(turns::Vector{Tuple{Float64, Float64}})::Vector{ConvictionState}
    trajectory = Vector{ConvictionState}()
    curr = ConvictionState(0.3, 0.7, 0.0)
    push!(trajectory, curr)

    for (l, e) in turns
        curr = step_conviction(curr, l, e)
        push!(trajectory, curr)
    end
    return trajectory
end

end # module
