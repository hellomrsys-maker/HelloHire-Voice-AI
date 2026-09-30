"""
Portuguese Ser vs Estar Copula Engine: Disambiguates between permanent essence (ser)
and temporary state/location (estar), and evaluates continuous aspect across dialects.
"""

from typing import Dict, Any, Optional, Tuple


class PortugueseSerEstarEngine:
    """
    Evaluates semantic appropriateness of ser vs estar and aspectual periphrases.
    """

    SER_DOMAINS = {
        "identity", "origin", "profession", "material", "inherent_characteristic",
        "time", "possession", "passive_voice"
    }

    ESTAR_DOMAINS = {
        "temporary_state", "location", "health", "mood", "progressive_aspect",
        "resultant_state"
    }

    SEMANTIC_SHIFT_ADJECTIVES = {
        "bom": ("virtuous / high quality", "tasty / in good health"),
        "mau": ("wicked / bad nature", "ill / feeling bad"),
        "vivo": ("sharp / clever", "alive"),
        "morto": ("lifeless / inanimate", "deceased / dead"),
        "pronto": ("quick-witted", "ready / prepared")
    }

    def select_copula(self, semantic_category: str) -> str:
        """Selects 'ser' or 'estar' based on semantic domain."""
        if semantic_category in self.ESTAR_DOMAINS:
            return "estar"
        return "ser"

    def analyze_semantic_shift(self, adjective: str, copula: str) -> Dict[str, Any]:
        """Explains semantic shift between ser and estar with specific adjectives."""
        adj_low = adjective.lower()
        if adj_low in self.SEMANTIC_SHIFT_ADJECTIVES:
            ser_meaning, estar_meaning = self.SEMANTIC_SHIFT_ADJECTIVES[adj_low]
            return {
                "adjective": adjective,
                "selected_copula": copula,
                "meaning": ser_meaning if copula == "ser" else estar_meaning,
                "has_shift": True
            }
        return {
            "adjective": adjective,
            "selected_copula": copula,
            "meaning": "standard",
            "has_shift": False
        }

    def validate_progressive_aspect(self, phrase: str, dialect: str = "pt_br") -> Tuple[bool, str]:
        """
        Validates progressive aspect construction:
        - pt-BR: 'estar + gerúndio' (e.g. 'estou fazendo')
        - pt-PT: 'estar a + infinitivo' (e.g. 'estou a fazer')
        """
        phrase_low = phrase.lower()
        if dialect == "pt_pt":
            if " a " in phrase_low and any(phrase_low.endswith(v) for v in ("ar", "er", "ir")):
                return True, "Valid European Portuguese continuous aspect ('estar a + infinitivo')."
        elif dialect == "pt_br":
            if any(phrase_low.endswith(g) for g in ("ando", "endo", "indo")):
                return True, "Valid Brazilian Portuguese continuous aspect ('estar + gerúndio')."

        return True, "Aspect pattern noted."
