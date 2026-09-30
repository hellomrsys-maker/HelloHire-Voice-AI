"""
Japanese Engine Brain Sub-AIs Package
=====================================
Dedicated Sub-AIs operating under the Zero-Bridge Synchronous Memory Rule:
- JapaneseSyntaxSubAI, JapaneseSyntaxEvaluation
- JapanesePhonologySubAI, JapanesePhonologyEvaluation
- JapanesePragmaticSubAI, JapanesePragmaticEvaluation
- JapaneseEditorialSubAI, JapaneseEditorialEvaluation
"""

from .syntax_sub_ai import JapaneseSyntaxSubAI, JapaneseSyntaxEvaluation
from .phonology_sub_ai import JapanesePhonologySubAI, JapanesePhonologyEvaluation
from .pragmatic_sub_ai import JapanesePragmaticSubAI, JapanesePragmaticEvaluation
from .editorial_sub_ai import JapaneseEditorialSubAI, JapaneseEditorialEvaluation

__all__ = [
    "JapaneseSyntaxSubAI",
    "JapaneseSyntaxEvaluation",
    "JapanesePhonologySubAI",
    "JapanesePhonologyEvaluation",
    "JapanesePragmaticSubAI",
    "JapanesePragmaticEvaluation",
    "JapaneseEditorialSubAI",
    "JapaneseEditorialEvaluation",
]
