# TrainingOptimizer.jl
# Advanced optimizer implementations for the AI training system.
# Covers: AdamW, Lion, Sophia, Muon, learning rate schedules, gradient clipping,
# and parameter group management. All implementations are differentiable and
# compatible with Zygote automatic differentiation.

module TrainingOptimizer

using LinearAlgebra
using Statistics
using Printf
using Logging

export AdamWOptimizer, LionOptimizer, SophiaOptimizer, MuonOptimizer
export CosineAnnealingSchedule, WarmupCosineSchedule, OneCycleSchedule
export OptimizerState, step!, zero_grad!, get_lr
export GradientClipper, clip_gradients!
export ParameterGroup, OptimizerConfig

# ─────────────────────────────────────────────────────────────────────────────
# Optimizer state container
# ─────────────────────────────────────────────────────────────────────────────

"""
Mutable state for a single parameter tensor.
Stores first moment (m), second moment (v), and step count.
"""
mutable struct OptimizerState
    m::Array{Float32}          # first moment (momentum)
    v::Array{Float32}          # second moment (variance / curvature)
    step::Int                  # step counter for bias correction
    extra::Dict{Symbol,Any}    # algorithm-specific extra state
end

function OptimizerState(shape::NTuple)
    OptimizerState(
        zeros(Float32, shape),
        zeros(Float32, shape),
        0,
        Dict{Symbol,Any}()
    )
end

# ─────────────────────────────────────────────────────────────────────────────
# Parameter group
# ─────────────────────────────────────────────────────────────────────────────

"""
Group of parameters sharing optimizer hyperparameters.
Allows per-layer or per-block learning rate scaling.
"""
struct ParameterGroup
    name::String
    params::Vector{Array{Float32}}
    lr_scale::Float32
    weight_decay::Float32
end

function ParameterGroup(name::String, params; lr_scale=1.0f0, weight_decay=0.01f0)
    ParameterGroup(name, params, Float32(lr_scale), Float32(weight_decay))
end

# ─────────────────────────────────────────────────────────────────────────────
# Optimizer config
# ─────────────────────────────────────────────────────────────────────────────

struct OptimizerConfig
    lr::Float32
    weight_decay::Float32
    gradient_clip_norm::Float32
    warmup_steps::Int
    total_steps::Int
end

function OptimizerConfig(;
    lr=1e-4f0,
    weight_decay=0.01f0,
    gradient_clip_norm=1.0f0,
    warmup_steps=1000,
    total_steps=100_000
)
    OptimizerConfig(Float32(lr), Float32(weight_decay), Float32(gradient_clip_norm),
                    warmup_steps, total_steps)
end

# ─────────────────────────────────────────────────────────────────────────────
# AdamW Optimizer
# ─────────────────────────────────────────────────────────────────────────────

"""
AdamW optimizer (Adam with decoupled weight decay, Loshchilov & Hutter 2017).
Implements the standard update rule:
  m  = β₁·m + (1-β₁)·g
  v  = β₂·v + (1-β₂)·g²
  m̂  = m / (1 - β₁ᵗ)
  v̂  = v / (1 - β₂ᵗ)
  θ  = θ - α·(m̂/(√v̂+ε)) - α·λ·θ
"""
mutable struct AdamWOptimizer
    lr::Float32
    beta1::Float32
    beta2::Float32
    epsilon::Float32
    weight_decay::Float32
    states::Dict{UInt64, OptimizerState}
    global_step::Int
end

function AdamWOptimizer(;
    lr=1e-4f0,
    beta1=0.9f0,
    beta2=0.999f0,
    epsilon=1e-8f0,
    weight_decay=0.01f0
)
    AdamWOptimizer(
        Float32(lr), Float32(beta1), Float32(beta2), Float32(epsilon),
        Float32(weight_decay), Dict{UInt64,OptimizerState}(), 0
    )
end

"""
Perform one AdamW update step for parameter `param` given gradient `grad`.
"""
function step!(opt::AdamWOptimizer, param::Array{Float32}, grad::Array{Float32})
    @assert size(param) == size(grad) "Parameter and gradient must have the same shape"

    key = objectid(param)
    if !haskey(opt.states, key)
        opt.states[key] = OptimizerState(size(param))
    end
    state = opt.states[key]
    state.step += 1
    t = state.step

    β1, β2 = opt.beta1, opt.beta2
    ε = opt.epsilon
    lr = opt.lr
    λ = opt.weight_decay

    # Update biased first and second moment estimates
    @. state.m = β1 * state.m + (1.0f0 - β1) * grad
    @. state.v = β2 * state.v + (1.0f0 - β2) * grad^2

    # Bias-corrected estimates
    bias_correction1 = 1.0f0 - β1^t
    bias_correction2 = 1.0f0 - β2^t
    step_size = lr / bias_correction1

    @. param -= step_size * state.m / (sqrt(state.v / bias_correction2) + ε)
    # Decoupled weight decay
    @. param -= lr * λ * param
end

function zero_grad!(opt::AdamWOptimizer)
    opt.global_step += 1
end

function get_lr(opt::AdamWOptimizer)::Float32
    return opt.lr
end

# ─────────────────────────────────────────────────────────────────────────────
# Lion Optimizer (EvoLved Sign Momentum, Chen et al. 2023)
# ─────────────────────────────────────────────────────────────────────────────

"""
Lion optimizer: update direction is sign of (β₁·m + (1-β₁)·g),
weight decay applied decoupled from gradient.
  c  = sign(β₁·m + (1-β₁)·g)
  θ  = θ - α·(c + λ·θ)
  m  = β₂·m + (1-β₂)·g
"""
mutable struct LionOptimizer
    lr::Float32
    beta1::Float32
    beta2::Float32
    weight_decay::Float32
    states::Dict{UInt64, OptimizerState}
    global_step::Int
end

function LionOptimizer(;
    lr=1e-4f0,
    beta1=0.9f0,
    beta2=0.99f0,
    weight_decay=0.0f0
)
    LionOptimizer(
        Float32(lr), Float32(beta1), Float32(beta2), Float32(weight_decay),
        Dict{UInt64,OptimizerState}(), 0
    )
end

function step!(opt::LionOptimizer, param::Array{Float32}, grad::Array{Float32})
    key = objectid(param)
    if !haskey(opt.states, key)
        opt.states[key] = OptimizerState(size(param))
    end
    state = opt.states[key]
    state.step += 1

    β1, β2 = opt.beta1, opt.beta2
    lr = opt.lr
    λ = opt.weight_decay

    # Compute update direction: sign(β₁·m + (1-β₁)·g)
    update = @. sign(β1 * state.m + (1.0f0 - β1) * grad)

    # Update parameter with weight decay
    @. param -= lr * (update + λ * param)

    # Update momentum with β₂ (not bias-corrected for Lion)
    @. state.m = β2 * state.m + (1.0f0 - β2) * grad
end

function get_lr(opt::LionOptimizer)::Float32 = opt.lr

# ─────────────────────────────────────────────────────────────────────────────
# Sophia Optimizer (Liu et al. 2023 — second-order clipped)
# ─────────────────────────────────────────────────────────────────────────────

"""
Sophia: second-order optimizer using diagonal Hessian estimates.
  h  = β₂·h + (1-β₂)·ĥ      (diagonal Hessian EMA, estimated via Hutchinson or Gauss-Newton)
  m  = β₁·m + (1-β₁)·g
  θ  = θ - lr·clip(m/max(γh,ε), ρ)
where ĥ is a stochastic Hessian diagonal estimate.
"""
mutable struct SophiaOptimizer
    lr::Float32
    beta1::Float32
    beta2::Float32
    rho::Float32           # clipping threshold
    gamma::Float32         # Hessian scaling factor
    epsilon::Float32
    weight_decay::Float32
    hessian_update_freq::Int  # steps between Hessian re-estimates
    states::Dict{UInt64, OptimizerState}
    global_step::Int
end

function SophiaOptimizer(;
    lr=1e-4f0,
    beta1=0.965f0,
    beta2=0.99f0,
    rho=0.04f0,
    gamma=0.01f0,
    epsilon=1e-12f0,
    weight_decay=0.1f0,
    hessian_update_freq=10
)
    SophiaOptimizer(
        Float32(lr), Float32(beta1), Float32(beta2), Float32(rho), Float32(gamma),
        Float32(epsilon), Float32(weight_decay), hessian_update_freq,
        Dict{UInt64,OptimizerState}(), 0
    )
end

"""
Update Sophia state with a Hutchinson diagonal Hessian estimate.
`hvp` is a Hessian-vector product: H @ u where u ~ N(0,I).
"""
function update_hessian!(opt::SophiaOptimizer, param::Array{Float32}, hvp::Array{Float32})
    key = objectid(param)
    if !haskey(opt.states, key)
        opt.states[key] = OptimizerState(size(param))
    end
    state = opt.states[key]
    β2 = opt.beta2
    # h is stored in state.v
    @. state.v = β2 * state.v + (1.0f0 - β2) * hvp^2
end

function step!(opt::SophiaOptimizer, param::Array{Float32}, grad::Array{Float32})
    key = objectid(param)
    if !haskey(opt.states, key)
        opt.states[key] = OptimizerState(size(param))
    end
    state = opt.states[key]
    state.step += 1

    β1 = opt.beta1
    lr = opt.lr
    ρ = opt.rho
    γ = opt.gamma
    ε = opt.epsilon
    λ = opt.weight_decay

    # Update first moment
    @. state.m = β1 * state.m + (1.0f0 - β1) * grad

    # Compute clipped update: clip(m / max(γ·h, ε), ρ)
    denom = @. max(γ * state.v, ε)
    update = clamp.(state.m ./ denom, -ρ, ρ)

    # Parameter update with decoupled weight decay
    @. param -= lr * (update + λ * param)
end

function get_lr(opt::SophiaOptimizer)::Float32 = opt.lr

# ─────────────────────────────────────────────────────────────────────────────
# Muon Optimizer (Kosson et al. 2023 — momentum + orthogonalization)
# ─────────────────────────────────────────────────────────────────────────────

"""
Muon: momentum optimizer with Nesterov + approximate orthogonalization via Newton-Schulz.
Designed for weight matrices (2D params). Falls back to AdamW for vectors/scalars.
"""
mutable struct MuonOptimizer
    lr::Float32
    momentum::Float32
    nesterov::Bool
    ns_steps::Int          # Newton-Schulz iteration steps for orthogonalization
    weight_decay::Float32
    adam_fallback::AdamWOptimizer
    states::Dict{UInt64, Array{Float32}}   # momentum buffer per param
    global_step::Int
end

function MuonOptimizer(;
    lr=0.02f0,
    momentum=0.95f0,
    nesterov=true,
    ns_steps=5,
    weight_decay=0.0f0
)
    MuonOptimizer(
        Float32(lr), Float32(momentum), nesterov, ns_steps, Float32(weight_decay),
        AdamWOptimizer(lr=lr, weight_decay=weight_decay),
        Dict{UInt64,Array{Float32}}(), 0
    )
end

"""
Newton-Schulz iteration to orthogonalize a matrix G.
Converges to U·Vᵀ (the orthogonal factor of G's SVD) in ~5 steps.
  X_{k+1} = 1.5·X_k - 0.5·X_k·X_kᵀ·X_k
"""
function newton_schulz_orthogonalize!(G::Matrix{Float32}, steps::Int)::Matrix{Float32}
    # Normalize to prevent divergence
    norm_g = norm(G)
    if norm_g < 1e-8f0
        return G
    end
    X = G ./ norm_g
    for _ in 1:steps
        X = 1.5f0 .* X .- 0.5f0 .* (X * (X' * X))
    end
    X .* norm_g
end

function step!(opt::MuonOptimizer, param::Array{Float32}, grad::Array{Float32})
    # Fall back to AdamW for non-matrix params
    if ndims(param) < 2
        step!(opt.adam_fallback, param, grad)
        return
    end

    key = objectid(param)
    if !haskey(opt.states, key)
        opt.states[key] = zeros(Float32, size(param))
    end
    buf = opt.states[key]

    # Nesterov momentum
    @. buf = opt.momentum * buf + grad
    if opt.nesterov
        effective_grad = @. grad + opt.momentum * buf
    else
        effective_grad = buf
    end

    # Orthogonalize (reshape to 2D if necessary)
    rows, cols = size(param, 1), prod(size(param)[2:end])
    G2d = reshape(effective_grad, rows, cols)
    G_orth = newton_schulz_orthogonalize!(G2d, opt.ns_steps)
    update = reshape(G_orth, size(param))

    @. param -= opt.lr * (update + opt.weight_decay * param)
end

function get_lr(opt::MuonOptimizer)::Float32 = opt.lr

# ─────────────────────────────────────────────────────────────────────────────
# Learning rate schedules
# ─────────────────────────────────────────────────────────────────────────────

"""
Cosine annealing schedule with warm restarts (Loshchilov & Hutter 2016).
lr(t) = lr_min + 0.5*(lr_max-lr_min)*(1 + cos(π·t/T_max))
"""
struct CosineAnnealingSchedule
    lr_max::Float32
    lr_min::Float32
    T_max::Int
    T_mult::Int
end

function CosineAnnealingSchedule(lr_max; lr_min=0.0f0, T_max=10_000, T_mult=1)
    CosineAnnealingSchedule(Float32(lr_max), Float32(lr_min), T_max, T_mult)
end

function (sched::CosineAnnealingSchedule)(step::Int)::Float32
    t = step % sched.T_max
    sched.lr_min + 0.5f0 * (sched.lr_max - sched.lr_min) * (1.0f0 + cos(π * t / sched.T_max))
end

"""
Warmup + cosine decay schedule.
Linearly warm up for `warmup_steps`, then cosine decay to `lr_min`.
"""
struct WarmupCosineSchedule
    lr_max::Float32
    lr_min::Float32
    warmup_steps::Int
    total_steps::Int
end

function WarmupCosineSchedule(lr_max; lr_min=0.0f0, warmup_steps=1000, total_steps=100_000)
    WarmupCosineSchedule(Float32(lr_max), Float32(lr_min), warmup_steps, total_steps)
end

function (sched::WarmupCosineSchedule)(step::Int)::Float32
    if step < sched.warmup_steps
        # Linear warmup
        return sched.lr_max * Float32(step) / Float32(sched.warmup_steps)
    else
        # Cosine decay
        progress = Float32(step - sched.warmup_steps) /
                   Float32(max(sched.total_steps - sched.warmup_steps, 1))
        cosine = 0.5f0 * (1.0f0 + cos(π * progress))
        return sched.lr_min + (sched.lr_max - sched.lr_min) * cosine
    end
end

"""
1-cycle LR schedule (Smith & Touvron 2018): triangular warmup, cosine decay.
"""
struct OneCycleSchedule
    lr_max::Float32
    lr_min::Float32
    warmup_frac::Float32
    total_steps::Int
end

function OneCycleSchedule(lr_max; lr_min=nothing, warmup_frac=0.3f0, total_steps=100_000)
    lr_min_val = isnothing(lr_min) ? Float32(lr_max / 25.0f0) : Float32(lr_min)
    OneCycleSchedule(Float32(lr_max), lr_min_val, Float32(warmup_frac), total_steps)
end

function (sched::OneCycleSchedule)(step::Int)::Float32
    warmup_end = Int(floor(sched.warmup_frac * sched.total_steps))
    if step < warmup_end
        # Ascending phase
        return sched.lr_min + (sched.lr_max - sched.lr_min) * Float32(step) / Float32(warmup_end)
    else
        # Descending cosine phase
        progress = Float32(step - warmup_end) / Float32(max(sched.total_steps - warmup_end, 1))
        cosine = 0.5f0 * (1.0f0 + cos(π * progress))
        return sched.lr_min + (sched.lr_max - sched.lr_min) * cosine
    end
end

# ─────────────────────────────────────────────────────────────────────────────
# Gradient clipper
# ─────────────────────────────────────────────────────────────────────────────

"""
Gradient clipper supporting global L2 norm clipping and per-parameter clipping.
"""
struct GradientClipper
    max_norm::Float32
    clip_value::Union{Float32, Nothing}
end

function GradientClipper(max_norm; clip_value=nothing)
    GradientClipper(Float32(max_norm), isnothing(clip_value) ? nothing : Float32(clip_value))
end

"""
Clip gradients by global L2 norm (in-place, modifying all grad arrays).
Returns the pre-clip global norm.
"""
function clip_gradients!(clipper::GradientClipper, grads::Vector{Array{Float32}})::Float32
    # Compute global norm
    global_norm_sq = 0.0f0
    for g in grads
        global_norm_sq += sum(x -> x^2, g)
    end
    global_norm = sqrt(global_norm_sq)

    if global_norm > clipper.max_norm
        scale = clipper.max_norm / (global_norm + 1e-6f0)
        for g in grads
            @. g *= scale
        end
    end

    # Optional per-element value clipping
    if !isnothing(clipper.clip_value)
        for g in grads
            clamp!(g, -clipper.clip_value, clipper.clip_value)
        end
    end

    global_norm
end

end # module TrainingOptimizer
