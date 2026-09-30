"""
ConversationalPacing.jl — Turn Pacing & Phase Synchrony Dynamics (PACE Julia Layer)

Models the phase oscillator locking between candidate cadence theta_c(t)
and interviewer cadence theta_i(t) using the Kuramoto synchronization model:
  d(theta_c)/dt = omega_c + K * sin(theta_i - theta_c)
"""

module ConversationalPacing

export PacingState, step_kuramoto_sync

struct PacingState
    phase_candidate::Float64
    phase_interviewer::Float64
    order_parameter::Float64
end

function step_kuramoto_sync(
    s::PacingState,
    omega_c::Float64 = 1.0,
    omega_i::Float64 = 1.05,
    K::Float64 = 0.4,
    dt::Float64 = 0.05
)::PacingState
    d_theta_c = omega_c + K * sin(s.phase_interviewer - s.phase_candidate)
    d_theta_i = omega_i + K * sin(s.phase_candidate - s.phase_interviewer)

    new_tc = mod(s.phase_candidate + d_theta_c * dt, 2 * pi)
    new_ti = mod(s.phase_interviewer + d_theta_i * dt, 2 * pi)
    order = abs(cos(new_tc - new_ti))

    return PacingState(new_tc, new_ti, order)
end

end # module
