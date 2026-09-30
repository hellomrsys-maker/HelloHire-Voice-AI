"""
Thai Email and Administrative Correspondence Pipeline.
Synthesizes polite and formal Thai emails with appropriate salutations and closings.
"""

from typing import Dict
from Thai_engine.brain.skills.rachasap_engine import compose_email

class ThaiEmailPipeline:
    """
    Constructs well-formed Thai business emails and official letters.
    """
    def __init__(self):
        self.name = "Thai Email Pipeline"

    def compose(self, recipient: str, subject: str, message: str, gender: str = "male") -> Dict[str, any]:
        formatted = compose_email(recipient=recipient, subject=subject, message=message, gender=gender)
        return {
            "recipient": recipient,
            "subject": subject,
            "gender": gender,
            "email_body": formatted
        }
