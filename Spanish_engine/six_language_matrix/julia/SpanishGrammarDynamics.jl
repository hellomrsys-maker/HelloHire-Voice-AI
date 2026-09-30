"""
SpanishGrammarDynamics.jl
Continuous-time mathematical modeling of Spanish syllable-timed rhythm,
pitch accent trajectories, and morphosyntactic distribution entropy.
"""
module SpanishGrammarDynamics

export simulate_stress_trajectory, compute_lexical_entropy, SyllableTimingModel

struct SyllableTimingModel
    mean_syllable_duration::Float64 # Typically ~180-220ms in Spanish
    stress_boost::Float64
end

"""
Simulates continuous F0 fundamental frequency trajectory over N syllables.
Models Spanish syllable-timed rhythm with pitch peaks on tonic syllables.
"""
function simulate_stress_trajectory(base_f0::Float64, tonic_syllable_index::Int, num_syllables::Int; dt::Float64 = 0.01)
    syllable_dur = 0.18
    total_time = max(0.18, num_syllables * syllable_dur)
    time_steps = max(5, Int(round(total_time / dt)))
    t = range(0.0, stop=total_time, length=time_steps)
    f0 = zeros(Float64, time_steps)

    for (idx, time) in enumerate(t)
        curr_syllable = Int(floor(time / syllable_dur)) + 1
        # Syllable declination with tonic stress peak
        declination = 1.0 - (0.15 * (time / total_time))
        if curr_syllable == tonic_syllable_index
            f0[idx] = base_f0 * declination * 1.30
        else
            f0[idx] = base_f0 * declination
        end
    end

    return collect(t), f0
end

"""
Calculates Shannon information entropy of Spanish lexical distributions.
"""
function compute_lexical_entropy(probabilities::Vector{Float64})
    total = sum(probabilities)
    if total <= 0.0
        return 0.0
    end
    p_norm = probabilities ./ total
    ent = 0.0
    for p in p_norm
        if p > 1e-9
            ent -= p * log2(p)
        end
    end
    return ent
end

end # module
