"""
Polish Text Generation Engine
Generates grammatically correct Polish affirmative/negative clauses with
Genitive of Negation, honorific Pan/Pani address, and formal email templates.
"""

from typing import Dict, Any, Optional
from .genitive_negation_engine import PolishGenitiveNegationEngine

class PolishGenerator:
    def __init__(self):
        self.negation_engine = PolishGenitiveNegationEngine()

    def generate_clause(self, subject: Optional[str], verb: str, noun_lemma: str, negate: bool = False) -> str:
        """
        Generates a clause adhering to the Genitive of Negation invariant.
        Affirmative -> Accusative; Negative -> Genitive.
        """
        lemma_info = self.negation_engine.noun_forms.get(noun_lemma.lower(), {"acc": noun_lemma, "gen": noun_lemma})

        if negate:
            obj = lemma_info["gen"]
            v_phrase = f"nie {verb}"
        else:
            obj = lemma_info["acc"]
            v_phrase = verb

        if subject:
            sub_cap = subject[0].upper() + subject[1:]
            return f"{sub_cap} {v_phrase} {obj}."
        else:
            v_cap = v_phrase[0].upper() + v_phrase[1:]
            return f"{v_cap} {obj}."

    def generate_honorific_question(self, honorific: str, verb_3rd_person: str, complement: str) -> str:
        """
        Generates a formal inquiry adhering to 3rd-person honorific concord.
        e.g., "Czy Pan wie, gdzie to jest?"
        """
        h_cap = honorific[0].upper() + honorific[1:]
        return f"Czy {h_cap} {verb_3rd_person} {complement}?"

    def generate_email_template(self, recipient_surname: str, recipient_gender: str, purpose: str, register: str = "formal") -> Dict[str, str]:
        """
        Generates formal or informal Polish business correspondence template.
        Uses correct vocative address for formal communications.
        """
        if register == "formal":
            if recipient_gender.lower() in {"m", "male", "mężczyzna"}:
                salutation = f"Szanowny Panie {recipient_surname},"
            else:
                salutation = f"Szanowna Pani {recipient_surname},"
            opening = f"Zwracam się z uprzejmą prośbą o informację w sprawie: {purpose}."
            closing = "Z góry dziękuję za odpowiedź i poświęcony czas."
            valediction = "Z poważaniem,"
        else:
            salutation = f"Cześć {recipient_surname}!"
            opening = f"Piszę do Ciebie w sprawie: {purpose}."
            closing = "Daj mi znać, co o tym myślisz."
            valediction = "Pozdrawiam serdecznie,"

        body = f"{salutation}\n\n{opening}\n\n{closing}\n\n{valediction}\n"
        return {
            "register": register,
            "salutation": salutation,
            "opening": opening,
            "closing": closing,
            "valediction": valediction,
            "full_text": body
        }
