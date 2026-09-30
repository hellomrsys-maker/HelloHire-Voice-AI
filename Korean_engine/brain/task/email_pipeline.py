"""
Korean Engine — Email Task Pipeline
Composes and audits formal business emails and everyday polite Korean communications.
"""

from typing import Dict, Any, Optional
from ..skills.generation import generate_business_email, generate_polite_message
from ..skills.tokenization import split_sentences
from ..skills.speech_level_engine import classify_speech_level, audit_speech_level_consistency

class KoreanEmailPipeline:
    """Pipeline for composing and auditing Korean email correspondence."""

    def __init__(self):
        pass

    def compose(
        self,
        form: str,
        recipient_name: str,
        body: str,
        sender_name: str,
        recipient_title: str = "팀장",
        company_name: str = "솔로락"
    ) -> str:
        """Compose business or polite everyday email."""
        if form.lower() == "formal":
            return generate_business_email(recipient_name, recipient_title, body, sender_name, company_name)
        else:
            return generate_polite_message(recipient_name, body, sender_name)

    def audit(self, email_text: str) -> Dict[str, Any]:
        """Audit an email for politeness level, proper closing, and register consistency."""
        sentences = split_sentences(email_text)
        audit_res = audit_speech_level_consistency(sentences)
        
        has_closing = (
            "올림" in email_text or
            "드림" in email_text or
            "감사합니다" in email_text or
            "배상" in email_text
        )
        
        has_opening = (
            "안녕하십니까" in email_text or
            "안녕하세요" in email_text or
            "님께" in email_text
        )
        
        passed = audit_res["is_consistent"] and has_closing and has_opening
        
        return {
            "has_opening": has_opening,
            "has_closing": has_closing,
            "speech_level": audit_res["primary_level"],
            "is_consistent": audit_res["is_consistent"],
            "passed": passed
        }
