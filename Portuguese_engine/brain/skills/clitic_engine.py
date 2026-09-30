"""
Portuguese Clitic Placement Engine: Evaluates Próclise, Ênclise, and Mesóclise,
and applies morphophonemic clitic allomorphy (-lo/-la, -no/-na).
"""

from typing import Dict, Any, Optional, Tuple, List
import os
import json


class PortugueseCliticEngine:
    """
    Manages Portuguese clitic positioning and morphophonemic transformations.
    """

    PROCLISIS_ATTRACTORS = {
        "não", "nunca", "jamais", "nada", "ninguém", "nem",
        "que", "quando", "se", "como", "embora", "porque", "caso",
        "alguém", "tudo", "algo", "sempre", "talvez", "já", "onde", "quem"
    }

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "clitic_placement_rules.json")
        
        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

    def apply_enclisis(self, verb: str, clitic: str) -> str:
        """
        Attaches a clitic enclitically to a verb, resolving morphophonemic sound shifts.
        """
        clean_clitic = clitic.lstrip("-").lower()

        # Rule 1: Direct object pronouns (o, a, os, as) after -r, -s, -z
        if clean_clitic in ("o", "a", "os", "as"):
            if verb.endswith(("r", "s", "z")):
                last_char = verb[-1]
                stem = verb[:-1]
                l_map = {"o": "lo", "a": "la", "os": "los", "as": "las"}
                l_clitic = l_map[clean_clitic]

                # Tonic vowel adjustment before dropped -r
                if last_char == "r":
                    if stem.endswith("a"):
                        stem = stem[:-1] + "á"
                    elif stem.endswith("e"):
                        stem = stem[:-1] + "ê"
                    elif stem.endswith("o"):
                        stem = stem[:-1] + "ô"

                return f"{stem}-{l_clitic}"

            # Rule 2: Direct object pronouns after nasal endings (-am, -em, -ão, -õe)
            if verb.endswith(("am", "em", "ão", "õe")):
                n_map = {"o": "no", "a": "na", "os": "nos", "as": "nas"}
                n_clitic = n_map[clean_clitic]
                return f"{verb}-{n_clitic}"

        # Standard enclisis
        return f"{verb}-{clean_clitic}"

    def apply_mesoclisis(self, verb_stem: str, clitic: str, ending: str) -> str:
        """
        Forms mesoclisis in Future or Conditional tenses.
        Example: dir-te-ei, far-se-ia.
        """
        clean_clitic = clitic.lstrip("-")
        return f"{verb_stem}-{clean_clitic}-{ending}"

    def validate_placement(
        self,
        preceding_tokens: List[str],
        verb: str,
        clitic: str,
        is_enclitic: bool
    ) -> Tuple[bool, str]:
        """
        Validates whether proclisis or enclisis is grammatically appropriate.
        """
        # Check for proclisis attractors in immediate preceding context
        for tok in preceding_tokens[-3:]:
            clean_tok = tok.lower().strip(",.?!;")
            if clean_tok in self.PROCLISIS_ATTRACTORS:
                if is_enclitic:
                    return False, f"Proclisis attractor '{clean_tok}' demands proclisis; enclisis on '{verb}' is incorrect."
                return True, f"Proclisis triggered correctly by '{clean_tok}'."

        # In standard formal Portuguese, sentences cannot begin with an enclitic pronoun
        if len(preceding_tokens) == 0 and not is_enclitic:
            return False, "Standard formal Portuguese prohibits sentence-initial proclitic pronouns."

        return True, "Clitic placement is valid."
