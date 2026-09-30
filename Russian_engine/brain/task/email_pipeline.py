"""Russian Email Pipeline.

Generates formal, academic, or informal Russian correspondence
with automated patronymic derivation and appropriate epistolary framing.
"""

from typing import Dict, Any, Optional
from ..skills.pragmatics_engine import RussianPragmaticsEngine


class RussianEmailPipeline:
    def __init__(self, pragmatics_engine: RussianPragmaticsEngine = None):
        self.pragmatics_engine = pragmatics_engine or RussianPragmaticsEngine()

    def compose_email(
        self,
        recipient_first_name: str,
        recipient_father_name: Optional[str] = None,
        recipient_gender: str = "masc",
        sender_name: str = "Александр",
        subject: str = "Рабочий вопрос",
        body_paragraphs: Optional[list] = None,
        register: str = "formal_business"
    ) -> Dict[str, Any]:
        """Composes a complete Russian email tailored to the chosen pragmatic register."""
        # Determine address form
        if recipient_father_name and register in ("formal_business", "official_academic"):
            full_recipient = self.pragmatics_engine.format_full_respectful_name(
                recipient_first_name, recipient_father_name, recipient_gender
            )
        else:
            full_recipient = recipient_first_name.strip().capitalize()

        salutation, valediction = self.pragmatics_engine.get_salutation_and_valediction(
            recipient_name=full_recipient,
            register=register,
            gender=recipient_gender
        )

        if not body_paragraphs:
            if register == "formal_business":
                body_paragraphs = [
                    "Направляю Вам обновлённые материалы по проекту для ознакомления.",
                    "Буду признателен за обратную связь при первой возможности."
                ]
            elif register == "official_academic":
                body_paragraphs = [
                    "Имею честь представить на Ваше рассмотрение результаты нашего научного исследования.",
                    "Надеемся на плодотворное продолжение нашего академического сотрудничества."
                ]
            else:
                body_paragraphs = [
                    "Привет! Хотел уточнить наши планы на завтра.",
                    "Дай знать, когда освободишься."
                ]

        body_text = "\n\n".join(body_paragraphs)
        full_email = f"Тема: {subject}\n\n{salutation}\n\n{body_text}\n\n{valediction}\n{sender_name}"

        return {
            "subject": subject,
            "recipient": full_recipient,
            "register": register,
            "salutation": salutation,
            "body": body_text,
            "valediction": valediction,
            "sender": sender_name,
            "full_email": full_email
        }
