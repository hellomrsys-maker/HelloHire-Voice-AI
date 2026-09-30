"""
Vietnamese Brain Sub-AIs Package
"""

from Vietnamese_engine.brain.sub_ais.syntax_sub_ai import VietnameseSyntaxSubAI
from Vietnamese_engine.brain.sub_ais.phonology_sub_ai import VietnamesePhonologySubAI
from Vietnamese_engine.brain.sub_ais.pragmatic_sub_ai import VietnamesePragmaticSubAI
from Vietnamese_engine.brain.sub_ais.editorial_sub_ai import VietnameseEditorialSubAI

__all__ = [
    "VietnameseSyntaxSubAI",
    "VietnamesePhonologySubAI",
    "VietnamesePragmaticSubAI",
    "VietnameseEditorialSubAI",
]
