"""
Dedicated Automated Test Suite for Thai Language Engine (Thai_engine/)
Verifies the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
Six-Language Matrix, and The Zero-Bridge Synchronous Memory Rule (0x54484149 'THAI').
"""

import os
import struct
import pytest

from Thai_engine import (
    ThaiEngineOrchestrator,
    ThaiMatrixBridge,
    THAI_MAGIC_BYTES,
    THAI_MAGIC_INT,
    AMSV_TOTAL_SIZE
)
from Thai_engine.brain.skills.tokenization import tokenize_thai
from Thai_engine.brain.skills.pos_tagging import tag_pos
from Thai_engine.brain.skills.tone_engine import calculate_syllable_tone, get_consonant_class
from Thai_engine.brain.skills.classifier_engine import (
    get_classifier_for_noun,
    audit_classifier_syntax
)
from Thai_engine.brain.skills.politeness_engine import audit_politeness_particles
from Thai_engine.brain.skills.rachasap_engine import detect_register, compose_email
from Thai_engine.brain.sub_ais.syntax_sub_ai import ThaiSyntaxSubAI
from Thai_engine.brain.sub_ais.phonology_sub_ai import ThaiPhonologySubAI
from Thai_engine.brain.sub_ais.pragmatic_sub_ai import ThaiPragmaticSubAI
from Thai_engine.brain.sub_ais.editorial_sub_ai import ThaiEditorialSubAI

# 1. AMSV Physical Layout & Magic
def test_amsv_physical_layout_and_magic():
    bridge = ThaiMatrixBridge()
    assert len(bridge.buffer) == AMSV_TOTAL_SIZE == 64
    assert bridge.verify_magic() is True
    assert bytes(bridge.buffer[0:4]) == THAI_MAGIC_BYTES == b"THAI"
    assert bridge.get_magic_uint32() == THAI_MAGIC_INT == 0x54484149
    assert bridge.buffer[4] == 0x01  # Major version
    assert bridge.buffer[5] == 0x00  # Minor version
    assert bridge.buffer[6] == 0x01  # Inference mode
    assert bridge.buffer[7] == 0x01  # Central Standard Thai

# 2. Zero-Bridge Memory Synchronization
def test_zero_bridge_memory_synchronization():
    shared_buf = bytearray(64)
    bridge = ThaiMatrixBridge(shared_buf)
    orchestrator = ThaiEngineOrchestrator(shared_buf)
    
    # Process text with SVO, classifier, and polite particle
    res = orchestrator.process_text("ผมอ่านหนังสือสองเล่มครับ")
    
    # Verify exact physical memory updates
    assert bytes(shared_buf[0:4]) == b"THAI"
    assert shared_buf[18] & 0x01 != 0  # Has verb
    assert shared_buf[18] & 0x04 != 0  # SVO present
    assert shared_buf[19] == 0x01      # Classifier syntax valid
    assert shared_buf[20] & 0x01 != 0  # Valid text
    assert shared_buf[21] == 0x01      # Politeness concordant
    assert shared_buf[23] == 0x01      # Segmented
    assert shared_buf[52] == 0x01      # Syntax active
    assert shared_buf[53] == 0x01      # Phonology active
    assert shared_buf[54] == 0x01      # Pragmatic active
    assert shared_buf[55] == 0x01      # Editorial active
    
    score = struct.unpack("<f", shared_buf[24:28])[0]
    assert 0.0 <= score <= 1.0

# 3. Tokenization Scriptio Continua
def test_tokenization_scriptio_continua():
    text = "ผมกินข้าวและอ่านหนังสือที่บ้าน"
    tokens = tokenize_thai(text)
    
    assert "ผม" in tokens
    assert "กินข้าว" in tokens or ("กิน" in tokens and "ข้าว" in tokens)
    assert "หนังสือ" in tokens
    assert "บ้าน" in tokens

# 4. POS Tagging UD Compliance
def test_pos_tagging_ud_compliance():
    tokens = ["ผม", "กิน", "ข้าว", "สอง", "จาน", "ครับ"]
    tagged = tag_pos(tokens)
    tag_dict = dict(tagged)
    
    assert tag_dict["ผม"] == "PRON"
    assert tag_dict["กิน"] == "VERB"
    assert tag_dict["ข้าว"] == "NOUN"
    assert tag_dict["สอง"] == "NUM"
    assert tag_dict["ครับ"] == "PART"

# 5. Five Tone Calculation Engine
def test_five_tone_calculation_engine():
    # กา (Mid class, live -> Mid tone)
    t_mid = calculate_syllable_tone("กา")
    assert t_mid["tone_name"] == "mid"
    assert t_mid["tone_number"] == 1
    
    # ก่า (Mid class + mai ek -> Low tone)
    t_low = calculate_syllable_tone("ก่า")
    assert t_low["tone_name"] == "low"
    assert t_low["tone_number"] == 2
    
    # ก้า (Mid class + mai tho -> Falling tone)
    t_fall = calculate_syllable_tone("ก้า")
    assert t_fall["tone_name"] == "falling"
    assert t_fall["tone_number"] == 3
    
    # ก๊า (Mid class + mai tri -> High tone)
    t_high = calculate_syllable_tone("ก๊า")
    assert t_high["tone_name"] == "high"
    assert t_high["tone_number"] == 4
    
    # ก๋า (Mid class + mai chattawa -> Rising tone)
    t_rise = calculate_syllable_tone("ก๋า")
    assert t_rise["tone_name"] == "rising"
    assert t_rise["tone_number"] == 5

# 6. Numeral Classifier Selection and Agreement
def test_numeral_classifier_selection_and_agreement():
    assert get_classifier_for_noun("หมา") == "ตัว"
    assert get_classifier_for_noun("แมว") == "ตัว"
    assert get_classifier_for_noun("หนังสือ") == "เล่ม"
    assert get_classifier_for_noun("รถยนต์") == "คัน"
    assert get_classifier_for_noun("บ้าน") == "หลัง"
    assert get_classifier_for_noun("กระเป๋า") == "ใบ"
    assert get_classifier_for_noun("คน") == "คน"

# 7. Classifier Post-Nominal Syntax vs Calque Error
def test_classifier_post_nominal_syntax():
    # Canonical: [Noun] + [Numeral] + [Classifier] (หมาสองตัว)
    can_tokens = ["หมา", "สอง", "ตัว"]
    can_audit = audit_classifier_syntax(can_tokens)
    assert can_audit["is_valid"] is True
    assert can_audit["concord_flag"] == 1
    
    # Calque error: [Numeral] + [Classifier] + [Noun] (*สองตัวหมา)
    calque_tokens = ["สอง", "ตัว", "หมา"]
    calque_audit = audit_classifier_syntax(calque_tokens)
    assert calque_audit["is_valid"] is False
    assert len(calque_audit["violations"]) > 0

# 8. Politeness Particle Harmony & Error Detection
def test_politeness_particle_harmony():
    # Correct male
    m_res = audit_politeness_particles("สวัสดีครับ")
    assert m_res["is_concordant"] is True
    assert m_res["speaker_gender_hint"] == "male"
    
    # Correct female declarative
    f_res = audit_politeness_particles("ขอบคุณค่ะ")
    assert f_res["is_concordant"] is True
    assert f_res["speaker_gender_hint"] == "female"
    
    # Error: female declarative with high-tone 'คะ'
    err_dec = audit_politeness_particles("ขอบคุณคะ")
    assert err_dec["is_concordant"] is False
    assert "ขอบคุณค่ะ" in err_dec["corrected_text"]
    
    # Error: female question with falling-tone 'ค่ะ'
    err_q = audit_politeness_particles("ไปไหนค่ะ?")
    assert err_q["is_concordant"] is False
    assert "ไปไหนคะ" in err_q["corrected_text"]

# 9. Rachasap and Register Hierarchy
def test_rachasap_and_register_hierarchy():
    # Colloquial (กิน)
    r1 = detect_register("เขากินข้าว")
    assert r1["tier_level"] == 1
    
    # Formal (รับประทาน)
    r2 = detect_register("ท่านผู้จัดการรับประทานอาหาร")
    assert r2["tier_level"] == 2
    
    # Monastic (ฉัน)
    r3 = detect_register("พระสงฆ์ฉันภัตตาหาร")
    assert r3["tier_level"] == 3
    
    # Royal Rachasap (เสวย, พระราช-)
    r4 = detect_register("พระมหากษัตริย์เสวยและมีพระราชดำรัส")
    assert r4["tier_level"] == 4

# 10. TAM Preverbal Aspect Markers
def test_tam_preverbal_aspect_markers():
    orchestrator = ThaiEngineOrchestrator()
    # Sentence with preverbal continuous marker กำลัง
    res = orchestrator.process_text("เขากำลังอ่านหนังสือสองเล่มครับ")
    assert res["syntax"]["has_aspect"] is True
    assert res["syntax"]["byte_18"] & 0x08 != 0

# 11. Four Dedicated Sub-AIs Direct AMSV Sync
def test_four_sub_ais_direct_amsv_sync():
    buf = bytearray(64)
    bridge = ThaiMatrixBridge(buf)
    
    syn_ai = ThaiSyntaxSubAI(buf)
    phon_ai = ThaiPhonologySubAI(buf)
    prag_ai = ThaiPragmaticSubAI(buf)
    edit_ai = ThaiEditorialSubAI(buf)
    
    text = "ผมอ่านหนังสือสองเล่มครับ"
    
    # 1. Syntax Sub-AI (Bytes 18 & 52)
    s_res = syn_ai.process(text)
    assert buf[18] & 0x01 != 0
    assert buf[52] == 0x01
    
    # 2. Phonology Sub-AI (Bytes 20 & 53)
    p_res = phon_ai.process(text)
    assert buf[20] & 0x01 != 0
    assert buf[53] == 0x01
    
    # 3. Pragmatic Sub-AI (Bytes 22, 23 & 54)
    pr_res = prag_ai.process(text)
    assert buf[22] >= 1
    assert buf[23] == 0x01
    assert buf[54] == 0x01
    
    # 4. Editorial Sub-AI (Bytes 19, 21, 24..27 & 55)
    e_res = edit_ai.process(text)
    assert buf[19] == 0x01
    assert buf[21] == 0x01
    assert buf[55] == 0x01
    conf = struct.unpack("<f", buf[24:28])[0]
    assert 0.0 <= conf <= 1.0

# 12. Task Pipelines: Grammar, Email, Composition
def test_task_pipelines_grammar_email_composition():
    orchestrator = ThaiEngineOrchestrator()
    
    # Grammar Check: Good
    chk_good = orchestrator.check_grammar("ผมอ่านหนังสือสองเล่มครับ")
    assert chk_good["is_grammatically_sound"] is True
    
    # Grammar Check: Bad female particle
    chk_bad = orchestrator.check_grammar("ขอบคุณคะ")
    assert chk_bad["is_grammatically_sound"] is False
    assert "ขอบคุณค่ะ" in chk_bad["corrected_text"]
    
    # Email Pipeline
    email = orchestrator.generate_email("ท่านผู้อำนวยการ", "ขอความอนุเคราะห์", "ทางเราขอความอนุเคราะห์ครับ", gender="male")
    assert "เรียน ท่านผู้อำนวยการ" in email["email_body"]
    assert "ขอแสดงความนับถืออย่างยิ่ง" in email["email_body"]
    
    # Composition Pipeline
    comp = orchestrator.compose_prose(theme="โอกาส", include_proverb=True)
    assert comp["line_count"] >= 3
    assert "น้ำขึ้นให้รีบตัก" in comp["proverb_used"]

# 13. Master Orchestrator End-to-End
def test_master_orchestrator_end_to_end():
    orchestrator = ThaiEngineOrchestrator()
    
    sentence = orchestrator.synthesize_sentence(
        subject="ผม",
        verb="อ่าน",
        object_noun="หนังสือ",
        numeral="สอง",
        polite_particle="ครับ"
    )
    assert sentence == "ผมอ่านหนังสือสองเล่มครับ"
    
    # Cognitive analysis loop
    analysis = orchestrator.process_text(sentence)
    amsv = analysis["amsv_state"]
    
    assert amsv["magic"] == "THAI"
    assert amsv["sub_ais_active"]["syntax"] is True
    assert amsv["sub_ais_active"]["phonology"] is True
    assert amsv["sub_ais_active"]["pragmatic"] is True
    assert amsv["sub_ais_active"]["editorial"] is True
    assert amsv["confidence_score"] > 0.5
