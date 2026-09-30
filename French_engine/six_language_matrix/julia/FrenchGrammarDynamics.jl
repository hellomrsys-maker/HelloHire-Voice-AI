# French Grammar Dynamics & Nasal Vowel Acoustic Modeling
# High-precision numerical computing in Julia

module FrenchGrammarDynamics

export simulate_nasal_formants, calculate_syllable_timing_entropy

"""
Simulates F1/F2 acoustic formant centers (Hz) and nasal bandwidth broadening
for the four historical French nasal vowels: /ɑ̃/, /ɛ̃/, /ɔ̃/, /œ̃/.
"""
function simulate_nasal_formants(vowel::String)
    v = lowercase(vowel)
    if v in ["an", "am", "en", "em", "ɑ̃"]
        return (F1 = 570.0, F2 = 1150.0, nasal_bandwidth_hz = 180.0)
    elseif v in ["in", "im", "ain", "aim", "ein", "ɛ̃"]
        return (F1 = 530.0, F2 = 1680.0, nasal_bandwidth_hz = 210.0)
    elseif v in ["on", "om", "ɔ̃"]
        return (F1 = 490.0, F2 = 980.0, nasal_bandwidth_hz = 195.0)
    elseif v in ["un", "um", "œ̃"]
        return (F1 = 510.0, F2 = 1380.0, nasal_bandwidth_hz = 200.0)
    else
        return (F1 = 500.0, F2 = 1500.0, nasal_bandwidth_hz = 100.0)
    end
end

"""
Calculates Shannon information entropy of syllable durations across a rhythmic cadence.
French is syllable-timed with phrase-final lengthening.
"""
function calculate_syllable_timing_entropy(durations::Vector{Float64})
    total = sum(durations)
    if total <= 0.0
        return 0.0
    end
    probs = durations ./ total
    entropy = -sum(p > 0.0 ? p * log2(p) : 0.0 for p in probs)
    return entropy
end

end # module
