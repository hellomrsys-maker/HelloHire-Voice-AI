"""
Bengali Email Pipeline Task: Synthesizes culturally authentic Bengali correspondence
across superior (Aapni), familiar (Tumi), and intimate (Tui) social registers.
"""

from typing import Dict, Any, Optional
from ..skills.generation import BengaliGenerator
from ..skills.pragmatics_engine import BengaliPragmaticsEngine


class BengaliEmailPipelineTask:
    """
    Epistolary composition pipeline for Bengali communications.
    """

    SALUTATIONS = {
        "superior": "শ্রদ্ধেয় মহাশয়,",
        "familiar": "প্রিয় বন্ধু,",
        "intimate": "স্নেহের ভাই,"
    }

    OPENINGS = {
        "superior": "আমার সশ্রদ্ধ প্রণাম গ্রহণ করবেন। আশা করি আপনি কুশলে আছেন।",
        "familiar": "আমার আন্তরিক শুভেচ্ছা নিও। আশা করি তুমি ভালো আছ।",
        "intimate": "কেমন আছিস রে? আশা করি ভালো আছিস।"
    }

    def __init__(self):
        self.generator = BengaliGenerator()
        self.pragmatics_engine = BengaliPragmaticsEngine()

    def compose_email(
        self,
        recipient_name: str,
        sender_name: str,
        purpose: str = "general",
        tier: str = "superior",
        custom_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes a complete Bengali letter or email.
        """
        salutation = self.SALUTATIONS.get(tier, "শ্রদ্ধেয় মহাশয়,")
        if recipient_name:
            if tier == "superior":
                salutation = f"শ্রদ্ধেয় {recipient_name} মহাশয়,"
            elif tier == "familiar":
                salutation = f"প্রিয় {recipient_name},"
            else:
                salutation = f"স্নেহের {recipient_name},"

        opening = self.OPENINGS.get(tier, self.OPENINGS["superior"])

        if custom_body:
            body = custom_body
        else:
            if purpose == "meeting":
                if tier == "superior":
                    body = "আগামীকাল আপনার সুবিধাজনক সময়ে একটি সংক্ষিপ্ত আলোচনার সুযোগ পেলে বাধিত হব।"
                else:
                    body = "কাল বিকেলে একবার দেখা করতে পারলে খুব ভালো হত।"
            else:
                if tier == "superior":
                    body = "এই বিষয়ে আপনার সুচিন্তিত মতামত জানালে অত্যন্ত উপকৃত হব।"
                else:
                    body = "এই বিষয়ে তোমার মতামত জানিও।"

        closing = self.pragmatics_engine.get_epistolary_closing(tier)
        valediction = f"{closing},\n{sender_name}"

        full_text = f"{salutation}\n\n{opening}\n{body}\n\n{valediction}"

        return {
            "tier": tier,
            "salutation": salutation,
            "opening": opening,
            "body": body,
            "closing": closing,
            "full_email": full_text
        }
