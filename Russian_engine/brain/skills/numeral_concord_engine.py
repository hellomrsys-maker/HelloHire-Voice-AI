"""Russian Numeral Concord Skill.

Implements paucal numeral concord rules:
- Ending in 1 (except 11): Nominative Singular (1 стол, 21 день)
- Ending in 2, 3, 4 (except 12, 13, 14): Genitive Singular (2 стола, 3 дня, 4 книги)
- Ending in 5-9, 0 or 11-14: Genitive Plural (5 столов, 12 дней, 20 книг)
"""

from typing import Dict, Any, Tuple
from .case_engine import RussianCaseEngine


class RussianNumeralConcordEngine:
    def __init__(self, case_engine: RussianCaseEngine = None):
        self.case_engine = case_engine or RussianCaseEngine()

    def get_noun_form_requirements(self, number: int) -> Tuple[str, str]:
        """Determines the required case ('nom' or 'gen') and number ('sing' or 'plur')

        for a noun governed by a Russian cardinal numeral.
        """
        abs_num = abs(number)
        last_digit = abs_num % 10
        last_two = abs_num % 100

        if last_two in (11, 12, 13, 14):
            return "gen", "plur"
        if last_digit == 1:
            return "nom", "sing"
        if last_digit in (2, 3, 4):
            return "gen", "sing"
        return "gen", "plur"

    def combine(
        self,
        number: int,
        lemma: str,
        gender: str = "masc",
        declension: str = "2nd",
        animacy: bool = False
    ) -> str:
        """Produces the fully inflected numeral-noun phrase (e.g., 2 + стол -> '2 стола')."""
        case_req, num_req = self.get_noun_form_requirements(number)
        inflected_noun = self.case_engine.inflect_noun(
            lemma=lemma,
            case=case_req,
            gender=gender,
            declension=declension,
            number=num_req,
            animacy=animacy
        )
        return f"{number} {inflected_noun}"

    def verify_concord(
        self,
        number: int,
        observed_noun: str,
        lemma: str,
        gender: str = "masc",
        declension: str = "2nd",
        animacy: bool = False
    ) -> Dict[str, Any]:
        """Checks whether observed noun form agrees correctly with the preceding numeral."""
        case_req, num_req = self.get_noun_form_requirements(number)
        expected_noun = self.case_engine.inflect_noun(
            lemma=lemma,
            case=case_req,
            gender=gender,
            declension=declension,
            number=num_req,
            animacy=animacy
        )
        is_valid = (observed_noun.lower() == expected_noun.lower())
        return {
            "number": number,
            "observed": observed_noun,
            "expected": expected_noun,
            "required_case": case_req,
            "required_number": num_req,
            "is_valid": is_valid
        }
