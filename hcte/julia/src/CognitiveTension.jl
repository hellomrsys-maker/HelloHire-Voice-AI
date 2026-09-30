"""
CognitiveTension.jl — Dynamic Multi-Persona Cognitive Tension Modeling (HCTE Julia Layer)

Simulates the non-linear interaction and consensus convergence among
optimistic, pessimistic, systems, and pre-mortem cognitive agents:
  dP_i/dt = sum_j K_ij * (P_j - P_i) + Ext_drive
"""

module CognitiveTension

export CognitiveState, step_cognitive_consensus

struct CognitiveState
    gci::Float64
    tension::Float64
    premortem_impact::Float64
end

function step_cognitive_consensus(
    personas::Vector{Float64},
    dt::Float64 = 0.05,
    coupling::Float64 = 0.2
)::CognitiveState
    n = length(personas)
    mean_val = sum(personas) / n
    diffs = personas .- mean_val
    tension = sqrt(sum(diffs .^ 2) / n)

    # Pre-mortem analyst index is 5 (1-based Julia indexing)
    premortem = n >= 5 ? personas[5] : mean_val

    # Weighted GCI with 2x pre-mortem
    weights = ones(n)
    if n >= 5
        weights[5] = 2.0
    end
    weighted_gci = sum(personas .* weights) / sum(weights)

    return CognitiveState(weighted_gci, tension, premortem)
end

end # module
