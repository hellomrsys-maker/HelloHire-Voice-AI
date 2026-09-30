"""
Dedicated Automated Test Suite for Cantonese Language Engine (Cantonese_engine/)
Verifies the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
Six-Language Matrix, and The Zero-Bridge Synchronous Memory Rule (0x59554554 'YUET').
"""

import os
import struct
import pytest

from Cantonese_engine import (
    CantoneseEngineOrchestrator,
    CantoneseMatrixBridge,
    CANTONESE_MAGIC_BYTES,
    CANTONESE_MAGIC_INT,
    AMSV_TOTAL_SIZE
)
from Cantonese_engine.brain.skills.tokenization import tokenize_cantonese
from Cantonese_engine.brain.skills.pos_tagging import tag_pos
from Cantonese_engine.brain.skills.tone_engine import (
    analyze_character_tone,
    text_to_jyutping,
    is_entering_tone
)
from Cantonese_engine.brain.skills.classifier_engine import (
    get_classifier_for_noun,
    parse_classifier_phrase
)
from Cantonese_engine.brain.skills.doc_inversion_engine import (
    analyze_doc_structure,
    analyze_postverbal_adverb,
    invert_to_canonical_cantonese
)
from Cantonese_engine.brain.skills.aspect_engine import (
    extract_aspect_markers,
    has_aspect
)
from Cantonese_engine.brain.skills.sfp_engine import (
    extract_sfps,
    has_sfp
)
from Cantonese_engine.brain.skills.pragmatics_engine import (
    detect_register,
    compose_email
)
from Cantonese_engine.brain.sub_ais.syntax_sub_ai import CantoneseSyntaxSubAI
from Cantonese_engine.brain.sub_ais.phonology_sub_ai import CantonesePhonologySubAI
from Cantonese_engine.brain.sub_ais.pragmatic_sub_ai import CantonesePragmaticSubAI
from Cantonese_engine.brain.sub_ais.editorial_sub_ai import CantoneseEditorialSubAI

# 1. AMSV Physical Layout & Magic
def test_amsv_physical_layout_and_magic():
    bridge = CantoneseMatrixBridge()
    assert len(bridge.buffer) == AMSV_TOTAL_SIZE == 64
    assert bridge.verify_magic() is True
    assert bytes(bridge.buffer[0:4]) == CANTONESE_MAGIC_BYTES == b"YUET"
    assert bridge.get_magic_uint32() == CANTONESE_MAGIC_INT == 0x59554554
    assert bridge.buffer[4] == 0x01  # Major version
    assert bridge.buffer[5] == 0x00  # Minor version
    assert bridge.buffer[6] == 0x01  # Inference mode
    assert bridge.buffer[7] == 0x01  # Hong Kong Cantonese

# 2. Zero-Bridge Memory Synchronization
def test_zero_bridge_memory_synchronization():
    shared_buf = bytearray(64)
    bridge = CantoneseMatrixBridge(shared_buf)
    orchestrator = CantoneseEngineOrchestrator(shared_buf)
    
    # Process text with ditransitive DOC, aspect enclitic, and SFP
    res = orchestrator.process_text("我畀本書你喇。")
    
    # Verify exact physical memory updates
    assert bytes(shared_buf[0:4]) == b"YUET"
    assert shared_buf[18] & 0x01 != 0  # Has verb
    assert shared_buf[18] & 0x08 != 0  # Has canonical DOC (V + DO + IO)
    assert shared_buf[19] == 0x01      # Canonical DOC flag
    assert shared_buf[20] & 0x01 != 0  # Valid text
    assert shared_buf[22] == 0x01      # Colloquial register (Hau2 Jyu5)
    assert shared_buf[23] & 0x01 != 0  # Has SFP
    assert shared_buf[52] == 0x01      # Syntax Sub-AI active
    assert shared_buf[53] == 0x01      # Phonology Sub-AI active
    assert shared_buf[54] == 0x01      # Pragmatic Sub-AI active
    assert shared_buf[55] == 0x01      # Editorial Sub-AI active
    
    score = struct.unpack("<f", shared_buf[24:28])[0]
    assert 0.0 <= score <= 1.0

# 3. Tokenization and Multi-Character Compounds
def test_tokenization_and_compounds():
    text = "我哋去茶餐廳食點心同飲絲襪奶茶。"
    tokens = tokenize_cantonese(text)
    
    assert "我哋" in tokens
    assert "茶餐廳" in tokens
    assert "點心" in tokens
    assert "絲襪奶茶" in tokens
    assert "食" in tokens
    assert "飲" in tokens

# 4. POS Tagging UD Compliance
def test_pos_tagging_ud_compliance():
    tokens = ["我", "畀", "本", "書", "佢", "喇"]
    tagged = tag_pos(tokens)
    tag_dict = dict(tagged)
    
    assert tag_dict["我"] == "PRON"
    assert tag_dict["畀"] == "VERB"
    assert tag_dict["本"] == "CLF"
    assert tag_dict["書"] == "NOUN"
    assert tag_dict["佢"] == "PRON"
    assert tag_dict["喇"] == "PART"

# 5. Nine-Tone and Entering Checked Tones (-p, -t, -k)
def test_nine_tone_and_checked_codas():
    # Entering tone examples: 識 (tone 7), 錫 (tone 8), 食 (tone 9)
    p7 = analyze_character_tone("識")
    p8 = analyze_character_tone("錫")
    p9 = analyze_character_tone("食")
    
    assert p7["tone_number"] == 7
    assert p7["is_checked_tone"] is True
    assert p7["category_name"] == "上陰入"
    
    assert p8["tone_number"] == 8
    assert p8["is_checked_tone"] is True
    assert p8["category_name"] == "下陰入"
    
    assert p9["tone_number"] == 9
    assert p9["is_checked_tone"] is True
    assert p9["category_name"] == "陽入"
    
    # Non-checked citation tones
    p1 = analyze_character_tone("書")
    assert p1["tone_number"] == 1
    assert p1["is_checked_tone"] is False
    
    assert is_entering_tone("食") is True
    assert is_entering_tone("書") is False

# 6. Classifier Engine Selection and Definiteness
def test_classifier_engine_selection_and_definiteness():
    assert get_classifier_for_noun("狗") == "隻"
    assert get_classifier_for_noun("書") == "本"
    assert get_classifier_for_noun("車") == "架"
    assert get_classifier_for_noun("屋") == "間"
    assert get_classifier_for_noun("魚") == "條"
    
    # Bare classifier definiteness: 隻狗 = the dog
    phrase_info = parse_classifier_phrase("隻狗")
    assert phrase_info["type"] == "bare_classifier_definite"
    assert phrase_info["classifier"] == "隻"
    assert phrase_info["noun"] == "狗"
    assert phrase_info["is_definite"] is True
    
    # Quantified phrase: 一條魚
    q_info = parse_classifier_phrase("一條魚")
    assert q_info["type"] == "quantified"
    assert q_info["numeral"] == "一"
    assert q_info["classifier"] == "條"

# 7. DOC Inversion Canonical Order vs Calque
def test_doc_inversion_canonical_order():
    # Canonical: V + DO + IO (畀本書我)
    can_eval = analyze_doc_structure("畀本書我")
    assert can_eval["is_canonical"] is True
    assert can_eval["verb"] == "畀"
    assert can_eval["recipient_io"] == "我"
    assert can_eval["theme_do"] == "本書"
    
    # Calque: V + IO + DO (畀我本書)
    calque_eval = analyze_doc_structure("畀我本書")
    assert calque_eval["is_canonical"] is False
    assert calque_eval["verb"] == "畀"
    assert calque_eval["suggested_canonical"] == "畀本書我"
    
    # Auto-inversion
    corrected = invert_to_canonical_cantonese("畀我本書")
    assert corrected == "畀本書我"

# 8. Postverbal Adverbs and Comparatives
def test_postverbal_adverbs_and_comparatives():
    # Canonical: 行先 vs Mandarin calque 先行
    adv_can = analyze_postverbal_adverb("行先")
    assert adv_can["is_canonical"] is True
    
    adv_calque = analyze_postverbal_adverb("先行")
    assert adv_calque["is_canonical"] is False
    assert adv_calque["suggested_canonical"] == "行先"
    
    # Comparative: A + Adj + 過 + B (我大過你) vs Mandarin (我比你大)
    comp_can = analyze_postverbal_adverb("我大過你")
    assert comp_can["is_canonical"] is True
    
    comp_calque = analyze_postverbal_adverb("我比你大")
    assert comp_calque["is_canonical"] is False
    assert comp_calque["suggested_canonical"] == "我大過你"

# 9. Aspect Enclitic Parsing
def test_aspect_enclitic_parsing():
    text = "我食咗飯，依家睇緊波，之前去過日本。"
    markers = extract_aspect_markers(text)
    
    aspect_types = [m["aspect"] for m in markers]
    assert "perfective" in aspect_types   # 咗
    assert "progressive" in aspect_types  # 緊
    assert "experiential" in aspect_types # 過
    
    assert has_aspect(text, "perfective") is True
    assert has_aspect(text, "progressive") is True
    assert has_aspect(text, "experiential") is True

# 10. Sentence-Final Particles and Punctuation Stripping
def test_sfp_engine_robust_punctuation_stripping():
    # Test stripping of trailing full stop, exclamation mark, questions
    s1 = "搞掂喇。"
    s2 = "快啲啦！"
    s3 = "係呀？"
    s4 = "好叻㗎～"
    
    sfps1 = extract_sfps(s1)
    sfps2 = extract_sfps(s2)
    sfps3 = extract_sfps(s3)
    sfps4 = extract_sfps(s4)
    
    assert len(sfps1) > 0 and sfps1[0]["particle"] == "喇"
    assert len(sfps2) > 0 and sfps2[0]["particle"] == "啦"
    assert len(sfps3) > 0 and sfps3[0]["particle"] == "呀"
    assert len(sfps4) > 0 and sfps4[0]["particle"] == "㗎"
    
    assert has_sfp(s1, "喇") is True
    assert has_sfp(s2, "啦") is True

# 11. Four Dedicated Sub-AIs Direct AMSV Sync
def test_four_sub_ais_direct_amsv_sync():
    buf = bytearray(64)
    bridge = CantoneseMatrixBridge(buf)
    
    syn_ai = CantoneseSyntaxSubAI(buf)
    phon_ai = CantonesePhonologySubAI(buf)
    prag_ai = CantonesePragmaticSubAI(buf)
    edit_ai = CantoneseEditorialSubAI(buf)
    
    text = "我哋送部車畀佢喇。"
    
    # 1. Syntax Sub-AI (Bytes 18 & 52)
    s_res = syn_ai.process(text)
    assert buf[18] & 0x01 != 0  # Has verb
    assert buf[52] == 0x01      # Syntax active
    
    # 2. Phonology Sub-AI (Bytes 20 & 53)
    p_res = phon_ai.process(text)
    assert buf[20] & 0x01 != 0  # Text valid
    assert buf[53] == 0x01      # Phonology active
    
    # 3. Pragmatic Sub-AI (Bytes 22, 23 & 54)
    pr_res = prag_ai.process(text)
    assert buf[22] == 0x01      # Colloquial tier
    assert buf[23] & 0x01 != 0  # Has SFP
    assert buf[54] == 0x01      # Pragmatic active
    
    # 4. Editorial Sub-AI (Bytes 19, 21, 24..27 & 55)
    e_res = edit_ai.process(text)
    assert buf[55] == 0x01      # Editorial active
    conf = struct.unpack("<f", buf[24:28])[0]
    assert 0.0 <= conf <= 1.0

# 12. Task Pipelines: Grammar, Email, Composition
def test_task_pipelines_grammar_email_composition():
    orchestrator = CantoneseEngineOrchestrator()
    
    # Grammar checker
    chk_canonical = orchestrator.check_grammar("畀本書我喇。")
    assert chk_canonical["is_grammatically_sound"] is True
    
    chk_calque = orchestrator.check_grammar("畀我本書")
    assert chk_calque["is_grammatically_sound"] is False
    assert "畀本書我" in chk_calque["suggested_text"]
    
    # Email generation
    email = orchestrator.generate_email("陳總", "業務會議", "明天下午開會。", register="formal")
    assert "陳總 閣下" in email["email_body"]
    assert "此致" in email["email_body"]
    
    # Composition pipeline
    comp = orchestrator.compose_prose("香港生活", include_idiom=True)
    assert comp["line_count"] >= 3
    assert comp["idiom_used"] == "飲茶"

# 13. Master Orchestrator End-to-End
def test_master_orchestrator_end_to_end():
    orchestrator = CantoneseEngineOrchestrator()
    
    sentence = orchestrator.synthesize_sentence(
        subject="佢",
        verb="畀",
        theme_object="本書",
        recipient_io="我",
        aspect="咗",
        sfp="喇。"
    )
    assert sentence == "佢畀咗本書我喇。"
    
    # Run full cognitive loop
    analysis = orchestrator.process_text(sentence)
    amsv = analysis["amsv_state"]
    
    assert amsv["magic"] == "YUET"
    assert amsv["sub_ais_active"]["syntax"] is True
    assert amsv["sub_ais_active"]["phonology"] is True
    assert amsv["sub_ais_active"]["pragmatic"] is True
    assert amsv["sub_ais_active"]["editorial"] is True
    assert amsv["confidence_score"] > 0.5
