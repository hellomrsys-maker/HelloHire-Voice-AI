"""Tamil Brain Computational Skills Package."""

from Tamil_engine.brain.skills.tokenization import tokenize_tamil
from Tamil_engine.brain.skills.pos_tagging import tag_pos
from Tamil_engine.brain.skills.case_engine import analyze_noun_case, inflect_case
from Tamil_engine.brain.skills.png_concord_engine import check_png_concord
from Tamil_engine.brain.skills.retroflex_engine import analyze_phonological_profile
from Tamil_engine.brain.skills.sandhi_engine import audit_sandhi, apply_sandhi
from Tamil_engine.brain.skills.pragmatics_engine import detect_register, compose_email
from Tamil_engine.brain.skills.generation import (
    generate_sov_sentence,
    generate_dative_experiencer_sentence
)

__all__ = [
    "tokenize_tamil",
    "tag_pos",
    "analyze_noun_case",
    "inflect_case",
    "check_png_concord",
    "analyze_phonological_profile",
    "audit_sandhi",
    "apply_sandhi",
    "detect_register",
    "compose_email",
    "generate_sov_sentence",
    "generate_dative_experiencer_sentence"
]
