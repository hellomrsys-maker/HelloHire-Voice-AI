"""
EnduranceDepletion.jl — Cognitive Fatigue & Ego Depletion Dynamics (LSCE Julia Layer)

Models the depletion of cognitive energy E(t) during intense interviews:
  dE/dt = -gamma_depletion * complexity + eta_recovery * pause_duration
"""

module EnduranceDepletion

export FatigueState, step_endurance

struct FatigueState
    energy::Float64
    fatigue::Float64
    recovery_potential::Float64
end

function step_endurance(
    s::FatigueState,
    turn_complexity::Float64,
    dt::Float64 = 0.1,
    gamma::Float64 = 0.08,
    eta::Float64 = 0.05
)::FatigueState
    dE = -gamma * turn_complexity + eta * s.recovery_potential
    new_e = clamp(s.energy + dE * dt, 0.0, 1.0)
    new_f = clamp(1.0 - new_e, 0.0, 1.0)
    new_rec = clamp(s.recovery_potential - 0.02 * dt, 0.1, 1.0)
    return FatigueState(new_e, new_f, new_rec)
end

end # module
