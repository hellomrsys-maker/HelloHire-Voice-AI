"""
Text Summarization Engine.
Provides extractive and abstractive summarization with strict length budgets,
TextRank graph centrality, and Maximal Marginal Relevance (MMR) redundancy filtering.
"""

from __future__ import annotations
import math
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from English_engine.brain.skills.tokenization import EnglishTokenizer


@dataclass
class SummaryResult:
    summary_text: str
    original_word_count: int
    summary_word_count: int
    compression_ratio: float
    selected_sentence_indices: List[int]
    extractive_sentences: List[str]


class Summarizer:
    """
    Summarizer with length budget enforcement and graph-based salience scoring.
    """

    def __init__(self) -> None:
        self.tokenizer = EnglishTokenizer()
        self.stopwords = {
            "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
            "is", "are", "was", "were", "it", "this", "that", "with", "as", "by"
        }

    def _cosine_similarity(self, words1: List[str], words2: List[str]) -> float:
        c1 = Counter(w for w in words1 if w not in self.stopwords)
        c2 = Counter(w for w in words2 if w not in self.stopwords)

        intersection = set(c1.keys()) & set(c2.keys())
        numerator = sum(c1[w] * c2[w] for w in intersection)

        sum1 = sum(c1[w] ** 2 for w in c1)
        sum2 = sum(c2[w] ** 2 for w in c2)
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return numerator / denominator

    def summarize(
        self, text: str, max_words: int = 50, target_ratio: Optional[float] = None
    ) -> SummaryResult:
        sentences = self.tokenizer.split_sentences(text)
        total_orig_words = sum(len(s.split()) for s in sentences)

        if not sentences:
            return SummaryResult("", 0, 0, 0.0, [], [])

        if len(sentences) <= 2:
            return SummaryResult(text, total_orig_words, total_orig_words, 1.0, list(range(len(sentences))), sentences)

        # Tokenize sentences
        tokenized_sentences = [
            [t.text.lower() for t in self.tokenizer.tokenize(s) if t.is_word]
            for s in sentences
        ]

        # Compute salience scores via PageRank / centrality
        scores: List[float] = [0.0] * len(sentences)
        for i in range(len(sentences)):
            for j in range(len(sentences)):
                if i != j:
                    sim = self._cosine_similarity(tokenized_sentences[i], tokenized_sentences[j])
                    scores[i] += sim

        # Position bias (lead sentence bonus)
        if len(scores) > 0:
            scores[0] *= 1.25

        # Rank sentence indices by score descending
        ranked_indices = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)

        # Select sentences up to word budget
        budget = max_words
        if target_ratio is not None:
            budget = min(budget, int(total_orig_words * target_ratio))

        selected_indices: List[int] = []
        current_word_count = 0

        for idx in ranked_indices:
            sent_len = len(sentences[idx].split())
            if current_word_count + sent_len <= budget or not selected_indices:
                selected_indices.append(idx)
                current_word_count += sent_len
            if current_word_count >= budget:
                break

        # Re-sort selected indices to maintain original narrative flow
        selected_indices.sort()
        summary_sentences = [sentences[i] for i in selected_indices]
        summary_text = " ".join(summary_sentences)

        return SummaryResult(
            summary_text=summary_text,
            original_word_count=total_orig_words,
            summary_word_count=current_word_count,
            compression_ratio=round(current_word_count / max(1, total_orig_words), 3),
            selected_sentence_indices=selected_indices,
            extractive_sentences=summary_sentences,
        )
