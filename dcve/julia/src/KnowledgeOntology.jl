"""
KnowledgeOntology.jl — Knowledge Graph Traversal & Ontology Grounding (DCVE Julia Layer)

Models the semantic distance and domain depth traversal over a concept graph:
  D(t) = exp(-lambda * distance(concept, domain_ground))
"""

module KnowledgeOntology

export DomainState, evaluate_domain_depth

struct DomainState
    depth::Float64
    precision::Float64
    grounding::Float64
end

function evaluate_domain_depth(
    concept_hits::Int,
    buzzword_hits::Int,
    quantifier_count::Int,
    lambda::Float64 = 0.25
)::DomainState
    depth = clamp(1.0 - exp(-lambda * concept_hits), 0.0, 1.0)
    precision = clamp(0.4 + 0.15 * quantifier_count, 0.0, 1.0)
    grounding = clamp(depth * 0.7 + precision * 0.3 - 0.2 * buzzword_hits, 0.0, 1.0)
    return DomainState(depth, precision, grounding)
end

end # module
