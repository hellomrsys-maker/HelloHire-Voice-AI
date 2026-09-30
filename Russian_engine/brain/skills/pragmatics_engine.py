"""Russian Pragmatics & Honorifics Skill.

Derives patronymics, generates formal/informal salutations,
and handles the T-V ('ты' vs 'Вы') honorific address spectrum.
"""

import json
import os
from typing import Dict, Any, Optional, Tuple


class RussianPragmaticsEngine:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "pragmatic_patronymic_matrix.json")

        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

        self.patronymic_rules = self.db.get("patronymic_rules", {})
        self.registers = self.db.get("registers", {})

    def generate_patronymic(self, father_name: str, gender: str = "masc") -> str:
        """Derives a Russian patronymic (Отчество) from the father's given name."""
        f_name = father_name.strip().capitalize()
        g_key = "masculine" if gender.lower().startswith("m") else "feminine"
        rules = self.patronymic_rules.get(g_key, {})
        exceptions = rules.get("exceptions", {})

        if f_name in exceptions:
            return exceptions[f_name]

        # General derivation rules
        if g_key == "masculine":
            if f_name.endswith(("ь", "й")):
                return f_name[:-1] + "евич"
            elif f_name.endswith("а") or f_name.endswith("я"):
                return f_name[:-1] + "ич"
            else:
                return f_name + "ович"
        else:
            if f_name.endswith(("ь", "й")):
                return f_name[:-1] + "евна"
            elif f_name.endswith("а") or f_name.endswith("я"):
                return f_name[:-1] + "ична"
            else:
                return f_name + "овна"

    def format_full_respectful_name(self, first_name: str, father_name: str, gender: str = "masc") -> str:
        """Formats the classic Russian respectful name: Имя + Отчество."""
        patronymic = self.generate_patronymic(father_name, gender)
        return f"{first_name.strip().capitalize()} {patronymic}"

    def detect_register(self, text: str) -> str:
        """Detects if text exhibits formal ('Вы') or informal ('ты') register."""
        tokens = set(text.lower().split())
        formal_markers = {"вы", "вас", "вам", "вами", "уважаемый", "уважаемая", "здравствуйте"}
        informal_markers = {"ты", "тебя", "тебе", "тобой", "привет", "здравствуй"}

        f_count = len(tokens.intersection(formal_markers))
        i_count = len(tokens.intersection(informal_markers))

        if f_count > i_count:
            return "formal_business"
        elif i_count > f_count:
            return "informal_friendly"
        return "neutral"

    def get_salutation_and_valediction(self, recipient_name: str, register: str = "formal_business", gender: str = "masc") -> Tuple[str, str]:
        """Returns appropriate epistolary salutation and valediction."""
        reg_info = self.registers.get(register, self.registers.get("formal_business", {}))
        salutations = reg_info.get("salutations", ["Здравствуйте, {name}!"])
        valedictions = reg_info.get("valedictions", ["С уважением,"])

        # Pick gender-appropriate template
        sal_template = salutations[0]
        if "{name}" in sal_template:
            salutation = sal_template.format(name=recipient_name)
        else:
            salutation = f"{sal_template} {recipient_name}!"

        valediction = valedictions[0]
        return salutation, valediction
