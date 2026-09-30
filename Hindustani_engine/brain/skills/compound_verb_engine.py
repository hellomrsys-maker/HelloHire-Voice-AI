"""
Hindustani Compound & Conjunct Verb Skill.
Analyzes polar verb (V1 stem) + vector auxiliary (V2) combinations and noun/adj + light verb conjuncts.
"""

from typing import Dict, Any, List, Optional


class CompoundVerbEngine:
    """
    Analyzes South Asian compound verb complexes (V1 + V2) and semantic aspectual modulations.
    """

    VECTOR_VERBS = {
        "lena": {
            "devanagari": "लेना",
            "semantic_role": "self_benefactive",
            "meaning": "action executed for oneself or completed inward"
        },
        "dena": {
            "devanagari": "देना",
            "semantic_role": "other_benefactive",
            "meaning": "action directed towards another person or outward"
        },
        "jaana": {
            "devanagari": "जाना",
            "semantic_role": "completive_change_of_state",
            "meaning": "thorough completion, departure, or irreversible transition"
        },
        "daalna": {
            "devanagari": "डालना",
            "semantic_role": "violent_forceful",
            "meaning": "action done forcefully, recklessly, or with finality"
        },
        "baithna": {
            "devanagari": "बैठना",
            "semantic_role": "inadvertent_foolish",
            "meaning": "action done regretfully or foolishly"
        },
        "uthna": {
            "devanagari": "उठना",
            "semantic_role": "sudden_inchoative",
            "meaning": "sudden eruption or spontaneous burst of action"
        }
    }

    def analyze_compound_verb(self, v1_stem: str, v2_vector: str) -> Dict[str, Any]:
        """
        Analyzes a candidate V1 + V2 verbal combination.
        """
        v2_clean = v2_vector.lower().strip()
        # Normalization
        v2_lemma = v2_clean
        for key in self.VECTOR_VERBS:
            if v2_clean.startswith(key[:3]) or v2_clean == key:
                v2_lemma = key
                break

        if v2_lemma in self.VECTOR_VERBS:
            meta = self.VECTOR_VERBS[v2_lemma]
            return {
                "is_compound_verb": True,
                "v1_stem": v1_stem,
                "v2_vector": v2_lemma,
                "semantic_role": meta["semantic_role"],
                "aspectual_gloss": meta["meaning"],
                "full_compound": f"{v1_stem} {v2_lemma}"
            }

        return {
            "is_compound_verb": False,
            "v1_stem": v1_stem,
            "v2_vector": v2_vector,
            "semantic_role": "standard_simplex",
            "aspectual_gloss": "Simplex or non-vector verb sequence"
        }
