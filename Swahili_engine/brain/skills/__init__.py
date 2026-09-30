"""
Swahili Engine — Skills Package
"""

from .tokenization import split_sentences, tokenize_words
from .noun_class_engine import identify_noun_class, NOUN_CLASS_LEXICON
from .concord_engine import (
    get_adjective_form,
    get_demonstrative,
    get_possessive,
    get_associative_a,
    generate_concordial_np,
    validate_concord
)
from .verbal_template_engine import synthesize_verb, parse_verb_structure
from .verbal_extensions_engine import derive_extension, get_root_vowel
from .monosyllabic_verb_engine import is_monosyllabic_verb, should_retain_ku
from .pos_tagging import tag_pos
from .pragmatics_engine import validate_greeting_turn, audit_letter_etiquette
from .generation import generate_svo_clause, generate_formal_email

__all__ = [
    "split_sentences",
    "tokenize_words",
    "identify_noun_class",
    "NOUN_CLASS_LEXICON",
    "get_adjective_form",
    "get_demonstrative",
    "get_possessive",
    "get_associative_a",
    "generate_concordial_np",
    "validate_concord",
    "synthesize_verb",
    "parse_verb_structure",
    "derive_extension",
    "get_root_vowel",
    "is_monosyllabic_verb",
    "should_retain_ku",
    "tag_pos",
    "validate_greeting_turn",
    "audit_letter_etiquette",
    "generate_svo_clause",
    "generate_formal_email"
]
