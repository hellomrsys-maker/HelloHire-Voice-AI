"""
Spanish Morphosyntactic Agreement Checker (Concordancia).
Validates gender (masculine/feminine) and number (singular/plural) harmony in noun phrases.
"""

from typing import Dict, Any, List, Tuple
from ..skills.tokenization import SpanishTokenizer
from ..skills.pos_tagging import SpanishPOSTagger


class SpanishAgreementChecker:
    """
    Diagnostic checker for nominal and verbal morphosyntactic concord.
    """

    def __init__(self):
        self.tokenizer = SpanishTokenizer()
        self.tagger = SpanishPOSTagger()

    def check_noun_phrase_agreement(self, det: str, noun: str, adj: str) -> Dict[str, Any]:
        """
        Validates gender and number concord across Determiner + Noun + Adjective.
        """
        d = det.lower().strip()
        n = noun.lower().strip()
        a = adj.lower().strip()

        # Determiner gender & number
        is_fem_d = d in {"la", "las", "una", "unas", "esta", "estas", "esa", "esas"}
        is_plur_d = d in {"los", "las", "unos", "unas", "estos", "estas", "esos", "esas", "mis", "tus", "sus"}

        # Noun gender & number
        is_fem_n = n.endswith(("a", "as", "ción", "sión", "dad", "tad")) or n in {"mano", "manos", "noche", "noches"}
        is_plur_n = n.endswith(("s", "es")) and n not in {"mes", "país", "tres", "autobús"}

        # Adjective gender & number
        is_fem_a = a.endswith(("a", "as")) or a.endswith(("e", "es", "al", "les", "ar", "ares", "nte", "ntes"))
        is_plur_a = a.endswith(("s", "es"))

        # Invariant adjectives (e.g. grande, azul, feliz) agree with both genders
        is_invariant_adj = a.endswith(("e", "es", "al", "les", "ar", "ares", "nte", "ntes", "z", "ces"))

        gender_match = (is_fem_d == is_fem_n) and (is_fem_n == is_fem_a or is_invariant_adj)
        number_match = (is_plur_d == is_plur_n == is_plur_a)

        is_valid = gender_match and number_match
        phrase = f"{det} {noun} {adj}"

        errors = []
        if not gender_match:
            errors.append(f"Gender mismatch: det({d}), noun({n}), adj({a})")
        if not number_match:
            errors.append(f"Number mismatch: det({d}), noun({n}), adj({a})")

        return {
            "phrase": phrase,
            "is_valid": is_valid,
            "gender_concord": gender_match,
            "number_concord": number_match,
            "errors": errors,
        }
