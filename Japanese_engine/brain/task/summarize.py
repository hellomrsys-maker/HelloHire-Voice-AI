"""
Japanese Text Summarization Pipeline
====================================
Extractive summarizer for Japanese discourse leveraging Bunsetsu topic centrality,
Ki-shō-ten-ketsu positioning, and argumentative connective salience.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.skills.parsing import JapaneseParser


@dataclass
class JapaneseSummaryResult:
    original_text: str
    summary_text: str
    compression_ratio: float
    selected_sentence_indices: List[int]
    key_topics: List[str] = field(default_factory=list)


class JapaneseSummarizer:
    """
    Extractive summarization tailored to Japanese discourse conventions.
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()
        self.parser = JapaneseParser()

    def summarize(self, text: str, max_sentences: int = 2) -> JapaneseSummaryResult:
        sentences = [s.strip() for s in re.split(r"[。！？\n]+", text) if s.strip()]
        if not sentences:
            return JapaneseSummaryResult(text, "", 0.0, [], [])

        if len(sentences) <= max_sentences:
            return JapaneseSummaryResult(
                original_text=text,
                summary_text="。".join(sentences) + "。",
                compression_ratio=1.0,
                selected_sentence_indices=list(range(len(sentences))),
                key_topics=[],
            )

        scored_sentences = []
        n = len(sentences)
        all_topics = set()

        for idx, s in enumerate(sentences):
            score = 0.0
            # 1. Positional weight (Lead and Concluding sentences)
            if idx == 0:
                score += 3.0  # Ki (Introduction)
            elif idx == n - 1:
                score += 3.5  # Ketsu (Conclusion)

            # 2. Argumentative and summary markers
            summary_markers = ["結論", "要するに", "したがって", "そのため", "重要", "要点", "本稿", "目的"]
            for sm in summary_markers:
                if sm in s:
                    score += 2.5

            # 3. Topic marker 'は'
            topics = re.findall(r"([^\s、。]+)は", s)
            score += len(topics) * 1.2
            all_topics.update(topics)

            # 4. Length penalty (neither too short nor overly long run-on)
            char_len = len(s)
            if 25 <= char_len <= 90:
                score += 1.5

            scored_sentences.append((score, idx, s))

        # Sort by score descending and take top N
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        chosen = scored_sentences[:max_sentences]
        # Restore chronological reading order
        chosen.sort(key=lambda x: x[1])

        summary = "。".join([item[2] for item in chosen]) + "。"
        indices = [item[1] for item in chosen]
        ratio = round(len(summary) / max(1, len(text)), 2)

        return JapaneseSummaryResult(
            original_text=text,
            summary_text=summary,
            compression_ratio=ratio,
            selected_sentence_indices=indices,
            key_topics=list(all_topics)[:5],
        )
