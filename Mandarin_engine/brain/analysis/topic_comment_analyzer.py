"""
Mandarin Topic-Comment Syntactic Analyzer.
Evaluates pragmatic grounding (Topic) vs predication (Comment) structure.
"""

from typing import Dict, Any, Optional


class TopicCommentAnalyzer:
    """
    Analyzes information packaging in Mandarin Chinese.
    """

    def analyze(self, text: str) -> Dict[str, Any]:
        has_comma = "，" in text or "," in text
        topic = None
        comment = None

        if "，" in text:
            parts = text.split("，", 1)
            topic = parts[0].strip()
            comment = parts[1].strip()
        elif "," in text:
            parts = text.split(",", 1)
            topic = parts[0].strip()
            comment = parts[1].strip()

        is_topic_comment = topic is not None and len(topic) > 0

        return {
            "is_topic_comment": is_topic_comment,
            "topic": topic,
            "comment": comment,
            "syntactic_harmony": "Topic-Prominent" if is_topic_comment else "Canonical-SVO",
        }
