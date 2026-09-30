"""Cantonese Brain Computational Skills Package."""

from Cantonese_engine.brain.skills.tokenization import tokenize_cantonese
from Cantonese_engine.brain.skills.pos_tagging import tag_pos
from Cantonese_engine.brain.skills.tone_engine import (
    analyze_character_tone,
    text_to_jyutping,
    is_entering_tone
)
from Cantonese_engine.brain.skills.classifier_engine import (
    get_classifier_for_noun,
    parse_classifier_phrase
)
from Cantonese_engine.brain.skills.doc_inversion_engine import (
    analyze_doc_structure,
    analyze_postverbal_adverb,
    invert_to_canonical_cantonese
)
from Cantonese_engine.brain.skills.aspect_engine import (
    extract_aspect_markers,
    has_aspect
)
from Cantonese_engine.brain.skills.sfp_engine import (
    extract_sfps,
    has_sfp
)
from Cantonese_engine.brain.skills.pragmatics_engine import (
    detect_register,
    compose_email
)
from Cantonese_engine.brain.skills.generation import (
    generate_cantonese_sentence,
    generate_comparative
)

__all__ = [
    "tokenize_cantonese",
    "tag_pos",
    "analyze_character_tone",
    "text_to_jyutping",
    "is_entering_tone",
    "get_classifier_for_noun",
    "parse_classifier_phrase",
    "analyze_doc_structure",
    "analyze_postverbal_adverb",
    "invert_to_canonical_cantonese",
    "extract_aspect_markers",
    "has_aspect",
    "extract_sfps",
    "has_sfp",
    "detect_register",
    "compose_email",
    "generate_cantonese_sentence",
    "generate_comparative"
]
