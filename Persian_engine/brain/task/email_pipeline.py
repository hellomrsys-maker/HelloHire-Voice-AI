"""
Persian Email Task Pipeline
Generates and audits institutional and administrative Persian correspondence
with proper Ta'arof salutations, modesty framing, and respectful closings.
"""

from typing import Dict, Any, Optional
from Persian_engine.brain.skills.pragmatics_engine import PersianPragmaticsEngine
from Persian_engine.brain.analysis.taarof_deference_analyzer import TaarofDeferenceAnalyzer

class PersianEmailPipeline:
    """
    Administrative correspondence pipeline enforcing Iranian epistolary protocol.
    """

    def __init__(self):
        self.pragmatics = PersianPragmaticsEngine()
        self.deference_analyzer = TaarofDeferenceAnalyzer()

    def generate_formal_email(
        self,
        recipient_name: str,
        recipient_title: str,
        body_points: str,
        sender_name: str,
        is_high_taarof: bool = True
    ) -> str:
        """
        Synthesizes a complete formal Persian letter/email.
        """
        return self.pragmatics.format_formal_letter(
            addressee=recipient_name,
            title=recipient_title,
            body=body_points,
            sender=sender_name,
            is_high_taarof=is_high_taarof
        )

    def audit_incoming_email(self, email_text: str) -> Dict[str, Any]:
        """
        Audits an email for formal register compliance, colloquial leaks, and Ta'arof etiquette.
        """
        audit = self.deference_analyzer.audit_deference_and_register(email_text, target_register="formal")
        
        has_salutation = any(sal in email_text for sal in ["سلام", "درود", "احترام", "محترم"])
        has_closing = any(close in email_text for close in ["سپاس", "احترام", "تشکر", "توفیق"])
        
        is_professional = audit["is_aligned"] and has_salutation and has_closing
        
        return {
            "has_salutation": has_salutation,
            "has_closing": has_closing,
            "register_tier": audit["detected_register"],
            "deference_score": audit["deference_score"],
            "colloquial_issues": audit["colloquial_findings"],
            "is_professional": is_professional
        }
