"""
Mandarin Chengyu (成语) Four-Character Idiomatic Skill.
Identifies classical idioms, verifies historical semantics, and evaluates stylistic density.
"""

import json
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "rules", "chengyu_db.json")


class ChengyuEngine:
    """
    Evaluator and dictionary lookup for 4-character classical Chinese idioms.
    """

    def __init__(self, db_path: Optional[str] = None):
        target = db_path or DB_PATH
        self.chengyu_data: Dict[str, Any] = {}
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                raw = json.load(f)
                self.chengyu_data = raw.get("chengyu", {})

    def extract_chengyu(self, text: str) -> List[Dict[str, Any]]:
        """Identifies all recognized 4-character chengyu in an input text."""
        detected = []
        n = len(text)
        for i in range(n - 3):
            quad = text[i:i + 4]
            if quad in self.chengyu_data:
                info = dict(self.chengyu_data[quad])
                info["idiom"] = quad
                info["position"] = i
                detected.append(info)
        return detected

    def evaluate_density(self, text: str) -> Dict[str, Any]:
        """Calculates idiom density and stylistic sophistication index."""
        detected = self.extract_chengyu(text)
        total_chars = max(1, len(text.replace(" ", "").replace("，", "").replace("。", "")))
        idiom_char_count = len(detected) * 4
        density_ratio = idiom_char_count / total_chars

        # Stylistic classification
        level = "Basic / Colloquial"
        if len(detected) >= 2 or density_ratio > 0.15:
            level = "Highly Literary / Scholarly (典雅)"
        elif len(detected) == 1:
            level = "Standard Formal / Expressive (标准书面语)"

        idiom_strings = [d["idiom"] for d in detected]
        return {
            "idiom_count": len(detected),
            "density_ratio": round(density_ratio, 4),
            "stylistic_level": level,
            "detected_idioms": idiom_strings,
            "detected_idiom_details": detected,
        }
