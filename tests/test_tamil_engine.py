"""
Dedicated Automated Test Suite for Tamil Language Engine (Tamil_engine/)
Verifies the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
Six-Language Matrix, and The Zero-Bridge Synchronous Memory Rule (0x54414D4C 'TAML').
"""

import os
import struct
import pytest

from Tamil_engine import (
    TamilEngineOrchestrator,
    TamilMatrixBridge,
    TAMIL_MAGIC_BYTES,
    TAMIL_MAGIC_INT,
    AMSV_TOTAL_SIZE
)
from Tamil_engine.brain.skills.tokenization import tokenize_tamil
from Tamil_engine.brain.skills.pos_tagging import tag_pos
from Tamil_engine.brain.skills.case_engine import analyze_noun_case, inflect_case
from Tamil_engine.brain.skills.png_concord_engine import check_png_concord
from Tamil_engine.brain.skills.retroflex_engine import analyze_phonological_profile
from Tamil_engine.brain.skills.sandhi_engine import audit_sandhi, apply_sandhi
from Tamil_engine.brain.skills.pragmatics_engine import detect_register, compose_email
from Tamil_engine.brain.sub_ais.syntax_sub_ai import TamilSyntaxSubAI
from Tamil_engine.brain.sub_ais.phonology_sub_ai import TamilPhonologySubAI
from Tamil_engine.brain.sub_ais.pragmatic_sub_ai import TamilPragmaticSubAI
from Tamil_engine.brain.sub_ais.editorial_sub_ai import TamilEditorialSubAI

# 1. AMSV Physical Layout & Magic
def test_amsv_physical_layout_and_magic():
    bridge = TamilMatrixBridge()
    assert len(bridge.buffer) == AMSV_TOTAL_SIZE == 64
    assert bridge.verify_magic() is True
    assert bytes(bridge.buffer[0:4]) == TAMIL_MAGIC_BYTES == b"TAML"
    assert bridge.get_magic_uint32() == TAMIL_MAGIC_INT == 0x54414D4C
    assert bridge.buffer[4] == 0x01  # Major version
    assert bridge.buffer[5] == 0x00  # Minor version
    assert bridge.buffer[6] == 0x01  # Inference mode
    assert bridge.buffer[7] == 0x01  # Centamil

# 2. Zero-Bridge Memory Synchronization
def test_zero_bridge_memory_synchronization():
    shared_buf = bytearray(64)
    bridge = TamilMatrixBridge(shared_buf)
    orchestrator = TamilEngineOrchestrator(shared_buf)
    
    # Process text with SOV, case marking, retroflex 'ழ' (Tamiḻ), and sandhi
    res = orchestrator.process_text("நான் தமிழ்ப் புத்தகம் படித்தேன்.")
    
    # Verify exact physical memory updates
    assert bytes(shared_buf[0:4]) == b"TAML"
    assert shared_buf[18] & 0x01 != 0  # Has verb
    assert shared_buf[18] & 0x08 != 0  # Is SOV
    assert shared_buf[20] & 0x04 != 0  # Has retroflex ழ (ḻ)
    assert shared_buf[22] == 0x01      # Centamil tier
    assert shared_buf[52] == 0x01      # Syntax Sub-AI active
    assert shared_buf[53] == 0x01      # Phonology Sub-AI active
    assert shared_buf[54] == 0x01      # Pragmatic Sub-AI active
    assert shared_buf[55] == 0x01      # Editorial Sub-AI active
    
    score = struct.unpack("<f", shared_buf[24:28])[0]
    assert 0.0 <= score <= 1.0

# 3. Tokenization Tamil Unicode
def test_tokenization_tamil_unicode():
    text = "நான் பள்ளிக்கூடம் சென்று தமிழ் படித்தேன்."
    tokens = tokenize_tamil(text)
    
    assert "நான்" in tokens
    assert "பள்ளிக்கூடம்" in tokens
    assert "சென்று" in tokens
    assert "தமிழ்" in tokens
    assert "படித்தேன்" in tokens

# 4. POS Tagging UD Compliance
def test_pos_tagging_ud_compliance():
    tokens = ["நான்", "புத்தகம்", "படித்தேன்", "மேலே", "இல்லை"]
    tagged = tag_pos(tokens)
    tag_dict = dict(tagged)
    
    assert tag_dict["நான்"] == "PRON"
    assert tag_dict["புத்தகம்"] == "NOUN"
    assert tag_dict["படித்தேன்"] == "VERB"
    assert tag_dict["மேலே"] == "ADP"
    assert tag_dict["இல்லை"] == "PART"

# 5. Eight Grammatical Cases Declension
def test_eight_grammatical_cases_declension():
    # Accusative: -ai
    acc = inflect_case("புத்தகம்", 2)
    assert acc == "புத்தகத்தை"
    a_info = analyze_noun_case("புத்தகத்தை")
    assert a_info["case_number"] == 2
    
    # Instrumental: -āl
    inst = inflect_case("மரம்", 3)
    assert inst == "மரத்தால்"
    i_info = analyze_noun_case("மரத்தால்")
    assert i_info["case_number"] == 3
    
    # Dative: -ku / -ukku
    dat = inflect_case("வீடு", 4)
    assert dat == "வீட்டுக்கு"
    d_info = analyze_noun_case("வீட்டுக்கு")
    assert d_info["case_number"] == 4
    
    # Ablative: -iliruntu
    abl = inflect_case("ஊர்", 5)
    assert abl == "ஊரிலிருந்து"
    ab_info = analyze_noun_case("ஊரிலிருந்து")
    assert ab_info["case_number"] == 5
    
    # Locative: -il
    loc = inflect_case("மரம்", 7)
    assert loc == "மரத்தில்"
    l_info = analyze_noun_case("மரத்தில்")
    assert l_info["case_number"] == 7

# 6. PNG Concord Agreement
def test_png_concord_agreement():
    # 1SG: நான் -> படித்தேன் (Valid) vs படித்தான் (Invalid)
    c1 = check_png_concord("நான்", "படித்தேன்")
    assert c1["is_concordant"] is True
    
    c1_bad = check_png_concord("நான்", "படித்தான்")
    assert c1_bad["is_concordant"] is False
    
    # 3MSG: அவன் -> படித்தான்
    c2 = check_png_concord("அவன்", "படித்தான்")
    assert c2["is_concordant"] is True
    
    # 3FSG: அவள் -> படித்தாள்
    c3 = check_png_concord("அ அவள்", "படித்தாள்") # check with aval
    c3_ok = check_png_concord("அவள்", "படித்தாள்")
    assert c3_ok["is_concordant"] is True
    
    # 2PL: நீங்கள் -> படித்தீர்கள்
    c4 = check_png_concord("நீங்கள்", "படித்தீர்கள்")
    assert c4["is_concordant"] is True

# 7. Retroflex Triad and Zha Approximant
def test_retroflex_triad_and_zha_approximant():
    # Test with text containing ழ (ḻ) in தமிழ்
    prof_tamil = analyze_phonological_profile("தமிழ்")
    assert prof_tamil["has_retroflex"] is True
    assert prof_tamil["has_zha_approximant"] is True
    assert prof_tamil["byte_20_val"] & 0x04 != 0
    
    # Test text without retroflex
    prof_plain = analyze_phonological_profile("நான் வந்தேன்")
    assert prof_plain["has_zha_approximant"] is False

# 8. Sandhi Plosive Doubling (Valikattal)
def test_sandhi_plosive_doubling_valikattal():
    # After accusative -ai, initial 'p' (ப) must double
    before = "புத்தகத்தை படி"
    audit = audit_sandhi(before)
    assert audit["is_sandhi_valid"] is False
    
    after = apply_sandhi(before)
    assert after == "புத்தகத்தைப் படி"
    assert audit_sandhi(after)["is_sandhi_valid"] is True

# 9. Dative Subject Experiencer Constructions
def test_dative_subject_experiencer_constructions():
    orchestrator = TamilEngineOrchestrator()
    sentence = orchestrator.synthesize_dative_experiencer("நான்", "தெரியும்", theme="தமிழ்")
    assert "எனக்கு" in sentence
    assert "தெரியும்" in sentence

# 10. Diglossic Register Detection
def test_diglossic_register_detection():
    # Centamil: வருகிறேன்
    reg_cen = detect_register("நான் இப்போது வருகிறேன்.")
    assert reg_cen["register"] == "centamil"
    assert reg_cen["tier_level"] == 1
    
    # Koduntamil: வர்றேன்
    reg_kodun = detect_register("நான் இப்போ வர்றேன்.")
    assert reg_kodun["register"] == "koduntamil"
    assert reg_kodun["tier_level"] == 2

# 11. Four Dedicated Sub-AIs Direct AMSV Sync
def test_four_sub_ais_direct_amsv_sync():
    buf = bytearray(64)
    bridge = TamilMatrixBridge(buf)
    
    syn_ai = TamilSyntaxSubAI(buf)
    phon_ai = TamilPhonologySubAI(buf)
    prag_ai = TamilPragmaticSubAI(buf)
    edit_ai = TamilEditorialSubAI(buf)
    
    text = "நான் தமிழ்ப் புத்தகம் படித்தேன்."
    
    # 1. Syntax Sub-AI (Bytes 18 & 52)
    s_res = syn_ai.process(text)
    assert buf[18] & 0x01 != 0
    assert buf[52] == 0x01
    
    # 2. Phonology Sub-AI (Bytes 20 & 53)
    p_res = phon_ai.process(text)
    assert buf[20] & 0x04 != 0  # ழ present
    assert buf[53] == 0x01
    
    # 3. Pragmatic Sub-AI (Bytes 22, 23 & 54)
    pr_res = prag_ai.process(text)
    assert buf[22] == 0x01
    assert buf[54] == 0x01
    
    # 4. Editorial Sub-AI (Bytes 19, 21, 24..27 & 55)
    e_res = edit_ai.process(text)
    assert buf[55] == 0x01
    conf = struct.unpack("<f", buf[24:28])[0]
    assert 0.0 <= conf <= 1.0

# 12. Task Pipelines: Grammar, Email, Composition
def test_task_pipelines_grammar_email_composition():
    orchestrator = TamilEngineOrchestrator()
    
    # Grammar Check
    chk_good = orchestrator.check_grammar("நான் புத்தகம் படித்தேன்.")
    assert chk_good["is_grammatically_sound"] is True
    
    chk_bad_concord = orchestrator.check_grammar("நான் புத்தகம் படித்தான்.")
    assert chk_bad_concord["is_grammatically_sound"] is False
    
    # Email Pipeline
    email = orchestrator.generate_email("அதிகாரி", "வேலை விண்ணப்பம்", "என் விண்ணப்பத்தை ஏற்கவும்.", register="formal")
    assert "மதிப்பிற்குரிய அதிகாரி" in email["email_body"]
    assert "இங்ஙனம்" in email["email_body"]
    
    # Composition Pipeline
    comp = orchestrator.compose_prose(theme="அறிவு", include_proverb=True)
    assert comp["line_count"] >= 3
    assert "கற்றது கைமண் அளவு" in comp["proverb_used"]

# 13. Master Orchestrator End-to-End
def test_master_orchestrator_end_to_end():
    orchestrator = TamilEngineOrchestrator()
    
    sentence = orchestrator.synthesize_sov_sentence(
        subject="நான்",
        verb="படித்தேன்",
        object_noun="புத்தகம்"
    )
    assert "நான்" in sentence
    assert "படித்தேன்" in sentence
    
    # Cognitive analysis
    analysis = orchestrator.process_text(sentence)
    amsv = analysis["amsv_state"]
    
    assert amsv["magic"] == "TAML"
    assert amsv["sub_ais_active"]["syntax"] is True
    assert amsv["sub_ais_active"]["phonology"] is True
    assert amsv["sub_ais_active"]["pragmatic"] is True
    assert amsv["sub_ais_active"]["editorial"] is True
    assert amsv["confidence_score"] > 0.5
