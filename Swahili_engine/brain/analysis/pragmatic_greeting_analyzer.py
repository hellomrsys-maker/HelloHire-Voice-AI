"""
Swahili Engine — Pragmatic Greeting Analyzer
Audits Swahili salutations, greeting turns, and epistolary etiquette.
"""

from typing import Dict, Any, List
from ..skills.pragmatics_engine import validate_greeting_turn, audit_letter_etiquette

class PragmaticGreetingAnalyzer:
    """Cognitive analyzer for Swahili greetings, politeness protocol, and social deixis."""

    def __init__(self):
        pass

    def analyze_dialogue(self, call: str, response: str) -> Dict[str, Any]:
        """Validate whether a conversational turn adheres to Swahili greeting etiquette."""
        return validate_greeting_turn(call, response)

    def analyze_letter(self, letter_text: str) -> Dict[str, Any]:
        """Validate formal business letter etiquette."""
        return audit_letter_etiquette(letter_text)
