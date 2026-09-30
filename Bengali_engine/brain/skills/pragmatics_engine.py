"""
Bengali Pragmatics & Register Engine: Evaluates 3-tier social politeness (Aapni/Tumi/Tui),
Sadhu vs Cholito register diglossia, and prevents Guru-Chondali solecisms.
"""

from typing import Dict, Any, Optional, Tuple, List
import os
import json


class BengaliPragmaticsEngine:
    """
    Evaluates pragmatic register, politeness hierarchy, and Guru-Chondali stylistic solecisms.
    """

    SUPERIOR_MARKERS = {
        "আপনি", "আপনারা", "আপনাকে", "আপনাদের", "আপনার", "তিনি", "তাঁরা", "তাঁকে", "তাঁদের", "তাঁর",
        "মহাশয়", "মহাশয়া", "শ্রদ্ধেয়", "নমস্কার", "প্রণাম", "আজ্ঞে", "দয়া করে"
    }

    FAMILIAR_MARKERS = {
        "তুমি", "তোমরা", "তোমাকে", "তোমাদের", "তোমার", "সে", "তারা", "তাকে", "তাদের", "তার",
        "অনুগ্রহ করে", "প্রিয়", "বন্ধু"
    }

    INTIMATE_MARKERS = {
        "তুই", "তোরা", "তোকে", "তোর", "তোদের", "রে"
    }

    SADHU_MARKERS = {
        "করিতেছেন", "করিতেছে", "করিয়াছিল", "তাহাকে", "তাহারা", "যাঁহার", "উহার",
        "হইয়াছিল", "সহিত", "হইতে", "যাইতেছে", "আসিতেছে", "বলিলেন"
    }

    CHOLITO_MARKERS = {
        "করছেন", "করছে", "করেছিল", "তাকে", "তারা", "যার", "ওর",
        "হয়েছিল", "সাথে", "থেকে", "যাচ্ছে", "আসছে", "বললেন"
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
        Calculates politeness index, dominant register, and address tier.
        """
        sup_count = sum(1 for t in tokens if t in self.SUPERIOR_MARKERS or t.endswith(("েন", "ুন", "বেন")))
        fam_count = sum(1 for t in tokens if t in self.FAMILIAR_MARKERS or t.endswith(("ো", "বে", "লে")))
        int_count = sum(1 for t in tokens if t in self.INTIMATE_MARKERS or t.endswith(("িস", "লি", "বি")))

        # Check verbal endings specifically
        if sup_count > fam_count and sup_count > int_count:
            tier = "superior"
            politeness_score = 0.95
        elif int_count > fam_count and int_count > sup_count:
            tier = "intimate"
            politeness_score = 0.35
        else:
            tier = "familiar"
            politeness_score = 0.70

        # Register evaluation
        sadhu_count = sum(1 for t in tokens if t in self.SADHU_MARKERS)
        cholito_count = sum(1 for t in tokens if t in self.CHOLITO_MARKERS)
        
        register = "cholito"
        if sadhu_count > cholito_count:
            register = "sadhu"

        return {
            "tier": tier,
            "politeness_score": politeness_score,
            "register": register,
            "counts": {
                "superior": sup_count,
                "familiar": fam_count,
                "intimate": int_count,
                "sadhu": sadhu_count,
                "cholito": cholito_count
            }
        }

    def detect_guru_chondali(self, tokens: List[str]) -> List[Dict[str, Any]]:
        """
        Detects Guru-Chondali Dosh (inappropriate mixing of Sadhu and Cholito forms in one utterance).
        """
        found_sadhu = [t for t in tokens if t in self.SADHU_MARKERS]
        found_cholito = [t for t in tokens if t in self.CHOLITO_MARKERS]

        violations = []
        if found_sadhu and found_cholito:
            violations.append({
                "rule": "GURU_CHONDALI_DOSH",
                "message": f"Stylistic solecism: Mixed Sadhu forms {found_sadhu} with Cholito forms {found_cholito}.",
                "sadhu_tokens": found_sadhu,
                "cholito_tokens": found_cholito
            })
        return violations

    def get_epistolary_closing(self, tier: str = "superior") -> str:
        """Returns culturally authentic letter closing formulas."""
        if tier == "superior":
            return "আপনার বিশ্বস্ত"
        elif tier == "intimate":
            return "তোর ভাই/বন্ধু"
        return "তোমার প্রিয় বন্ধু"
