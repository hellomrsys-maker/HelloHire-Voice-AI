"""
Ambiguity Ranker for English Sentences.
Identifies and ranks lexical (polysemy/homonymy), syntactic (PP-attachment),
and scope (quantifier interaction) ambiguities with information-theoretic entropy scores.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from English_engine.brain.skills.tokenization import EnglishTokenizer
from English_engine.brain.skills.parsing import EnglishParser


@dataclass
class AmbiguityCandidate:
    ambiguity_type: str  # "syntactic_attachment", "lexical_sense", "quantifier_scope"
    trigger_phrase: str
    readings: List[Dict[str, Any]]
    entropy: float  # Higher entropy indicates higher uncertainty/ambiguity
    severity: str   # "high", "moderate", "low"


@dataclass
class AmbiguityReport:
    text: str
    total_ambiguities: int
    mean_entropy: float
    candidates: List[AmbiguityCandidate] = field(default_factory=list)


class AmbiguityRanker:
    """
    Evaluates syntactic, lexical, and structural ambiguities in English utterances,
    ranking interpretations by posterior probability and Shannon entropy.
    """

    def __init__(self) -> None:
        self.tokenizer = EnglishTokenizer()
        self.parser = EnglishParser()

        # Polysemous anchor words with multiple common frames
        self.polysemous_lexicon = {
            "bank": [("financial institution", 0.65), ("river edge", 0.35)],
            "crane": [("construction machine", 0.50), ("wading bird", 0.50)],
            "plant": [("flora / organism", 0.60), ("factory / industrial facility", 0.40)],
            "bark": [("tree covering", 0.45), ("canine vocalization", 0.55)],
            "bat": [("flying mammal", 0.40), ("sports equipment", 0.60)],
            "light": [("visible illumination", 0.70), ("low weight", 0.30)],
        }

    def _calc_entropy(self, probabilities: List[float]) -> float:
        """Calculates Shannon entropy: - sum(p * log2(p))."""
        ent = 0.0
        for p in probabilities:
            if p > 0:
                ent -= p * math.log2(p)
        return round(ent, 4)

    def analyze(self, text: str) -> AmbiguityReport:
        tokens = self.tokenizer.tokenize(text)
        words_lower = [t.text.lower() for t in tokens if t.is_word]
        candidates: List[AmbiguityCandidate] = []

        # 1. Lexical Polysemy Ambiguity
        for w in words_lower:
            if w in self.polysemous_lexicon:
                senses = self.polysemous_lexicon[w]
                probs = [s[1] for s in senses]
                ent = self._calc_entropy(probs)
                candidates.append(
                    AmbiguityCandidate(
                        ambiguity_type="lexical_sense",
                        trigger_phrase=w,
                        readings=[{"sense": s[0], "prior_probability": s[1]} for s in senses],
                        entropy=ent,
                        severity="high" if ent > 0.9 else "moderate",
                    )
                )

        # 2. Prepositional Phrase (PP) Attachment Ambiguity
        # Classic pattern: VERB + NP + PREP + NP (e.g., "saw the man with telescope", "observed the star with a telescope")
        for i in range(len(words_lower) - 2):
            if words_lower[i] in {"saw", "observed", "hit", "caught", "inspected"}:
                for p_offset in range(2, min(5, len(words_lower) - i)):
                    if words_lower[i + p_offset] in {"with", "in", "from", "on"}:
                        prep_word = words_lower[i + p_offset]
                        rem = words_lower[i + p_offset + 1 :]
                        target_obj = rem[0] if rem else "object"
                        candidate_readings = [
                            {
                                "attachment": "VP-attached (instrument)",
                                "interpretation": f"The action of '{words_lower[i]}' was done using '{target_obj}'",
                                "probability": 0.52,
                            },
                            {
                                "attachment": "NP-attached (modifier)",
                                "interpretation": f"The object of '{words_lower[i]}' possessed or was associated with '{target_obj}'",
                                "probability": 0.48,
                            },
                        ]
                        ent = self._calc_entropy([0.52, 0.48])
                        candidates.append(
                            AmbiguityCandidate(
                                ambiguity_type="syntactic_attachment",
                                trigger_phrase=f"{words_lower[i]} ... {prep_word} {target_obj}",
                                readings=candidate_readings,
                                entropy=ent,
                                severity="high",
                            )
                        )
                        break

        # 3. Quantifier Scope Ambiguity
        # Pattern: "Every/All ... a/some ..."
        if ("every" in words_lower or "all" in words_lower) and ("a" in words_lower or "one" in words_lower):
            scope_readings = [
                {
                    "scope": "Surface Scope (Universal > Existential)",
                    "meaning": "For each entity x, there is an entity y",
                    "probability": 0.65,
                },
                {
                    "scope": "Inverse Scope (Existential > Universal)",
                    "meaning": "There is a single entity y such that for all x...",
                    "probability": 0.35,
                },
            ]
            ent = self._calc_entropy([0.65, 0.35])
            candidates.append(
                AmbiguityCandidate(
                    ambiguity_type="quantifier_scope",
                    trigger_phrase=text,
                    readings=scope_readings,
                    entropy=ent,
                    severity="moderate",
                )
            )

        # Sort by entropy descending
        candidates.sort(key=lambda c: c.entropy, reverse=True)
        mean_ent = (
            sum(c.entropy for c in candidates) / len(candidates) if candidates else 0.0
        )

        return AmbiguityReport(
            text=text,
            total_ambiguities=len(candidates),
            mean_entropy=round(mean_ent, 4),
            candidates=candidates,
        )
