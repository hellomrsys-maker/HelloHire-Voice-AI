"""
Intent Mapper for English Speech Acts (Searle's Taxonomy).
Classifies utterances into Assertives, Directives, Commissives, Expressives,
and Declarations, computing illocutionary force and pragmatic parameters.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class SpeechActClassification:
    primary_speech_act: str  # Assertive, Directive, Commissive, Expressive, Declaration
    illocutionary_force: str  # e.g., "command", "request", "inquiry", "claim", "promise"
    confidence: float
    is_indirect: bool
    underlying_intent: str
    politeness_level: str  # "neutral", "polite", "blunt", "formal"


class IntentMapper:
    """
    Classifies pragmatic speaker intent according to Searle's taxonomy of speech acts.
    """

    DIRECTIVE_TRIGGERS = [
        (r"^(please\s+)?(open|close|give|bring|stop|send|check|verify|run|execute)\b", "command", False),
        (r"^(can|could|would)\s+you\s+(please\s+)?", "polite_request", True),
        (r"^what|^where|^who|^when|^why|^how|^is\s+there|^do\s+you", "inquiry", False),
    ]

    COMMISSIVE_TRIGGERS = [
        (r"\b(i|we)\s+(promise|swear|guarantee|pledge|vow)\b", "promise", False),
        (r"\b(i|we)\s+will\s+(definitely|certainly|ensure)\b", "commitment", False),
        (r"\b(let\s+me|allow\s+me\s+to)\s+help\b", "offer", False),
    ]

    EXPRESSIVE_TRIGGERS = [
        (r"\b(thank\s+you|thanks|appreciate)\b", "gratitude", False),
        (r"\b(i am sorry|sorry|apologize|my bad)\b", "apology", False),
        (r"\b(congratulations|congrats|well done|great job)\b", "congratulation", False),
        (r"\b(hello|hi|good morning|greetings)\b", "greeting", False),
    ]

    DECLARATION_TRIGGERS = [
        (r"\b(i\s+hereby\s+declare|i\s+pronounce|you\s+are\s+fired|i\s+resign)\b", "official_declaration", False),
        (r"\b(court\s+is\s+adjourned|meeting\s+is\s+called\s+to\s+order)\b", "institutional_declaration", False),
    ]

    def classify(self, utterance: str) -> SpeechActClassification:
        u_lower = utterance.strip().lower()

        # Check Expressives
        for pat, force, indirect in self.EXPRESSIVE_TRIGGERS:
            if re.search(pat, u_lower):
                return SpeechActClassification(
                    primary_speech_act="Expressive",
                    illocutionary_force=force,
                    confidence=0.92,
                    is_indirect=indirect,
                    underlying_intent=f"Express psychological state: {force}",
                    politeness_level="polite" if "please" in u_lower or "thank" in u_lower else "neutral",
                )

        # Check Commissives
        for pat, force, indirect in self.COMMISSIVE_TRIGGERS:
            if re.search(pat, u_lower):
                return SpeechActClassification(
                    primary_speech_act="Commissive",
                    illocutionary_force=force,
                    confidence=0.90,
                    is_indirect=indirect,
                    underlying_intent="Commit speaker to a future course of action",
                    politeness_level="formal" if "pledge" in u_lower or "hereby" in u_lower else "neutral",
                )

        # Check Declarations
        for pat, force, indirect in self.DECLARATION_TRIGGERS:
            if re.search(pat, u_lower):
                return SpeechActClassification(
                    primary_speech_act="Declaration",
                    illocutionary_force=force,
                    confidence=0.95,
                    is_indirect=indirect,
                    underlying_intent="Alter institutional or world state through utterance",
                    politeness_level="formal",
                )

        # Check Directives
        for pat, force, indirect in self.DIRECTIVE_TRIGGERS:
            if re.search(pat, u_lower):
                return SpeechActClassification(
                    primary_speech_act="Directive",
                    illocutionary_force=force,
                    confidence=0.88,
                    is_indirect=indirect,
                    underlying_intent="Attempt to cause the hearer to take action or provide information",
                    politeness_level="polite" if "could" in u_lower or "please" in u_lower else "direct",
                )

        # Default: Assertive / Representative
        return SpeechActClassification(
            primary_speech_act="Assertive",
            illocutionary_force="statement_or_assertion",
            confidence=0.80,
            is_indirect=False,
            underlying_intent="Represent a state of affairs or truth claim about the world",
            politeness_level="neutral",
        )
