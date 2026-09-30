"""
CognitiveMath.jl — Mathematical Formulations for the 8 Cognitive Capabilities.
Pure analytical equations covering neural field simulations, memory dynamics,
entropy of reasoning, and affective biomarker calculus.
"""
module CognitiveMath

export reasoning_entropy, wilson_cowan_neural_oscillation, actr_memory_activation,
       ltp_probability, conceptual_divergence_novelty, dempster_shafer_evidence,
       discourse_coherence_cosine, vocal_stress_biomarker_calc

"""
1. Thinking Ability: Reasoning Depth & Propositional Entropy
   H(R) = -\\sum_{i=1}^K P(r_i) \\log_2 P(r_i)
"""
function reasoning_entropy(probabilities::Vector{Float32})::Float32
    h = 0.0f0
    for p in probabilities
        if p > 1e-7f0
            h -= p * log2(p)
        end
    end
    return h
end

"""
2. Concentration & Focus: Wilson-Cowan Neural Field Dynamics
   \\tau_E \\frac{dE}{dt} = -E + S_E(w_{EE}E - w_{EI}I + P)
   \\tau_I \\frac{dI}{dt} = -I + S_I(w_{IE}E - w_{II}I + Q)
"""
function wilson_cowan_neural_oscillation(
    steps::Int = 100, dt::Float32 = 0.01f0, P::Float32 = 1.2f0
)::Tuple{Vector{Float32}, Vector{Float32}}
    E = zeros(Float32, steps)
    I = zeros(Float32, steps)
    E[1] = 0.1f0
    I[1] = 0.05f0

    tau_E = 0.01f0
    tau_I = 0.02f0
    w_ee = 12.0f0
    w_ei = 10.0f0
    w_ie = 10.0f0
    w_ii = 1.5f0

    sigmoid(x) = 1.0f0 / (1.0f0 + exp(-x))

    for t in 1:(steps - 1)
        dE = (-E[t] + sigmoid(w_ee * E[t] - w_ei * I[t] + P)) / tau_E
        dI = (-I[t] + sigmoid(w_ie * E[t] - w_ii * I[t])) / tau_I
        E[t + 1] = max(0.0f0, E[t] + dt * dE)
        I[t + 1] = max(0.0f0, I[t] + dt * dI)
    end

    return (E, I)
end

"""
3. Memory Function: ACT-R Base-Level Activation & LTP Probability
   A_i = \\ln \\left( \\sum_{k=1}^n t_k^{-d} \\right)
   P(LTP) = \\frac{1}{1 + e^{-\\beta (A_i - \\theta)}}
"""
function actr_memory_activation(time_offsets_sec::Vector{Float32}, decay_d::Float32 = 0.5f0)::Float32
    sum_t = sum(t -> t^(-decay_d), time_offsets_sec)
    return log(max(sum_t, 1e-6f0))
end

function ltp_probability(activation::Float32, threshold::Float32 = 1.0f0, beta::Float32 = 2.0f0)::Float32
    return 1.0f0 / (1.0f0 + exp(-beta * (activation - threshold)))
end

"""
4. Creative Thinking: Manifold Geodesic Novelty Metric
   D_{nov} = \\frac{1}{M} \\sum_{m=1}^M \\arccos \\left( \\frac{u \\cdot v_m}{\\|u\\| \\|v_m\\|} \\right)
"""
function conceptual_divergence_novelty(idea_vec::Vector{Float32}, cluster_centroids::Matrix{Float32})::Float32
    dim, num_clusters = size(cluster_centroids)
    norm_u = norm(idea_vec) + 1e-7f0
    total_angle = 0.0f0

    for c in 1:num_clusters
        v = cluster_centroids[:, c]
        norm_v = norm(v) + 1e-7f0
        cos_sim = clamp(dot(idea_vec, v) / (norm_u * norm_v), -1.0f0, 1.0f0)
        total_angle += acos(cos_sim)
    end

    return total_angle / Float32(num_clusters)
end

"""
5. Analytical Thinking: Dempster-Shafer Evidence Fusion
   (m_1 \\oplus m_2)(A) = \\frac{1}{1 - K} \\sum_{B \\cap C = A} m_1(B) m_2(C)
"""
function dempster_shafer_evidence(m1_true::Float32, m1_false::Float32,
                                  m2_true::Float32, m2_false::Float32)::Float32
    k_conflict = m1_true * m2_false + m1_false * m2_true
    if k_conflict >= 0.999f0
        return 0.5f0
    end
    combined_true = (m1_true * m2_true) / (1.0f0 - k_conflict)
    return combined_true
end

"""
6. Verbal Reasoning: Cross-Sentence Discourse Coherence
   C_{disc} = \\frac{1}{N-1} \\sum_{i=1}^{N-1} \\cos(v_i, v_{i+1})
"""
function discourse_coherence_cosine(sentence_embeddings::Matrix{Float32})::Float32
    dim, num_sentences = size(sentence_embeddings)
    if num_sentences <= 1
        return 1.0f0
    end

    total_sim = 0.0f0
    for i in 1:(num_sentences - 1)
        v1 = sentence_embeddings[:, i]
        v2 = sentence_embeddings[:, i + 1]
        sim = dot(v1, v2) / (norm(v1) * norm(v2) + 1e-7f0)
        total_sim += sim
    end

    return clamp(total_sim / Float32(num_sentences - 1), 0.0f0, 1.0f0)
end

"""
7. Emotional Regulation: Acoustic Vocal Stress Biomarker
   S = \\alpha \\cdot \\text{Jitter} + \\beta \\cdot \\text{Shimmer} + \\gamma \\cdot \\frac{\\text{TremorHz}}{F_0}
"""
function vocal_stress_biomarker_calc(jitter::Float32, shimmer::Float32, tremor_hz::Float32, f0_hz::Float32)::Float32
    tremor_ratio = tremor_hz / max(f0_hz, 50.0f0)
    stress = 0.35f0 * (jitter / 0.015f0) + 0.35f0 * (shimmer / 0.035f0) + 0.30f0 * (tremor_ratio / 0.05f0)
    return clamp(stress, 0.0f0, 1.0f0)
end

# Linear algebra helper
norm(x::Vector{Float32}) = sqrt(sum(x .^ 2))
dot(x::Vector{Float32}, y::Vector{Float32}) = sum(x .* y)

end # module CognitiveMath
