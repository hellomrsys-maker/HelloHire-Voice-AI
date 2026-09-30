"""
Pragmatic Competence, Speech Act Theory, and Politeness Engine.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import re


@dataclass
class PragmaticAnalysisResult:
    utterance: str
    locutionary_act: str
    illocutionary_force: str  # Assertive, Directive, Commissive, Expressive, Declaration
    intended_perlocutionary_effect: str
    gricean_maxims_status: Dict[str, str]  # Quantity, Quality, Relation, Manner
    conversational_implicature: str
    politeness_strategy: str  # Bald on-record, Positive Politeness, Negative Politeness, Off-record
    face_threat_mitigation_score: float  # 0.0 to 1.0


class PragmaticsEngine:
    """
    Analyzes intentionality, illocutionary force, Gricean maxims,
    conversational implicatures, and Brown-Levinson politeness face strategies.
    """

    def analyze_pragmatics(self, utterance: str, context: Optional[str] = None) -> PragmaticAnalysisResult:
        u = utterance.strip()
        u_lower = u.lower()

        # 1. Austin & Searle Speech Act Categorization
        if any(u_lower.startswith(w) for w in ["i promise", "i vow", "we will ensure", "i swear", "i commit"]):
            force = "Commissive (Commits speaker to future course of action)"
            perlocution = "Interlocutor acquires expectation of reliable future performance."
        elif any(u_lower.startswith(w) for w in ["please", "can you", "could you", "would you mind", "shut", "open", "pass", "send"]):
            force = "Directive (Attempts to get addressee to perform an action)"
            perlocution = "Addressee is persuaded, requested, or obliged to comply."
        elif any(u_lower.startswith(w) for w in ["thank you", "congratulations", "i apologize", "sorry", "great job"]):
            force = "Expressive (Expresses psychological state / interpersonal attitude)"
            perlocution = "Interpersonal rapport or social equilibrium is repaired or affirmed."
        elif any(u_lower.startswith(w) for w in ["i hereby pronounce", "you are fired", "i declare", "session is adjourned"]):
            force = "Declaration (Brings about an immediate change in institutional reality)"
            perlocution = "Immediate alteration of social/institutional status."
        else:
            force = "Assertive / Representative (Commits speaker to the truth of the proposition)"
            perlocution = "Addressee updates their internal belief model regarding the world."

        # 2. Gricean Maxims & Implicature
        maxims = {
            "Maxim of Quantity": "Adhered: Informational payload is sufficient without unnecessary verbosity.",
            "Maxim of Quality": "Adhered: Proposition is asserted as truthful without known falsity.",
            "Maxim of Relation": "Adhered: Utterance is relevant to the active conversational topic.",
            "Maxim of Manner": "Adhered: Expression avoids obscure jargon and maintains clarity."
        }

        implicature = "Literal propositional content aligns directly with speaker meaning."

        # Detect indirect speech acts and flouting
        if re.match(r"^(can|could|would)\s+you\s+(please\s+)?([a-z\s]+)\?", u_lower):
            maxims["Maxim of Relation"] = "Flouted superficially: Query regarding physical capacity conveys an indirect request."
            implicature = "Conventionalized Indirect Directive: Speaker is not querying ability, but politely requesting immediate action."

        if "it's cold in here" in u_lower:
            implicature = "Conversational Implicature: Hint (Off-Record) requesting addressee to close the window or adjust thermostat."

        # 3. Brown & Levinson Politeness Strategies
        if any(w in u_lower for w in ["could you possibly", "if it wouldn't be too much trouble", "would you mind", "please"]):
            politeness = "Negative Politeness (Reduces imposition, respects addressee's autonomy and negative face)"
            mitigation_score = 0.90
        elif any(w in u_lower for w in ["friend", "colleague", "we can", "let's", "great job"]):
            politeness = "Positive Politeness (Claims common ground, affirms solidarity and positive face)"
            mitigation_score = 0.85
        elif any(u_lower.startswith(w) for w in ["do this", "give me", "stop", "shut"]):
            politeness = "Bald On-Record (Direct directive without redress; high efficiency, potential face threat)"
            mitigation_score = 0.20
        elif "cold in here" in u_lower or "warm in here" in u_lower:
            politeness = "Off-Record (Hinting / indirect strategy giving speaker deniability)"
            mitigation_score = 0.95
        else:
            politeness = "Standard Conversational Neutral"
            mitigation_score = 0.70

        return PragmaticAnalysisResult(
            utterance=u,
            locutionary_act=f"The physical articulation of the phonemes, words, and syntax: '{u}'.",
            illocutionary_force=force,
            intended_perlocutionary_effect=perlocution,
            gricean_maxims_status=maxims,
            conversational_implicature=implicature,
            politeness_strategy=politeness,
            face_threat_mitigation_score=mitigation_score
        )
