# =============================================================================
# engine/julia/src/NumericalOptimizer.jl
# Numerical optimization routines for language model parameter tuning,
# differentiable programming, and gradient-based learning utilities.
# =============================================================================

module NumericalOptimizer

using LinearAlgebra
using Statistics
using Random

export AdamOptimizer, SGDOptimizer, AdaGradOptimizer,
       optimizer_step!, zero_grad!,
       gradient_clipping!, cosine_annealing_lr,
       warmup_schedule, polynomial_decay,
       numerical_gradient, gradient_check

# =============================================================================
# Optimizer State Types
# =============================================================================

"""
    AdamOptimizer

Adam optimizer state: tracks first and second moment estimates,
step count, and hyperparameters.

Default hyperparameters follow the original Adam paper (Kingma & Ba, 2014).
"""
mutable struct AdamOptimizer
    learning_rate::Float32
    beta1::Float32
    beta2::Float32
    epsilon::Float32
    weight_decay::Float32
    step::Int

    # Moment estimates: Dict mapping parameter id → moment vector
    m::Dict{String, Vector{Float32}}  # First moment
    v::Dict{String, Vector{Float32}}  # Second moment

    function AdamOptimizer(;
        learning_rate::Float32 = 3e-4f0,
        beta1::Float32         = 0.9f0,
        beta2::Float32         = 0.999f0,
        epsilon::Float32       = 1e-8f0,
        weight_decay::Float32  = 0.01f0,
    )
        new(learning_rate, beta1, beta2, epsilon, weight_decay, 0,
            Dict{String, Vector{Float32}}(),
            Dict{String, Vector{Float32}}())
    end
end

"""
    SGDOptimizer

Stochastic Gradient Descent with optional momentum and weight decay.
"""
mutable struct SGDOptimizer
    learning_rate::Float32
    momentum::Float32
    weight_decay::Float32
    velocity::Dict{String, Vector{Float32}}

    function SGDOptimizer(;
        learning_rate::Float32 = 0.01f0,
        momentum::Float32      = 0.9f0,
        weight_decay::Float32  = 1e-4f0,
    )
        new(learning_rate, momentum, weight_decay, Dict{String, Vector{Float32}}())
    end
end

"""
    AdaGradOptimizer

AdaGrad optimizer: adapts learning rates per parameter.
"""
mutable struct AdaGradOptimizer
    learning_rate::Float32
    epsilon::Float32
    sum_sq_grads::Dict{String, Vector{Float32}}

    function AdaGradOptimizer(;
        learning_rate::Float32 = 0.01f0,
        epsilon::Float32       = 1e-8f0,
    )
        new(learning_rate, epsilon, Dict{String, Vector{Float32}}())
    end
end

# =============================================================================
# Adam Step
# =============================================================================

"""
    optimizer_step!(opt::AdamOptimizer, param_id::String,
                     params::Vector{Float32}, grads::Vector{Float32})

Applies one Adam update step to `params` using gradients `grads`.
Modifies `params` in-place.

# Algorithm (with bias correction and decoupled weight decay — AdamW):
1. mₜ = β₁ mₜ₋₁ + (1 - β₁) g
2. vₜ = β₂ vₜ₋₁ + (1 - β₂) g²
3. m̂ₜ = mₜ / (1 - β₁ᵗ)     (bias correction)
4. v̂ₜ = vₜ / (1 - β₂ᵗ)
5. params -= lr × (m̂ₜ / (√v̂ₜ + ε) + λ × params)

# Arguments
- `opt`:      Optimizer state (modified in place)
- `param_id`: Unique string key for this parameter tensor
- `params`:   Parameter vector (modified in place)
- `grads`:    Gradient vector of the same shape
"""
function optimizer_step!(
    opt::AdamOptimizer,
    param_id::String,
    params::Vector{Float32},
    grads::Vector{Float32}
)
    @assert length(params) == length(grads) "params and grads must have same length"

    opt.step += 1
    t = opt.step

    # Initialize moments if first time seeing this parameter
    if !haskey(opt.m, param_id)
        opt.m[param_id] = zeros(Float32, length(params))
        opt.v[param_id] = zeros(Float32, length(params))
    end

    m = opt.m[param_id]
    v = opt.v[param_id]

    # Update biased first and second moment estimates
    @. m = opt.beta1 * m + (1.0f0 - opt.beta1) * grads
    @. v = opt.beta2 * v + (1.0f0 - opt.beta2) * grads^2

    # Bias correction
    bc1 = 1.0f0 - opt.beta1^t
    bc2 = 1.0f0 - opt.beta2^t
    m_hat = m ./ bc1
    v_hat = v ./ bc2

    # AdamW update: includes decoupled weight decay
    @. params -= opt.learning_rate * (m_hat / (sqrt(v_hat) + opt.epsilon) + opt.weight_decay * params)

    return nothing
end

# =============================================================================
# SGD Step
# =============================================================================

"""
    optimizer_step!(opt::SGDOptimizer, param_id::String,
                     params::Vector{Float32}, grads::Vector{Float32})

Applies one SGD update step with momentum.
"""
function optimizer_step!(
    opt::SGDOptimizer,
    param_id::String,
    params::Vector{Float32},
    grads::Vector{Float32}
)
    @assert length(params) == length(grads)

    if !haskey(opt.velocity, param_id)
        opt.velocity[param_id] = zeros(Float32, length(params))
    end

    vel = opt.velocity[param_id]

    # Gradient with weight decay (L2 regularization)
    g_eff = grads .+ opt.weight_decay .* params

    # Momentum update
    @. vel = opt.momentum * vel + g_eff

    # Parameter update
    @. params -= opt.learning_rate * vel

    return nothing
end

# =============================================================================
# AdaGrad Step
# =============================================================================

"""
    optimizer_step!(opt::AdaGradOptimizer, param_id::String,
                     params::Vector{Float32}, grads::Vector{Float32})

Applies one AdaGrad update step.
"""
function optimizer_step!(
    opt::AdaGradOptimizer,
    param_id::String,
    params::Vector{Float32},
    grads::Vector{Float32}
)
    @assert length(params) == length(grads)

    if !haskey(opt.sum_sq_grads, param_id)
        opt.sum_sq_grads[param_id] = zeros(Float32, length(params))
    end

    G = opt.sum_sq_grads[param_id]
    @. G += grads^2
    @. params -= opt.learning_rate * grads / (sqrt(G) + opt.epsilon)

    return nothing
end

# =============================================================================
# Gradient utilities
# =============================================================================

"""
    zero_grad!(grads::Dict{String, Vector{Float32}})

Zeros all gradient vectors in the dictionary.
"""
function zero_grad!(grads::Dict{String, Vector{Float32}})
    for (_, g) in grads
        fill!(g, 0.0f0)
    end
end

"""
    gradient_clipping!(grads::Dict{String, Vector{Float32}};
                        max_norm::Float32 = 1.0f0)

Clips gradients by global norm. If total gradient norm exceeds `max_norm`,
all gradients are scaled down proportionally.

# Returns
- Gradient norm before clipping (Float32)
"""
function gradient_clipping!(
    grads::Dict{String, Vector{Float32}};
    max_norm::Float32 = 1.0f0
) :: Float32

    # Compute global norm
    global_norm_sq = 0.0f0
    for (_, g) in grads
        global_norm_sq += sum(g .^ 2)
    end
    global_norm = sqrt(global_norm_sq)

    # Clip if necessary
    if global_norm > max_norm
        clip_coeff = max_norm / (global_norm + 1e-6f0)
        for (_, g) in grads
            g .*= clip_coeff
        end
    end

    return global_norm
end

# =============================================================================
# Learning Rate Schedules
# =============================================================================

"""
    cosine_annealing_lr(step::Int; max_lr::Float32, min_lr::Float32,
                         total_steps::Int) -> Float32

Cosine annealing learning rate schedule.
lr = min_lr + 0.5 * (max_lr - min_lr) * (1 + cos(π * step / total_steps))
"""
function cosine_annealing_lr(
    step::Int;
    max_lr::Float32    = 3e-4f0,
    min_lr::Float32    = 1e-6f0,
    total_steps::Int   = 10_000
) :: Float32

    if step >= total_steps
        return min_lr
    end
    progress = Float32(step) / Float32(total_steps)
    return min_lr + 0.5f0 * (max_lr - min_lr) * (1.0f0 + cos(Float32(π) * progress))
end

"""
    warmup_schedule(step::Int; warmup_steps::Int, base_lr::Float32) -> Float32

Linear warmup learning rate schedule.
LR increases linearly from 0 to base_lr over `warmup_steps` steps.
"""
function warmup_schedule(
    step::Int;
    warmup_steps::Int = 1000,
    base_lr::Float32  = 3e-4f0
) :: Float32

    if step >= warmup_steps
        return base_lr
    end
    return base_lr * (Float32(step) / Float32(warmup_steps))
end

"""
    polynomial_decay(step::Int; initial_lr::Float32, end_lr::Float32,
                      total_steps::Int, power::Float32 = 1.0f0) -> Float32

Polynomial learning rate decay.
"""
function polynomial_decay(
    step::Int;
    initial_lr::Float32 = 3e-4f0,
    end_lr::Float32     = 1e-7f0,
    total_steps::Int    = 50_000,
    power::Float32      = 1.0f0
) :: Float32

    if step >= total_steps
        return end_lr
    end
    decay = (1.0f0 - Float32(step) / Float32(total_steps)) ^ power
    return (initial_lr - end_lr) * decay + end_lr
end

# =============================================================================
# Gradient Checking (for testing/validation)
# =============================================================================

"""
    numerical_gradient(f, params::Vector{Float32}; epsilon::Float32 = 1e-4f0)
                      -> Vector{Float32}

Computes numerical gradient of scalar function `f` at `params`
using central differences: ∂f/∂xᵢ ≈ (f(x + ε) - f(x - ε)) / (2ε)

# Arguments
- `f`:       Function mapping Vector{Float32} → Float32
- `params`:  Point at which to compute gradient
- `epsilon`: Step size for finite differences

# Returns
- Numerical gradient vector of same shape as `params`
"""
function numerical_gradient(
    f::Function,
    params::Vector{Float32};
    epsilon::Float32 = 1e-4f0
) :: Vector{Float32}

    grad = similar(params)
    p_plus  = copy(params)
    p_minus = copy(params)

    for i in eachindex(params)
        p_plus[i]  = params[i] + epsilon
        p_minus[i] = params[i] - epsilon

        f_plus  = f(p_plus)
        f_minus = f(p_minus)

        grad[i] = (f_plus - f_minus) / (2.0f0 * epsilon)

        # Reset
        p_plus[i]  = params[i]
        p_minus[i] = params[i]
    end

    return grad
end

"""
    gradient_check(analytic_grad::Vector{Float32}, numerical_grad::Vector{Float32};
                    atol::Float32 = 1e-3f0) -> Bool

Checks whether analytic and numerical gradients agree within tolerance.
Returns true if max absolute difference is within `atol`.
"""
function gradient_check(
    analytic_grad::Vector{Float32},
    numerical_grad::Vector{Float32};
    atol::Float32 = 1e-3f0
) :: Bool

    @assert length(analytic_grad) == length(numerical_grad)
    diff = maximum(abs.(analytic_grad .- numerical_grad))
    norm_diff = diff / (maximum(abs.(analytic_grad)) + maximum(abs.(numerical_grad)) + 1e-8f0)
    return norm_diff < atol
end

# =============================================================================
# Tests
# =============================================================================

function run_optimizer_tests()
    using Test

    @testset "NumericalOptimizer" begin

        @testset "AdamOptimizer" begin
            opt = AdamOptimizer(learning_rate=0.01f0)
            params = [1.0f0, 2.0f0, 3.0f0]
            grads  = [0.1f0, 0.2f0, 0.3f0]
            params_before = copy(params)
            optimizer_step!(opt, "test", params, grads)
            # Parameters should have decreased
            @test all(params .< params_before)
            @test opt.step == 1
        end

        @testset "SGDOptimizer" begin
            opt = SGDOptimizer(learning_rate=0.1f0, momentum=0.9f0)
            params = [1.0f0, 1.0f0]
            grads  = [0.5f0, 0.5f0]
            params_before = copy(params)
            optimizer_step!(opt, "test", params, grads)
            @test all(params .< params_before)
        end

        @testset "gradient_clipping" begin
            grads = Dict("w1" => [10.0f0, 10.0f0], "w2" => [10.0f0])
            norm_before = gradient_clipping!(grads, max_norm=1.0f0)
            @test norm_before > 1.0f0
            total_norm = sqrt(sum([sum(g.^2) for g in values(grads)]))
            @test isapprox(total_norm, 1.0f0, atol=1e-4)
        end

        @testset "cosine_annealing_lr" begin
            lr_start = cosine_annealing_lr(0,    max_lr=0.01f0, min_lr=1e-6f0, total_steps=1000)
            lr_mid   = cosine_annealing_lr(500,  max_lr=0.01f0, min_lr=1e-6f0, total_steps=1000)
            lr_end   = cosine_annealing_lr(1000, max_lr=0.01f0, min_lr=1e-6f0, total_steps=1000)
            @test lr_start ≈ 0.01f0 atol=1e-5
            @test lr_end   ≈ 1e-6f0 atol=1e-6
            @test lr_mid   > lr_end
        end

        @testset "numerical_gradient" begin
            # f(x) = x[1]^2 + 2*x[2]^2 → grad = [2*x[1], 4*x[2]]
            f = x -> x[1]^2 + 2.0f0 * x[2]^2
            params = [3.0f0, 2.0f0]
            num_grad = numerical_gradient(f, params)
            @test isapprox(num_grad[1], 6.0f0, atol=1e-3)
            @test isapprox(num_grad[2], 8.0f0, atol=1e-3)
        end

        @testset "gradient_check" begin
            analytic = [6.0f0, 8.0f0]
            numerical = [6.001f0, 7.999f0]
            @test gradient_check(analytic, numerical, atol=0.01f0)
        end

    end

    @info "NumericalOptimizer tests completed"
end

end # module NumericalOptimizer
