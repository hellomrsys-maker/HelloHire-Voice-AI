"""Tamil Sub-AIs Package."""

from Tamil_engine.brain.sub_ais.syntax_sub_ai import TamilSyntaxSubAI
from Tamil_engine.brain.sub_ais.phonology_sub_ai import TamilPhonologySubAI
from Tamil_engine.brain.sub_ais.pragmatic_sub_ai import TamilPragmaticSubAI
from Tamil_engine.brain.sub_ais.editorial_sub_ai import TamilEditorialSubAI

__all__ = [
    "TamilSyntaxSubAI",
    "TamilPhonologySubAI",
    "TamilPragmaticSubAI",
    "TamilEditorialSubAI"
]
