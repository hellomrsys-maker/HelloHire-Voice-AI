"""
Persian Light Verb Construction (LVC) Engine
Deconstructs and validates complex predicates (اسم/صفت + فعل معین).
"""

from typing import Dict, Any, List, Optional, Tuple

LIGHT_VERB_MAP = {
    "کردن": {"type": "transitive_agentive", "passive_counterpart": "شدن"},
    "شدن": {"type": "inchoative_passive", "active_counterpart": "کردن"},
    "زدن": {"type": "contact_percussive", "passive_counterpart": "خوردن"},
    "دادن": {"type": "transfer_causative", "passive_counterpart": "گرفتن"},
    "گرفتن": {"type": "receptive_inceptive", "active_counterpart": "دادن"},
    "داشتن": {"type": "stative_durative", "passive_counterpart": None},
    "کشیدن": {"type": "protracted_durative", "passive_counterpart": None},
    "خوردن": {"type": "patientive_absorption", "active_counterpart": "زدن"}
}

# Common non-verbal elements
NON_VERBAL_ELEMENTS = {
    "کار": ["کردن"],
    "صحبت": ["کردن"],
    "پیدا": ["کردن", "شدن"],
    "کمک": ["کردن"],
    "زندگی": ["کردن"],
    "نگاه": ["کردن"],
    "حرف": ["زدن"],
    "زنگ": ["زدن"],
    "لبخند": ["زدن"],
    "انجام": ["دادن", "شدن"],
    "نشان": ["دادن"],
    "پاسخ": ["دادن"],
    "یاد": ["گرفتن", "دادن"],
    "تصمیم": ["گرفتن"],
    "دوست": ["داشتن"],
    "آغاز": ["شدن", "کردن"],
    "تمام": ["شدن", "کردن"],
    "تسلیم": ["شدن", "کردن"],
    "حرکت": ["کردن"]
}

LIGHT_VERB_STEMS = {
    "کردن": ["کرد", "کن", "کردن"],
    "شدن": ["شد", "شو", "شدن"],
    "زدن": ["زد", "زن", "زدن"],
    "دادن": ["داد", "ده", "دادن"],
    "گرفتن": ["گرفت", "گیر", "گرفتن"],
    "داشتن": ["داشت", "دار", "داشتن"],
    "کشیدن": ["کشید", "کش", "کشیدن"],
    "خوردن": ["خورد", "خور", "خوردن"]
}

class PersianLightVerbEngine:
    """
    Identifies, analyzes, and transforms Persian complex predicates (Compound Verbs).
    """

    def is_light_verb_compound(self, non_verbal: str, verbal_token: str) -> bool:
        """Checks if a noun/adjective and a verbal root form an established complex predicate."""
        clean_nv = non_verbal.strip()
        clean_v = verbal_token.strip()
        
        # Strip prefixes like mi-, be-, ne-, na-
        v_stem = clean_v
        for prefix in ["می‌", "می\u200c", "می", "نمی‌", "نمی\u200c", "نمی", "ب", "ن"]:
            if v_stem.startswith(prefix) and len(v_stem) > len(prefix):
                v_stem = v_stem[len(prefix):]
                break

        if clean_nv in NON_VERBAL_ELEMENTS:
            allowed_infinitives = NON_VERBAL_ELEMENTS[clean_nv]
            for inf in allowed_infinitives:
                if clean_v == inf or clean_v in inf or inf in clean_v:
                    return True
                stems = LIGHT_VERB_STEMS.get(inf, [inf[:-1]])
                for s in stems:
                    if s in v_stem or v_stem.startswith(s):
                        return True
        return False

    def extract_compound_predicate(self, words: List[str]) -> List[Dict[str, Any]]:
        """
        Scans a sequence of words to detect consecutive non-verbal + light verb pairs.
        """
        compounds = []
        for i in range(len(words) - 1):
            w1 = words[i]
            w2 = words[i + 1]
            if self.is_light_verb_compound(w1, w2):
                compounds.append({
                    "non_verbal": w1,
                    "light_verb": w2,
                    "compound": f"{w1} {w2}",
                    "indices": (i, i + 1)
                })
        return compounds

    def transform_voice(self, non_verbal: str, current_light_verb: str) -> Optional[str]:
        """
        Transforms an active complex predicate to its inchoative/passive equivalent
        (e.g., پیدا کردن -> پیدا شدن, انجام دادن -> انجام شدن).
        """
        for base_lv, data in LIGHT_VERB_MAP.items():
            if base_lv in current_light_verb:
                passive_lv = data.get("passive_counterpart")
                if passive_lv:
                    return f"{non_verbal} {passive_lv}"
        return None
