# Portuguese Grammar Dynamics (Julia High-Performance Computing)
# Models nasal formant resonance (/ɐ̃/, /ẽ/, /õ/) and stress-timed vs syllable-timed rhythm transitions.

module PortugueseGrammarDynamics

export PortugueseDynamicState, simulate_nasal_coupling, compute_rhythm_ratio

struct PortugueseDynamicState
    nasal_coupling_factor::Float64   # [0.0, 1.0]
    stress_timing_ratio::Float64     # 0.0 (syllable-timed pt-BR) to 1.0 (stress-timed pt-PT)
    clitic_stability::Float64        # [0.0, 1.0]
end

"""
Simulates velopharyngeal port opening dynamics during nasal vowel articulation.
"""
function simulate_nasal_coupling(base_airflow::Float64, is_nasal_vowel::Bool)::Float64
    if is_nasal_vowel
        return min(1.0, base_airflow * 1.85)
    else
        return base_airflow * 0.15
    end
end

"""
Computes normalized pairwise variability index (nPVI) distinguishing pt-BR from pt-PT.
"""
function compute_rhythm_ratio(durations::Vector{Float64})::Float64
    m = length(durations)
    if m < 2
        return 0.5
    end
    total = 0.0
    for k in 1:(m - 1)
        dk = durations[k]
        dk1 = durations[k + 1]
        total += abs(dk - dk1) / ((dk + dk1) / 2.0)
    end
    return (100.0 / (m - 1)) * total
end

end # module
