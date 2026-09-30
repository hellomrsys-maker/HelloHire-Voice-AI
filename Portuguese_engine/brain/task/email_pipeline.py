"""
Portuguese Email Pipeline Task: Synthesizes culturally authentic Lusophone correspondence
across formal (o senhor / prezado) and informal (você / tu) registers.
"""

from typing import Dict, Any, Optional
from ..skills.pragmatics_engine import PortuguesePragmaticsEngine


class PortugueseEmailPipelineTask:
    """
    Epistolary composition pipeline for Portuguese business and personal correspondence.
    """

    SALUTATIONS = {
        "formal": "Prezado(a) Senhor(a),",
        "familiar": "Olá, amigo(a),",
        "intimate": "Querido(a) [Nome],"
    }

    OPENINGS = {
        "formal": "Espero que esta mensagem o(a) encontre bem.",
        "familiar": "Espero que você esteja bem.",
        "intimate": "Como estás? Espero que estejas muito bem."
    }

    def __init__(self):
        self.pragmatics = PortuguesePragmaticsEngine()

    def compose_email(
        self,
        recipient_name: str,
        sender_name: str,
        purpose: str = "general",
        tier: str = "formal",
        custom_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes a complete Portuguese letter or email.
        """
        salutation = self.SALUTATIONS.get(tier, "Prezado(a) Senhor(a),")
        if recipient_name:
            if tier == "formal":
                salutation = f"Prezado(a) {recipient_name},"
            elif tier == "familiar":
                salutation = f"Olá, {recipient_name},"
            else:
                salutation = f"Querido(a) {recipient_name},"

        opening = self.OPENINGS.get(tier, self.OPENINGS["formal"])

        if custom_body:
            body = custom_body
        else:
            if purpose == "meeting":
                if tier == "formal":
                    body = "Gostaria de agendar uma reunião nesta semana para discutirmos os próximos passos do projeto."
                else:
                    body = "Vamos marcar uma conversa rápida nesta semana para combinarmos os detalhes?"
            else:
                if tier == "formal":
                    body = "Agradeço desde já pela atenção e aguardo o seu retorno com considerações."
                else:
                    body = "Qualquer novidade, me avise por aqui."

        closing = self.pragmatics.get_epistolary_closing(tier)
        valediction = f"{closing}\n{sender_name}"

        full_text = f"{salutation}\n\n{opening}\n{body}\n\n{valediction}"

        return {
            "tier": tier,
            "salutation": salutation,
            "opening": opening,
            "body": body,
            "closing": closing,
            "full_email": full_text
        }
