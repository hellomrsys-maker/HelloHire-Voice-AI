"""
Polish Honorific Deixis & Agreement Engine
Validates the mandatory 3rd-person verb agreement rule with honorific subjects
(Pan, Pani, Państwo, Panie, Panowie) and prevents 2nd-person discord.
"""

from typing import Dict, Any, List

class PolishHonorificDeixisEngine:
    def __init__(self):
        self.honorifics_sg = {"pan", "pani"}
        self.honorifics_pl = {"państwo", "panie", "panowie"}

        # 2nd-person verb endings that violate formal honorific agreement
        # e.g., -sz (2SG present), -cie (2PL present), -łeś/-łaś (2SG past)
        self.second_person_violating_endings = ("sz", "cie", "łeś", "łaś", "liście", "łyście")

        # Sample 2nd-person verb forms to catch
        self.second_person_forms = {
            "wiesz", "masz", "czytasz", "piszesz", "robisz", "widzisz", "kupujesz", "chcesz", "możesz",
            "wiecie", "macie", "czytacie", "piszecie", "robicie", "widzicie", "kupujecie", "chcecie", "możecie",
            "czytałeś", "czytałaś", "napisałeś", "napisałaś", "zrobiłeś", "zrobiłaś"
        }

    def verify_honorific_agreement(self, tokens: List[str]) -> Dict[str, Any]:
        low_tokens = [t.lower() for t in tokens if t not in {".", ",", "!", "?", ";", ":"}]
        errors = []
        is_formal = False

        for i, tok in enumerate(low_tokens):
            if tok in self.honorifics_sg or tok in self.honorifics_pl:
                is_formal = True
                # Check adjacent or subsequent verb
                for j in range(i + 1, min(i + 4, len(low_tokens))):
                    v_tok = low_tokens[j]
                    if v_tok in self.second_person_forms or any(v_tok.endswith(end) for end in ("sz", "cie", "łeś", "łaś")):
                        errors.append(
                            f"Honorific Concord Violation: Formal subject '{tokens[i]}' obligatorily requires 3rd-person "
                            f"verb agreement, but found 2nd-person verb form '{tokens[j]}'."
                        )

        valid = len(errors) == 0
        return {
            "is_formal": is_formal,
            "honorific_concord_valid": valid,
            "errors": errors
        }
