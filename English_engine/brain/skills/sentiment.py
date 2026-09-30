"""
sentiment.py - Negation-aware sentiment analysis, affective valence, and epistemic certainty scoring.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, Any

POSITIVE_WORDS = {
    "good", "great", "excellent", "accurate", "clean", "rigorous", "efficient",
    "superior", "robust", "resilient", "mastery", "flawless", "proven", "positive", "exceptionally"
}
NEGATIVE_WORDS = {
    "bad", "terrible", "faulty", "error", "failing", "broken", "flawed",
    "inefficient", "sluggish", "defect", "bottleneck", "rejected", "negative"
}
NEGATORS = {"not", "never", "no", "n't", "hardly", "barely", "scarcely", "without"}
CERTAINTY_BOOSTERS = {"definitely", "certainly", "clearly", "undoubtedly", "proven", "always"}
HEDGES = {"maybe", "perhaps", "possibly", "likely", "might", "could", "somewhat"}


@dataclass
class SentimentResult:
    sentiment: str  # "POSITIVE", "NEGATIVE", "NEUTRAL"
    valence: float  # -1.0 to +1.0 (or normalized positive score)
    certainty: float  # 0.0 to 1.0

    def __getitem__(self, item):
        return getattr(self, item)


class EnglishSentimentClassifier:
    """
    Negation-sensitive valence analyzer and epistemic certainty ranker.
    """

    def classify(self, text: str) -> SentimentResult:
        data = self.analyze(text)
        return SentimentResult(
            sentiment=data["sentiment"],
            valence=data["valence_score"],
            certainty=data["epistemic_certainty"],
        )

    def analyze(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"\b[\w']+\b", text.lower())
        pos_hits = 0
        neg_hits = 0
        hedge_count = 0
        certainty_count = 0

        negated = False
        negation_window = 0

        for w in words:
            if w in NEGATORS:
                negated = True
                negation_window = 3
                continue

            if w in CERTAINTY_BOOSTERS:
                certainty_count += 1
            if w in HEDGES:
                hedge_count += 1

            if w in POSITIVE_WORDS:
                if negated and negation_window > 0:
                    neg_hits += 1
                else:
                    pos_hits += 1

            elif w in NEGATIVE_WORDS:
                if negated and negation_window > 0:
                    pos_hits += 1
                else:
                    neg_hits += 1

            if negation_window > 0:
                negation_window -= 1
                if negation_window == 0:
                    negated = False

        total_sentiment_tokens = pos_hits + neg_hits
        if total_sentiment_tokens == 0:
            sentiment = "NEUTRAL"
            valence_score = 0.5
        elif pos_hits > neg_hits:
            sentiment = "POSITIVE"
            valence_score = round(pos_hits / total_sentiment_tokens, 2)
        elif neg_hits > pos_hits:
            sentiment = "NEGATIVE"
            valence_score = round(- (neg_hits / total_sentiment_tokens), 2)
        else:
            sentiment = "MIXED"
            valence_score = 0.5

        # Epistemic certainty score
        total_markers = hedge_count + certainty_count
        if total_markers == 0:
            certainty = 0.5
        else:
            certainty = round(certainty_count / total_markers, 2)

        return {
            "sentiment": sentiment,
            "valence_score": valence_score,
            "epistemic_certainty": certainty,
            "positive_hits": pos_hits,
            "negative_hits": neg_hits,
            "hedge_count": hedge_count,
            "booster_count": certainty_count
        }
