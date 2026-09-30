"""
cross_domain_analogies_ai.py — Cross-Domain Analogy & Metaphor Detection Sub-AI (CDIE)

Detects analogies that bridge disparate domains (e.g., Biology -> Systems, Physics -> Economics,
Military -> Strategy, Immunology -> Cybersecurity).
"""
from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple

class CrossDomainAnalogiesAI:
    ANALOGY_CONNECTORS = [
        "like a", "similar to how", "just as", "akin to", "analogous to",
        "much like", "draws inspiration from", "in the same way that", "mirrors the concept of"
    ]

    DOMAIN_LEXICONS = {
        "biology": ["dna", "rna", "enzyme", "cellular", "evolution", "organism", "immune", "t-cell", "antigen", "metabolism", "homeostasis", "synapse", "biology", "biological"],
        "physics": ["gravity", "entropy", "thermodynamics", "momentum", "quantum", "inertia", "kinetic", "resonance", "friction", "equilibrium"],
        "military": ["flanking", "vanguard", "attrition", "tactical", "reconnaissance", "blitzkrieg", "defense-in-depth", "air-gap"],
        "architecture": ["scaffolding", "load-bearing", "foundation", "cantilever", "blueprint", "structural pillar"],
        "software": ["latency", "cache", "throughput", "concurrency", "distributed", "microservices", "raft", "database", "api", "cluster", "payload", "firewall", "bottleneck", "engine", "algorithm", "pipeline"]
    }

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        connector_hits = sum(1 for c in self.ANALOGY_CONNECTORS if c in l)

        # Detect active domains
        active_domains = []
        domain_term_counts = {}
        for dom, terms in self.DOMAIN_LEXICONS.items():
            hits = [t for t in terms if t in l]
            if hits:
                active_domains.append(dom)
                domain_term_counts[dom] = len(hits)

        # A true cross-domain analogy bridges at least 2 distinct domain lexicons
        has_bridge = len(active_domains) >= 2 and connector_hits >= 1
        transfer_score = 0.0
        if has_bridge:
            transfer_score = min(1.0, 0.50 + 0.25 * connector_hits + 0.15 * len(active_domains))
        elif len(active_domains) >= 2:
            transfer_score = min(0.70, 0.35 + 0.15 * len(active_domains))
        elif connector_hits >= 1:
            transfer_score = 0.40
        else:
            transfer_score = 0.20

        return {
            "sub_ai": "cross_domain_analogies",
            "analogy_connectors_found": connector_hits,
            "domains_detected": active_domains,
            "has_cross_domain_bridge": has_bridge,
            "transfer_score": round(transfer_score, 3),
            "composite_score": round(transfer_score, 3)
        }
