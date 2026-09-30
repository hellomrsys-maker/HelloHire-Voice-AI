"""
Ambiguity Ranker for Japanese Sentences.
=======================================
Identifies and ranks lexical homophony, particle attachment ambiguity (Kakariuke),
and zero-pronoun scope ambiguities with Shannon entropy calculations.
"""

from __future__ import annotations
import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.skills.parsing import JapaneseParser


@dataclass
class JapaneseAmbiguityCandidate:
    ambiguity_type: str  # "homophone_lexical", "particle_attachment", "zero_subject_scope"
    trigger_phrase: str
    readings: List[Dict[str, Any]]
    entropy: float  # Higher entropy = higher uncertainty
    severity: str   # "high", "moderate", "low"


@dataclass
class JapaneseAmbiguityReport:
    text: str
    total_ambiguities: int
    mean_entropy: float
    candidates: List[JapaneseAmbiguityCandidate] = field(default_factory=list)


class JapaneseAmbiguityRanker:
    """
    Evaluates lexical homophones, particle coordination scope, and omitted subject
    ambiguities in Japanese text, ranking interpretations by Shannon entropy.
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()
        self.parser = JapaneseParser()

        # Homophones with high frequency collision
        self.homophone_lexicon = {
            "かんしょう": [("鑑賞 - Appreciation of art", 0.40), ("干渉 - Interference", 0.35), ("感傷 - Sentimentality", 0.25)],
            "こうしょう": [("交渉 - Negotiation", 0.50), ("考証 - Historical investigation", 0.25), ("高尚 - Noble/Sublime", 0.25)],
            "せいこう": [("成功 - Success", 0.60), ("精巧 - Elaborate/Exquisite", 0.25), ("性向 - Propensity", 0.15)],
            "きかん": [("期間 - Time period", 0.45), ("機関 - Institution/Engine", 0.35), ("器官 - Organ", 0.20)],
            "かいとう": [("回答 - Reply/Answer", 0.50), ("解答 - Solution to problem", 0.35), ("解凍 - Thawing/Decompress", 0.15)],
            "きしゃ": [("記者 - Journalist", 0.55), ("貴社 - Your esteemed company", 0.35), ("汽車 - Steam train", 0.10)],
        }

    def _calc_entropy(self, probabilities: List[float]) -> float:
        """Calculates Shannon entropy: - sum(p * log2(p))."""
        ent = 0.0
        for p in probabilities:
            if p > 0:
                ent -= p * math.log2(p)
        return round(ent, 4)

    def analyze(self, text: str) -> JapaneseAmbiguityReport:
        tokens = self.tokenizer.tokenize(text)
        candidates: List[JapaneseAmbiguityCandidate] = []

        # 1. Lexical homophone ambiguity (checking Kana or Romaji input)
        for tok in tokens:
            t_text = tok.text
            if t_text in self.homophone_lexicon:
                senses = self.homophone_lexicon[t_text]
                probs = [s[1] for s in senses]
                ent = self._calc_entropy(probs)
                candidates.append(
                    JapaneseAmbiguityCandidate(
                        ambiguity_type="homophone_lexical",
                        trigger_phrase=t_text,
                        readings=[{"meaning": s[0], "prior": s[1]} for s in senses],
                        entropy=ent,
                        severity="high" if ent > 1.2 else "moderate",
                    )
                )

        # 2. Particle attachment & coordination ambiguity
        # Example: AとBのC (Is it [A] and [B's C], or [(A and B)'s C]?)
        coordination_matches = re.finditer(r"([^\s、。]+)と([^\s、。]+)の([^\s、。]+)", text)
        for m in coordination_matches:
            a, b, c = m.group(1), m.group(2), m.group(3)
            readings = [
                {"reading": f"[{a} と {b}] の {c}", "probability": 0.55},
                {"reading": f"{a} と [{b} の {c}]", "probability": 0.45},
            ]
            ent = self._calc_entropy([0.55, 0.45])
            candidates.append(
                JapaneseAmbiguityCandidate(
                    ambiguity_type="particle_attachment",
                    trigger_phrase=m.group(0),
                    readings=readings,
                    entropy=ent,
                    severity="moderate",
                )
            )

        # 3. Relative clause zero-subject ambiguity
        # Example: [書いた] 人 (Did the person write, or was the person written about?)
        rel_matches = re.finditer(r"(食べた|書いた|読んだ|話した)\s*([^\s、。]+)", text)
        for m in rel_matches:
            verb, noun = m.group(1), m.group(2)
            readings = [
                {"reading": f"{noun} が {verb} (Agent relation)", "probability": 0.70},
                {"reading": f"{noun} を {verb} (Patient relation)", "probability": 0.30},
            ]
            ent = self._calc_entropy([0.70, 0.30])
            candidates.append(
                JapaneseAmbiguityCandidate(
                    ambiguity_type="zero_subject_scope",
                    trigger_phrase=m.group(0),
                    readings=readings,
                    entropy=ent,
                    severity="low",
                )
            )

        mean_ent = (
            round(sum(c.entropy for c in candidates) / len(candidates), 4)
            if candidates
            else 0.0
        )

        return JapaneseAmbiguityReport(
            text=text,
            total_ambiguities=len(candidates),
            mean_entropy=mean_ent,
            candidates=candidates,
        )
