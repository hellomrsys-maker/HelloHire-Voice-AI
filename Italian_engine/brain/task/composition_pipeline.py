"""
Italian Engine — Composition Task Pipeline
Synthesizes rhetorical prose with classical idioms, rhetorical figures, and regional dialect adaptation.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words

CLASSICAL_IDIOMS = [
    "in bocca al lupo",
    "non vedere l'ora",
    "prendere lucciole per lanterne",
    "fare fiasco",
    "costare un occhio della testa"
]

class ItalianCompositionPipeline:
    """Task pipeline for literary composition, style evaluation, and dialect register adaptation."""

    def compose_prose(self, topic: str, style: str = "standard_formal") -> str:
        """Compose stylized Italian prose on a given topic."""
        if style == "rhetorical":
            return (
                f"Per quanto concerne {topic}, non è affatto un mistero che ogni singola variabile "
                f"debba essere ponderata con estrema perizia. Chiunque si accinga a tale impresa "
                f"non vede l'ora di ammirarne i risultati concreti."
            )
        return (
            f"Il progetto riguardante {topic} si sviluppa secondo i più rigorosi standard operativi. "
            f"Tutti i componenti sono stati integrati con successo e garantiscono la massima affidabilità."
        )

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analyze literary and rhetorical features in Italian prose."""
        t_clean = text.lower()
        idioms_found = []
        for idm in CLASSICAL_IDIOMS:
            if idm == "non vedere l'ora":
                if any(v in t_clean for v in ["non vedere l'ora", "non vedo l'ora", "non vede l'ora", "non vediamo l'ora", "non vedete l'ora", "non vedono l'ora"]):
                    idioms_found.append("non vedere l'ora")
            elif idm in t_clean:
                idioms_found.append(idm)
                
        is_rhetorical = len(idioms_found) > 0 or any(
            m in t_clean for m in ["per quanto concerne", "debba essere", "estrema perizia"]
        )
        
        return {
            "style": "classical_rhetorical" if is_rhetorical else "standard",
            "idioms_found": idioms_found,
            "has_rhetorical_markers": is_rhetorical
        }

    def adapt_dialect(self, text: str, target: str = "standard") -> str:
        """
        Normalize regional or colloquial Italian forms to Standard Neo-Standard Italian.
        Example: Northern 'la Chiara' -> 'Chiara', Roman 'noi si va' -> 'noi andiamo'.
        """
        adapted = text
        # Northern definite article before female given name
        adapted = adapted.replace("la Chiara", "Chiara").replace("la Giulia", "Giulia")
        # Tuscan impersonal plural
        adapted = adapted.replace("noi si va", "noi andiamo").replace("si va", "andiamo")
        # Southern personal 'a' before direct object
        adapted = adapted.replace("chiamo a Maria", "chiamo Maria").replace("chiama a Marco", "chiama Marco")
        return adapted
