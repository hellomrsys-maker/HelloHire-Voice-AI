"""
test_unified_language_training.py - Test Suite for Single Total Training Files.

Verifies:
1. EnglishUnifiedTrainer execution across curriculum, sub-AIs, intent trees, vocal cord prosody, and AMSV 0-ns sync.
2. HindustaniUnifiedTrainer execution across SOV curriculum, social deixis sub-AIs, intent tree, and AMSV 0-ns sync.
3. UniversalLanguageTrainer multi-engine single-file execution from canonical_engine_data.json.
"""

import os
import sys
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from amsv.python.amsv_embedded import AMSVEmbeddedView
from training.train_english_unified import EnglishUnifiedTrainer
from training.train_hindustani_unified import HindustaniUnifiedTrainer
from training.train_language_engine import UniversalLanguageTrainer


def test_english_unified_trainer_phases():
    amsv = AMSVEmbeddedView()
    trainer = EnglishUnifiedTrainer(amsv_view=amsv)

    # 1. Verify canonical dataset ingestion
    assert trainer.canonical_data is not None
    assert "curriculum_sentences" in trainer.canonical_data

    # 2. Phase 3: Intent tree & Latency
    p3 = trainer.train_phase3_intent_tree_and_latency()
    assert p3["status"] == "SUCCESS"
    assert p3["total_capacity"] >= 200

    # 3. Phase 4: Vocal Cord Bio-Acoustics
    p4 = trainer.train_phase4_vocal_cord_prosody(epochs=1)
    assert p4["status"] == "SUCCESS"
    assert os.path.exists(p4["checkpoint"])

    # 4. Phase 5: AMSV Sync & Verification
    p5 = trainer.train_phase5_amsv_sync_and_verification()
    assert p5["status"] == "SUCCESS"
    assert len(p5["verified_checkpoints"]) >= 2
    assert bytes(amsv._view[:4]) != b"\x00\x00\x00\x00"


def test_hindustani_unified_trainer_phases():
    amsv = AMSVEmbeddedView()
    trainer = HindustaniUnifiedTrainer(amsv_view=amsv)

    # 1. Verify canonical dataset ingestion
    assert trainer.canonical_data is not None
    assert "curriculum_sentences" in trainer.canonical_data

    # 2. Phase 3: Intent tree & Latency
    p3 = trainer.train_phase3_intent_tree_and_latency()
    assert p3["status"] == "SUCCESS"
    assert p3["total_capacity"] >= 100

    # 3. Phase 5: AMSV Sync & Verification
    p5 = trainer.train_phase5_amsv_sync_and_verification()
    assert p5["status"] == "SUCCESS"
    assert len(p5["verified_checkpoints"]) >= 2


def test_universal_language_trainer_spanish():
    amsv = AMSVEmbeddedView()
    trainer = UniversalLanguageTrainer(language="Spanish", amsv_view=amsv)

    # 1. Canonical data loaded
    assert trainer.canonical_data is not None

    # 2. Phase 3: Intent tree & Latency
    p3 = trainer.train_phase3_intent_tree_and_latency()
    assert p3["status"] == "SUCCESS"

    # 3. Phase 4: Vocal Cord Bio-Acoustics
    p4 = trainer.train_phase4_vocal_cord_prosody()
    assert p4["status"] == "SUCCESS"
    assert p4["scenarios_evaluated"] == 6

    # 4. Phase 5: AMSV Sync & Verification
    p5 = trainer.train_phase5_amsv_sync_and_verification()
    assert p5["status"] == "SUCCESS"
    assert "spanish_main_model_verified.pt" in p5["verified_checkpoints"]


def test_english_engine_dedicated_single_file_trainer():
    from English_engine.train import EnglishEngineMasterTrainer, GenderGenericRegister
    amsv = AMSVEmbeddedView()
    trainer = EnglishEngineMasterTrainer(amsv_view=amsv)

    # 1. Verify Gender-Generic register cohorts
    assert GenderGenericRegister.LOW_REGISTER.value == "low_register_cohort"
    assert GenderGenericRegister.MEDIUM_REGISTER.value == "medium_register_cohort"
    assert GenderGenericRegister.HIGH_REGISTER.value == "high_register_cohort"

    # 2. Verify Intent Tree execution
    p3 = trainer.train_phase3_intent_tree_and_latency()
    assert p3["status"] == "SUCCESS"
    assert p3["total_capacity"] >= 200

    # 3. Verify Vocal Cord Frequency modulation on 6 scenarios
    p4 = trainer.train_phase4_vocal_cord_prosody(epochs=1)
    assert p4["status"] == "SUCCESS"

    # 4. Verify 0-ns AMSV memory sync & ENGL magic header
    p5 = trainer.train_phase5_amsv_sync_and_verification()
    assert p5["status"] == "SUCCESS"
    magic_readback = int.from_bytes(amsv._view[:4], "little")
    assert magic_readback == 0x454E474C  # 'ENGL'

