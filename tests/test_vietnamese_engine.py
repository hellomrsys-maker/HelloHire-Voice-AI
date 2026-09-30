"""
Dedicated Automated Test Suite for Vietnamese Language Engine (Vietnamese_engine/)
Verifies the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
Six-Language Matrix, and The Zero-Bridge Synchronous Memory Rule (0x56494554 'VIET').
"""

import os
import struct
import pytest
from Vietnamese_engine import (
    VietnameseEngineOrchestrator,
    VietnameseMatrixBridge,
    VIETNAMESE_MAGIC_BYTES,
    VIETNAMESE_MAGIC_INT,
    AMSV_TOTAL_SIZE
)
from Vietnamese_engine.brain.skills.tokenization import VietnameseTokenizer
from Vietnamese_engine.brain.skills.pos_tagging import VietnamesePOSTagger
from Vietnamese_engine.brain.skills.tone_engine import VietnameseToneEngine
from Vietnamese_engine.brain.skills.classifier_engine import VietnameseClassifierEngine
from Vietnamese_engine.brain.skills.tam_engine import VietnameseTAMEngine
from Vietnamese_engine.brain.skills.kinship_engine import VietnameseKinshipEngine
from Vietnamese_engine.brain.skills.reduplication_engine import VietnameseReduplicationEngine
from Vietnamese_engine.brain.skills.pragmatics_engine import VietnamesePragmaticsEngine
from Vietnamese_engine.brain.sub_ais.syntax_sub_ai import VietnameseSyntaxSubAI
from Vietnamese_engine.brain.sub_ais.phonology_sub_ai import VietnamesePhonologySubAI
from Vietnamese_engine.brain.sub_ais.pragmatic_sub_ai import VietnamesePragmaticSubAI
from Vietnamese_engine.brain.sub_ais.editorial_sub_ai import VietnameseEditorialSubAI

# 1. AMSV Physical Layout & Magic
def test_amsv_physical_layout_and_magic():
    bridge = VietnameseMatrixBridge()
    assert len(bridge.buffer) == AMSV_TOTAL_SIZE == 64
    assert bridge.verify_magic() is True
    assert bytes(bridge.buffer[0:4]) == VIETNAMESE_MAGIC_BYTES == b"VIET"
    assert bridge.get_magic_uint32() == VIETNAMESE_MAGIC_INT == 0x56494554
    assert bridge.buffer[4] == 0x01  # Major version
    assert bridge.buffer[5] == 0x00  # Minor version
    assert bridge.buffer[7] == 0x01  # Northern / Hanoi

# 2. Zero-Bridge Memory Synchronization
def test_zero_bridge_memory_synchronization():
    shared_buf = bytearray(64)
    bridge = VietnameseMatrixBridge(shared_buf)
    orchestrator = VietnameseEngineOrchestrator(shared_buf)
    
    res = orchestrator.process_text("Tôi đang đọc một cuốn sách hay.")
    
    assert bytes(shared_buf[0:4]) == b"VIET"
    assert shared_buf[52] == 0x01  # Syntax active
    assert shared_buf[53] == 0x01  # Phonology active
    assert shared_buf[54] == 0x01  # Pragmatic active
    assert shared_buf[55] == 0x01  # Editorial active
    
    score = struct.unpack("<f", shared_buf[24:28])[0]
    assert 0.0 <= score <= 1.0

# 3. Tokenization and Compounds
def test_tokenization_and_compounds():
    tokenizer = VietnameseTokenizer()
    text = "Học sinh thành phố đi học bằng xe đạp ."
    words = tokenizer.tokenize_words(text)
    
    assert "Học sinh" in words
    assert "thành phố" in words
    assert "xe đạp" in words
    
    spans = tokenizer.tokenize_with_spans(text)
    compounds = [s for s in spans if s["is_compound"]]
    assert len(compounds) >= 3

# 4. POS Tagging
def test_pos_tagging():
    tagger = VietnamesePOSTagger()
    sentence = "Tôi đang đọc một cuốn sách hay ."
    tagged = tagger.tag_sentence(sentence)
    tags = {tok: pos for tok, pos in tagged}
    
    assert tags.get("Tôi") == "PRON"
    assert tags.get("đang") == "PART"
    assert tags.get("đọc") == "VERB"
    assert tags.get("một") == "NUM"
    assert tags.get("cuốn") == "CLF"
    assert tags.get("sách") == "NOUN"

# 5. Tone Engine 6 Tones
def test_tone_engine_6_tones():
    engine = VietnameseToneEngine()
    
    t1 = engine.detect_syllable_tone("ba")     # Ngang (none)
    t2 = engine.detect_syllable_tone("bà")     # Huyền (grave)
    t3 = engine.detect_syllable_tone("bá")     # Sắc (acute)
    t4 = engine.detect_syllable_tone("bả")     # Hỏi (hook)
    t5 = engine.detect_syllable_tone("bã")     # Ngã (tilde)
    t6 = engine.detect_syllable_tone("bạ")     # Nặng (dot below)
    
    assert t1["tone_id"] == 1
    assert t2["tone_id"] == 2
    assert t3["tone_id"] == 3
    assert t4["tone_id"] == 4
    assert t5["tone_id"] == 5
    assert t6["tone_id"] == 6
    
    dist = engine.analyze_text_tones("Tôi đi học bài hôm nay")
    assert dist["total_syllables"] == 6

# 6. Classifier Engine and Concord
def test_classifier_engine_and_concord():
    clf = VietnameseClassifierEngine()
    
    assert clf.get_preferred_classifier("chó") == "con"
    assert clf.get_preferred_classifier("bàn") == "cái"
    assert clf.get_preferred_classifier("sách") in {"cuốn", "quyển"}
    
    assert clf.validate_classifier_noun_pair("con", "mèo") is True
    assert clf.validate_classifier_noun_pair("bức", "thư") is True
    
    np = clf.construct_quantified_np("ba", "cá")
    assert np == "ba con cá"

# 7. TAM Preverbal Markers
def test_tam_preverbal_markers():
    tam = VietnameseTAMEngine()
    
    res = tam.analyze_verbal_cluster(["đang"])
    assert res["aspect"] == "progressive"
    assert res["is_negative"] is False
    
    res_neg = tam.analyze_verbal_cluster(["sẽ", "không"])
    assert res_neg["tense"] == "future"
    assert res_neg["is_negative"] is True
    
    pred = tam.construct_tam_predicate("đi", tense="past", aspect="progressive")
    assert "đã" in pred
    assert "đang" in pred
    assert "đi" in pred

# 8. Kinship Deixis Symmetry
def test_kinship_deixis_symmetry():
    kin = VietnameseKinshipEngine()
    
    # Valid symmetrical pairs
    assert kin.is_valid_reciprocal_pair("em", "anh") is True
    assert kin.is_valid_reciprocal_pair("cháu", "ông") is True
    assert kin.is_valid_reciprocal_pair("con", "mẹ") is True
    
    # Invalid asymmetrical pairs
    assert kin.is_valid_reciprocal_pair("anh", "ông") is False
    
    audit = kin.audit_kinship_consistency("cháu", "bà")
    assert audit["is_reciprocal_valid"] is True

# 9. Reduplication Từ Láy
def test_reduplication_tu_lay():
    lay = VietnameseReduplicationEngine()
    
    res1 = lay.classify_reduplication("xanh xanh")
    assert res1["is_reduplication"] is True
    assert res1["type"] == "lay_toan_bo"
    
    res2 = lay.classify_reduplication("đẹp đẽ")
    assert res2["is_reduplication"] is True
    assert res2["type"] == "lay_am_dau"
    
    res3 = lay.classify_reduplication("lác đác")
    assert res3["is_reduplication"] is True
    assert res3["type"] == "lay_van"

# 10. Sub-AIs Direct AMSV Execution
def test_sub_ais_direct_amsv_execution():
    buf = bytearray(64)
    bridge = VietnameseMatrixBridge(buf)
    
    syn_ai = VietnameseSyntaxSubAI(buf)
    phon_ai = VietnamesePhonologySubAI(buf)
    prag_ai = VietnamesePragmaticSubAI(buf)
    edit_ai = VietnameseEditorialSubAI(buf)
    
    text = "Em chào thầy ạ, em đã đọc cuốn sách này rồi ạ."
    
    syn_ai.process(text, buf)
    assert buf[52] == 0x01 # Syntax active
    assert buf[18] > 0
    
    phon_ai.process(text, buf)
    assert buf[53] == 0x01 # Phonology active
    assert buf[20] > 0
    
    prag_ai.process(text, buf)
    assert buf[54] == 0x01 # Pragmatic active
    assert buf[23] > 0     # Politeness particle flag
    
    edit_ai.process(text, buf)
    assert buf[55] == 0x01 # Editorial active
    assert buf[19] == 0x01 # Classifier concord
    
    # Verify zero-bleed in untouched bytes (bytes 28..31 reserved hardware)
    assert buf[28] == 0x00
    assert buf[29] == 0x00

# 11. Orchestrator End-to-End and Pipeline
def test_orchestrator_end_to_end_and_pipeline():
    orch = VietnameseEngineOrchestrator()
    res = orch.process_text("Giáo viên đang giảng bài cho học sinh.")
    
    assert res["text"].startswith("Giáo viên")
    assert res["syntax"]["has_verb"] is True
    assert res["amsv_state"]["magic"] == "VIET"
    assert res["amsv_state"]["sub_ais_active"]["syntax"] is True
    assert res["amsv_state"]["sub_ais_active"]["editorial"] is True
    
    # Sentence synthesis
    svo_sent = orch.synthesize_svo_sentence(
        subject="Tôi",
        verb="đọc",
        direct_object_noun="sách",
        quantifier="hai",
        classifier="cuốn",
        aspect="progressive"
    )
    assert svo_sent == "Tôi đang đọc hai cuốn sách"

# 12. Task Pipelines and Dialect Adaptation
def test_task_pipelines_and_dialect_adaptation():
    orch = VietnameseEngineOrchestrator()
    
    # 1. Grammar check
    valid_text = "Tôi ăn một quả táo ."
    check = orch.check_grammar(valid_text)
    assert check["is_valid"] is True
    assert check["confidence_score"] >= 0.85
    
    # 2. Southern to Northern dialect adaptation
    southern_text = "Tôi uống một ly nước và ăn một trái chuối."
    adapted = orch.compose_prose(southern_text, adapt_dialect=True)
    assert "cốc" in adapted
    assert "quả" in adapted
    
    # 3. Proverb injection
    proverb_text = orch.compose_prose("Kiên trì sẽ mang lại thành công.", theme="perseverance", adapt_dialect=False)
    assert "Nước chảy đá mòn" in proverb_text

# 13. Six-Language Matrix Nodes
def test_six_language_matrix_nodes():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    matrix_dir = os.path.join(base_dir, "Vietnamese_engine", "six_language_matrix")
    
    expected_files = [
        "vietnamese_syntax_safety.rs",
        "vietnamese_core_engine.hpp",
        "vietnamese_core_engine.cpp",
        "vietnamese_gpu_kernels.cu",
        "VietnameseEngineService.java",
        "VietnameseGrammarDynamics.jl",
        "vietnamese_matrix_bridge.py",
        "__init__.py"
    ]
    
    for filename in expected_files:
        path = os.path.join(matrix_dir, filename)
        assert os.path.exists(path), f"Missing matrix node: {filename}"
        assert os.path.getsize(path) > 50, f"Matrix node too small: {filename}"
