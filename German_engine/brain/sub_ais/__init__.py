"""
German Engine — Dedicated Sub-AIs Package
"""

from .syntax_sub_ai import GermanSyntaxSubAI
from .phonology_sub_ai import GermanPhonologySubAI
from .pragmatic_sub_ai import GermanPragmaticSubAI
from .editorial_sub_ai import GermanEditorialSubAI

__all__ = [
    "GermanSyntaxSubAI",
    "GermanPhonologySubAI",
    "GermanPragmaticSubAI",
    "GermanEditorialSubAI"
]
