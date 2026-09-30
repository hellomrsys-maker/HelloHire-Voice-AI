"""
Polish Honorific Register Cognitive Analyzer
Validates formal address (Pan / Pani / Państwo) 3rd-person concord and detects register clashes.
"""

from typing import Dict, Any, List
from ..skills.tokenization import PolishTokenizer
from ..skills.honorific_deixis_engine import PolishHonorificDeixisEngine

class PolishHonorificRegisterAnalyzer:
    def __init__(self):
        self.tokenizer = PolishTokenizer()
        self.honorific_engine = PolishHonorificDeixisEngine()

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        low_tokens = [t.lower() for t in tokens if t not in {".", ",", "!", "?", ";", ":"}]

        res = self.honorific_engine.verify_honorific_agreement(tokens)

        # Detect informal pronouns: ty, cię, tobie, twój, twoja
        has_informal = any(t in {"ty", "cię", "tobie", "twój", "twoja", "twoje"} for t in low_tokens)
        has_formal = res["is_formal"]

        is_mixed = has_formal and has_informal
        if has_formal:
            register_code = 2  # Formal Pan/Pani
            register_str = "formal_pan_pani"
        elif has_informal:
            register_code = 1  # Informal ty
            register_str = "informal_ty"
        else:
            register_code = 0  # Neutral
            register_str = "neutral"

        warnings = []
        if is_mixed:
            warnings.append("Register Clashing: Message mixes formal 'Pan/Pani' address with informal 'ty' pronouns.")

        score = 100 if res["honorific_concord_valid"] and not is_mixed else 60

        return {
            "register": register_str,
            "register_code": register_code,
            "concord_valid": res["honorific_concord_valid"],
            "is_mixed": is_mixed,
            "score": score,
            "errors": res["errors"],
            "warnings": warnings
        }
