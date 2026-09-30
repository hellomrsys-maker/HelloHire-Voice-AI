"""Cantonese Dedicated Sub-AIs Package."""

from Cantonese_engine.brain.sub_ais.syntax_sub_ai import CantoneseSyntaxSubAI
from Cantonese_engine.brain.sub_ais.phonology_sub_ai import CantonesePhonologySubAI
from Cantonese_engine.brain.sub_ais.pragmatic_sub_ai import CantonesePragmaticSubAI
from Cantonese_engine.brain.sub_ais.editorial_sub_ai import CantoneseEditorialSubAI

__all__ = [
    "CantoneseSyntaxSubAI",
    "CantonesePhonologySubAI",
    "CantonesePragmaticSubAI",
    "CantoneseEditorialSubAI"
]
