"""
Vietnamese Email Task Pipeline
Generates and audits formal Vietnamese administrative and corporate correspondence.
"""

from typing import Dict, Any, Optional
from Vietnamese_engine.brain.skills.pragmatics_engine import VietnamesePragmaticsEngine

class VietnameseEmailPipeline:
    """
    Administrative correspondence pipeline enforcing Vietnamese epistolary protocol.
    """

    def __init__(self):
        self.pragmatics = VietnamesePragmaticsEngine()

    def generate_formal_email(
        self,
        recipient_name: str,
        recipient_title: str,
        body: str,
        sender_name: str
    ) -> str:
        """
        Synthesizes an official administrative letter.
        """
        return self.pragmatics.format_formal_letter(
            recipient_name=recipient_name,
            recipient_title=recipient_title,
            body=body,
            sender_name=sender_name
        )

    def audit_incoming_email(self, email_text: str) -> Dict[str, Any]:
        """Audits email for formal salutation, closing, and register tier."""
        reg = self.pragmatics.detect_register(email_text)
        has_salutation = "kính gửi" in email_text.lower() or "thưa" in email_text.lower()
        has_closing = "trân trọng" in email_text.lower() or "kính chúc" in email_text.lower()
        
        is_professional = has_salutation and has_closing and reg["dominant_register"] in {"high_formal", "formal"}
        return {
            "has_salutation": has_salutation,
            "has_closing": has_closing,
            "register": reg["dominant_register"],
            "tier_level": reg["tier_level"],
            "is_professional": is_professional
        }
