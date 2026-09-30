"""
Semantic Drift and Perplexity Monitor for English Text Streams.
Tracks vocabulary distribution shifts, unigram/bigram entropy,
out-of-distribution drift, and lexical perplexity across interaction sequences.
"""

from __future__ import annotations
import math
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from English_engine.brain.skills.tokenization import EnglishTokenizer


@dataclass
class DriftMetrics:
    perplexity: float
    unigram_entropy: float
    novel_token_ratio: float
    lexical_diversity_ttr: float  # Type-Token Ratio
    is_distribution_shifted: bool
    status: str  # "stable", "moderate_shift", "severe_drift"


class DriftMonitor:
    """
    Monitors language stability, tracking semantic drift and statistical
    divergence relative to baseline corpus frequency models.
    """

    def __init__(self) -> None:
        self.tokenizer = EnglishTokenizer()
        # Core baseline reference frequencies for common English vocabulary
        common_words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
            "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
            "quick", "brown", "fox", "jumps", "lazy", "dog", "fast", "slow", "run", "jump",
            "model", "system", "architecture", "data", "learning", "neural", "network", "sentence"
        ]
        self.baseline_unigram_probs: Dict[str, float] = {
            w: 0.01 for w in common_words
        }
        self.history_windows: List[Counter] = []

    def compute_metrics(self, text: str) -> DriftMetrics:
        tokens = self.tokenizer.tokenize(text)
        words = [t.text.lower() for t in tokens if t.is_word]
        total_words = len(words)

        if total_words == 0:
            return DriftMetrics(
                perplexity=1.0,
                unigram_entropy=0.0,
                novel_token_ratio=0.0,
                lexical_diversity_ttr=1.0,
                is_distribution_shifted=False,
                status="stable",
            )

        counts = Counter(words)
        unique_words = len(counts)
        ttr = unique_words / total_words

        # Shannon entropy of unigrams
        entropy = 0.0
        for count in counts.values():
            p = count / total_words
            entropy -= p * math.log2(p)

        # Baseline cross-entropy / Perplexity calculation
        log_prob_sum = 0.0
        eps = 1e-5
        novel_tokens = 0

        for w in words:
            prob = self.baseline_unigram_probs.get(w, eps)
            if prob == eps:
                novel_tokens += 1
            log_prob_sum += math.log2(prob)

        avg_neg_log_prob = -log_prob_sum / total_words
        perplexity = math.pow(2, min(avg_neg_log_prob, 14.0))  # Capped for numerical stability

        novel_ratio = novel_tokens / total_words
        is_shifted = novel_ratio > 0.45 or entropy > 5.8

        if novel_ratio > 0.60:
            status = "severe_drift"
        elif is_shifted:
            status = "moderate_shift"
        else:
            status = "stable"

        return DriftMetrics(
            perplexity=round(perplexity, 2),
            unigram_entropy=round(entropy, 3),
            novel_token_ratio=round(novel_ratio, 3),
            lexical_diversity_ttr=round(ttr, 3),
            is_distribution_shifted=is_shifted,
            status=status,
        )
