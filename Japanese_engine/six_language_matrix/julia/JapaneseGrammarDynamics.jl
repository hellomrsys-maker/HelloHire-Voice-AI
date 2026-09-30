"""
JapaneseGrammarDynamics.jl
Continuous-time mathematical modeling of Japanese pitch accent contours,
mora timing stability, and lexical distribution entropy.
"""
module JapaneseGrammarDynamics

export simulate_pitch_trajectory, compute_shannon_entropy, ParticleDiffusionModel

struct ParticleDiffusionModel
    alpha::Float64
    beta::Float64
    decay_rate::Float64
end

"""
Simulates continuous F0 fundamental frequency trajectory over N morae.
"""
function simulate_pitch_trajectory(base_f0::Float64, accent_kernel::Int, num_morae::Int; dt::Float64 = 0.01)
    time_steps = Int(round((num_morae * 0.13) / dt))
    t = range(0.0, stop=num_morae * 0.13, length=time_steps)
    f0 = zeros(Float64, time_steps)

    for (idx, time) in enumerate(t)
        mora_idx = Int(floor(time / 0.13)) + 1
        if mora_idx == 1
            f0[idx] = (accent_kernel == 1) ? base_f0 * 1.35 : base_f0 * 0.95
        elseif mora_idx <= accent_kernel || accent_kernel == 0
            f0[idx] = base_f0 * 1.25
        else
            f0[idx] = base_f0 * 0.90
        end
    end

    return collect(t), f0
end

"""
Calculates Shannon information entropy of Japanese morpheme distributions.
"""
function compute_shannon_entropy(probabilities::Vector{Float64})
    p_norm = probabilities ./ sum(probabilities)
    ent = 0.0
    for p in p_norm
        if p > 1e-9
            ent -= p * log2(p)
        end
    end
    return ent
end

end # module
