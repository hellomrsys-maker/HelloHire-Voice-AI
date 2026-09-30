"""
Dutch Text Generation Engine
Generates grammatically correct V2 main clauses, subordinate SOV clauses,
diminutive phrases, and register-appropriate correspondence templates.
"""

from typing import Dict, Any, List, Optional
from .diminutive_engine import DutchDiminutiveEngine

class DutchGenerator:
    def __init__(self):
        self.diminutive_engine = DutchDiminutiveEngine()

    def generate_v2_sentence(self, subject: str, verb: str, obj: str, fronted_adjunct: Optional[str] = None) -> str:
        """
        Generates a declarative Dutch clause adhering strictly to V2 rules.
        If fronted_adjunct is provided, inverts Subject and Verb (Verb at Pos 2, Subject at Pos 3).
        """
        if fronted_adjunct:
            # Fronted: [Adjunct] [Verb] [Subject] [Object]
            fa_cap = fronted_adjunct[0].upper() + fronted_adjunct[1:] if fronted_adjunct else ""
            return f"{fa_cap} {verb} {subject} {obj}."
        # Canonical SVO: [Subject] [Verb] [Object]
        sub_cap = subject[0].upper() + subject[1:] if subject else ""
        return f"{sub_cap} {verb} {obj}."

    def generate_subordinate_clause(self, subordinator: str, subject: str, obj: str, verb: str) -> str:
        """
        Generates a subordinate clause with SOV verb-final order.
        """
        return f"{subordinator} {subject} {obj} {verb}"

    def generate_diminutive_phrase(self, base_noun: str, adjective: Optional[str] = None) -> str:
        """
        Generates a noun phrase with diminutive noun and mandatory neuter concord ('het' or 'een').
        """
        dim_info = self.diminutive_engine.generate_diminutive(base_noun)
        dim_noun = dim_info["diminutive"]

        if adjective:
            # Definite: het [adj]+e [dim_noun]
            adj_e = adjective if adjective.endswith("e") else adjective + "e"
            return f"het {adj_e} {dim_noun}"
        return f"het {dim_noun}"

    def generate_email_template(self, recipient_name: str, purpose: str, register: str = "formal") -> Dict[str, str]:
        """
        Generates formal or informal Dutch correspondence template.
        """
        if register == "formal":
            salutation = f"Geachte heer/mevrouw {recipient_name},"
            opening = f"Ik schrijf u met betrekking tot {purpose}."
            closing = "In afwachting van uw reactie verblijf ik,"
            valediction = "Met vriendelijke groet,"
        else:
            salutation = f"Beste {recipient_name},"
            opening = f"Ik wilde je even vragen over {purpose}."
            closing = "Laat het me maar weten als je vragen hebt!"
            valediction = "Hartelijke groet,"

        body = f"{salutation}\n\n{opening}\n\n{closing}\n\n{valediction}\n"
        return {
            "register": register,
            "salutation": salutation,
            "opening": opening,
            "valediction": valediction,
            "full_text": body
        }
