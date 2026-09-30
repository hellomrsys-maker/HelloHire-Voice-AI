"""
German Engine — Skills Package
"""

from .tokenization import tokenize_words, split_sentences, normalize_orthography, detect_compounds
from .pos_tagging import tag_pos
from .adjective_declension_engine import (
    DECLENSION_TABLE,
    determine_declension_type,
    inflect_adjective,
    validate_adjective_agreement
)
from .case_engine import (
    get_preposition_governed_case,
    validate_prepositional_phrase,
    get_verb_valency
)
from .separable_verb_engine import (
    is_separable_prefix,
    split_infinitive,
    detect_clause_separable_verb
)
from .verb_conjugator import conjugate_present, form_participle_ii
from .modal_particle_engine import analyze_modal_particles
from .pragmatics_engine import analyze_register, validate_substantive_capitalization
from .parsing import parse_topological_fields
from .generation import generate_noun_phrase, generate_formal_email, generate_informal_message

__all__ = [
    "tokenize_words",
    "split_sentences",
    "normalize_orthography",
    "detect_compounds",
    "tag_pos",
    "DECLENSION_TABLE",
    "determine_declension_type",
    "inflect_adjective",
    "validate_adjective_agreement",
    "get_preposition_governed_case",
    "validate_prepositional_phrase",
    "get_verb_valency",
    "is_separable_prefix",
    "split_infinitive",
    "detect_clause_separable_verb",
    "conjugate_present",
    "form_participle_ii",
    "analyze_modal_particles",
    "analyze_register",
    "validate_substantive_capitalization",
    "parse_topological_fields",
    "generate_noun_phrase",
    "generate_formal_email",
    "generate_informal_message"
]
