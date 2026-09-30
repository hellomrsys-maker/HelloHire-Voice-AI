"""
jargon_vs_depth_ai.py — Distinguishes empty buzzwords from verifiable technical substance.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

# Buzzwords / Surface jargon (hand-waving without substance)
SURFACE_BUZZWORDS = {
    "synergy", "synergies", "paradigm shift", "disruptive", "cutting-edge",
    "world-class", "next-gen", "game-changer", "ai-driven", "cloud-native",
    "mission-critical", "seamless", "frictionless", "scalable", "blazing fast",
    "revolutionize", "hyper-growth", "holistic", "robust", "future-proof",
    "streamline", "low-hanging fruit", "touch base", "deep dive", "move the needle"
}

# Verifiable, deep technical & domain markers
DEEP_SUBSTANCE_MARKERS = {
    "idempotency", "idempotent", "linearizability", "serializability",
    "two-phase commit", "2pc", "raft", "paxos", "vector clock", "eventual consistency",
    "backpressure", "bounded queue", "memory-mapped", "mmap", "cache coherence",
    "p99", "p95", "tail latency", "amortized complexity", "b-tree", "lsm tree",
    "simd", "zero-copy", "atomic compare-and-swap", "cas", "mutex", "deadlock avoidance",
    "circuit breaker", "exponential backoff", "sharding", "consistent hashing",
    "bloom filter", "ebpf", "write-ahead log", "wal", "garbage collection tuning",
    "discounted cash flow", "dcf", "ebitda", "wacc", "black-scholes", "monte carlo",
    "monte-carlo", "var", "value at risk", "solvency ratio", "capm", "alpha", "beta",
    "differential diagnosis", "etiology", "pharmacokinetics", "bioavailability",
    "cross-examination", "promissory estoppel", "force majeure", "mens rea", "habeas corpus"
}


class JargonVsDepthAI:
    """
    Evaluates whether an utterance contains substantive domain concepts
    or relies primarily on superficial jargon.
    """

    def evaluate(self, text: str) -> Dict[str, Any]:
        cleaned = text.lower()
        words = re.findall(r"\b[a-z0-9\-]+\b", cleaned)
        total_words = max(len(words), 1)

        buzz_hits: List[str] = []
        for phrase in SURFACE_BUZZWORDS:
            if " " in phrase:
                if phrase in cleaned:
                    buzz_hits.append(phrase)
            elif phrase in words:
                buzz_hits.append(phrase)

        depth_hits: List[str] = []
        for term in DEEP_SUBSTANCE_MARKERS:
            if " " in term or "-" in term:
                if term in cleaned:
                    depth_hits.append(term)
            elif term in words:
                depth_hits.append(term)

        buzz_density = min(1.0, len(buzz_hits) / max(total_words / 15.0, 1.0))
        depth_density = min(1.0, len(depth_hits) / max(total_words / 20.0, 1.0))

        # Depth score rewards substantive markers while penalizing empty buzzword density
        if len(depth_hits) == 0 and len(buzz_hits) > 0:
            depth_score = max(0.10, 0.40 - buzz_density * 0.30)
        else:
            depth_score = min(1.0, max(0.0, 0.20 + (depth_density * 0.70) - (buzz_density * 0.20) + min(len(depth_hits) * 0.08, 0.20)))

        return {
            "depth_score": round(depth_score, 3),
            "buzzword_count": len(buzz_hits),
            "substance_count": len(depth_hits),
            "buzzwords_found": sorted(list(set(buzz_hits))),
            "substance_terms_found": sorted(list(set(depth_hits))),
            "buzzword_density": round(buzz_density, 3),
            "substance_density": round(depth_density, 3),
            "is_substantive": len(depth_hits) >= 2 or (len(depth_hits) >= 1 and len(buzz_hits) <= 1)
        }
