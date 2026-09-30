"""
sentiment.py - Japanese Sentiment Analysis, Affective Valence, and Epistemic Modality Certainty.
Evaluates polarity while accounting for Japanese suffixal negation (-nai, -masen)
and epistemic sentence-final modals (-darou, -kamoshirenai, -ni chigainai).
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class JapaneseSentimentResult:
    sentiment: str  # "POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"
    valence: float  # -1.0 to +1.0
    certainty: float  # 0.0 to 1.0

    def __getitem__(self, item):
        return getattr(self, item)


class JapaneseSentimentClassifier:
    """
    Japanese valence and epistemic certainty classifier.
    """

    POSITIVE_WORDS = {
        "素晴らしい", "良い", "いい", "正確", "優れた", "優れている", "成功",
        "美しい", "適切", "効果的", "高度", "向上", "達成", "満足", "最高"
    }

    NEGATIVE_WORDS = {
        "悪い", "間違い", "欠陥", "遅い", "失敗", "不良", "危険", "困難",
        "問題", "不具合", "低下", "悪化", "不快", "最悪", "不足"
    }

    NEGATORS = {"ない", "なかった", "ず", "ぬ", "ません", "でした", "なく"}

    CERTAINTY_BOOSTERS = {"確実に", "必ず", "に違いない", "明確に", "絶対に", "当然"}
    HEDGES = {"かもしれない", "だろう", "と思う", "ようだ", "らしい", "そうだ", "おそらく"}

    def classify(self, text: str) -> JapaneseSentimentResult:
        data = self.analyze(text)
        return JapaneseSentimentResult(
            sentiment=data["sentiment"],
            valence=data["valence_score"],
            certainty=data["epistemic_certainty"],
        )

    def analyze(self, text: str) -> Dict[str, Any]:
        pos_hits = sum(1 for w in self.POSITIVE_WORDS if w in text)
        neg_hits = sum(1 for w in self.NEGATIVE_WORDS if w in text)

        # Check for clause-final or word-adjacent negation
        has_negation = any(neg in text for neg in self.NEGATORS)
        if has_negation and (pos_hits > 0 or neg_hits > 0):
            # Invert hits if negated
            pos_hits, neg_hits = neg_hits, pos_hits

        total_hits = pos_hits + neg_hits
        if total_hits == 0:
            sentiment = "NEUTRAL"
            valence = 0.5
        elif pos_hits > neg_hits:
            sentiment = "POSITIVE"
            valence = round(pos_hits / total_hits, 2)
        elif neg_hits > pos_hits:
            sentiment = "NEGATIVE"
            valence = round(-(neg_hits / total_hits), 2)
        else:
            sentiment = "MIXED"
            valence = 0.5

        # Epistemic certainty
        booster_count = sum(1 for b in self.CERTAINTY_BOOSTERS if b in text)
        hedge_count = sum(1 for h in self.HEDGES if h in text)

        if booster_count > 0 and hedge_count == 0:
            certainty = 0.90
        elif hedge_count > 0:
            certainty = 0.45
        else:
            certainty = 0.70

        return {
            "sentiment": sentiment,
            "valence_score": valence,
            "epistemic_certainty": certainty,
            "positive_hits": pos_hits,
            "negative_hits": neg_hits,
            "has_negation": has_negation,
        }
