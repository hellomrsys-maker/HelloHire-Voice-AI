"""
Japanese Semantic Drift Monitor
===============================
Tracks distribution shifts, vocabulary divergence, and semantic drift
in Japanese texts using Kullback-Leibler (KL) divergence and kanji/kana ratio telemetry.
"""

from __future__ import annotations
import math
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer


@dataclass
class JapaneseDriftMetrics:
    total_tokens: int
    unique_tokens: int
    ttr: float  # Type-Token Ratio
    kanji_ratio: float
    kl_divergence: float
    drift_detected: bool
    summary: str


class JapaneseDriftMonitor:
    """
    Monitors linguistic shifts from reference baseline distributions in Japanese,
    measuring lexical entropy, vocabulary exhaustion, and divergence.
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()
        # Baseline reference distribution of common Japanese lexical and grammatical items
        self.baseline_dist: Dict[str, float] = {
            "これ": 0.05, "それ": 0.04, "日本": 0.03, "言語": 0.04, "システム": 0.03,
            "開発": 0.03, "研究": 0.02, "考える": 0.03, "行う": 0.04, "機能": 0.03,
            "人間": 0.02, "処理": 0.03, "時間": 0.02, "問題": 0.03, "必要": 0.03,
            "情報": 0.03, "技術": 0.03, "分析": 0.03, "結果": 0.02, "構造": 0.02,
        }
        # Normalize baseline
        b_sum = sum(self.baseline_dist.values())
        self.baseline_dist = {k: v / b_sum for k, v in self.baseline_dist.items()}

    def evaluate(self, text: str) -> JapaneseDriftMetrics:
        tokens = self.tokenizer.tokenize(text)
        token_texts = [t.text for t in tokens if len(t.text.strip()) > 0]
        n_total = len(token_texts)

        if n_total == 0:
            return JapaneseDriftMetrics(
                total_tokens=0,
                unique_tokens=0,
                ttr=0.0,
                kanji_ratio=0.0,
                kl_divergence=0.0,
                drift_detected=False,
                summary="Empty text - no drift detectable.",
            )

        # Type-Token Ratio (TTR)
        unique_counts = Counter(token_texts)
        ttr = len(unique_counts) / n_total

        # Kanji ratio
        kanji_count = sum(len([c for c in t.text if "\u4e00" <= c <= "\u9faf"]) for t in tokens)
        total_chars = sum(len(t.text) for t in tokens)
        kanji_ratio = kanji_count / max(1, total_chars)

        # Relative distribution of observed vocabulary against baseline
        obs_dist = {w: count / n_total for w, count in unique_counts.items()}

        # KL Divergence: D_KL(P || Q) with Laplace smoothing
        vocab_union = set(self.baseline_dist.keys()) | set(obs_dist.keys())
        epsilon = 1e-5
        kl_div = 0.0

        for w in vocab_union:
            p = obs_dist.get(w, epsilon)
            q = self.baseline_dist.get(w, epsilon)
            kl_div += p * math.log2(p / q)

        kl_div = round(max(0.0, kl_div), 4)
        is_drift = kl_div > 4.5 or kanji_ratio > 0.70 or kanji_ratio < 0.05

        summary = (
            f"Drift alert: KL divergence is {kl_div} with kanji density {round(kanji_ratio, 2)}."
            if is_drift
            else f"Stable distribution: KL divergence is {kl_div}, TTR is {round(ttr, 2)}."
        )

        return JapaneseDriftMetrics(
            total_tokens=n_total,
            unique_tokens=len(unique_counts),
            ttr=round(ttr, 4),
            kanji_ratio=round(kanji_ratio, 4),
            kl_divergence=kl_div,
            drift_detected=is_drift,
            summary=summary,
        )
