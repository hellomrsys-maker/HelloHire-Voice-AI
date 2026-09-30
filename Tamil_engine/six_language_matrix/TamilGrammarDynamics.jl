# Tamil Grammar Dynamics - Julia Language
# Models agglutinative case-stacking lattices and sandhi plosive doubling probability fields.

module TamilGrammarDynamics

export simulate_case_stacking_transitions, evaluate_sandhi_energy

const CASE_LATTICE_WEIGHTS = Dict(
    :nominative => 1.0,
    :accusative => 0.95,
    :instrumental => 0.88,
    :sociative => 0.85,
    :dative => 0.92,
    :ablative => 0.80,
    :genitive => 0.90,
    :locative => 0.89,
    :vocative => 0.75
)

function simulate_case_stacking_transitions(stem_energy::Float64, case_sym::Symbol)::Float64
    weight = get(CASE_LATTICE_WEIGHTS, case_sym, 0.5)
    return stem_energy * weight
end

function evaluate_sandhi_energy(w1_coda::Symbol, w2_onset::Symbol)::Float64
    # Check if accusative/dative triggers plosive doubling (k, c, t, p)
    if w1_coda in [:accusative_ai, :dative_ku] && w2_onset in [:k, :c, :t, :p]
        return 1.0  # High energy requiring gemination
    else
        return 0.1  # Neutral energy
    end
end

end # module
