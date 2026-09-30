"""Turkish Case & Postposition Valency Analyzer.

Audits postpositional phrases to ensure preceding noun phrases
carry obligatory case markings, and computes the clausal case diversity bitfield.
"""

from typing import Dict, Any, List
from ..skills.tokenization import TurkishTokenizer
from ..skills.pos_tagging import TurkishPOSTagger
from ..skills.vowel_harmony_engine import TurkishVowelHarmonyEngine


class TurkishCasePostpositionAnalyzer:
    CASE_BITS = {
        "nom": 1 << 0,
        "acc": 1 << 1,
        "dat": 1 << 2,
        "loc": 1 << 3,
        "abl": 1 << 4,
        "gen": 1 << 5
    }

    POSTPOSITION_CASES = {
        "kadar": "dat",
        "doğru": "dat",
        "göre": "dat",
        "rağmen": "dat",
        "karşın": "dat",
        "sonra": "abl",
        "önce": "abl",
        "beri": "abl",
        "dolayı": "abl",
        "ötürü": "abl",
        "için": "nom",
        "ile": "nom",
        "gibi": "nom"
    }

    def __init__(
        self,
        tokenizer: TurkishTokenizer = None,
        pos_tagger: TurkishPOSTagger = None,
        harmony_engine: TurkishVowelHarmonyEngine = None
    ):
        self.tokenizer = tokenizer or TurkishTokenizer()
        self.pos_tagger = pos_tagger or TurkishPOSTagger()
        self.harmony = harmony_engine or TurkishVowelHarmonyEngine()

    def detect_case_suffix(self, token: str) -> str:
        """Heuristically detects case marker on a Turkish nominal token."""
        tok_low = TurkishTokenizer.turkish_lower(token)
        if "'" in tok_low:
            _, sfx = tok_low.split("'", 1)
        else:
            sfx = tok_low

        if sfx.endswith(("den", "dan", "ten", "tan")):
            return "abl"
        if sfx.endswith(("de", "da", "te", "ta")):
            return "loc"
        if sfx.endswith(("e", "a", "ye", "ya")):
            return "dat"
        if sfx.endswith(("i", "ı", "ü", "u", "yi", "yı", "yü", "yu")) and len(sfx) >= 3:
            return "acc"
        if sfx.endswith(("in", "ın", "ün", "un", "nin", "nın", "nün", "nun")):
            return "gen"
        return "nom"

    def analyze(self, text: str) -> Dict[str, Any]:
        """Performs full audit of case government across postpositions."""
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag(tokens)

        case_bitfield = 0
        postposition_checks = []
        issues = []

        for i, item in enumerate(tagged):
            tok = item["token"]
            tok_low = TurkishTokenizer.turkish_lower(tok)
            pos = item["pos"]

            c_detected = self.detect_case_suffix(tok)
            case_bitfield |= self.CASE_BITS.get(c_detected, 0)

            if pos == "ADP" and tok_low in self.POSTPOSITION_CASES:
                req_case = self.POSTPOSITION_CASES[tok_low]
                if i > 0:
                    prev_item = tagged[i - 1]
                    prev_tok = prev_item["token"]
                    prev_pos = prev_item["pos"]

                    # If 'sonra' or 'önce' is preceded by a conjunction, verb, or punctuation, it functions adverbially
                    if tok_low in ("sonra", "önce", "beri") and prev_pos in ("CCONJ", "PUNCT", "VERB", "ADV"):
                        continue

                    prev_case = self.detect_case_suffix(prev_tok)
                    # Check compatibility
                    is_valid = (prev_case == req_case) or (req_case == "nom")

                    postposition_checks.append({
                        "postposition": tok,
                        "dependent": prev_tok,
                        "required_case": req_case,
                        "observed_case": prev_case,
                        "is_valid": is_valid
                    })

                    if not is_valid:
                        issues.append({
                            "type": "case_postposition_mismatch",
                            "message": f"Postposition '{tok}' requires {req_case.upper()} case, but '{prev_tok}' was observed as {prev_case.upper()}.",
                            "severity": "error"
                        })


        case_count = bin(case_bitfield).count("1")

        return {
            "text": text,
            "case_bitfield": case_bitfield,
            "case_count": case_count,
            "postposition_checks": postposition_checks,
            "issues": issues,
            "is_valid": len(issues) == 0
        }
