"""
Persian Brain Sub-AIs Package
"""

from Persian_engine.brain.sub_ais.syntax_sub_ai import PersianSyntaxSubAI
from Persian_engine.brain.sub_ais.phonology_sub_ai import PersianPhonologySubAI
from Persian_engine.brain.sub_ais.pragmatic_sub_ai import PersianPragmaticSubAI
from Persian_engine.brain.sub_ais.editorial_sub_ai import PersianEditorialSubAI

__all__ = [
    "PersianSyntaxSubAI",
    "PersianPhonologySubAI",
    "PersianPragmaticSubAI",
    "PersianEditorialSubAI",
]
