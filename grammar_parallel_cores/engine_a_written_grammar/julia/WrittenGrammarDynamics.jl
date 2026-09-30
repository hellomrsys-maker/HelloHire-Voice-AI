# WrittenGrammarDynamics.jl - Engine A Sub-Core A6 (Julia)
# Written Grammar & Discourse Engine: Mathematical linguistics,
# diachronic syntactic drift differential models, and clausal entropy calculus.

module WrittenGrammarDynamics

export compute_syntactic_entropy, model_diachronic_drift, WrittenGrammarDynamicsReport

struct WrittenGrammarDynamicsReport
    token_entropy::Float64
    clause_branching_ratio::Float64
    diachronic_drift_velocity::Float64
    register_stability::Float64
end

"""
    compute_syntactic_entropy(word_frequencies::Vector{Float64}) -> Float64

Computes Shannon entropy over syntactic token frequency distributions.
"""
function compute_syntactic_entropy(freqs::Vector{Float64})::Float64
    total = sum(freqs)
    if total <= 0.0
        return 0.0
    end
    probs = freqs ./ total
    entropy = -sum(p * log2(p + 1e-12) for p in probs if p > 0.0)
    return max(0.0, entropy)
end

"""
    model_diachronic_drift(syntax_depth::Float64, archaic_tokens::Int, modern_tokens::Int) -> WrittenGrammarDynamicsReport

Models diachronic syntactic drift using a logistic drift trajectory.
"""
function model_diachronic_drift(syntax_depth::Float64, archaic_tokens::Int, modern_tokens::Int)::WrittenGrammarDynamicsReport
    total_tokens = max(1, archaic_tokens + modern_tokens)
    archaic_ratio = archaic_tokens / total_tokens

    # Syntactic entropy estimate
    entropy = 1.4427 * log(1.0 + syntax_depth)

    # Drift velocity: rate of transition from synthetic to analytic syntax
    drift_velocity = 0.05 * (1.0 - archaic_ratio) * syntax_depth

    # Register stability: high when syntax depth matches modern/archaic consistency
    register_stability = clamp(1.0 - abs(archaic_ratio - 0.2), 0.0, 1.0)

    return WrittenGrammarDynamicsReport(
        round(entropy, digits=4),
        round(syntax_depth / 5.0, digits=4),
        round(drift_velocity, digits=4),
        round(register_stability, digits=4)
    )
end

end # module WrittenGrammarDynamics
