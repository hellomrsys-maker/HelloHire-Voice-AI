"""
French Email Generation Task Pipeline.
Generates authentic business and personal correspondence adhering to strict
French epistolary conventions, salutations, and closing formulas.
"""

from typing import Dict, Any, Optional
from ..skills.pragmatics_engine import FrenchPragmaticsEngine


class FrenchEmailPipeline:
    """
    Epistolary correspondence generator for French communication.
    """

    def __init__(self):
        self.pragmatics = FrenchPragmaticsEngine()

    def generate_email(
        self,
        recipient_name: str,
        topic: str,
        body_content: str,
        sender_name: str,
        formal: bool = True,
        recipient_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a complete French email with standard salutation, formatted body, and closing.
        """
        if formal:
            if recipient_title:
                salutation = f"{recipient_title} {recipient_name},"
            else:
                salutation = f"Madame, Monsieur {recipient_name},"
            closing = "Je vous prie d'agréer, l'expression de mes salutations distinguées."
        else:
            salutation = f"Cher {recipient_name}," if not recipient_name.endswith("e") else f"Chère {recipient_name},"
            closing = "Bien amicalement,"

        subject_line = f"Objet : {topic}"

        full_email = (
            f"{subject_line}\n\n"
            f"{salutation}\n\n"
            f"{body_content}\n\n"
            f"{closing}\n\n"
            f"{sender_name}"
        )

        return {
            "subject": subject_line,
            "salutation": salutation,
            "body": body_content,
            "closing": closing,
            "sender": sender_name,
            "full_email": full_email,
            "is_formal": formal,
            "register": "vouvoiement" if formal else "tutoiement"
        }
