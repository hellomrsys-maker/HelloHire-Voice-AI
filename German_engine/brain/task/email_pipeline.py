"""
German Engine — Email Task Pipeline
Composes and validates formal and informal German email correspondence.
"""

from typing import Dict, Any, Optional
from ..skills.generation import generate_formal_email, generate_informal_message
from ..skills.pragmatics_engine import analyze_register
from ..skills.tokenization import tokenize_words

class GermanEmailPipeline:
    """Pipeline for composing and auditing German email communication."""

    def __init__(self):
        pass

    def compose(self, form: str, recipient_name: str, body: str, sender_name: str, title: str = "Herr") -> str:
        """Compose formal or informal email according to German business etiquette."""
        if form.lower() == "formal":
            return generate_formal_email(title, recipient_name, body, sender_name)
        else:
            return generate_informal_message(recipient_name, body, sender_name)

    def audit(self, email_text: str) -> Dict[str, Any]:
        """Audit an existing email for register consistency and standard closing."""
        tokens = tokenize_words(email_text)
        reg = analyze_register(email_text, tokens)
        
        has_closing = (
            "Mit freundlichen Grüßen" in email_text or
            "Mit besten Grüßen" in email_text or
            "Liebe Grüße" in email_text or
            "Herzliche Grüße" in email_text or
            "Viele Grüße" in email_text
        )
        
        # Check rule: German closing does NOT have a trailing comma
        has_invalid_closing_comma = "Mit freundlichen Grüßen," in email_text or "Liebe Grüße," in email_text
        
        return {
            "register": reg["register"],
            "is_register_consistent": reg["is_consistent"],
            "has_proper_closing": has_closing,
            "has_invalid_closing_comma": has_invalid_closing_comma,
            "passed": reg["is_consistent"] and has_closing and not has_invalid_closing_comma
        }
