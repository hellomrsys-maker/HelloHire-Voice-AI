# =============================================================================
# engine/julia/src/CognitiveSim.jl
# Simulation of cognitive processes:
#   - Attention decay (forgetting over time)
#   - Memory salience dynamics
#   - Curiosity-driven exploration model
#   - Associative reasoning graphs
#   - Metacognitive monitoring
# =============================================================================

module CognitiveSim

using LinearAlgebra
using Statistics
using Random

export AttentionDecayModel, MemorySalienceModel, CuriosityExplorer,
       AssociativeGraph, MetacognitiveMonitor,
       step_attention_decay!, update_salience!, compute_curiosity,
       associative_spread!, metacognitive_confidence

# =============================================================================
# Attention Decay Model
# Implements sustained attention with temporal decay.
# Models how attention intensity decreases over time without reinforcement.
# =============================================================================

"""
    AttentionDecayModel

Simulates sustained attention as exponential decay of attention intensity.
Models the "concentration and sustained attention" capability.

Fields:
- `decay_rate`:   λ in A(t) = A₀ × exp(-λ × t); higher = faster decay
- `refresh_gain`: How much a new relevant stimulus boosts attention
- `min_attention`: Floor on attention intensity
- `attention_intensity`: Current attention state vector (per topic)
- `time_step`: Current simulation time
"""
mutable struct AttentionDecayModel
    decay_rate::Float32
    refresh_gain::Float32
    min_attention::Float32
    attention_intensity::Vector{Float32}  # Per-topic attention values
    time_step::Int
    topic_labels::Vector{String}

    function AttentionDecayModel(
        n_topics::Int;
        decay_rate::Float32    = 0.05f0,
        refresh_gain::Float32  = 0.3f0,
        min_attention::Float32 = 0.01f0,
    )
        new(decay_rate, refresh_gain, min_attention,
            ones(Float32, n_topics),
            0, fill("topic_$(1:n_topics)", n_topics))
    end
end

"""
    step_attention_decay!(model::AttentionDecayModel;
                           stimulus_vector::Union{Nothing, Vector{Float32}} = nothing)

Advances the attention model by one time step.
If `stimulus_vector` is provided, topics with high stimulus values are refreshed.

The update rule is:
    A(t+1) = max(A(t) × exp(-λ) + gain × stimulus, min_attention)
"""
function step_attention_decay!(
    model::AttentionDecayModel;
    stimulus_vector::Union{Nothing, Vector{Float32}} = nothing
)
    # Exponential decay
    model.attention_intensity .*= exp(-model.decay_rate)

    # Apply stimulus refresh
    if !isnothing(stimulus_vector)
        @assert length(stimulus_vector) == length(model.attention_intensity)
        model.attention_intensity .+= model.refresh_gain .* max.(stimulus_vector, 0.0f0)
    end

    # Clamp to [min_attention, 1.0]
    model.attention_intensity .= clamp.(model.attention_intensity,
                                        model.min_attention, 1.0f0)
    model.time_step += 1
    return nothing
end

"""
    most_attended_topics(model::AttentionDecayModel; top_k::Int = 3)
                        -> Vector{Tuple{String, Float32}}

Returns the top-k most attended topics with their current intensities.
"""
function most_attended_topics(
    model::AttentionDecayModel;
    top_k::Int = 3
) :: Vector{Tuple{String, Float32}}

    top_k = min(top_k, length(model.attention_intensity))
    idx   = sortperm(model.attention_intensity, rev=true)[1:top_k]
    return [(model.topic_labels[i], model.attention_intensity[i]) for i in idx]
end

# =============================================================================
# Memory Salience Model
# Simulates memory salience dynamics: recent and emotionally salient
# memories are more accessible.
# =============================================================================

"""
    MemorySalienceModel

Models how memory salience evolves with recency, access frequency,
and emotional valence.

Salience update rule (Power Law of Forgetting):
    S(t) = S₀ × (t_since_access + 1)^(-decay_exponent)
    + access_bonus × access_count
    + valence_weight × abs(emotional_valence)
"""
mutable struct MemorySalienceModel
    decay_exponent::Float32
    access_bonus::Float32
    valence_weight::Float32
    entries::Vector{NamedTuple}  # {id, salience, access_count, last_access_t, valence}
    current_time::Int

    function MemorySalienceModel(;
        decay_exponent::Float32 = 0.5f0,
        access_bonus::Float32   = 0.1f0,
        valence_weight::Float32 = 0.2f0,
    )
        new(decay_exponent, access_bonus, valence_weight, [], 0)
    end
end

"""
    update_salience!(model::MemorySalienceModel)

Recomputes salience for all entries based on current time.
"""
function update_salience!(model::MemorySalienceModel)
    model.current_time += 1
    t = Float32(model.current_time)

    model.entries = map(model.entries) do entry
        t_since = t - Float32(entry.last_access_t)
        new_salience = (
            Float32(t_since + 1.0)^(-model.decay_exponent)
            + model.access_bonus * Float32(entry.access_count)
            + model.valence_weight * abs(entry.valence)
        )
        new_salience = clamp(new_salience, 0.0f0, 1.0f0)
        (; entry..., salience = new_salience)
    end
    return nothing
end

"""
    add_memory!(model::MemorySalienceModel, id::String;
                 valence::Float32 = 0.0f0) -> NamedTuple

Adds a new memory entry with initial high salience.
"""
function add_memory!(
    model::MemorySalienceModel,
    id::String;
    valence::Float32 = 0.0f0
)
    entry = (
        id            = id,
        salience      = 1.0f0,
        access_count  = 1,
        last_access_t = model.current_time,
        valence       = valence
    )
    push!(model.entries, entry)
    return entry
end

"""
    top_salient_memories(model::MemorySalienceModel; top_k::Int = 5)

Returns the top-k most salient memory entries.
"""
function top_salient_memories(model::MemorySalienceModel; top_k::Int = 5)
    sorted = sort(model.entries, by = e -> e.salience, rev=true)
    return sorted[1:min(top_k, length(sorted))]
end

# =============================================================================
# Curiosity-Driven Exploration Model
# Implements "curiosity-driven exploration" as intrinsic motivation
# based on prediction uncertainty.
# =============================================================================

"""
    CuriosityExplorer

Models intrinsic curiosity as information gain — the agent is more
curious about states that reduce predictive uncertainty.

Curiosity score = expected surprise ≈ variance of predictions.
"""
struct CuriosityExplorer
    uncertainty_scale::Float32
    novelty_decay::Float32

    function CuriosityExplorer(;
        uncertainty_scale::Float32 = 1.0f0,
        novelty_decay::Float32     = 0.95f0,
    )
        new(uncertainty_scale, novelty_decay)
    end
end

"""
    compute_curiosity(explorer::CuriosityExplorer,
                       predictions::Matrix{Float32};
                       seen_state_counts::Vector{Int} = Int[]) -> Vector{Float32}

Computes a curiosity score for each candidate state.

# Arguments
- `predictions`:       Matrix (n_states × n_samples) of model predictions
                       For each state, multiple stochastic predictions (e.g., MC dropout)
- `seen_state_counts`: How many times each state has been visited previously

# Returns
- Curiosity scores (n_states,): higher = more curious
"""
function compute_curiosity(
    explorer::CuriosityExplorer,
    predictions::Matrix{Float32};
    seen_state_counts::Vector{Int} = Int[]
) :: Vector{Float32}

    n_states = size(predictions, 1)

    # Variance of predictions = epistemic uncertainty
    pred_var = vec(var(predictions, dims=2))

    # Intrinsic curiosity = scaled prediction variance
    curiosity = explorer.uncertainty_scale .* pred_var

    # Reduce curiosity for frequently visited states (novelty bonus)
    if !isempty(seen_state_counts)
        @assert length(seen_state_counts) == n_states
        novelty_bonus = explorer.novelty_decay .^ Float32.(seen_state_counts)
        curiosity .*= novelty_bonus
    end

    return curiosity
end

# =============================================================================
# Associative Reasoning Graph
# Models "associative reasoning" — spreading activation across a concept graph.
# =============================================================================

"""
    AssociativeGraph

A weighted graph of concepts where activation spreads via associative links.
Implements the "associative reasoning" cognitive faculty from the spec.
"""
mutable struct AssociativeGraph
    n_nodes::Int
    adjacency::Matrix{Float32}   # (n_nodes × n_nodes) weighted adjacency matrix
    activation::Vector{Float32}  # Current activation level of each concept
    decay_rate::Float32
    node_labels::Vector{String}

    function AssociativeGraph(n_nodes::Int;
                               decay_rate::Float32 = 0.3f0,
                               labels::Vector{String} = String[])
        adj = zeros(Float32, n_nodes, n_nodes)
        act = zeros(Float32, n_nodes)
        lbls = isempty(labels) ? ["node_$i" for i in 1:n_nodes] : labels
        new(n_nodes, adj, act, decay_rate, lbls)
    end
end

"""
    add_association!(graph::AssociativeGraph, from::Int, to::Int;
                      weight::Float32 = 1.0f0, bidirectional::Bool = true)

Adds an associative link between two concepts.
"""
function add_association!(
    graph::AssociativeGraph,
    from::Int, to::Int;
    weight::Float32       = 1.0f0,
    bidirectional::Bool   = true
)
    graph.adjacency[from, to] = weight
    if bidirectional
        graph.adjacency[to, from] = weight
    end
end

"""
    associative_spread!(graph::AssociativeGraph; n_steps::Int = 3)

Runs n steps of spreading activation through the association graph.
Active nodes activate their neighbors according to link weights.

Update rule:
    A(t+1) = (1 - λ) × A(t) + λ × normalize(W @ A(t))
"""
function associative_spread!(
    graph::AssociativeGraph;
    n_steps::Int = 3
)
    for _ in 1:n_steps
        # Compute spreading: W @ A
        spread = graph.adjacency * graph.activation
        # Normalize to prevent runaway activation
        max_val = maximum(spread)
        if max_val > 1e-6f0
            spread ./= max_val
        end
        # Blend: decay existing + add spread
        graph.activation .= (1.0f0 - graph.decay_rate) .* graph.activation .+ graph.decay_rate .* spread
        # Clamp to [0, 1]
        graph.activation .= clamp.(graph.activation, 0.0f0, 1.0f0)
    end
    return nothing
end

"""
    activate_concept!(graph::AssociativeGraph, node_id::Int;
                       strength::Float32 = 1.0f0)

Sets the activation of a specific concept node.
"""
function activate_concept!(
    graph::AssociativeGraph,
    node_id::Int;
    strength::Float32 = 1.0f0
)
    graph.activation[node_id] = clamp(strength, 0.0f0, 1.0f0)
end

"""
    most_active_concepts(graph::AssociativeGraph; top_k::Int = 5)

Returns the top-k most activated concepts.
"""
function most_active_concepts(graph::AssociativeGraph; top_k::Int = 5)
    top_k = min(top_k, graph.n_nodes)
    idx   = sortperm(graph.activation, rev=true)[1:top_k]
    return [(graph.node_labels[i], graph.activation[i]) for i in idx]
end

# =============================================================================
# Metacognitive Monitor
# Models "metacognition" — the system's ability to monitor its own confidence
# and detect when it might be wrong.
# =============================================================================

"""
    MetacognitiveMonitor

Tracks prediction confidence history and detects calibration drift.
Implements "metacognition" from the cognitive faculties in the spec.
"""
mutable struct MetacognitiveMonitor
    confidence_history::Vector{Float32}
    outcome_history::Vector{Float32}   # 1.0 = correct, 0.0 = wrong
    window_size::Int

    function MetacognitiveMonitor(window_size::Int = 100)
        new(Float32[], Float32[], window_size)
    end
end

"""
    record_prediction!(monitor::MetacognitiveMonitor,
                        confidence::Float32, correct::Bool)

Records a new prediction with its outcome.
"""
function record_prediction!(
    monitor::MetacognitiveMonitor,
    confidence::Float32,
    correct::Bool
)
    push!(monitor.confidence_history, confidence)
    push!(monitor.outcome_history, correct ? 1.0f0 : 0.0f0)

    # Keep only last window_size entries
    if length(monitor.confidence_history) > monitor.window_size
        deleteat!(monitor.confidence_history, 1)
        deleteat!(monitor.outcome_history, 1)
    end
end

"""
    metacognitive_confidence(monitor::MetacognitiveMonitor) -> NamedTuple

Returns metacognitive statistics: calibration error, overconfidence flag,
and recommended confidence adjustment.

Calibration error = mean |confidence - accuracy|
Over-confidence = mean confidence >> accuracy
"""
function metacognitive_confidence(
    monitor::MetacognitiveMonitor
) :: NamedTuple

    if isempty(monitor.confidence_history)
        return (
            mean_confidence   = 0.5f0,
            accuracy          = 0.5f0,
            calibration_error = 0.0f0,
            overconfident     = false,
            suggested_scale   = 1.0f0
        )
    end

    mean_conf = mean(monitor.confidence_history)
    accuracy  = mean(monitor.outcome_history)
    calib_err = abs(mean_conf - accuracy)
    overconf  = mean_conf > accuracy + 0.1f0

    # Suggest a calibration scaling factor
    suggested_scale = accuracy / (mean_conf + 1e-6f0)

    return (
        mean_confidence   = mean_conf,
        accuracy          = accuracy,
        calibration_error = calib_err,
        overconfident     = overconf,
        suggested_scale   = suggested_scale
    )
end

# =============================================================================
# Tests
# =============================================================================

function run_cognitive_sim_tests()
    using Test

    @testset "CognitiveSim" begin

        @testset "AttentionDecayModel" begin
            model = AttentionDecayModel(3, decay_rate=0.1f0)
            initial = copy(model.attention_intensity)
            # Without stimulus, attention should decay
            for _ in 1:10
                step_attention_decay!(model)
            end
            @test all(model.attention_intensity .<= initial)
            @test all(model.attention_intensity .>= model.min_attention)
        end

        @testset "MemorySalienceModel" begin
            model = MemorySalienceModel()
            add_memory!(model, "hello_world", valence=0.5f0)
            update_salience!(model)
            @test !isempty(model.entries)
            top = top_salient_memories(model, top_k=1)
            @test top[1].id == "hello_world"
        end

        @testset "CuriosityExplorer" begin
            explorer = CuriosityExplorer()
            # High variance predictions → high curiosity
            preds = randn(Float32, 5, 50)  # 5 states × 50 samples
            curiosity = compute_curiosity(explorer, preds)
            @test length(curiosity) == 5
            @test all(curiosity .>= 0.0f0)
        end

        @testset "AssociativeGraph" begin
            g = AssociativeGraph(4, labels=["cat", "dog", "pet", "animal"])
            add_association!(g, 1, 3)  # cat → pet
            add_association!(g, 2, 3)  # dog → pet
            add_association!(g, 3, 4)  # pet → animal
            activate_concept!(g, 1, strength=1.0f0)  # Activate "cat"
            associative_spread!(g, n_steps=5)
            top = most_active_concepts(g, top_k=2)
            # After spreading from "cat", "pet" and "animal" should be activated
            activated_labels = [t[1] for t in top]
            @test "cat" in activated_labels || "pet" in activated_labels
        end

        @testset "MetacognitiveMonitor" begin
            monitor = MetacognitiveMonitor(20)
            for i in 1:20
                record_prediction!(monitor, 0.8f0, i <= 16)
            end
            stats = metacognitive_confidence(monitor)
            @test stats.mean_confidence ≈ 0.8f0 atol=0.01
            @test stats.accuracy ≈ 0.8f0 atol=0.01
            @test !stats.overconfident
        end

    end

    @info "CognitiveSim tests completed"
end

end # module CognitiveSim
