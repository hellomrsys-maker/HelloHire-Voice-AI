"""
test_english_training_and_sub_ais.py - Validation Suite for English Engine Models & AMSV Sync Offset Isolation.

Verifies:
1. Grammar extraction corpus integrity from Oxford & DK grammar library.
2. Neural inference and checkpoint loading across all 4 dedicated English Engine Sub-AIs.
3. Exact physical memory sync offset isolation in the 64-byte Atomic Memory State Vector (AMSV).
4. Main Multi-Task Agent prediction across all 13 domain heads.
5. End-to-end master orchestrator execution with trained neural sub-AIs.
"""

import os
import sys
import json
import pytest
import torch

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from amsv.python.amsv_embedded import AMSVEmbeddedView
from English_engine.brain.sub_ais.syntax_sub_ai import EnglishSyntaxSubAI
from English_engine.brain.sub_ais.phonology_sub_ai import EnglishPhonologySubAI
from English_engine.brain.sub_ais.pragmatic_sub_ai import EnglishPragmaticSubAI
from English_engine.brain.sub_ais.editorial_sub_ai import EnglishEditorialSubAI
from English_engine.english_engine_orchestrator import EnglishEngineOrchestrator
from training.multi_task_trainer import MultiTaskModel


CORPUS_PATH = os.path.join(WORKSPACE_ROOT, "English_engine", "6_DATA_REQUIREMENTS", "extracted_grammar_corpus.json")
MAIN_CKPT = os.path.join(WORKSPACE_ROOT, "checkpoints", "english_main_model_verified.pt")
SUB_CKPT = os.path.join(WORKSPACE_ROOT, "checkpoints", "english_engine_sub_ais_verified.pt")


def test_grammar_extraction_dataset_integrity():
    """Verify that Oxford & DK grammar library was extracted into structured training corpora."""
    assert os.path.exists(CORPUS_PATH), f"Extracted corpus file missing at {CORPUS_PATH}"
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "metadata" in data
    assert data["metadata"]["total_extracted_sentences"] > 1000
    assert len(data["writing_corpus"]) > 1000
    assert len(data["email_corpus"]) >= 15
    assert len(data["listening_corpus"]) >= 10
    assert len(data["pronunciation_corpus"]) >= 10
    assert len(data["reviewing_corpus"]) >= 10
    assert len(data["book_writing_corpus"]) >= 10


def test_sub_ai_neural_inference_and_weights():
    """Verify each Sub-AI loads the trained checkpoint and executes neural inference."""
    assert os.path.exists(SUB_CKPT), f"Trained checkpoint missing at {SUB_CKPT}"

    # 1. Syntax Sub-AI
    syn_ai = EnglishSyntaxSubAI(checkpoint_path=SUB_CKPT)
    assert syn_ai.is_neural_loaded is True
    syn_res = syn_ai.evaluate("The committee submitted the comprehensive report yesterday.")
    assert syn_res.syntactic_integrity_score > 0.0
    assert syn_res.neural_completeness_score > 0.5
    assert syn_res.amsv_synced is True

    # 2. Phonology Sub-AI
    phon_ai = EnglishPhonologySubAI(checkpoint_path=SUB_CKPT)
    assert phon_ai.is_neural_loaded is True
    phon_res = phon_ai.evaluate("The official record was examined.")
    assert len(phon_res.phoneme_sequence) > 0
    assert phon_res.accuracy_score > 0.0
    assert phon_res.amsv_synced is True

    # 3. Pragmatic Sub-AI
    prag_ai = EnglishPragmaticSubAI(checkpoint_path=SUB_CKPT)
    assert prag_ai.is_neural_loaded is True
    prag_res = prag_ai.evaluate("Dear Dr. Henderson, would you please review our draft? Sincerely.")
    assert prag_res.pragmatic_score > 0.0
    assert prag_res.neural_politeness_index > 0.6
    assert prag_res.amsv_synced is True

    # 4. Editorial Sub-AI
    edit_ai = EnglishEditorialSubAI(checkpoint_path=SUB_CKPT)
    assert edit_ai.is_neural_loaded is True
    edit_res = edit_ai.evaluate("The detective walked into the quiet room. Rain battered the window.")
    assert edit_res.editorial_grade in {"A", "B", "C", "D"}
    assert 0.0 <= edit_res.tense_collision_risk <= 1.0
    assert edit_res.amsv_synced is True


def test_amsv_offset_isolation():
    """
    STRICT ZERO-BRIDGE OFFSET ISOLATION TEST:
    Verifies that each Sub-AI writes ONLY to its designated memory offsets,
    leaving all other bytes in the 64-byte AMSV completely untouched.
    """
    text_sample = "The research team presented their findings at the conference."

    # 1. Test Syntax Sub-AI Offset Isolation
    # Allowed to write ONLY: Offset 18..19 (Capability 1) and Offset 52..53 (Global Structural Score)
    buf1 = bytearray(64)
    amsv1 = AMSVEmbeddedView(memoryview(buf1))
    syn_ai = EnglishSyntaxSubAI(amsv_view=amsv1, checkpoint_path=SUB_CKPT)
    syn_ai.evaluate(text_sample)

    for i in range(64):
        if i in {18, 19, 52, 53}:
            pass  # Allowed designated offsets
        else:
            assert buf1[i] == 0, f"SyntaxSubAI illegally wrote to AMSV offset 0x{i:02X} (Byte {i})!"

    assert amsv1.get_cognitive_score(1) > 0.0
    assert amsv1.get_global_structural_score() > 0.0

    # 2. Test Phonology Sub-AI Offset Isolation
    # Allowed to write ONLY: Offsets 0..7 (VCE Phonemes), 8..15 (VCE Prosody), 24..25 (Capability 4)
    buf2 = bytearray(64)
    amsv2 = AMSVEmbeddedView(memoryview(buf2))
    phon_ai = EnglishPhonologySubAI(amsv_view=amsv2, checkpoint_path=SUB_CKPT)
    phon_ai.evaluate(text_sample)

    allowed_phonology = set(range(0, 16)) | {24, 25}
    for i in range(64):
        if i in allowed_phonology:
            pass
        else:
            assert buf2[i] == 0, f"PhonologySubAI illegally wrote to AMSV offset 0x{i:02X} (Byte {i})!"

    assert amsv2.get_phoneme_state() != 0
    assert amsv2.get_cognitive_score(4) > 0.0

    # 3. Test Pragmatic Sub-AI Offset Isolation
    # Allowed to write ONLY: Offset 22..23 (Capability 3) and Offset 54..55 (Global Register Score)
    buf3 = bytearray(64)
    amsv3 = AMSVEmbeddedView(memoryview(buf3))
    prag_ai = EnglishPragmaticSubAI(amsv_view=amsv3, checkpoint_path=SUB_CKPT)
    prag_ai.evaluate(text_sample)

    allowed_pragmatic = {22, 23, 54, 55}
    for i in range(64):
        if i in allowed_pragmatic:
            pass
        else:
            assert buf3[i] == 0, f"PragmaticSubAI illegally wrote to AMSV offset 0x{i:02X} (Byte {i})!"

    assert amsv3.get_cognitive_score(3) > 0.0
    assert amsv3.get_global_register_score() > 0.0

    # 4. Test Editorial Sub-AI Offset Isolation
    # Allowed to write ONLY: Offset 20..21 (Capability 2: Discourse) and Offset 26..27 (Capability 5: Reviewing)
    buf4 = bytearray(64)
    amsv4 = AMSVEmbeddedView(memoryview(buf4))
    edit_ai = EnglishEditorialSubAI(amsv_view=amsv4, checkpoint_path=SUB_CKPT)
    edit_ai.evaluate(text_sample)

    allowed_editorial = {20, 21, 26, 27}
    for i in range(64):
        if i in allowed_editorial:
            pass
        else:
            assert buf4[i] == 0, f"EditorialSubAI illegally wrote to AMSV offset 0x{i:02X} (Byte {i})!"

    assert amsv4.get_cognitive_score(2) > 0.0
    assert amsv4.get_cognitive_score(5) > 0.0


def test_main_agent_multi_task_predictions():
    """Verify the trained Main Model loads from checkpoint and predicts across 13 domain heads."""
    assert os.path.exists(MAIN_CKPT), f"Main model checkpoint missing at {MAIN_CKPT}"
    model = MultiTaskModel(d_model=128)
    state = torch.load(MAIN_CKPT, map_location="cpu")
    model.load_state_dict(state)
    model.eval()

    # Create multi-modal input [Batch=2, Time=40, Mel=80]
    x = torch.randn(2, 40, 80)
    with torch.no_grad():
        preds = model(x)

    required_heads = [
        "phoneme_logits", "prosody_preds", "cognitive_scores",
        "format_logits", "compliance_pred", "irt_params",
        "grammar_validity", "grammar_depth", "error_logits",
        "writing_cohesion", "writing_register", "speech_act_logits",
        "checklist_scores"
    ]
    for h in required_heads:
        assert h in preds, f"Missing prediction head: {h}"
        assert preds[h].shape[0] == 2


def test_end_to_end_english_orchestrator_trained():
    """Verify master orchestrator end-to-end execution with trained neural sub-AIs and AMSV."""
    amsv = AMSVEmbeddedView()
    orchestrator = EnglishEngineOrchestrator(amsv_view=amsv)

    text = "The syntax committee delivered the formal report to the linguistics department."
    output = orchestrator.process(text, request_id="req-trained-001")

    assert output.input_text == text
    assert len(output.tokens) > 5
    assert len(output.tagged_tokens) > 5
    assert output.syntax_sub_ai.amsv_synced is True
    assert output.phonology_sub_ai.amsv_synced is True
    assert output.pragmatic_sub_ai.amsv_synced is True
    assert output.editorial_sub_ai.amsv_synced is True

    # Check that cognitive scores in AMSV are populated
    cog_scores = amsv.get_all_cognitive_scores()
    # Capability 1 (Syntax), Capability 2 (Discourse), Capability 3 (Pragmatics), Capability 4 (Phonology), Capability 5 (Reviewing)
    assert cog_scores[1] > 0.0
    assert cog_scores[2] > 0.0
    assert cog_scores[3] > 0.0
    assert cog_scores[4] > 0.0
    assert cog_scores[5] > 0.0
    assert len(output.amsv_bytes_hex) == 128
    assert output.latency_ms > 0.0


def test_sequential_multi_book_checkpoints_and_curriculum():
    """Verify one-by-one sequential training artifacts across Oxford, DK, and 1891 grammar books."""
    import hashlib

    # 1. Verify Curriculum Manifest & Per-Book Datasets
    manifest_path = os.path.join(WORKSPACE_ROOT, "English_engine", "6_DATA_REQUIREMENTS", "english_full_curriculum_manifest.json")
    assert os.path.exists(manifest_path), f"Manifest missing: {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["total_sentences_extracted"] >= 7000
    assert len(manifest["books"]) == 3
    book_ids = [b["id"] for b in manifest["books"]]
    assert book_ids == ["book1_oxford", "book2_dk", "book3_1891"]

    for b in manifest["books"]:
        p = os.path.join(WORKSPACE_ROOT, "English_engine", "6_DATA_REQUIREMENTS", b["output_json"])
        assert os.path.exists(p), f"Per-book corpus missing: {p}"
        with open(p, "r", encoding="utf-8") as bf:
            bdata = json.load(bf)
            assert len(bdata["writing_corpus"]) > 0
            assert len(bdata["email_corpus"]) > 0

    # 2. Verify Sequential Intermediate Stage Checkpoints & Cryptographic Fingerprints
    stage_checkpoints = [
        ("english_stage1_oxford.pt", "english_stage1_oxford.pt.json"),
        ("english_stage2_dk.pt", "english_stage2_dk.pt.json"),
        ("english_stage3_1891.pt", "english_stage3_1891.pt.json"),
    ]

    for ckpt_file, meta_file in stage_checkpoints:
        ckpt_path = os.path.join(WORKSPACE_ROOT, "checkpoints", ckpt_file)
        meta_path = os.path.join(WORKSPACE_ROOT, "checkpoints", meta_file)
        assert os.path.exists(ckpt_path), f"Missing stage checkpoint: {ckpt_path}"
        assert os.path.exists(meta_path), f"Missing stage metadata: {meta_path}"

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        hasher = hashlib.sha256()
        with open(ckpt_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        actual_hash = hasher.hexdigest()
        assert actual_hash == meta["sha256"], f"Hash mismatch for {ckpt_file}!"
        print(f"  [PASS] Verified Stage Checkpoint: {ckpt_file} (SHA-256: {actual_hash[:16]}...)")

    # 3. Verify Master Synthesis Checkpoint
    master_ckpt = os.path.join(WORKSPACE_ROOT, "checkpoints", "english_engine_sub_ais_verified.pt")
    master_meta = master_ckpt + ".json"
    assert os.path.exists(master_ckpt)
    assert os.path.exists(master_meta)
    with open(master_meta, "r", encoding="utf-8") as f:
        mm = json.load(f)
    assert mm["status"] == "PRODUCTION_VERIFIED_ALL_BOOKS"
    assert len(mm["stages"]) == 3
    print("  [PASS] All 3 English Grammar Book stages verified with cryptographic integrity.")
