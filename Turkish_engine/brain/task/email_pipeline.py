"""Turkish Email Pipeline.

Generates formal, academic, or informal Turkish correspondence
with automated honorific title integration and epistolary framing.
"""

from typing import Dict, Any, Optional, List
from ..skills.pragmatics_engine import TurkishPragmaticsEngine


class TurkishEmailPipeline:
    def __init__(self, pragmatics_engine: TurkishPragmaticsEngine = None):
        self.pragmatics = pragmatics_engine or TurkishPragmaticsEngine()

    def compose_email(
        self,
        recipient_name: str,
        sender_name: str = "Ahmet",
        subject: str = "Proje Güncellemesi",
        recipient_gender: str = "masc",
        register: str = "formal_business",
        body_paragraphs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Composes a complete Turkish email tailored to the chosen pragmatic register."""
        salutation, valediction = self.pragmatics.get_salutation_and_valediction(
            recipient_name=recipient_name,
            register=register,
            gender=recipient_gender
        )

        if not body_paragraphs:
            if register == "formal_business":
                body_paragraphs = [
                    "Projemizin güncel ilerleme raporunu ekte bilgilerinize sunuyorum.",
                    "Konuyla ilgili değerlendirmelerinizi rica eder, iyi çalışmalar dilerim."
                ]
            elif register == "academic":
                body_paragraphs = [
                    "Yürüttüğümüz akademik araştırmanın son analiz sonuçlarını dikkatlerinize sunarım.",
                    "Görüş ve önerileriniz bizim için büyük değer taşımaktadır."
                ]
            else:
                body_paragraphs = [
                    "Umarım her şey yolundadır. Yarınki planımızı konuşmak istedim.",
                    "Müsait olduğunda bana haber ver, görüşmek üzere."
                ]

        body_text = "\n\n".join(body_paragraphs)
        full_email = f"Konu: {subject}\n\n{salutation}\n\n{body_text}\n\n{valediction}\n{sender_name}"

        return {
            "subject": subject,
            "recipient": recipient_name,
            "register": register,
            "salutation": salutation,
            "body": body_text,
            "valediction": valediction,
            "sender": sender_name,
            "full_email": full_email
        }
