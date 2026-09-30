"""Russian Motion Verb Skill.

Classifies determinate (unidirectional) vs indeterminate (multidirectional) motion verbs,
analyzes spatial prefixation vectors, and resolves aspectual transitions.
"""

import json
import os
from typing import Dict, Any, Optional, List


class RussianMotionVerbEngine:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "motion_verbs_matrix.json")

        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

        self.base_pairs = self.db.get("base_pairs", [])
        self.prefixes = self.db.get("prefixes", {})
        
        # Build quick lookups
        self.det_map = {pair["det"]: pair for pair in self.base_pairs}
        self.indet_map = {pair["indet"]: pair for pair in self.base_pairs}

    def analyze_motion_verb(self, verb: str) -> Dict[str, Any]:
        """Analyzes a Russian verb to determine if it is a motion verb, its determinacy, prefix, and aspect."""
        v_low = verb.lower()

        # Check unprefixed base forms
        if v_low in self.det_map:
            return {
                "is_motion_verb": True,
                "type": "determinate",
                "partner": self.det_map[v_low]["indet"],
                "prefix": None,
                "aspect": "impf",
                "gloss": self.det_map[v_low]["gloss"]
            }
        if v_low in self.indet_map:
            return {
                "is_motion_verb": True,
                "type": "indeterminate",
                "partner": self.indet_map[v_low]["det"],
                "prefix": None,
                "aspect": "impf",
                "gloss": self.indet_map[v_low]["gloss"]
            }

        # Check prefixed forms
        det_roots = ("идти", "йти", "шел", "шёл", "шла", "шли", "еха", "еде", "едут", "беж", "лет", "плы", "нес", "вед", "вез")
        indet_roots = ("ходи", "ход", "езжа", "езд", "бега", "лета", "плава", "носи", "води", "вози")

        for pref, pinfo in self.prefixes.items():
            if v_low.startswith(pref):
                root = v_low[len(pref):]
                if any(root.startswith(dr) for dr in det_roots) or root in self.det_map:
                    return {
                        "is_motion_verb": True,
                        "type": "prefixed_determinate",
                        "prefix": pref,
                        "meaning": pinfo["meaning"],
                        "governed_prep": pinfo["prep_trigger"],
                        "aspect": "perf"
                    }
                if any(root.startswith(ir) for ir in indet_roots) or root in self.indet_map:
                    return {
                        "is_motion_verb": True,
                        "type": "prefixed_indeterminate",
                        "prefix": pref,
                        "meaning": pinfo["meaning"],
                        "governed_prep": pinfo["prep_trigger"],
                        "aspect": "impf"
                    }


        return {
            "is_motion_verb": False,
            "type": None,
            "prefix": None,
            "aspect": None
        }
