"""
Unit tests for UniversalLanguageEngine.
Verifies completeness, Old World vs World language listing, multi-attribute queries,
ISO code lookups, edge-case error handling, and data invariants.
"""

import pytest
from gra_voi.typology.universal_language_engine import (
    UniversalLanguageEngine,
    LanguageEntry,
    LanguageClassification,
    MacroRegion,
    VitalityStatus,
    ScriptDirection,
    LanguageNotFoundError,
    InvalidQueryError,
    get_default_engine,
    get_language,
    get_language_details,
    list_old_world_languages,
    list_all_world_languages,
    search_languages,
    filter_languages,
    count_languages,
)


@pytest.fixture
def engine() -> UniversalLanguageEngine:
    return UniversalLanguageEngine()


def test_catalog_completeness(engine: UniversalLanguageEngine):
    counts = engine.count_languages()
    assert counts["total_languages"] >= 100
    assert counts["old_world_languages"] >= 80
    assert counts["new_world_languages"] >= 15
    assert counts["pacific_and_australian_languages"] >= 10
    assert counts["creole_and_contact_languages"] >= 5
    assert counts["constructed_languages"] >= 5
    assert counts["distinct_families_count"] >= 20


def test_old_world_languages_partition(engine: UniversalLanguageEngine):
    old_world = engine.list_old_world_languages()
    assert len(old_world) > 0
    for l in old_world:
        assert l.is_old_world is True
        assert l.classification == LanguageClassification.OLD_WORLD


def test_all_world_languages_partition(engine: UniversalLanguageEngine):
    all_langs = engine.list_all_world_languages()
    old_langs = engine.list_old_world_languages()
    new_langs = engine.list_new_world_languages()
    pacific = engine.list_pacific_and_australian_languages()
    creoles = engine.list_creole_and_contact_languages()
    conlangs = engine.list_constructed_languages()

    assert len(all_langs) == len(old_langs) + len(new_langs) + len(pacific) + len(creoles) + len(conlangs)


def test_lookup_by_iso_and_name(engine: UniversalLanguageEngine):
    # Lookup by 2-letter ISO
    en = engine.get_language("en")
    assert en is not None
    assert en.name == "English"
    assert en.iso_639_3 == "eng"

    # Lookup by 3-letter ISO
    cmn = engine.get_language("cmn")
    assert cmn is not None
    assert "Mandarin" in cmn.name

    # Lookup by Native Name
    jp = engine.get_language("日本語")
    assert jp is not None
    assert jp.name == "Japanese"

    # Lookup by English Name
    sw = engine.get_language("Swahili")
    assert sw is not None
    assert sw.family == "Niger-Congo"


def test_language_details_format(engine: UniversalLanguageEngine):
    details = engine.get_language_details("de")
    assert details["name"] == "German"
    assert "iso_codes" in details
    assert details["iso_codes"]["iso_639_1"] == "de"
    assert details["iso_codes"]["iso_639_3"] == "deu"
    assert "genealogy" in details
    assert details["genealogy"]["family"] == "Indo-European"
    assert "geography" in details
    assert details["geography"]["is_old_world"] is True


def test_error_handling_invalid_queries(engine: UniversalLanguageEngine):
    # Non-existent language
    with pytest.raises(LanguageNotFoundError):
        engine.get_language_or_raise("NonExistentLanguageXYZ123")

    # Negative speaker count
    with pytest.raises(InvalidQueryError):
        engine.search_by_speakers(min_speakers=-10)

    # Inverted speaker range
    with pytest.raises(InvalidQueryError):
        engine.search_by_speakers(min_speakers=5000, max_speakers=100)


def test_search_and_filter_attributes(engine: UniversalLanguageEngine):
    # Search by family
    slavic = engine.search_by_family("Slavic")
    assert len(slavic) >= 5
    for l in slavic:
        assert "Slavic" in l.branch or "Slavic" in l.subfamily or "Slavic" in l.family

    # Search by region
    middle_east = engine.search_by_region("Middle East")
    assert len(middle_east) >= 5

    # Filter by script and direction
    rtl_langs = engine.filter_languages(predicate=lambda l: l.script_direction == ScriptDirection.RTL)
    assert len(rtl_langs) >= 10
    for l in rtl_langs:
        assert l.script_direction == ScriptDirection.RTL


def test_module_level_convenience_functions():
    counts = count_languages()
    assert counts["total_languages"] > 100

    lang = get_language("la")
    assert lang is not None
    assert lang.name == "Latin"

    details = get_language_details("Latin")
    assert details["name"] == "Latin"

    old_world = list_old_world_languages()
    assert len(old_world) > 50

    all_world = list_all_world_languages()
    assert len(all_world) >= len(old_world)

    res = search_languages("Greek")
    assert len(res) >= 1
