"""
MandarinGrammarDynamics.jl
Continuous-time mathematical modeling of Mandarin lexical tone contours,
tone sandhi transition dynamics, and syllable distribution entropy.
"""
module MandarinGrammarDynamics

export simulate_tone_contour, compute_tone_entropy, ToneTransitionModel

struct ToneTransitionModel
    transition_matrix::Matrix{Float64}
    sandhi_threshold::Float64
end

"""
Simulates continuous F0 fundamental frequency trajectory for Mandarin tones (1 to 4 and neutral 0).
- Tone 1 (High Level, 55): steady ~ 1.30 * base_f0
- Tone 2 (Rising, 35): rising from 1.05 to 1.30 * base_f0
- Tone 3 (Dipping, 214): dips from 0.95 to 0.80 then rises to 1.15 * base_f0
- Tone 4 (Falling, 51): falls from 1.35 to 0.75 * base_f0
- Tone 0 (Neutral): short, intermediate ~ 1.00 * base_f0
"""
function simulate_tone_contour(base_f0::Float64, tone::Int, duration::Float64 = 0.25; dt::Float64 = 0.01)
    time_steps = max(5, Int(round(duration / dt)))
    t = range(0.0, stop=duration, length=time_steps)
    f0 = zeros(Float64, time_steps)

    for (idx, time) in enumerate(t)
        progress = time / duration
        if tone == 1
            f0[idx] = base_f0 * 1.30
        elseif tone == 2
            f0[idx] = base_f0 * (1.05 + 0.25 * progress)
        elseif tone == 3
            if progress < 0.5
                f0[idx] = base_f0 * (0.95 - 0.30 * (progress / 0.5))
            else
                f0[idx] = base_f0 * (0.80 + 0.35 * ((progress - 0.5) / 0.5))
            end
        elseif tone == 4
            f0[idx] = base_f0 * (1.35 - 0.60 * progress)
        else # neutral
            f0[idx] = base_f0 * (1.00 - 0.15 * progress)
        end
    end

    return collect(t), f0
end

"""
Calculates Shannon information entropy of Mandarin tone sequences.
"""
function compute_tone_entropy(tone_counts::Vector{Float64})
    total = sum(tone_counts)
    if total <= 0.0
        return 0.0
    end
    p_norm = tone_counts ./ total
    ent = 0.0
    for p in p_norm
        if p > 1e-9
            ent -= p * log2(p)
        end
    end
    return ent
end

end # module
