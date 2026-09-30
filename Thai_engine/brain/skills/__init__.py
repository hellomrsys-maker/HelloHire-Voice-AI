"""Thai Brain Computational Skills Package."""

from Thai_engine.brain.skills.tokenization import tokenize_thai
from Thai_engine.brain.skills.pos_tagging import tag_pos
from Thai_engine.brain.skills.tone_engine import calculate_syllable_tone, get_consonant_class
from Thai_engine.brain.skills.classifier_engine import (
    get_classifier_for_noun,
    audit_classifier_syntax
)
from Thai_engine.brain.skills.politeness_engine import audit_politeness_particles
from Thai_engine.brain.skills.rachasap_engine import detect_register, compose_email
from Thai_engine.brain.skills.generation import generate_thai_sentence

__all__ = [
    "tokenize_thai",
    "tag_pos",
    "calculate_syllable_tone",
    "get_consonant_class",
    "get_classifier_for_noun",
    "audit_classifier_syntax",
    "audit_politeness_particles",
    "detect_register",
    "compose_email",
    "generate_thai_sentence"
]
