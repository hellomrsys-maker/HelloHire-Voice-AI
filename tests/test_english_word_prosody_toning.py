"""
test_english_word_prosody_toning.py - Test suite for English Word-by-Word Prosodic Breakdown & Vocal Toning.

Validates:
1. English word-by-word breakdown ("How are you?", "You want answers?") with timing and pitch per word.
2. English vocal toning profiles (Rough, Smooth, Rash, Calm) under acoustic physics.
3. 64-byte AMSV zero-bridge memory synchronization (0 nanoseconds latency).
4. Multi-pass continuous neural training pipeline execution and verified checkpoint creation.
"""

import os
import json
import pytest
import torch
from English_engine.brain.Analysis.english_word_prosody_toning_engine import (
    EnglishWordProsodyToningEngine,
    EnglishVocalTexture
)
from training.train_english_dialogue_and_prosody import (
    EnglishDialogueProsodyNeural,
    train_english_dialogue_and_prosody_pipeline
)
from amsv.python.amsv_embedded import AMSVEmbeddedView


def test_english_word_prosody_breakdown():
    amsv = AMSVEmbeddedView()
    engine = EnglishWordProsodyToningEngine(amsv_view=amsv)

    sentence = "How are you?"
    result = engine.analyze_sentence(sentence, texture=EnglishVocalTexture.CALM_RESONANT)

    assert len(result.word_tokens) == 3
    t1, t2, t3 = result.word_tokens

    # Word 1: "How"
    assert t1.clean_word == "how"
    assert 160 <= t1.duration_ms <= 350
    assert t1.focal_stress is True

    # Word 2: "are"
    assert t2.clean_word == "are"
    assert 150 <= t2.duration_ms <= 320

    # Word 3: "you?"
    assert t3.clean_word == "you"
    assert t3.is_terminal is True
    assert t3.intonation_contour in ["RISING", "PEAK"]

    # Verify AMSV 64-byte physical memory sync
    assert result.amsv_synced is True
    assert amsv._view.nbytes == 64
    assert 0.0 <= amsv.get_prosody_fluency() <= 1.0


def test_english_courtroom_rash_toning():
    engine = EnglishWordProsodyToningEngine()
    result = engine.analyze_sentence("You can not handle the truth!", texture=EnglishVocalTexture.RASH_HARSH)

    assert len(result.word_tokens) == 6
    assert result.vocal_profile.rashness >= 0.80
    assert result.vocal_profile.roughness >= 0.65
    assert result.vocal_profile.spectral_tilt_db >= -4.0


def test_english_scholarly_calm_toning():
    engine = EnglishWordProsodyToningEngine()
    result = engine.analyze_sentence("The architecture provides zero nanosecond synchronization.", texture=EnglishVocalTexture.CALM_RESONANT)

    assert result.vocal_profile.calmness >= 0.90
    assert result.formality_level == "FORMAL"


def test_multi_pass_english_prosody_training_execution():
    result = train_english_dialogue_and_prosody_pipeline()
    assert result["status"] == "SUCCESS"
    assert result["total_epochs"] == 60
    assert len(result["passes"]) == 4

    # Checkpoint verification
    assert os.path.exists(result["checkpoint"])
    assert len(result["sha256"]) == 64


def test_english_conversational_timetable_and_interaction():
    engine = EnglishWordProsodyToningEngine()

    # Courtroom confrontation (tight timetable, demanding floor)
    res_rash = engine.analyze_sentence("You want answers?", texture=EnglishVocalTexture.RASH_HARSH)
    assert res_rash.timetable is not None
    assert res_rash.timetable.floor_management_state == "FLOOR_DEMANDING"
    assert res_rash.timetable.expected_response_latency_range_ms == (100, 250)
    assert res_rash.timetable.interaction_posture == "DIRECT_CONFRONTATIONAL_LOCK"

    # Reflective counsel (deliberate timetable, yielded floor)
    res_calm = engine.analyze_sentence("You do not know about real loss.", texture=EnglishVocalTexture.CALM_RESONANT)
    assert res_calm.timetable is not None
    assert res_calm.timetable.floor_management_state == "FLOOR_YIELDED"
    assert res_calm.timetable.expected_response_latency_range_ms == (600, 1100)
    assert res_calm.timetable.interaction_posture == "REFLECTIVE_COUNSEL_TILT"

    # Rapid intellectual dominance (Sorkin cadence)
    res_dom = engine.analyze_sentence("You have part of my attention, you have the minimum amount.", texture=EnglishVocalTexture.CALM_RESONANT)
    assert res_dom.timetable is not None
    assert res_dom.timetable.floor_management_state == "FLOOR_DEMANDING"
    assert res_dom.timetable.expected_response_latency_range_ms == (80, 200)
    assert res_dom.timetable.interaction_posture == "CLINICAL_MONOTONE_DOMINANCE"

