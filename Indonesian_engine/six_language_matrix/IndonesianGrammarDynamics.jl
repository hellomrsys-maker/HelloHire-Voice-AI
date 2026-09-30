# Indonesian Engine — Julia Grammar Dynamics
# Mathematical modeling of Indonesian agglutinative affixation entropy and reduplication dynamics.

module IndonesianGrammarDynamics

export compute_affix_entropy, model_nasal_assimilation_probability

"""
Compute Shannon entropy of derivational affix chains in Indonesian clauses.
"""
function compute_affix_entropy(affix_counts::Vector{Int})::Float64
    total = sum(affix_counts)
    if total == 0
        return 0.0
    end
    entropy = 0.0
    for c in affix_counts
        if c > 0
            p = c / total
            entropy -= p * log2(p)
        end
    end
    return entropy
end

"""
Model morphophonemic nasal assimilation probability for root-initial voiceless stops (p, t, s, k).
"""
function model_nasal_assimilation_probability(is_voiceless_stop::Bool, is_loanword::Bool)::Float64
    if is_voiceless_stop && !is_loanword
        return 1.0 # Mandatory deletion (e.g. tulis -> menulis)
    elseif is_loanword
        return 0.15 # Frequently retained in loans (e.g. proses -> memproses)
    else
        return 0.0
    end
end

end # module
