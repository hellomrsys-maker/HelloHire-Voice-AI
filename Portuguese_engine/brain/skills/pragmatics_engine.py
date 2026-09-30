"""
Portuguese Pragmatics & Address Stratification Engine: Evaluates social distance,
address hierarchy (você vs tu vs o senhor), and epistolary formulas.
"""

from typing import Dict, Any, Optional, List
import os
import json


class PortuguesePragmaticsEngine:
    """
    Evaluates pragmatic register and politeness stratification in Portuguese.
    """

    FORMAL_MARKERS = {
        "senhor", "senhora", "senhores", "senhoras", "prezado", "prezada",
        "excelentíssimo", "excelentíssima", "doutor", "doutora", "atenciosamente",
        "cordialmente", "por favor", "por gentileza", "se faz favor"
    }

    FAMILIAR_MARKERS = {
        "você", "vocês", "amigo", "amiga", "abraço", "olá", "oi"
    }

    INTIMATE_MARKERS = {
        "tu", "te", "ti", "contigo", "beijo", "beijos", "querido", "querida"
    }

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "pragmatic_register_matrix.json")
        
        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

    def evaluate_pragmatics(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Evaluates the address tier, formality, and politeness index.
        """
        form_count = sum(1 for t in tokens if t.lower() in self.FORMAL_MARKERS)
        fam_count = sum(1 for t in tokens if t.lower() in self.FAMILIAR_MARKERS)
        int_count = sum(1 for t in tokens if t.lower() in self.INTIMATE_MARKERS)

        if form_count > fam_count and form_count > int_count:
            tier = "formal"
            politeness_score = 0.95
        elif int_count > fam_count and int_count > form_count:
            tier = "intimate"
            politeness_score = 0.40
        else:
            tier = "familiar"
            politeness_score = 0.75

        return {
            "tier": tier,
            "politeness_score": politeness_score,
            "counts": {
                "formal": form_count,
                "familiar": fam_count,
                "intimate": int_count
            }
        }

    def get_epistolary_closing(self, tier: str = "formal") -> str:
        """Returns culturally authentic Portuguese valedictions."""
        if tier == "formal":
            return "Atenciosamente,"
        elif tier == "intimate":
            return "Com muito carinho,"
        return "Um forte abraço,"
