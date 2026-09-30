"""
Arabic Engine Computational Skills
"""

from .tokenization import split_sentences, tokenize_words, strip_tatweel
from .root_pattern_engine import derive_form, extract_root_heuristic
from .broken_plural_engine import get_plural, analyze_plural
from .concord_agreement_engine import (
    validate_vso_agreement,
    validate_svo_agreement,
    validate_noun_adjective_agreement
)
from .idafa_engine import validate_idafa, synthesize_idafa
from .sun_moon_engine import is_sun_letter, apply_sun_moon_article, check_phonological_assimilation
from .pos_tagging import tag_pos
from .pragmatics_engine import validate_greeting_turn, audit_letter_etiquette
from .generation import generate_vso_clause, generate_svo_clause, generate_formal_email, generate_polite_message

__all__ = [
    "split_sentences",
    "tokenize_words",
    "strip_tatweel",
    "derive_form",
    "extract_root_heuristic",
    "get_plural",
    "analyze_plural",
    "validate_vso_agreement",
    "validate_svo_agreement",
    "validate_noun_adjective_agreement",
    "validate_idafa",
    "synthesize_idafa",
    "is_sun_letter",
    "apply_sun_moon_article",
    "check_phonological_assimilation",
    "tag_pos",
    "validate_greeting_turn",
    "audit_letter_etiquette",
    "generate_vso_clause",
    "generate_svo_clause",
    "generate_formal_email",
    "generate_polite_message"
]
