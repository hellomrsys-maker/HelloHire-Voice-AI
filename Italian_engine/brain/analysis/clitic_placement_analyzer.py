"""
Italian Engine — Clitic Placement Analyzer
Audits clitic clusters and ordering, detecting untransformed chains (*mi lo -> me lo) and
misplaced clitics.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words

class CliticPlacementAnalyzer:
    """Cognitive analyzer for Italian pronominal clitic placement and clusters."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        violations = []
        clusters_found = []
        
        # Scan for illegal unshifted double clitic chains (e.g. "mi lo" instead of "me lo")
        for i in range(len(tokens) - 1):
            w1 = tokens[i].lower()
            w2 = tokens[i + 1].lower()
            
            # Illegal untransformed chains: mi/ti/ci/vi/si + lo/la/li/le/ne
            if w1 in {"mi", "ti", "ci", "vi", "si"} and w2 in {"lo", "la", "li", "le", "ne"}:
                corrected = w1[:-1] + "e " + w2
                violations.append({
                    "cluster": f"{w1} {w2}",
                    "rule": "clitic_cluster_vowel_shift",
                    "error": f"Clitic chain '{w1} {w2}' must undergo vowel shift to '{corrected}'."
                })
                
            # Illegal split gli/le + lo/la/li/le/ne
            if w1 in {"gli", "le"} and w2 in {"lo", "la", "li", "le", "ne"}:
                corrected = f"glie{w2}"
                violations.append({
                    "cluster": f"{w1} {w2}",
                    "rule": "clitic_cluster_fusion",
                    "error": f"Indirect clitic '{w1}' followed by direct '{w2}' must fuse into single word '{corrected}'."
                })
                
            # Valid combined clusters
            if w1 in {"me", "te", "ce", "ve", "se"} and w2 in {"lo", "la", "li", "le", "ne"}:
                clusters_found.append(f"{w1} {w2}")
            elif w1.startswith("glie") and w1[4:] in {"lo", "la", "li", "le", "ne"}:
                clusters_found.append(w1)
                
        return {
            "text": text,
            "clusters_found": clusters_found,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
