"""
Italian Engine — Sub-AIs Package
"""

from .syntax_sub_ai import ItalianSyntaxSubAI
from .phonology_sub_ai import ItalianPhonologySubAI
from .pragmatic_sub_ai import ItalianPragmaticSubAI
from .editorial_sub_ai import ItalianEditorialSubAI

__all__ = [
    "ItalianSyntaxSubAI",
    "ItalianPhonologySubAI",
    "ItalianPragmaticSubAI",
    "ItalianEditorialSubAI"
]
