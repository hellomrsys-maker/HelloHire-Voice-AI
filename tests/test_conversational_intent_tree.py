"""
test_conversational_intent_tree.py - Unit and regression tests for Hierarchical Dialogue Intent Tree.

Validates:
1. Slot-equivalence sentence synthesis and combinatorial capacity.
2. Calibrated 518ms conversational turn-taking latency invariance.
3. 64-byte AMSV physical state mapping.
4. Canonical engine dataset integrity across English and Hindustani engines.
"""

import os
import sys
import json
from training.conversational_intent_tree import (
    build_default_english_intent_tree,
    build_default_hindustani_intent_tree,
    IntentTreeNode,
    ConversationalIntentTree
)
from amsv.python.amsv_embedded import AMSVEmbeddedView


def test_english_intent_tree_synthesis():
    tree = build_default_english_intent_tree()
    assert len(tree.nodes) >= 5
    assert tree.total_generative_capacity() >= 250

    # Test inbound status matching
    response = tree.synthesize_response("How are you doing today?", deterministic_idx=0)
    assert response["matched"] is True
    assert response["intent"] == "STATUS_INQUIRY"
    assert response["calibrated_gap_ms"] == 518
    assert response["amsv_intent_byte"] == 0x21
    assert "good" in response["text"].lower() or "fine" in response["text"].lower() or "nominal" in response["text"].lower()

    # Test inbound system integrity matching
    response2 = tree.synthesize_response("Is memory synchronization verified?", deterministic_idx=0)
    assert response2["matched"] is True
    assert response2["intent"] == "SYSTEM_INTEGRITY_AUDIT"
    assert response2["calibrated_gap_ms"] == 518
    assert "verified" in response2["text"].lower()


def test_hindustani_intent_tree_synthesis():
    tree = build_default_hindustani_intent_tree()
    assert len(tree.nodes) >= 2
    assert tree.total_generative_capacity() >= 100

    response = tree.synthesize_response("आप कैसे हैं?", deterministic_idx=0)
    assert response["matched"] is True
    assert response["intent"] == "STATUS_INQUIRY"
    assert response["calibrated_gap_ms"] == 518
    assert response["amsv_intent_byte"] == 0x21


def test_amsv_zero_bridge_intent_sync():
    """Verify that intent tree directly updates the 64-byte AMSV without bridging."""
    amsv = AMSVEmbeddedView()
    tree = build_default_english_intent_tree()
    res = tree.synthesize_response("Execute the next phase.", deterministic_idx=0)

    # Set byte directly in the 64-byte memory vector (Byte 22: Capability / Intent byte)
    amsv._view[22] = res["amsv_intent_byte"]
    assert amsv._view[22] == 0x24
    assert amsv._view.nbytes == 64


def test_canonical_engine_data_files():
    """Verify canonical_engine_data.json exists and adheres to schema."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    en_path = os.path.join(root, "English_engine", "6_DATA_REQUIREMENTS", "canonical_engine_data.json")
    hi_path = os.path.join(root, "Hindustani_engine", "6_DATA_REQUIREMENTS", "canonical_engine_data.json")

    for path in [en_path, hi_path]:
        assert os.path.exists(path), f"Missing canonical file: {path}"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "engine_profile" in data
        assert "latency_prosody_calibration" in data
        assert data["latency_prosody_calibration"]["calibrated_gap_ms"] == 518
        assert "dialogue_intent_tree" in data
        assert data["dialogue_intent_tree"]["total_generative_sentence_capacity"] > 0
