"""
French Grammatical Agreement Skill.
Validates noun-adjective concordance and past participle agreement with auxiliary
'être' (subject agreement) and 'avoir' (preceding direct object COD agreement).
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class FrenchAgreementEngine:
    """
    Engine evaluating French gender/number concord and past participle agreement.
    """

    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            rules_path = str(Path(__file__).parent.parent / "rules" / "participle_agreement_rules.json")
        self.rules_path = rules_path
        self._load_rules()

    def _load_rules(self):
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        except Exception:
            self.db = {
                "etre_rules": {"patterns": {"masc_sing": "", "fem_sing": "e", "masc_plur": "s", "fem_plur": "es"}},
                "avoir_rules": {"preceding_cod_markers": ["que", "qu'", "le", "la", "les", "l'"]}
            }

    def evaluate_noun_adjective_agreement(
        self,
        noun_gender: str,  # "M" or "F"
        noun_number: str,  # "SG" or "PL"
        adjective_base: str,
        adjective_surface: str
    ) -> Dict[str, Any]:
        """Validates gender and number agreement between noun and adjective."""
        expected_suffix = ""
        if noun_gender == "F":
            expected_suffix += "e"
        if noun_number == "PL":
            expected_suffix += "s"

        expected_form = adjective_base + expected_suffix
        is_match = (adjective_surface.lower() == expected_form.lower()) or (adjective_surface.lower() == adjective_base.lower() and expected_suffix == "")

        return {
            "is_valid": is_match,
            "noun_gender": noun_gender,
            "noun_number": noun_number,
            "expected_form": expected_form,
            "actual_form": adjective_surface,
            "message": "Accord correct" if is_match else f"Discordance: attendu '{expected_form}', trouvé '{adjective_surface}'"
        }

    def evaluate_participle_with_etre(
        self,
        subject_gender: str,  # "M" or "F"
        subject_number: str,  # "SG" or "PL"
        participle_base: str,
        participle_surface: str
    ) -> Dict[str, Any]:
        """
        Validates past participle agreement with subject when auxiliary is 'être'.
        """
        suffix = ""
        if subject_gender == "F":
            suffix += "e"
        if subject_number == "PL":
            suffix += "s"

        expected = participle_base + suffix
        is_valid = participle_surface.lower() == expected.lower()

        return {
            "auxiliary": "être",
            "is_valid": is_valid,
            "subject_features": f"{subject_gender}_{subject_number}",
            "expected_participle": expected,
            "surface_participle": participle_surface,
            "message": "Accord du participe avec être valide" if is_valid else f"Erreur d'accord: '{expected}' requis."
        }

    def evaluate_participle_with_avoir(
        self,
        cod_precedes: bool,
        cod_gender: Optional[str] = None,  # "M" or "F"
        cod_number: Optional[str] = None,  # "SG" or "PL"
        participle_base: str = "mangé",
        participle_surface: str = "mangé"
    ) -> Dict[str, Any]:
        """
        Validates past participle agreement when auxiliary is 'avoir'.
        Agrees with preceding direct object (COD) only.
        """
        if not cod_precedes or cod_gender is None or cod_number is None:
            # No agreement: participle must remain in masculine singular default
            is_valid = participle_surface.lower() == participle_base.lower()
            return {
                "auxiliary": "avoir",
                "cod_precedes": False,
                "is_valid": is_valid,
                "expected_participle": participle_base,
                "surface_participle": participle_surface,
                "message": "Pas d'accord (le COD ne précède pas ou est absent)."
            }

        suffix = ""
        if cod_gender == "F":
            suffix += "e"
        if cod_number == "PL":
            suffix += "s"

        expected = participle_base + suffix
        is_valid = participle_surface.lower() == expected.lower()

        return {
            "auxiliary": "avoir",
            "cod_precedes": True,
            "is_valid": is_valid,
            "cod_features": f"{cod_gender}_{cod_number}",
            "expected_participle": expected,
            "surface_participle": participle_surface,
            "message": "Accord avec le COD antéposé respecté" if is_valid else f"Erreur d'accord avec le COD: '{expected}' requis."
        }
