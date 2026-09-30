"""
French Pragmatics & Register Skill.
Evaluates the T-V distinction (tutoiement vs. vouvoiement), politeness markers,
epistolary correspondence formulas, and register consistency.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set


class FrenchPragmaticsEngine:
    """
    Evaluates sociolinguistic register, honorifics, and politeness in French utterances.
    """

    TUTOIE_MARKERS: Set[str] = {
        "tu", "te", "t'", "toi", "ton", "ta", "tes"
    }

    VOUVOIE_MARKERS: Set[str] = {
        "vous", "votre", "vos"
    }

    COURTESY_PHRASES: List[str] = [
        "s'il vous plaît", "s'il te plaît", "je vous en prie", "je t'en prie",
        "veuillez", "auriez-vous l'amabilité", "pourriez-vous", "cordialement",
        "salutations distinguées", "parfaite considération"
    ]

    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            rules_path = str(Path(__file__).parent.parent / "rules" / "pragmatic_register_matrix.json")
        self.rules_path = rules_path
        self._load_rules()

    def _load_rules(self):
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        except Exception:
            self.db = {
                "registers": {},
                "epistolary_closings": {},
                "courtesy_modifiers": self.COURTESY_PHRASES
            }

    def evaluate_register(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the text for T-V markers, register consistency, and politeness score.
        """
        low = text.lower()
        tokens = low.replace("'", "' ").replace(",", " ").replace(".", " ").replace("?", " ").split()

        tutoie_count = sum(1 for t in tokens if t in self.TUTOIE_MARKERS)
        vouvoie_count = sum(1 for t in tokens if t in self.VOUVOIE_MARKERS)

        has_courtesy = any(p in low for p in self.COURTESY_PHRASES)

        formal_titles = {"monsieur", "madame", "mademoiselle", "maître", "veuillez", "agréer"}
        formal_title_count = sum(1 for t in tokens if t in formal_titles)

        # Detect register clash
        has_clash = tutoie_count > 0 and vouvoie_count > 0

        # Classification
        if (vouvoie_count > 0 or formal_title_count > 0 or has_courtesy) and tutoie_count == 0:
            assigned_register = "vouvoiement"
            politeness_score = 0.85 if not has_courtesy else 0.98
        elif tutoie_count > 0 and vouvoie_count == 0 and formal_title_count == 0:
            assigned_register = "tutoiement"
            politeness_score = 0.35 if not has_courtesy else 0.50
        else:
            assigned_register = "neutral_or_mixed"
            politeness_score = 0.60 if has_courtesy else 0.50

        return {
            "assigned_register": assigned_register,
            "is_formal": assigned_register == "vouvoiement",
            "is_informal": assigned_register == "tutoiement",
            "has_register_clash": has_clash,
            "tutoie_marker_count": tutoie_count,
            "vouvoie_marker_count": vouvoie_count,
            "has_courtesy_formula": has_courtesy,
            "politeness_score": round(politeness_score, 2),
            "message": "Conflit de registre détecté (mélange de tutoiement et vouvoiement) !" if has_clash else "Registre cohérent."
        }

    def get_closing_formula(self, formal: bool = True) -> str:
        """Returns standard closing formula according to required formality."""
        if formal:
            return "Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées."
        return "Bien amicalement,"
