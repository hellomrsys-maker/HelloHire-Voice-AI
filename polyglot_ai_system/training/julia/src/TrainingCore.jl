# =============================================================================
# training/julia/src/TrainingCore.jl
# Julia mathematical training kernels:
#   - Loss function implementations
#   - Gradient verification
#   - Numerical optimization for training
#   - Cognitive simulation metrics
# =============================================================================

module TrainingCore

using LinearAlgebra
using Statistics
using Random

include("LossFunctions.jl")
include("TrainingOptimizer.jl")
include("CognitiveBenchmarks.jl")
include("TrainingFFI.jl")

export LossFunctions, TrainingOptimizer, CognitiveBenchmarks, TrainingFFI

"""
    initialize_training_julia(; seed::Int = 42)

Initializes the Julia training module.
"""
function initialize_training_julia(; seed::Int = 42)
    Random.seed!(seed)
    @info "TrainingCore Julia module initialized" seed=seed
    return nothing
end

end # module TrainingCore
