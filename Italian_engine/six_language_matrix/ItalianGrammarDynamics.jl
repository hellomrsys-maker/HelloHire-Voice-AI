# Italian Engine — Julia Grammar Dynamics
# Mathematical modeling of Italian syllable-timed rhythm and raddoppiamento fonosintattico.

module ItalianGrammarDynamics

export compute_npvi, model_raddoppiamento

"""
Compute normalized Pairwise Variability Index (nPVI) for Italian vocalic durations.
Italian is characteristically syllable-timed with moderate vocalic nPVI (approx 40-50).
"""
function compute_npvi(durations::Vector{Float64})::Float64
    m = length(durations)
    if m < 2
        return 0.0
    end
    sum_diff = 0.0
    for k in 1:(m - 1)
        d_k = durations[k]
        d_next = durations[k + 1]
        sum_diff += abs(d_k - d_next) / ((d_k + d_next) / 2.0)
    end
    return (100.0 / (m - 1)) * sum_diff
end

"""
Model consonant lengthening probability under Raddoppiamento Fonosintattico (RF).
"""
function model_raddoppiamento(stress_tonic::Bool, is_monosyllable::Bool)::Float64
    if stress_tonic && is_monosyllable
        return 0.98
    elseif stress_tonic
        return 0.85
    else
        return 0.05
    end
end

end # module
