"""
RecruitmentCognitiveDynamics.jl - Mathematical & Dynamical Systems Modeling for RVCE

Implements continuous dynamical modeling of candidate cognitive faculties during interview:
1. Cognitive Endurance & Attentional Focus ODE (decay under stress & replenishment through fluency)
2. Hopfield Attractor Dynamics for Working Memory Recall
3. Stochastic Langevin Dynamics for Out-of-the-Box Creative Ideation
4. Prospective Counterfactual Forecasting & Theory-of-Mind Projection Matrix
"""

module RecruitmentCognitiveDynamics

using LinearAlgebra
using Statistics

export CognitiveEnduranceModel, simulate_focus_trajectory
export WorkingMemoryAttractor, simulate_recall_dynamics
export CreativeLangevinModel, simulate_divergent_ideation
export CounterfactualProjectionMatrix, predict_hiring_trajectory

"""
    CognitiveEnduranceModel

Models the continuous evolution of attentional focus F(t) during high-pressure interview turns:
dF/dt = -lambda * F(t) + gamma * Fluency(t) - delta * Stress(t)
"""
struct CognitiveEnduranceModel
    lambda::Float64   # Natural cognitive fatigue rate (e.g., 0.015 / min)
    gamma::Float64    # Reinforcement from high verbal fluency & positive rapport (e.g., 0.04)
    delta::Float64    # Depletion rate from adversarial / rapid-fire questioning (e.g., 0.035)
    f0::Float64       # Initial focus baseline (default: 1.0)

    function CognitiveEnduranceModel(lambda=0.015, gamma=0.04, delta=0.035, f0=1.0)
        new(lambda, gamma, delta, f0)
    end
end

"""
    simulate_focus_trajectory(model, total_minutes, dt, fluency_vector, stress_vector) -> Vector{Float64}
Integrates the ODE using 4th-order Runge-Kutta.
"""
function simulate_focus_trajectory(
    model::CognitiveEnduranceModel,
    total_minutes::Float64,
    dt::Float64,
    fluency_fn::Function,
    stress_fn::Function
)::Vector{Float64}
    steps = Int(round(total_minutes / dt))
    trajectory = zeros(Float64, steps + 1)
    trajectory[1] = model.f0

    for i in 1:steps
        t = (i - 1) * dt
        f = trajectory[i]

        dF = (curr_f, curr_t) -> -model.lambda * curr_f + model.gamma * fluency_fn(curr_t) - model.delta * stress_fn(curr_t)

        k1 = dF(f, t)
        k2 = dF(f + 0.5 * dt * k1, t + 0.5 * dt)
        k3 = dF(f + 0.5 * dt * k2, t + 0.5 * dt)
        k4 = dF(f + dt * k3, t + dt)

        f_next = f + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        trajectory[i + 1] = clamp(f_next, 0.05, 1.0)
    end
    return trajectory
end

"""
    WorkingMemoryAttractor

Models recall dynamics using an attractor neural energy surface:
E(m) = -0.5 * m' * W * m
"""
struct WorkingMemoryAttractor
    dim::Int
    weights::Matrix{Float64}

    function WorkingMemoryAttractor(dim::Int=8)
        # Symmetrical zero-diagonal connection weight matrix
        W = randn(dim, dim)
        W = 0.5 * (W + W')
        for i in 1:dim
            W[i, i] = 0.0
        end
        new(dim, W)
    end
end

function simulate_recall_dynamics(attractor::WorkingMemoryAttractor, initial_probe::Vector{Float64}, max_iter::Int=20)::Vector{Float64}
    m = copy(initial_probe)
    for _ in 1:max_iter
        m_new = tanh.(attractor.weights * m)
        if norm(m_new - m) < 1e-4
            break
        end
        m = m_new
    end
    return m
end

"""
    CreativeLangevinModel

Models divergent / out-of-the-box conceptual jumps using double-well potential Langevin dynamics:
dX_t = -grad_V(X_t)*dt + sigma*dW_t
where V(x) = (x^2 - 1)^2 (bistable cognitive paradigm)
"""
struct CreativeLangevinModel
    sigma::Float64   # Cognitive randomness / creative leap parameter

    function CreativeLangevinModel(sigma=0.35)
        new(sigma)
    end
end

function simulate_divergent_ideation(model::CreativeLangevinModel, n_steps::Int=50, dt::Float64=0.05)::Vector{Float64}
    x = zeros(Float64, n_steps)
    x[1] = -1.0 # Standard conventional paradigm well
    for i in 1:(n_steps - 1)
        # Potential derivative: V'(x) = 4*x*(x^2 - 1)
        grad_v = 4.0 * x[i] * (x[i]^2 - 1.0)
        noise = model.sigma * sqrt(dt) * randn()
        x[i + 1] = x[i] - grad_v * dt + noise
    end
    return x
end

"""
    CounterfactualProjectionMatrix

Projects candidate performance vector across 5 interview rounds:
[Thinking, Concentration, Recall, Creativity, Imagination, Verbal]
"""
struct CounterfactualProjectionMatrix
    transfer_matrix::Matrix{Float64}

    function CounterfactualProjectionMatrix()
        # 6x6 Markov transition matrix representing cognitive trait inter-dependencies
        # Row: [Think, Focus, Recall, Creat, Imagi, Verbal]
        M = [
            0.50 0.10 0.15 0.10 0.10 0.05;
            0.15 0.60 0.10 0.05 0.05 0.05;
            0.20 0.15 0.50 0.05 0.05 0.05;
            0.10 0.05 0.05 0.60 0.15 0.05;
            0.10 0.05 0.05 0.20 0.55 0.05;
            0.10 0.10 0.05 0.05 0.05 0.65
        ]
        new(M)
    end
end

function predict_hiring_trajectory(
    proj::CounterfactualProjectionMatrix,
    initial_scorecard::Vector{Float64},
    rounds::Int=5
)::Matrix{Float64}
    trajectory = zeros(Float64, 6, rounds)
    curr = copy(initial_scorecard)
    for r in 1:rounds
        curr = proj.transfer_matrix * curr
        curr = clamp.(curr, 0.0, 1.0)
        trajectory[:, r] = curr
    end
    return trajectory
end

end # module RecruitmentCognitiveDynamics
