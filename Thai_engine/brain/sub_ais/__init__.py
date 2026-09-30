"""Thai Sub-AIs Package."""

from Thai_engine.brain.sub_ais.syntax_sub_ai import ThaiSyntaxSubAI
from Thai_engine.brain.sub_ais.phonology_sub_ai import ThaiPhonologySubAI
from Thai_engine.brain.sub_ais.pragmatic_sub_ai import ThaiPragmaticSubAI
from Thai_engine.brain.sub_ais.editorial_sub_ai import ThaiEditorialSubAI

__all__ = [
    "ThaiSyntaxSubAI",
    "ThaiPhonologySubAI",
    "ThaiPragmaticSubAI",
    "ThaiEditorialSubAI"
]
