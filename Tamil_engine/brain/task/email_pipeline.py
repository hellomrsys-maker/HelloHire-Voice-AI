"""
Tamil Email and Epistolary Task Pipeline.
Synthesizes formal administrative and colloquial correspondence.
"""

from typing import Dict
from Tamil_engine.brain.skills.pragmatics_engine import compose_email

class TamilEmailPipeline:
    """
    Constructs well-formed Tamil letters and business emails.
    """
    def __init__(self):
        self.name = "Tamil Email Pipeline"

    def compose(self, recipient: str, subject: str, message: str, register: str = "formal") -> Dict[str, any]:
        formatted = compose_email(recipient=recipient, subject=subject, message=message, register=register)
        return {
            "recipient": recipient,
            "subject": subject,
            "register": register,
            "email_body": formatted
        }
