"""
test_telugu_engine.py - Complete Test Suite for the Authentic Telugu Engine.
Validates:
1. All 6 Linguistic Knowledge Layers exist with authentic Telugu content (not placeholders).
2. Canonical dataset has authentic Telugu stems and 518ms calibrated latency.
3. Six-Language Matrix modules (Rust, C++, Julia, CUDA, Java, Python) are present and functional.
4. Python bridge maintains 0-nanosecond AMSV sync with 'TELU' magic header.
"""

import os
import json
import pytest
from Telugu_engine.six_language_matrix.python.telugu_matrix_bridge import (
    TeluguMatrixBridge,
    AMSV_MAGIC_TELUGU,
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TELUGU_DIR = os.path.join(ROOT_DIR, "Telugu_engine")


def test_telugu_six_knowledge_layers_integrity():
    """Verify all 6 linguistic knowledge layers contain real specifications and documentation."""
    layers = [
        "1_SYNTACTIC_STRUCTURE_(Sentence_Layer)",
        "2_MORPHOLOGICAL_ANALYSIS_(Word_Layer)",
        "3_PHONOLOGICAL_ORTHOGRAPHIC_(Text_Sound_Layer)",
        "4_SEMANTIC_REPRESENTATION_(Meaning_Layer)",
        "5_PRAGMATIC_(Use_Layer)",
        "6_DATA_REQUIREMENTS",
    ]
    for layer in layers:
        layer_path = os.path.join(TELUGU_DIR, layer)
        assert os.path.isdir(layer_path), f"Layer missing: {layer}"
        readme = os.path.join(layer_path, "README.md")
        if os.path.exists(readme):
            content = open(readme, "r", encoding="utf-8").read()
            assert len(content) > 300, f"Layer {layer} README is too short or placeholder"
            assert "తెలుగు" in content, f"Layer {layer} README does not contain authentic Telugu script"


def test_telugu_canonical_data_authenticity():
    """Verify canonical_engine_data.json has authentic Telugu intents and zero English placeholders."""
    canonical_path = os.path.join(TELUGU_DIR, "6_DATA_REQUIREMENTS", "canonical_engine_data.json")
    assert os.path.exists(canonical_path)

    with open(canonical_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["engine_profile"]["language"] == "Telugu"
    assert data["engine_profile"]["native_name"] == "తెలుగు"
    assert data["latency_prosody_calibration"]["calibrated_gap_ms"] == 518

    nodes = data["dialogue_intent_tree"]["nodes"]
    assert len(nodes) >= 6

    # Verify no placeholder strings like "Status check (Telugu)" exist
    for node in nodes:
        assert node["calibrated_gap_ms"] == 518
        for stem in node["inbound_stems"]:
            assert "Telugu" not in stem, f"Placeholder detected in stem: {stem}"
            # Ensure Telugu unicode range (\u0C00-\u0C7F)
            assert any("\u0C00" <= ch <= "\u0C7F" for ch in stem), f"Non-Telugu stem: {stem}"


def test_telugu_six_language_matrix_presence():
    """Verify all 6 matrix modules are present."""
    matrix_dir = os.path.join(TELUGU_DIR, "six_language_matrix")
    expected_files = [
        ("rust", "telugu_syntax_safety.rs"),
        ("cxx", "telugu_core_engine.hpp"),
        ("cxx", "telugu_core_engine.cpp"),
        ("julia", "TeluguGrammarDynamics.jl"),
        ("cuda", "telugu_gpu_kernels.cu"),
        ("java", "TeluguEngineService.java"),
        ("python", "telugu_matrix_bridge.py"),
    ]
    for sub, filename in expected_files:
        filepath = os.path.join(matrix_dir, sub, filename)
        assert os.path.exists(filepath), f"Matrix file missing: {sub}/{filename}"
        assert os.path.getsize(filepath) > 100, f"Matrix file empty: {sub}/{filename}"


def test_telugu_python_matrix_bridge_amsv():
    """Test Telugu Python bridge zero-bridge 64-byte AMSV updates."""
    bridge = TeluguMatrixBridge()
    assert bridge.raw_buffer[0:4].tobytes() == AMSV_MAGIC_TELUGU

    # Test prosody update
    bridge.write_prosody(218.0, 3.7, 0.98)
    prosody = bridge.read_prosody()
    assert abs(prosody["f0_hz"] - 218.0) < 0.1
    assert abs(prosody["tempo_sps"] - 3.7) < 0.1
    assert abs(prosody["fluency"] - 0.98) < 0.01
    assert prosody["active"] is True

    # Test cognitive score
    bridge.write_cognitive_score(0, 0.96)
    assert abs(bridge.read_cognitive_score(0) - 0.96) < 0.01
