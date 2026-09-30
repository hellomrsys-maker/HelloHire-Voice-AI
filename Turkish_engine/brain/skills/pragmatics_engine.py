"""Turkish Pragmatics & Honorifics Skill.

Handles the T-V ('sen' vs 'siz') social deixis spectrum,
postpositive honorific titles ('Bey', 'Hanım', 'Hocam'),
and email salutation/valediction synthesis.
"""

import json
import os
from typing import Dict, Any, Optional, Tuple
from .tokenization import TurkishTokenizer


class TurkishPragmaticsEngine:
    HONORIFIC_POSTPOSITIVES = {"bey", "hanım", "hocam", "beyefendi", "hanımefendi", "efendim"}

    def __init__(self, db_path: Optional[str] = None):
        self.tokenizer = TurkishTokenizer()
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "pragmatic_honorific_matrix.json")

        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

        self.registers = self.db.get("registers", {})


    def format_honorific_name(self, given_name: str, title: str = "Bey") -> str:
        """Formats a respectful Turkish name with postpositive title (e.g. 'Ahmet Bey', 'Ayşe Hanım')."""
        return f"{given_name.strip().capitalize()} {title.strip().capitalize()}"

    def detect_register(self, text: str) -> str:
        """Determines whether text exhibits formal ('siz'), academic ('hocam'), or informal ('sen') register."""
        tokens = self.tokenizer.tokenize(text)
        tok_set = {TurkishTokenizer.turkish_lower(t) for t in tokens}

        formal_markers = {"siz", "size", "sizi", "sizde", "sizden", "sizin", "sayın", "saygılarımla", "merhabalar"}
        academic_markers = {"hocam", "hocamın", "akademik", "araştırma", "makale"}
        informal_markers = {"sen", "sana", "seni", "sende", "senden", "senin", "merhaba", "selam", "sevgiler"}

        if tok_set.intersection(academic_markers):
            return "academic"
        if len(tok_set.intersection(formal_markers)) > len(tok_set.intersection(informal_markers)):
            return "formal_business"
        if len(tok_set.intersection(informal_markers)) > 0:
            return "informal"

        return "neutral"


    def get_salutation_and_valediction(
        self,
        recipient_name: str,
        register: str = "formal_business",
        gender: str = "masc"
    ) -> Tuple[str, str]:
        """Returns harmonic salutations and closings based on the target pragmatic register."""
        reg_data = self.registers.get(register, self.registers.get("formal_business", {}))
        salutations = reg_data.get("salutations", ["Sayın {name} Bey,"])
        valedictions = reg_data.get("valedictions", ["Saygılarımla,"])

        if register == "formal_business":
            title = "Bey" if gender.lower().startswith("m") else "Hanım"
            sal_template = f"Sayın {recipient_name} {title},"
        elif register == "academic":
            sal_template = f"Sayın {recipient_name} Hocam,"
        else:
            sal_template = f"Sevgili {recipient_name},"

        valediction = valedictions[0]
        return sal_template, valediction
