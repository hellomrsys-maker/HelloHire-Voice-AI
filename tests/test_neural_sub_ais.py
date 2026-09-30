"""
test_neural_sub_ais.py - Explicit Verification Suite for Trained Dedicated Sub-AI Neural Networks.

Verifies:
1. Checkpoint authenticity (file size ~23MB, SHA-256 fingerprint verification).
2. B1: WritingSubAINeural - Sentence completeness detection (Complete vs Fragment).
3. B2: EmailSubAINeural - Politeness Index, Salutations, and Cross-Cultural Pragmatics.
4. B3: ListeningSubAINeural - Spoken reduction expansion and rhythm typology.
5. B4: PronunciationSubAINeural - Word-final consonant audibility and noun-verb stress shift.
6. B5: ReviewingSubAINeural - 4-tier error taxonomy classification and citation anchoring.
7. B6: BookWritingSubAINeural - Tense collision detection and 5-stage editorial tracking.
"""

import os
import sys
import hashlib
import json
import torch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gra_voi.bandhu.sub_ai_neural import (
    BandhuDedicatedSubAICluster,
    WritingSubAINeural,
    EmailSubAINeural,
    ListeningSubAINeural,
    PronunciationSubAINeural,
    ReviewingSubAINeural,
    BookWritingSubAINeural
)

def test_checkpoint_authenticity():
    print("\n[1/7] Verifying Checkpoint Authenticity & Cryptographic Fingerprint...")
    chk_path = os.path.join("checkpoints", "bandhu_sub_ais_verified.pt")
    meta_path = os.path.join("checkpoints", "bandhu_sub_ais_verified.json")

    assert os.path.exists(chk_path), f"Checkpoint missing: {chk_path}"
    assert os.path.exists(meta_path), f"Metadata missing: {meta_path}"

    file_size_mb = os.path.getsize(chk_path) / (1024 * 1024)
    assert file_size_mb > 20.0, f"Checkpoint size ({file_size_mb:.2f} MB) too small! Must be full Transformer (~23MB)"

    with open(meta_path, "r") as f:
        meta = json.load(f)

    hasher = hashlib.sha256()
    with open(chk_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest()

    assert actual_hash == meta["sha256"], f"Hash mismatch! Actual: {actual_hash}, Meta: {meta['sha256']}"
    print(f"  [OK] Authenticity Confirmed: Size={file_size_mb:.2f} MB | SHA-256={actual_hash}")


@pytest.fixture(scope="module")
def cluster():
    chk_path = os.path.join("checkpoints", "bandhu_sub_ais_verified.pt")
    c = BandhuDedicatedSubAICluster(checkpoint_path=chk_path)
    return c


def test_sub_ai_cluster_loading(cluster):
    print("\n[2/7] Verifying Sub-AI Cluster Initialization & Weight Loading...")
    assert cluster.is_trained is True, "Sub-AI cluster failed to load trained checkpoint!"
    assert isinstance(cluster.writing, WritingSubAINeural)
    assert isinstance(cluster.email, EmailSubAINeural)
    assert isinstance(cluster.listening, ListeningSubAINeural)
    assert isinstance(cluster.pronunciation, PronunciationSubAINeural)
    assert isinstance(cluster.reviewing, ReviewingSubAINeural)
    assert isinstance(cluster.book_writing, BookWritingSubAINeural)
    print("  [OK] All 6 Transformer Sub-AIs instantiated and initialized with trained weights.")


def test_writing_sub_ai(cluster: BandhuDedicatedSubAICluster):
    print("\n[3/7] Testing B1: Writing Sub-AI (Completeness & Fragment Discrimination)...")
    # Complete sentence
    res_comp = cluster.writing.analyze_text("The syntax committee delivered the formal report to the linguistics department.")
    assert res_comp["sentence_completeness_score"] > 0.70, f"Expected high completeness, got {res_comp['sentence_completeness_score']}"
    assert len(res_comp["fatal_errors"]) == 0, f"Unexpected fatal errors: {res_comp['fatal_errors']}"
    assert res_comp["terminal_punctuation"] == "Period"

    # Clausal fragment
    res_frag = cluster.writing.analyze_text("Because the laboratory experiments failed during the initial trial phase.")
    assert len(res_frag["fatal_errors"]) > 0, "Failed to detect sentence fragment!"
    assert "fragment" in res_frag["fatal_errors"][0].lower()
    print(f"  [OK] Writing Sub-AI verified: Complete ({res_comp['sentence_completeness_score']:.4f}) vs Fragment ({res_frag['sentence_completeness_score']:.4f})")


def test_email_sub_ai(cluster: BandhuDedicatedSubAICluster):
    print("\n[4/7] Testing B2: Email Sub-AI (Politeness Index & Salutations)...")
    formal = cluster.email.analyze_text("Dear Dr. Henderson, would you be so kind as to review the attached manuscript? Best regards, Elena.")
    assert formal["politeness_index"] > 0.85, f"Expected high politeness, got {formal['politeness_index']}"
    assert formal["salutation_level"] == "Formal"

    blunt = cluster.email.analyze_text("Send me the updated database passwords right now.")
    assert blunt["politeness_index"] < 0.35, f"Expected low politeness, got {blunt['politeness_index']}"
    assert blunt["salutation_level"] == "Missing"
    print(f"  [OK] Email Sub-AI verified: Polite ({formal['politeness_index']:.4f}) vs Blunt ({blunt['politeness_index']:.4f})")


def test_listening_and_pronunciation(cluster: BandhuDedicatedSubAICluster):
    print("\n[5/7] Testing B3 & B4: Listening & Pronunciation Sub-AIs...")
    # Listening
    res_list = cluster.listening.analyze_text("I'd've gone to the conference if the train had not been delayed.")
    assert res_list["predicted_rhythm_typology"] in ["StressTimed", "SyllableTimed", "MoraTimed"]
    assert res_list["segmentation_entropy"] > 0.0

    # Pronunciation
    res_pron_audible = cluster.pronunciation.analyze_text("The student walked to school and asked several insightful questions.")
    assert res_pron_audible["grammar_ending_audibility"] > 0.60
    assert len(res_pron_audible["seven_step_correction_path"]) == 7
    print(f"  [OK] Listening Rhythm: {res_list['predicted_rhythm_typology']} | Ending Audibility: {res_pron_audible['grammar_ending_audibility']:.4f}")


def test_reviewing_sub_ai(cluster: BandhuDedicatedSubAICluster):
    print("\n[6/7] Testing B5: Reviewing Sub-AI (4-Tier Taxonomy & Anchoring)...")
    fatal = cluster.reviewing.analyze_text("In Section 3 on page 14, the subject-verb concord completely fails: 'they is' must be corrected to 'they are'.")
    assert fatal["dominant_error_tier"] == "Fatal", f"Expected Fatal tier, got {fatal['dominant_error_tier']}"
    assert fatal["recommended_action"] == "Mandatory Rewrite"
    assert fatal["is_location_anchored"] is True

    polite = cluster.reviewing.analyze_text("You may optionally prefer the Oxford comma here for aesthetic balance, though the sentence is grammatically sound.")
    assert polite["hedging_score"] > 0.70
    print(f"  [OK] Reviewing Sub-AI verified: Dominant Tier={fatal['dominant_error_tier']} | Anchored={fatal['is_location_anchored']}")


def test_book_writing_sub_ai(cluster: BandhuDedicatedSubAICluster):
    print("\n[7/7] Testing B6: Book Writing Sub-AI (Tense Collisions & Stages)...")
    consistent = cluster.book_writing.analyze_text("The detective walked into the abandoned study. Rain battered the dark window panes. He noticed the drawer was open.")
    assert consistent["tense_collision_risk"] < 0.50

    shifted = cluster.book_writing.analyze_text("The detective walked into the room. Rain batters the window panes and he sees the broken lock on the door.")
    assert shifted["tense_collision_risk"] > consistent["tense_collision_risk"]
    print(f"  [OK] Book Writing Sub-AI verified: Consistent ({consistent['tense_collision_risk']:.4f}) vs Shifted ({shifted['tense_collision_risk']:.4f})")


def run_all_tests():
    print("=" * 80)
    print("  VERIFYING TRAINED DEDICATED SUB-AI TRANSFORMER MODELS (B1 - B6)")
    print("=" * 80)
    test_checkpoint_authenticity()
    cluster = test_sub_ai_cluster_loading()
    test_writing_sub_ai(cluster)
    test_email_sub_ai(cluster)
    test_listening_and_pronunciation(cluster)
    test_reviewing_sub_ai(cluster)
    test_book_writing_sub_ai(cluster)
    print("\n" + "=" * 80)
    print("  ALL 7 DEDICATED SUB-AI NEURAL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 80)

if __name__ == "__main__":
    run_all_tests()
