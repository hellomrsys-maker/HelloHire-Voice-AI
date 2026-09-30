"""
Arabic Engine — Composition & Style Task Pipeline
Assists in Arabic prose composition, rhetorical balance, and colloquial-to-MSA dialect adaptation.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words

COLLOQUIAL_TO_MSA = {
    "kwayyis": "jayyid",
    "kwayyisa": "jayyida",
    "biddi": "uridu",
    "shu": "madha",
    "esh": "madha",
    "daba": "al-an",
    "dilwa'ti": "al-an",
    "zwin": "jamil",
    "barsha": "kathiran",
    "mashi": "hasanan"
}

CLASSICAL_IDIOMS = [
    "ala ar-ra'si wa-l-'ayn",
    "bi-fadli",
    "min jihatin ukhra",
    "qalban wa-qaliban",
    "fi ghayati al-ahammiyya",
    "la siyyama"
]

class ArabicCompositionPipeline:
    """Pipeline for prose style, rhetorical balance, and dialect adaptation."""

    def __init__(self):
        pass

    def adapt_dialect(self, text: str, target: str = "msa") -> str:
        """
        Adapt text from colloquial dialect vernaculars into pure Modern Standard Arabic (MSA).
        """
        adapted = text
        text_lower = text.lower()
        if target.lower() == "msa":
            for col, msa in COLLOQUIAL_TO_MSA.items():
                if col in text_lower:
                    adapted = adapted.replace(col, msa)
        return adapted

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analyze literary style, rhetorical idiom density, and dialect intrusions."""
        tokens = tokenize_words(text)
        text_lower = text.lower()
        
        idioms_found = [idiom for idiom in CLASSICAL_IDIOMS if idiom in text_lower]
        colloquials_found = [c for c in COLLOQUIAL_TO_MSA.keys() if c in text_lower]
        
        if colloquiuals_count := len(colloquials_found):
            style = "colloquial_dialectal"
        elif idioms_found:
            style = "classical_rhetorical"
        else:
            style = "standard_msa"
            
        return {
            "token_count": len(tokens),
            "idioms_found": idioms_found,
            "idiom_count": len(idioms_found),
            "colloquial_intrusions": colloquials_found,
            "style": style
        }
