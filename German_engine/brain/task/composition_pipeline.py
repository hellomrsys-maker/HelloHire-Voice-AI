"""
German Engine — Composition & Style Task Pipeline
Assists in German prose generation, modal particle enrichment, and Swiss orthographic adaptation.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words, normalize_orthography
from ..skills.modal_particle_engine import analyze_modal_particles
from ..skills.pragmatics_engine import analyze_register

class GermanCompositionPipeline:
    """Pipeline for stylistic enrichment, modal particle management, and orthographic adaptation."""

    def __init__(self):
        pass

    def adapt_orthography(self, text: str, swiss_mode: bool = False) -> str:
        """Convert standard German to Swiss orthography (replacing 'ß' with 'ss') if requested."""
        return normalize_orthography(text, swiss_mode=swiss_mode)

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analyze textual style, modal particles, and register profile."""
        tokens = tokenize_words(text)
        particles = analyze_modal_particles(tokens)
        reg = analyze_register(text, tokens)
        
        # Check compound richness
        long_words = [t for t in tokens if len(t) > 12 and t[0].isupper()]
        
        return {
            "token_count": len(tokens),
            "modal_particles": particles,
            "register": reg["register"],
            "compound_substantives": long_words,
            "style_assessment": "conversational" if particles["particle_count"] > 1 else ("formal" if reg["register"] == "siezen" else "standard")
        }
