# =============================================================================
# engine/julia/src/EngineCore.jl
# Julia mathematical kernels, numerical optimization, and differentiable
# programming for the Verbal Communication Engine.
#
# Role in the 6-language system:
#   - Mathematical kernels for attention scoring, embedding arithmetic
#   - Differentiable programming for gradient-based optimization
#   - Numerical simulation of cognitive processes (attention decay, memory salience)
#   - Statistical analysis of language distributions
# =============================================================================

module EngineCore

using LinearAlgebra
using Statistics
using Random
using Logging

# Sub-modules
include("AttentionMath.jl")
include("EmbeddingOps.jl")
include("NumericalOptimizer.jl")
include("CognitiveSim.jl")
include("EngineFFI.jl")

export AttentionMath, EmbeddingOps, NumericalOptimizer, CognitiveSim

"""
    initialize_engine_julia(; seed::Int = 42, log_level = Logging.Info)

Initializes the Julia engine module. Sets the global RNG seed and configures
logging. Must be called before any other function in this module.
"""
function initialize_engine_julia(; seed::Int = 42, log_level = Logging.Info)
    Random.seed!(seed)
    global_logger(ConsoleLogger(stderr, log_level))
    @info "EngineCore Julia module initialized" seed=seed
    return nothing
end

end # module EngineCore
