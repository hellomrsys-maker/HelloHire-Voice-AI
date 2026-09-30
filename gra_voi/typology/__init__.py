"""
Universal Comparative Grammar Typology Engine.
Translates cross-linguistic typological invariants across 11 families, 4 morphological types, and 8 pillars.
"""

from .typology_engine import UniversalTypologyAI
from .universal_language_engine import (
    UniversalLanguageEngine,
    LanguageEntry,
    LanguageClassification,
    MacroRegion,
    VitalityStatus,
    ScriptDirection,
    get_default_engine,
    get_language,
    get_language_details,
    list_old_world_languages,
    list_all_world_languages,
    search_languages,
    filter_languages,
    count_languages,
)

__all__ = [
    "UniversalTypologyAI",
    "UniversalLanguageEngine",
    "LanguageEntry",
    "LanguageClassification",
    "MacroRegion",
    "VitalityStatus",
    "ScriptDirection",
    "get_default_engine",
    "get_language",
    "get_language_details",
    "list_old_world_languages",
    "list_all_world_languages",
    "search_languages",
    "filter_languages",
    "count_languages",
]

