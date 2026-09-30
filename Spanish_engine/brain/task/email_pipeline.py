"""
Spanish Epistolary & Business Email Task Pipeline.
Generates culturally authentic correspondence respecting formal ustedeo vs informal tuteo.
"""

from typing import Dict, Any


class SpanishEmailPipeline:
    """
    Business and personal correspondence generator for Spanish communication.
    """

    def generate_email(
        self,
        recipient_name: str,
        recipient_title: str,
        topic: str,
        body_content: str,
        sender_name: str,
        formal: bool = True
    ) -> Dict[str, Any]:
        if formal:
            salutation = f"Estimado/a {recipient_title} {recipient_name}:"
            opening = "Espero que este mensaje le encuentre bien. Me dirijo a usted con el propósito de tratar lo siguiente."
            closing = "Agradeciendo de antemano su amable atención y quedando a su entera disposición,\n\nAtentamente,\n"
        else:
            salutation = f"Hola {recipient_name}:"
            opening = "¡Espero que estés muy bien! Te escribo rápidamente para contarte sobre lo siguiente."
            closing = "Cualquier duda me avisas. ¡Un fuerte abrazo!\n\nSaludos,\n"

        full_email = (
            f"{salutation}\n\n"
            f"  {opening}\n\n"
            f"  Respecto a '{topic}': {body_content}\n\n"
            f"{closing}"
            f"{sender_name}\n"
        )

        return {
            "full_email": full_email,
            "recipient": f"{recipient_title} {recipient_name}".strip(),
            "is_formal": formal,
            "topic": topic,
        }
