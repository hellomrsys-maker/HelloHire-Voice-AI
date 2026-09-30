"""
Indonesian Engine — Sub-AIs Package
"""

from .syntax_sub_ai import IndonesianSyntaxSubAI
from .phonology_sub_ai import IndonesianPhonologySubAI
from .pragmatic_sub_ai import IndonesianPragmaticSubAI
from .editorial_sub_ai import IndonesianEditorialSubAI

__all__ = [
    "IndonesianSyntaxSubAI",
    "IndonesianPhonologySubAI",
    "IndonesianPragmaticSubAI",
    "IndonesianEditorialSubAI"
]
