"""
NarrativeArcDynamics.jl — Freytag's Pyramid & Narrative Arc ODE Dynamics (NACE Julia Layer)

Models the evolution of narrative tension T(t) and climax resolution:
  dT/dt = k_exposition * (1 - T) - k_climax * delta(t - t_climax)
"""

module NarrativeArcDynamics

export ArcState, step_narrative_arc

struct ArcState
    tension::Float64
    momentum::Float64
    resolution::Float64
end

function step_narrative_arc(
    s::ArcState,
    is_climax_turn::Bool,
    dt::Float64 = 0.1,
    k_rise::Float64 = 0.35,
    k_resolve::Float64 = 0.50
)::ArcState
    if is_climax_turn
        dT = -k_resolve * s.tension
        res = clamp(s.resolution + 0.4, 0.0, 1.0)
    else
        dT = k_rise * (1.0 - s.tension)
        res = s.resolution
    end

    new_t = clamp(s.tension + dT * dt, 0.0, 1.0)
    new_m = clamp(dT / dt, -1.0, 1.0)
    return ArcState(new_t, new_m, res)
end

end # module
