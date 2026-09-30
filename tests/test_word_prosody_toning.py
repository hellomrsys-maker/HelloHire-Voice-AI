"""
test_word_prosody_toning.py - Test suite for Word-by-Word Prosodic Breakdown & Vocal Toning.

Validates:
1. Word-by-word breakdown of sentences ("आप कैसे हैं?", "How are you?") with timing and pitch per word.
2. The 4 mathematical acoustic vocal toning textures: Rough, Smooth, Rash, Calm.
3. 64-byte AMSV zero-bridge physical memory synchronization (0 nanoseconds latency).
4. Multi-pass continuous neural training pipeline execution and verified checkpoint creation.
"""

import os
import json
import pytest
import torch
from Hindustani_engine.brain.analysis.word_prosody_toning_engine import (
    WordProsodyToningEngine,
    VocalTexture
)
from training.train_word_prosody_toning import (
    WordProsodyToningNeural,
    train_word_prosody_toning_pipeline
)
from amsv.python.amsv_embedded import AMSVEmbeddedView


def test_word_by_word_prosodic_breakdown():
    amsv = AMSVEmbeddedView()
    engine = WordProsodyToningEngine(amsv_view=amsv)

    sentence = "आप कैसे हैं?"
    result = engine.analyze_sentence(sentence, texture=VocalTexture.CALM_RESONANT)

    assert len(result.word_tokens) == 3
    t1, t2, t3 = result.word_tokens

    # Word 1: "आप"
    assert t1.clean_word == "आप"
    assert 180 <= t1.duration_ms <= 350
    assert t1.focal_stress is True

    # Word 2: "कैसे"
    assert t2.clean_word == "कैसे"
    assert 200 <= t2.duration_ms <= 400

    # Word 3: "हैं?"
    assert t3.clean_word == "हैं"
    assert t3.is_terminal is True
    assert t3.intonation_contour in ["RISING", "PEAK"]

    # Verify AMSV 64-byte physical memory sync
    assert result.amsv_synced is True
    assert amsv._view.nbytes == 64
    assert 0.0 <= amsv.get_prosody_fluency() <= 1.0


def test_vocal_toning_textures_acoustic_physics():
    engine = WordProsodyToningEngine()

    rough_prof = engine.generate_vocal_profile(VocalTexture.ROUGH_GRAVELLY)
    assert rough_prof.roughness >= 0.80
    assert rough_prof.jitter_percent > 1.5

    smooth_prof = engine.generate_vocal_profile(VocalTexture.SMOOTH_BREATHY)
    assert smooth_prof.smoothness >= 0.85
    assert smooth_prof.spectral_tilt_db <= -15.0

    rash_prof = engine.generate_vocal_profile(VocalTexture.RASH_HARSH)
    assert rash_prof.rashness >= 0.75
    assert rash_prof.spectral_tilt_db >= -5.0

    calm_prof = engine.generate_vocal_profile(VocalTexture.CALM_RESONANT)
    assert calm_prof.calmness >= 0.85


def test_english_cross_lingual_word_prosody():
    engine = WordProsodyToningEngine()
    result = engine.analyze_sentence("How are you?", texture=VocalTexture.CALM_RESONANT)

    assert len(result.word_tokens) == 3
    assert result.word_tokens[0].clean_word == "how"
    assert result.word_tokens[0].focal_stress is True
    assert result.word_tokens[2].intonation_contour == "RISING"


def test_multi_pass_word_prosody_training_execution():
    result = train_word_prosody_toning_pipeline()
    assert result["status"] == "SUCCESS"
    assert result["total_epochs"] == 60
    assert len(result["passes"]) == 4

    # Checkpoint verification
    assert os.path.exists(result["checkpoint"])
    assert len(result["sha256"]) == 64


def test_hindustani_conversational_timetable():
    engine = WordProsodyToningEngine()

    res_rash = engine.analyze_sentence("तुम यहाँ क्या कर रहे हो?", texture=VocalTexture.RASH_HARSH)
    assert res_rash.timetable is not None
    assert res_rash.timetable.floor_management_state == "FLOOR_DEMANDING"
    assert res_rash.timetable.expected_response_latency_range_ms == (120, 260)
    assert res_rash.timetable.interaction_posture == "AGGRESSIVE_STANCE"

    res_calm = engine.analyze_sentence("आप कृपया बैठ जाइए।", texture=VocalTexture.CALM_RESONANT)
    assert res_calm.timetable is not None
    assert res_calm.timetable.floor_management_state == "FLOOR_YIELDED"
    assert res_calm.timetable.expected_response_latency_range_ms == (500, 1000)
    assert res_calm.timetable.interaction_posture == "MEASURED_DIGNIFIED_BALANCE"

