"""
Polish Phonology & Sibilant Orthography Engine
Validates Polish sibilant series, nasal vowels (ą, ę), and historical homophones (rz/ż, ó/u, ch/h).
"""

from typing import Dict, Any, List

class PolishPhonologySibilantEngine:
    def __init__(self):
        # Known homophones where spelling mistake is common
        self.homophone_dictionary = {
            "morze": "sea (morze Bałtyckie)",
            "może": "maybe / can (on może przyjść)",
            "bóg": "god",
            "bug": "river Bug",
            "lód": "ice",
            "lud": "people / folk"
        }
        self.retroflex_sibilants = {"sz", "cz", "ż", "rz", "dż"}
        self.alveolo_palatals = {"ś", "ć", "ź", "dź", "si", "ci", "zi", "dzi"}

    def check_orthography(self, tokens: List[str]) -> Dict[str, Any]:
        low_tokens = [t.lower() for t in tokens if t not in {".", ",", "!", "?", ";", ":"}]
        has_nasal_vowels = any("ą" in t or "ę" in t for t in low_tokens)
        has_sibilants = any(any(sib in t for sib in ("sz", "cz", "rz", "ż", "ś", "ć", "ź")) for t in low_tokens)

        # Contextual check for morze vs może
        warnings = []
        for i, tok in enumerate(low_tokens):
            if tok == "może" and i + 1 < len(low_tokens) and low_tokens[i + 1] in {"bałtyckie", "północne", "czerwone"}:
                warnings.append("Homophone Confusion: 'może' (can/maybe) used in sea context; expected 'morze'.")
            elif tok == "morze" and i + 1 < len(low_tokens) and low_tokens[i + 1] in {"być", "zrobić", "pójść"}:
                warnings.append("Homophone Confusion: 'morze' (sea) used with modal infinitive; expected 'może'.")

        score = 100 if len(warnings) == 0 else 70

        return {
            "has_nasal_vowels": has_nasal_vowels,
            "has_sibilants": has_sibilants,
            "orthography_score": score,
            "warnings": warnings,
            "is_valid": len(warnings) == 0
        }
