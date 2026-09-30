"""
Ser vs Estar Disambiguation & Semantic Shift Skill.
Validates copula selection and identifies ontological state vs essence distinctions.
"""

from __future__ import annotations
import json
import os
from typing import Dict, Any, Optional

RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "rules", "ser_estar_rules.json")


class SerEstarEngine:
    """
    Expert copula analyzer for Spanish predicate structures.
    """

    def __init__(self, rules_path: Optional[str] = None):
        target = rules_path or RULES_PATH
        self.semantic_shifts: Dict[str, Any] = {}
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.semantic_shifts = data.get("semantic_shift_adjectives", {})

    def evaluate_copula(self, copula: str, predicate: str) -> Dict[str, Any]:
        """
        Evaluates whether the copula ('ser' or 'estar' form) is appropriate with the predicate.
        """
        cop_low = copula.lower().strip()
        pred_low = predicate.lower().strip()

        is_ser = cop_low in {"ser", "soy", "eres", "es", "somos", "sois", "son", "era", "fui", "sea", "sido"}
        is_estar = cop_low in {"estar", "estoy", "estás", "está", "estamos", "estáis", "están", "estaba", "estuve", "esté", "estado"}

        # Adjective semantic shift check
        shift_info = self.semantic_shifts.get(pred_low)
        meaning = None
        if shift_info:
            if is_ser:
                meaning = shift_info.get("ser")
            elif is_estar:
                meaning = shift_info.get("estar")

        # General suitability heuristics
        location_words = {"aquí", "allí", "en", "cerca", "lejos", "madrid", "casa", "escuela", "biblioteca"}
        condition_words = {"cansado", "enfermo", "roto", "abierto", "cerrado", "contento", "triste", "preocupado"}
        identity_words = {"médico", "profesor", "español", "amigo", "alto", "inteligente", "importante", "necesario"}

        recommended = "ser"
        if any(w in pred_low for w in location_words) or any(w in pred_low for w in condition_words) or pred_low.endswith(("ando", "iendo")):
            recommended = "estar"
        elif any(w in pred_low for w in identity_words):
            recommended = "ser"

        chosen_copula = "ser" if is_ser else ("estar" if is_estar else "unknown")
        is_appropriate = (chosen_copula == recommended) or (shift_info is not None)

        return {
            "chosen_copula": chosen_copula,
            "recommended_copula": recommended,
            "predicate": predicate,
            "has_semantic_shift": shift_info is not None,
            "contextual_meaning": meaning,
            "is_appropriate": is_appropriate,
        }
