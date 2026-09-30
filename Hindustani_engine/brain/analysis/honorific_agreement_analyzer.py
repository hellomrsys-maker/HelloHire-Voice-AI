"""
Hindustani Honorific Agreement Cognitive Analyzer.
Validates concord between personal address pronouns (aap, tum, tu) and their
obligatory verbal/auxiliary agreement forms.
"""

from typing import Dict, Any, List, Tuple
from ..skills.tokenization import HindustaniTokenizer
from ..skills.pos_tagging import HindustaniPOSTagger


class HonorificAgreementAnalyzer:
    """
    Cognitive analyzer verifying concord across the 3 Hindustani honorific address tiers.
    """

    AAP_PRONOUNS = {"aap", "आप"}
    TUM_PRONOUNS = {"tum", "तुम"}
    TU_PRONOUNS = {"tu", "तू"}

    AAP_AUXILIARIES = {"hain", "the", "honge", "हैं", "थे", "होंगे"}
    TUM_AUXILIARIES = {"ho", "the", "hoge", "हो", "थे", "होगे"}
    TU_AUXILIARIES = {"hai", "tha", "thi", "hoga", "hogi", "है", "था", "थी", "होगा", "होगी"}

    def __init__(self):
        self.tokenizer = HindustaniTokenizer()
        self.tagger = HindustaniPOSTagger()

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        low_tokens = [t.lower() for t in tokens]

        has_aap = any(t in self.AAP_PRONOUNS for t in low_tokens) or any(t in self.AAP_PRONOUNS for t in tokens)
        has_tum = any(t in self.TUM_PRONOUNS for t in low_tokens) or any(t in self.TUM_PRONOUNS for t in tokens)
        has_tu = any(t in self.TU_PRONOUNS for t in low_tokens) or any(t in self.TU_PRONOUNS for t in tokens)

        concord_valid = True
        error_msg = None

        if has_aap:
            # Requires plural/honorific auxiliary or future ending
            has_valid_aux = any(t in self.AAP_AUXILIARIES for t in low_tokens) or any(t in self.AAP_AUXILIARIES for t in tokens) or any(t.endswith(("te", "enge", "ें", "ेंगे")) for t in low_tokens)
            has_invalid_singular = any(t in {"hai", "tha", "है", "था"} for t in low_tokens)
            if has_invalid_singular and not has_valid_aux:
                concord_valid = False
                error_msg = "Discordance honorifique: 'Aap' exige une forme verbale honorifique plurielle ('hain' / 'the'), pas singulière ('hai' / 'tha')."

        elif has_tum:
            has_valid_aux = any(t in self.TUM_AUXILIARIES for t in low_tokens) or any(t in self.TUM_AUXILIARIES for t in tokens) or any(t.endswith(("oge", "ो", "ोगे")) for t in low_tokens)
            has_invalid_hai = any(t in {"hai", "hain", "है", "हैं"} for t in low_tokens) and "ho" not in low_tokens and "हो" not in tokens
            if has_invalid_hai:
                concord_valid = False
                error_msg = "Discordance: 'Tum' exige l'auxiliaire 'ho' (ex: 'tum karte ho'), pas 'hai' ni 'hain'."

        return {
            "text": text,
            "has_aap": has_aap,
            "has_tum": has_tum,
            "has_tu": has_tu,
            "is_concord_valid": concord_valid,
            "message": "Accord honorifique conforme." if concord_valid else error_msg
        }
