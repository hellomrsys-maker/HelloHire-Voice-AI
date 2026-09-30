"""
ontology_grounding_ai.py — Validates whether domain concepts are used in semantically sound relationships.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple

# Domain ontology relationships: (concept_a, concept_b, relationship)
ONTOLOGY_RELATIONSHIPS = [
    # Distributed Systems / Engineering
    ("kafka", "topic", "partitions"),
    ("kafka", "partition", "ordering"),
    ("redis", "cache", "in-memory"),
    ("redis", "cluster", "replication"),
    ("b-tree", "database", "indexing"),
    ("lsm", "write", "throughput"),
    ("raft", "consensus", "leader"),
    ("paxos", "consensus", "quorum"),
    ("docker", "container", "isolation"),
    ("kubernetes", "pod", "scheduling"),
    ("load balancer", "traffic", "reverse proxy"),
    ("tls", "handshake", "encryption"),
    # Finance
    ("dcf", "cash flow", "discount rate"),
    ("wacc", "cost of capital", "equity"),
    ("var", "portfolio", "confidence interval"),
    ("black-scholes", "option", "volatility"),
    # Medical
    ("pathology", "biopsy", "tissue"),
    ("pharmacokinetics", "absorption", "half-life"),
    ("clinical trial", "phase 3", "efficacy"),
    # Legal
    ("tort", "negligence", "duty of care"),
    ("contract", "consideration", "breach"),
    ("jurisdiction", "court", "standing")
]

# Nonsensical / Hallucinatory pairings
HALLUCINATORY_MISMATCHES = [
    ("kafka", "css"),
    ("kubernetes", "stethoscope"),
    ("raft", "discounted cash flow"),
    ("docker", "habeas corpus"),
    ("ebitda", "sub-atomic particles"),
    ("dcf", "compiler backend")
]


class OntologyGroundingAI:
    """
    Evaluates whether the candidate connects technical concepts with appropriate
    mechanisms and ontology relations vs making bizarre or ungrounded claims.
    """

    def evaluate(self, text: str) -> Dict[str, Any]:
        cleaned = text.lower()

        valid_relations_found: List[str] = []
        for a, b, rel in ONTOLOGY_RELATIONSHIPS:
            if a in cleaned and (b in cleaned or rel in cleaned):
                valid_relations_found.append(f"{a} ↔ {b} ({rel})")

        mismatches_found: List[str] = []
        for x, y in HALLUCINATORY_MISMATCHES:
            if x in cleaned and y in cleaned:
                mismatches_found.append(f"{x} ↮ {y}")

        valid_count = len(valid_relations_found)
        mismatch_count = len(mismatches_found)

        if valid_count == 0 and mismatch_count == 0:
            grounding_score = 0.35  # neutral
        else:
            base = 0.30
            grounding_score = min(1.0, max(0.0, base + min(valid_count * 0.25, 0.70) - (mismatch_count * 0.40)))

        return {
            "ontology_grounding_score": round(grounding_score, 3),
            "valid_relations_count": valid_count,
            "valid_relations_found": valid_relations_found,
            "mismatch_count": mismatch_count,
            "mismatches_found": mismatches_found,
            "is_grounded": valid_count >= 1 and mismatch_count == 0
        }
