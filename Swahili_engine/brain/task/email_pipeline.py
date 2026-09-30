"""
Swahili Engine — Email Task Pipeline
Composes and audits formal business correspondence and everyday polite Swahili communications.
"""

from typing import Dict, Any, Optional
from ..skills.generation import generate_formal_email, generate_polite_message
from ..skills.tokenization import split_sentences

FORMAL_OPENINGS = [
    "kwa mheshimiwa", "ndugu", "mheshimiwa", "kwa bwana", "kwa bibi", "kwa heshima"
]

INFORMAL_OPENINGS = [
    "hujambo", "habari", "shikamoo", "salaam"
]

FORMAL_CLOSINGS = [
    "wasalaam", "wako mwaminifu", "wako mtiifu", "wako katika ujenzi wa taifa", "kwa heshima"
]

INFORMAL_CLOSINGS = [
    "wako rafiki", "kila la heri", "asante sana", "tutaonana"
]

class SwahiliEmailPipeline:
    """Pipeline for composing and auditing Swahili email and epistolary correspondence."""

    def __init__(self):
        pass

    def compose(
        self,
        form: str,
        recipient_name: str,
        body: str,
        sender_name: str,
        recipient_title: str = "Mkurugenzi",
        organization: str = "Solo Rock"
    ) -> str:
        """Compose business formal or polite everyday communication."""
        if form.lower() == "formal":
            return generate_formal_email(recipient_name, recipient_title, body, sender_name, organization)
        else:
            return generate_polite_message(recipient_name, body, sender_name)

    def audit(self, email_text: str) -> Dict[str, Any]:
        """Audit an email for appropriate openings, closings, and register consistency."""
        text_lower = email_text.lower()
        
        has_formal_open = any(op in text_lower for op in FORMAL_OPENINGS)
        has_informal_open = any(op in text_lower for op in INFORMAL_OPENINGS)
        has_opening = has_formal_open or has_informal_open
        
        has_formal_close = any(cl in text_lower for cl in FORMAL_CLOSINGS)
        has_informal_close = any(cl in text_lower for cl in INFORMAL_CLOSINGS)
        has_closing = has_formal_close or has_informal_close
        
        # Register identification
        if has_formal_open or has_formal_close:
            register = "formal"
        elif has_informal_open or has_informal_close:
            register = "polite_informal"
        else:
            register = "neutral"
            
        passed = has_opening and has_closing
        
        return {
            "has_opening": has_opening,
            "has_closing": has_closing,
            "register": register,
            "is_formal": register == "formal",
            "passed": passed
        }
