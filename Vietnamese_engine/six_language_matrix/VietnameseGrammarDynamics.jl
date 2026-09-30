# Vietnamese Grammar Dynamics (Julia 1.10+)
# Mathematical and statistical simulation of 6-tone pitch dynamics,
# isolating SVO information entropy, and classifier distribution models.

module VietnameseGrammarDynamics

export ToneContourState, simulate_pitch_trajectory, calculate_tonal_entropy

struct ToneContourState
    tone_id::Int
    pitch_start::Float64
    pitch_mid::Float64
    pitch_end::Float64
end

"""
Simulates F0 fundamental frequency pitch trajectories for Hanoi 6 tones.
"""
function simulate_pitch_trajectory(tone_id::Int, steps::Int=50)::Vector{Float64}
    trajectory = zeros(Float64, steps)
    t = range(0.0, 1.0, length=steps)
    
    if tone_id == 1      # Ngang (Level 33)
        trajectory .= 220.0
    elseif tone_id == 2  # Huyền (Falling 21)
        trajectory .= 210.0 .- 30.0 .* t
    elseif tone_id == 3  # Sắc (Rising 35)
        trajectory .= 220.0 .+ 60.0 .* (t .^ 1.5)
    elseif tone_id == 4  # Hỏi (Dipping 312)
        trajectory .= 215.0 .- 50.0 .* sin.(π .* t ./ 1.5) .+ 20.0 .* (t .^ 2)
    elseif tone_id == 5  # Ngã (Glottalized broken 3ʔ5)
        mid = div(steps, 2)
        trajectory[1:mid] .= 220.0 .+ 10.0 .* t[1:mid]
        trajectory[mid+1:end] .= 240.0 .+ 50.0 .* t[mid+1:end]
    elseif tone_id == 6  # Nặng (Dropping constricted 21ʔ)
        trajectory .= 200.0 .- 50.0 .* (t .^ 2)
    end
    
    return trajectory
end

"""
Calculates the Shannon information entropy of tone distribution.
"""
function calculate_tonal_entropy(probabilities::Vector{Float64})::Float64
    entropy = 0.0
    for p in probabilities
        if p > 0.0
            entropy -= p * log2(p)
        end
    end
    return entropy
end

end # module
