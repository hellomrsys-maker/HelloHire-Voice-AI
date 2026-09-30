"""
Dutch Email Task Pipeline
Generates and verifies professional and informal Dutch business/personal emails.
"""

from typing import Dict, Any, List
from ..skills.generation import DutchGenerator
from ..skills.tokenization import DutchTokenizer

class DutchEmailPipeline:
    def __init__(self):
        self.generator = DutchGenerator()
        self.tokenizer = DutchTokenizer()

    def generate(self, recipient_name: str, purpose: str, register: str = "formal") -> Dict[str, Any]:
        template = self.generator.generate_email_template(recipient_name, purpose, register)
        return {
            "status": "success",
            "email": template
        }

    def verify_register_consistency(self, email_text: str) -> Dict[str, Any]:
        """
        Detects mixed register (e.g. mixing 'u' and 'je' in the same communication).
        """
        tokens = self.tokenizer.tokenize(email_text)
        low_tokens = [t.lower() for t in tokens]

        formal_count = sum(1 for t in low_tokens if t in {"u", "uw"})
        informal_count = sum(1 for t in low_tokens if t in {"je", "jij", "jou", "jouw"})

        is_mixed = formal_count > 0 and informal_count > 0
        assigned_register = "formal" if formal_count > informal_count else ("informal" if informal_count > 0 else "neutral")

        warnings = []
        if is_mixed:
            warnings.append(
                f"Register Inconsistency: Found {formal_count} formal pronouns ('u/uw') and "
                f"{informal_count} informal pronouns ('je/jij/jouw') in the same message."
            )

        return {
            "register": assigned_register,
            "formal_tokens": formal_count,
            "informal_tokens": informal_count,
            "is_consistent": not is_mixed,
            "warnings": warnings
        }
