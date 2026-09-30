"""
Polish Email Task Pipeline
Generates and verifies professional and informal Polish correspondence.
"""

from typing import Dict, Any, List
from ..skills.generation import PolishGenerator
from ..skills.tokenization import PolishTokenizer

class PolishEmailPipeline:
    def __init__(self):
        self.generator = PolishGenerator()
        self.tokenizer = PolishTokenizer()

    def generate(self, recipient_surname: str, recipient_gender: str, purpose: str, register: str = "formal") -> Dict[str, Any]:
        template = self.generator.generate_email_template(recipient_surname, recipient_gender, purpose, register)
        return {
            "status": "success",
            "email": template
        }

    def verify_register(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        low_tokens = [t.lower() for t in tokens if t not in {".", ",", "!", "?", ";", ":"}]

        formal_count = sum(1 for t in low_tokens if t in {"pan", "pani", "państwo", "panem", "panią", "państwem"})
        informal_count = sum(1 for t in low_tokens if t in {"ty", "cię", "tobie", "twój", "twoja", "twoje", "twoim"})

        is_mixed = formal_count > 0 and informal_count > 0
        assigned_register = "formal" if formal_count > informal_count else ("informal" if informal_count > 0 else "neutral")

        warnings = []
        if is_mixed:
            warnings.append(
                f"Register Discord: Email contains {formal_count} formal honorifics and {informal_count} informal pronouns."
            )

        return {
            "register": assigned_register,
            "formal_tokens": formal_count,
            "informal_tokens": informal_count,
            "is_consistent": not is_mixed,
            "warnings": warnings
        }
