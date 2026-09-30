"""
Italian Engine — Brain Skills Package
"""

from .tokenization import tokenize_words, split_sentences, split_elision
from .pos_tagging import tag_pos
from .verb_conjugator import conjugate_verb
from .auxiliary_selector import select_auxiliary, compute_participle_concord, validate_passato_prossimo
from .clitic_engine import combine_clitics, attach_enclitic
from .articulated_prep_engine import select_article, fuse_preposition
from .subjunctive_engine import detect_subjunctive_triggers
from .pragmatics_engine import classify_register, format_salutation, format_closing
from .generation import generate_sentence

__all__ = [
    "tokenize_words",
    "split_sentences",
    "split_elision",
    "tag_pos",
    "conjugate_verb",
    "select_auxiliary",
    "compute_participle_concord",
    "validate_passato_prossimo",
    "combine_clitics",
    "attach_enclitic",
    "select_article",
    "fuse_preposition",
    "detect_subjunctive_triggers",
    "classify_register",
    "format_salutation",
    "format_closing",
    "generate_sentence",
]
