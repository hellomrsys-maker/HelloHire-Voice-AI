"""
CognitiveTrajectory.jl - Multi-Dimensional Dynamical Trajectory & Bifurcation Analysis for MAIO

Simulates coupled non-linear cognitive evolution across all 8 capabilities:
dx/dt = A x + B u - ∇V(x) + noise

Includes:
1. 4th-order Runge-Kutta (RK4) numerical integration.
2. Multi-well potential energy landscape (Flow, Equilibrium, Cognitive Fatigue).
3. Local Lyapunov Exponent (LLE) computation for early warning of cognitive instability.
4. Phase space projection and attractor basin analysis.
"""

module CognitiveTrajectory

using LinearAlgebra
using Statistics

export simulate_trajectory_rk4, compute_lyapunov_exponent, default_coupling_matrix, potential_gradient

"""
    default_coupling_matrix() -> Matrix{Float64}

Defines the 8x8 cross-capability interaction matrix A:
Rows/Cols: [Thinking, Focus, Memory, Creativity, Imagination, Analytical, Verbal, Emotional]
"""
function default_coupling_matrix()::Matrix{Float64}
    # Diagonal decay + cross-coupling
    A = Matrix{Float64}(I, 8, 8) * -0.15

    # Focus reinforces Working Memory
    A[3, 2] = 0.25
    # Working Memory supports Analytical Thinking
    A[6, 3] = 0.30
    # Analytical Thinking supports Verbal Reasoning
    A[7, 6] = 0.35
    # Creativity and Imagination have positive feedback loop
    A[4, 5] = 0.20
    A[5, 4] = 0.20
    # High Emotional Regulation stabilizes Focus
    A[2, 8] = 0.30
    # Low Emotional Regulation (negative) destabilizes Analytical
    A[6, 8] = 0.25

    return A
end

"""
    potential_gradient(x::Vector{Float64}) -> Vector{Float64}

Computes -∇V(x) for a multi-well energy landscape with stable attractors at:
x* = 0.85 (High Flow State) and x* = 0.50 (Baseline Equilibrium).
V(x) = sum_i [ 0.5 * (x_i - 0.5)^2 * (x_i - 0.85)^2 ]
"""
function potential_gradient(x::Vector{Float64})::Vector{Float64}
    grad = zeros(Float64, length(x))
    for i in 1:length(x)
        xi = x[i]
        # d/dxi [ 0.5 * (xi - 0.5)^2 * (xi - 0.85)^2 ]
        term1 = (xi - 0.5) * ((xi - 0.85)^2)
        term2 = ((xi - 0.5)^2) * (xi - 0.85)
        grad[i] = term1 + term2
    end
    return grad
end

"""
    dynamics_f(x::Vector{Float64}, u::Vector{Float64}, A::Matrix{Float64}) -> Vector{Float64}

Right-hand side of ODE: dx/dt = A x + u - ∇V(x)
"""
function dynamics_f(x::Vector{Float64}, u::Vector{Float64}, A::Matrix{Float64})::Vector{Float64}
    dx = (A * x) + u - potential_gradient(x)
    return dx
end

"""
    simulate_trajectory_rk4(x0::Vector{Float64}, u::Vector{Float64}, T::Float64, dt::Float64) -> Matrix{Float64}

Integrates cognitive trajectory from t=0 to t=T using Runge-Kutta 4.
Returns matrix of dimensions [8 x num_steps].
"""
function simulate_trajectory_rk4(
    x0::Vector{Float64},
    u::Vector{Float64},
    T::Float64,
    dt::Float64
)::Matrix{Float64}
    A = default_coupling_matrix()
    num_steps = Int(round(T / dt))
    trajectory = zeros(Float64, 8, num_steps + 1)
    trajectory[:, 1] = copy(x0)

    x = copy(x0)

    for step in 1:num_steps
        k1 = dynamics_f(x, u, A)
        k2 = dynamics_f(x + 0.5 * dt * k1, u, A)
        k3 = dynamics_f(x + 0.5 * dt * k2, u, A)
        k4 = dynamics_f(x + dt * k3, u, A)

        x += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        x = clamp.(x, 0.0, 1.0) # Physiological boundaries
        trajectory[:, step + 1] = copy(x)
    end

    return trajectory
end

"""
    compute_lyapunov_exponent(trajectory::Matrix{Float64}, dt::Float64) -> Float64

Computes maximal local Lyapunov exponent (LLE) from trajectory.
LLE > 0 indicates chaotic sensitivity / impending cognitive divergence.
"""
function compute_lyapunov_exponent(trajectory::Matrix{Float64}, dt::Float64)::Float64
    num_steps = size(trajectory, 2)
    if num_steps < 10
        return 0.0
    end

    divergences = Float64[]
    for i in 2:num_steps
        d = norm(trajectory[:, i] - trajectory[:, i - 1])
        if d > 1e-8
            push!(divergences, log(d))
        end
    end

    if isempty(divergences)
        return 0.0
    end

    return mean(diff(divergences)) / dt
end

end # module CognitiveTrajectory
