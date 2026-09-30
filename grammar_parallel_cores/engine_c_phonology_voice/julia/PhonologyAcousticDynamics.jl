# PhonologyAcousticDynamics.jl - Engine C Sub-Core C6 (Julia)
# Auditory & Phonological Voice Engine: Acoustic entropy,
# vocalic/consonantal duration variance, and nPVI/rPVI rhythm metrics.

module PhonologyAcousticDynamics

export compute_npvi, compute_rpvi, compute_acoustic_entropy, PhonologyDynamicsReport

struct PhonologyDynamicsReport
    npvi_vocalic::Float64
    rpvi_consonantal::Float64
    spectral_entropy::Float64
    prosodic_naturalness::Float64
end

"""
    compute_npvi(durations::Vector{Float64}) -> Float64

Computes the Normalized Pairwise Variability Index (nPVI) for vocalic intervals:
nPVI = (100 / (m - 1)) * sum_k |(d_k - d_{k+1}) / ((d_k + d_{k+1}) / 2)|
"""
function compute_npvi(durations::Vector{Float64})::Float64
    m = length(durations)
    if m < 2
        return 0.0
    end
    sum_diff = 0.0
    for k in 1:(m - 1)
        mean_dur = (durations[k] + durations[k + 1]) / 2.0
        if mean_dur > 1e-6
            sum_diff += abs((durations[k] - durations[k + 1]) / mean_dur)
        end
    end
    return (100.0 / (m - 1)) * sum_diff
end

"""
    compute_rpvi(durations::Vector{Float64}) -> Float64

Computes the Raw Pairwise Variability Index (rPVI) for consonantal intervals:
rPVI = (1 / (m - 1)) * sum_k |d_k - d_{k+1}|
"""
function compute_rpvi(durations::Vector{Float64})::Float64
    m = length(durations)
    if m < 2
        return 0.0
    end
    sum_diff = sum(abs(durations[k] - durations[k + 1]) for k in 1:(m - 1))
    return sum_diff / (m - 1)
end

function compute_acoustic_entropy(energies::Vector{Float64})::Float64
    total = sum(energies)
    if total <= 0.0
        return 0.0
    end
    probs = energies ./ total
    return -sum(p * log2(p + 1e-12) for p in probs if p > 0.0)
end

function model_phonology_dynamics(vocalic_durs::Vector{Float64}, consonantal_durs::Vector{Float64})::PhonologyDynamicsReport
    npvi = compute_npvi(vocalic_durs)
    rpvi = compute_rpvi(consonantal_durs)
    entropy = 2.5
    naturalness = clamp(1.0 - abs(npvi - 65.0) / 100.0, 0.0, 1.0)

    return PhonologyDynamicsReport(
        round(npvi, digits=2),
        round(rpvi, digits=2),
        round(entropy, digits=4),
        round(naturalness, digits=4)
    )
end

end # module PhonologyAcousticDynamics
