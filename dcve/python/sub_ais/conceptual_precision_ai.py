"""
conceptual_precision_ai.py — Evaluates quantitative precision, causal mechanics, and concrete metrics.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

# Vague, hand-waving qualifiers
VAGUE_QUALIFIERS = [
    "a lot of", "tons of", "pretty good", "really fast", "huge amount",
    "somewhat", "kind of", "sort of", "very big", "basically",
    "somehow", "more or less", "a bunch of", "greatly improved"
]

# Patterns for concrete quantifiers (numbers, percentages, time units, bandwidth, currencies)
QUANTIFIER_PATTERNS = [
    r"\b\d+(?:\.\d+)?%\b",                                        # 14.5%, 99%
    r"\b\d+(?:\.\d+)?\s*(?:ms|seconds?|mins?|hours?|μs|ns)\b",    # 32ms, 5 mins
    r"\b\d+(?:\.\d+)?\s*(?:gb|mb|tb|kb|req/s|rps|qps|tps)\b",     # 50,000 req/s, 16GB
    r"\$\d+(?:,\d{3})*(?:\.\d+)?(?:\s*[kmbt])?\b",                 # $1.2M, $450,000
    r"\b\d+(?:,\d{3})+\b",                                        # 50,000, 1,000,000
    r"\b(?:reduced|increased|optimized)\s+by\s+\d+",             # reduced by 30
]

# Causal / mechanistic transition markers
CAUSAL_CONNECTORS = [
    "because", "as a result of", "consequently", "resulting in",
    "due to", "led to", "mitigated by", "enabled by", "attributed to",
    "by replacing", "by implementing", "thereby"
]


class ConceptualPrecisionAI:
    """
    Measures the precision of statements: specific measurements, explicit mechanisms,
    and lack of vague hand-waving.
    """

    def evaluate(self, text: str) -> Dict[str, Any]:
        cleaned = text.lower()

        # 1. Detect vague qualifiers
        vague_matches: List[str] = []
        for phrase in VAGUE_QUALIFIERS:
            if phrase in cleaned:
                vague_matches.append(phrase)

        # 2. Detect quantitative metrics
        quant_matches: List[str] = []
        for pat in QUANTIFIER_PATTERNS:
            found = re.findall(pat, cleaned)
            quant_matches.extend(found)

        # 3. Detect causal links
        causal_matches: List[str] = []
        for conn in CAUSAL_CONNECTORS:
            if conn in cleaned:
                causal_matches.append(conn)

        # Metrics scoring
        quant_count = len(quant_matches)
        vague_count = len(vague_matches)
        causal_count = len(causal_matches)

        quant_score = min(1.0, quant_count * 0.35)
        causal_score = min(1.0, causal_count * 0.30)
        vague_penalty = min(0.50, vague_count * 0.15)

        base = 0.25
        precision = min(1.0, max(0.0, base + quant_score * 0.50 + causal_score * 0.35 - vague_penalty))

        return {
            "precision_score": round(precision, 3),
            "quantifier_count": quant_count,
            "quantifiers_found": quant_matches,
            "vague_qualifier_count": vague_count,
            "vague_qualifiers_found": vague_matches,
            "causal_link_count": causal_count,
            "causal_links_found": causal_matches,
            "is_quantitatively_grounded": quant_count >= 1 and causal_count >= 1
        }
