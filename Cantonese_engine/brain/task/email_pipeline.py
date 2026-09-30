"""
Cantonese Email Pipeline.
Synthesizes professional and colloquial emails adhering to Hong Kong epistolary customs.
"""

from typing import Dict
from Cantonese_engine.brain.skills.pragmatics_engine import compose_email

class CantoneseEmailPipeline:
    """
    Constructs well-formed Cantonese / Hong Kong business and colloquial correspondence.
    """
    def __init__(self):
        self.name = "Cantonese Email Pipeline"

    def compose(self, recipient: str, subject: str, message: str, register: str = "formal") -> Dict[str, any]:
        formatted_email = compose_email(recipient, subject, message, register=register)
        
        return {
            "recipient": recipient,
            "subject": subject,
            "register": register,
            "email_body": formatted_email
        }
