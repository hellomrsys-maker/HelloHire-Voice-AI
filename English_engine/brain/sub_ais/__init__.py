"""
English Sub-Artificial Intelligence Package.
Contains dedicated sub-AIs for Syntax, Phonology, Pragmatics, and Editorial writing,
all strictly conforming to the Zero-Bridge Synchronous Memory Rule via direct
physical memory mapping onto the 64-byte Atomic Memory State Vector (AMSV).
"""

from English_engine.brain.sub_ais.syntax_sub_ai import EnglishSyntaxSubAI, SyntaxEvaluation
from English_engine.brain.sub_ais.phonology_sub_ai import EnglishPhonologySubAI, PhonologyEvaluation
from English_engine.brain.sub_ais.pragmatic_sub_ai import EnglishPragmaticSubAI, PragmaticEvaluation
from English_engine.brain.sub_ais.editorial_sub_ai import EnglishEditorialSubAI, EditorialEvaluation

__all__ = [
    "EnglishSyntaxSubAI",
    "SyntaxEvaluation",
    "EnglishPhonologySubAI",
    "PhonologyEvaluation",
    "EnglishPragmaticSubAI",
    "PragmaticEvaluation",
    "EnglishEditorialSubAI",
    "EditorialEvaluation",
]
