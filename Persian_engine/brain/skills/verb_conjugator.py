"""
Persian Verb Conjugator
Handles dual stems (Past Stem & Present Stem) and person-number agreement suffixes.
"""

from typing import Dict, Any, List, Optional
from Persian_engine.brain.skills.tokenization import ZWNJ

# Irregular & high-frequency verb paradigms
VERB_PARADIGM_REGISTRY = {
    "رفتن": {"past_stem": "رفت", "present_stem": "رو", "translit": "raftan"},
    "خوردن": {"past_stem": "خورد", "present_stem": "خور", "translit": "khordan"},
    "دیدن": {"past_stem": "دید", "present_stem": "بین", "translit": "didan"},
    "کردن": {"past_stem": "کرد", "present_stem": "کن", "translit": "kardan"},
    "شدن": {"past_stem": "شد", "present_stem": "شو", "translit": "shodan"},
    "زدن": {"past_stem": "زد", "present_stem": "زن", "translit": "zadan"},
    "دادن": {"past_stem": "داد", "present_stem": "ده", "translit": "dādan"},
    "گرفتن": {"past_stem": "گرفت", "present_stem": "گیر", "translit": "gereftan"},
    "گفتن": {"past_stem": "گفت", "present_stem": "گو", "translit": "goftan"},
    "آمدن": {"past_stem": "آمد", "present_stem": "آی", "translit": "āmadan"},
    "خواندن": {"past_stem": "خواند", "present_stem": "خوان", "translit": "khāndan"},
    "نوشتن": {"past_stem": "نوشت", "present_stem": "نویس", "translit": "neveshtan"},
    "داشتن": {"past_stem": "داشت", "present_stem": "دار", "translit": "dāshtan"}
}

# Personal endings for 6 persons
PERSONAL_ENDINGS_PRESENT = {
    1: "م",    # -am
    2: "ی",    # -i
    3: "د",    # -ad
    4: "یم",   # -im
    5: "ید",   # -id
    6: "ند"    # -and
}

PERSONAL_ENDINGS_PAST = {
    1: "م",    # -am
    2: "ی",    # -i
    3: "",     # zero
    4: "یم",   # -im
    5: "ید",   # -id
    6: "ند"    # -and
}

class PersianVerbConjugator:
    """
    Synthesizes and analyzes Persian conjugated verbs:
    - Past Simple: Past Stem + Past Endings
    - Present Continuous: mi- (می‌) + Present Stem + Present Endings
    - Past Continuous: mi- (می‌) + Past Stem + Past Endings
    - Subjunctive Present: be- (بـ) + Present Stem + Present Endings
    """

    def get_stems(self, infinitive: str) -> Tuple[str, str]:
        """Returns (past_stem, present_stem) for a given infinitive."""
        clean = infinitive.strip()
        if clean in VERB_PARADIGM_REGISTRY:
            entry = VERB_PARADIGM_REGISTRY[clean]
            return entry["past_stem"], entry["present_stem"]
            
        # Regular fallback: drop 'an' / 'tan' / 'dan'
        if clean.endswith("دن") or clean.endswith("تن"):
            past = clean[:-1] # drop nun
        else:
            past = clean
        present = past # approximation for unlisted
        return past, present

    def conjugate(self, infinitive: str, tense: str, person: int, negative: bool = False) -> str:
        """
        Conjugates an infinitive verb for person (1..6) and tense.
        Tenses supported: 'past_simple', 'present_continuous', 'past_continuous', 'subjunctive'.
        """
        past_stem, pres_stem = self.get_stems(infinitive)
        
        # 1. Past Simple (گذشته ساده)
        if tense == "past_simple":
            ending = PERSONAL_ENDINGS_PAST[person]
            verb = f"{past_stem}{ending}"
            if negative:
                verb = f"ن{verb}"
            return verb
            
        # 2. Present Continuous (حال استمراری / مضارع اخباری)
        elif tense == "present_continuous":
            ending = PERSONAL_ENDINGS_PRESENT[person]
            prefix = f"نمی{ZWNJ}" if negative else f"می{ZWNJ}"
            return f"{prefix}{pres_stem}{ending}"
            
        # 3. Past Continuous (گذشته استمراری)
        elif tense == "past_continuous":
            ending = PERSONAL_ENDINGS_PAST[person]
            prefix = f"نمی{ZWNJ}" if negative else f"می{ZWNJ}"
            return f"{prefix}{past_stem}{ending}"
            
        # 4. Subjunctive Present (مضارع التزامی)
        elif tense == "subjunctive":
            ending = PERSONAL_ENDINGS_PRESENT[person]
            prefix = "ن" if negative else "ب"
            # If present stem starts with vowel (like آی)
            if pres_stem.startswith("آ"):
                stem_mod = "یا" + pres_stem[1:]
                return f"{prefix}{stem_mod}{ending}"
            return f"{prefix}{pres_stem}{ending}"
            
        return past_stem
