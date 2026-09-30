"""
domain_track_classifier_ai.py — Classifies candidate technical domain track and assesses track competence.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

DOMAIN_TAXONOMY = {
    "ENGINEERING": {
        "id": 1,
        "keywords": [
            "distributed", "microservices", "latency", "throughput", "concurrency",
            "database", "cache", "api", "pipeline", "docker", "kubernetes", "compiler",
            "memory", "thread", "architecture", "algorithm", "bandwidth", "async", "backend"
        ]
    },
    "FINANCE": {
        "id": 2,
        "keywords": [
            "ebitda", "liquidity", "portfolio", "arbitrage", "derivatives", "hedging",
            "valuation", "balance sheet", "p&l", "equity", "dcf", "fixed income", "treasury",
            "solvency", "capital expenditure", "revenue", "roi", "wacc"
        ]
    },
    "MEDICAL": {
        "id": 3,
        "keywords": [
            "clinical", "patient", "etiology", "pathology", "pharmacology", "diagnosis",
            "prognosis", "therapeutic", "oncology", "dosage", "efficacy", "biomarker",
            "randomized controlled trial", "contraindication", "mortality"
        ]
    },
    "LEGAL": {
        "id": 4,
        "keywords": [
            "jurisdiction", "statute", "tort", "contract", "litigation", "compliance",
            "indemnity", "liability", "arbitration", "intellectual property", "precedent",
            "affidavit", "fiduciary", "breach", "counsel"
        ]
    },
    "EXECUTIVE": {
        "id": 5,
        "keywords": [
            "stakeholders", "board", "strategy", "governance", "headcount", "okr", "kpi",
            "roadmap", "org design", "talent retention", "change management", "budget",
            "cross-functional", "p&l ownership", "synergies"
        ]
    }
}


class DomainTrackClassifierAI:
    """
    Identifies the primary domain track of the candidate and scores domain alignment.
    """

    def evaluate(self, text: str) -> Dict[str, Any]:
        cleaned = text.lower()
        words = set(re.findall(r"\b[a-z0-9\-]+\b", cleaned))

        track_scores: Dict[str, float] = {}
        track_hits: Dict[str, List[str]] = {}

        for domain, spec in DOMAIN_TAXONOMY.items():
            hits = [kw for kw in spec["keywords"] if kw in words or ((" " in kw) and (kw in cleaned))]
            track_hits[domain] = hits
            track_scores[domain] = len(hits)

        # Primary track
        sorted_tracks = sorted(track_scores.items(), key=lambda x: x[1], reverse=True)
        primary_track, top_hit_count = sorted_tracks[0]

        if top_hit_count == 0:
            primary_track = "GENERAL"
            track_id = 0
            confidence = 0.20
        else:
            total_hits = max(sum(track_scores.values()), 1)
            confidence = min(1.0, top_hit_count / total_hits + (0.10 if top_hit_count >= 3 else 0.0))
            track_id = DOMAIN_TAXONOMY[primary_track]["id"]

        return {
            "primary_track": primary_track,
            "track_id": track_id,
            "confidence": round(confidence, 3),
            "track_keyword_hits": track_hits[primary_track] if primary_track in track_hits else [],
            "track_distribution": track_scores
        }
