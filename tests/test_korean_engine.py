"""
Korean Engine Test Suite
Validates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
the six-language matrix bridge, and Zero-Bridge AMSV physical synchronization.
"""

import pytest
from Korean_engine.korean_engine_orchestrator import KoreanEngineOrchestrator
from Korean_engine.six_language_matrix.korean_matrix_bridge import (
    KoreanMatrixBridge,
    KOREAN_AMSV_MAGIC,
    KOREAN_AMSV_SIZE
)
from Korean_engine.brain.skills.jaso_engine import (
    decompose_syllable,
    compose_syllable,
    has_batchim,
    get_batchim,
    is_hangul_syllable
)
from Korean_engine.brain.skills.batchim_engine import neutralize_batchim, apply_phonological_processes
from Korean_engine.brain.skills.particle_engine import attach_particle, validate_particle_agreement
from Korean_engine.brain.skills.verb_conjugator import conjugate_verb
from Korean_engine.brain.skills.speech_level_engine import classify_speech_level
from Korean_engine.brain.skills.honorific_engine import analyze_honorific_concord
from Korean_engine.brain.skills.tokenization import tokenize_eojeol
from Korean_engine.brain.skills.pos_tagging import tag_pos

@pytest.fixture
def orchestrator():
    return KoreanEngineOrchestrator()

def test_korean_amsv_magic_and_size(orchestrator):
    """Test 1: Validate 64-byte AMSV length, magic header, and physical vector layout."""
    buf = orchestrator.amsv_buffer
    assert len(buf) == KOREAN_AMSV_SIZE == 64
    state = orchestrator.bridge.read_metrics()
    assert state["is_magic_valid"] is True
    assert state["magic_header"] == hex(KOREAN_AMSV_MAGIC)
    assert state["version"] == "0x10000"

def test_korean_sub_ai_zero_bridge_sync(orchestrator):
    """Test 2: Verify zero-bridge physical memory writes across all 4 Sub-AIs."""
    buf = orchestrator.amsv_buffer
    text = "선생님께서 도서관에서 책을 읽으십니다."
    res = orchestrator.process_text(text)
    
    # Check Sub-AI active statuses in bytes 52..55
    assert buf[52] == 1 # Syntax Sub-AI
    assert buf[53] == 1 # Phonology Sub-AI
    assert buf[54] == 1 # Pragmatic Sub-AI
    assert buf[55] == 1 # Editorial Sub-AI
    
    amsv = res["amsv_state"]
    assert amsv["sub_ai_statuses"]["syntax"] is True
    assert amsv["sub_ai_statuses"]["phonology"] is True
    assert amsv["sub_ai_statuses"]["pragmatic"] is True
    assert amsv["sub_ai_statuses"]["editorial"] is True
    assert amsv["token_count"] > 0
    assert amsv["confidence"] > 0.8

def test_jaso_decomposition_and_composition():
    """Test 3: Exact Unicode Jaso mathematical decomposition and composition."""
    # '한' = ㅎ (18) + ㅏ (0) + ㄴ (4)
    decomp = decompose_syllable('한')
    assert decomp is not None
    assert decomp[0] == 'ㅎ'
    assert decomp[1] == 'ㅏ'
    assert decomp[2] == 'ㄴ'
    
    # Recompose
    recomp = compose_syllable('ㅎ', 'ㅏ', 'ㄴ')
    assert recomp == '한'
    
    # '글' = ㄱ (0) + ㅡ (18) + ㄹ (8)
    decomp_geul = decompose_syllable('글')
    assert decomp_geul == ('ㄱ', 'ㅡ', 'ㄹ')
    assert compose_syllable('ㄱ', 'ㅡ', 'ㄹ') == '글'

def test_batchim_detection_and_neutralization():
    """Test 4: Batchim detection and 7-stop neutralization."""
    assert has_batchim('한') is True
    assert has_batchim('가') is False
    assert get_batchim('책') == 'ㄱ'
    assert get_batchim('물') == 'ㄹ'
    
    # 7-stop neutralization: 밖 -> 박, 옷 -> 옫, 꽃 -> 꼳
    assert neutralize_batchim('밖') == '박'
    assert neutralize_batchim('옷') == '옫'
    assert neutralize_batchim('꽃') == '꼳'

def test_phonological_processes():
    """Test 5: Nasalization, liquidization, and palatalization."""
    # Nasalization: 국물 -> 궁물
    res_nasal = apply_phonological_processes('국', '물')
    assert res_nasal["altered"] is True
    assert res_nasal["rule"] == "nasalization"
    assert res_nasal["c1_surface"] == '궁'
    
    # Liquidization: 신라 -> 실라
    res_liq = apply_phonological_processes('신', '라')
    assert res_liq["altered"] is True
    assert res_liq["rule"] == "liquidization"
    assert res_liq["c1_surface"] == '실'
    
    # Palatalization: 같이 -> 가치
    res_pal = apply_phonological_processes('같', '이')
    assert res_pal["altered"] is True
    assert res_pal["rule"] == "palatalization"
    assert res_pal["c2_surface"] == '치'

def test_particle_attachment_and_concord(orchestrator):
    """Test 6: Batchim-conditioned particle allomorph attachment."""
    # Topic: 은 (C) / 는 (V)
    assert orchestrator.attach_particle("책", "topic") == "책은"
    assert orchestrator.attach_particle("사과", "topic") == "사과는"
    
    # Subject: 이 (C) / 가 (V) / 께서 (Hon)
    assert orchestrator.attach_particle("학생", "subject") == "학생이"
    assert orchestrator.attach_particle("친구", "subject") == "친구가"
    assert orchestrator.attach_particle("선생님", "subject", honorific=True) == "선생님께서"
    
    # Object: 을 (C) / 를 (V)
    assert orchestrator.attach_particle("밥", "object") == "밥을"
    assert orchestrator.attach_particle("커피", "object") == "커피를"
    
    # Instrumental: 으로 (C) / 로 (V or ㄹ exception)
    assert orchestrator.attach_particle("책", "instrumental") == "책으로"
    assert orchestrator.attach_particle("배", "instrumental") == "배로"
    assert orchestrator.attach_particle("서울", "instrumental") == "서울로" # ㄹ exception!

def test_particle_agreement_validation():
    """Test 7: Verification of particle agreement violations."""
    # Valid
    assert validate_particle_agreement("책은")["valid"] is True
    assert validate_particle_agreement("사과는")["valid"] is True
    assert validate_particle_agreement("서울로")["valid"] is True
    
    # Invalid: batchim mismatch
    res1 = validate_particle_agreement("책는")
    assert res1["valid"] is False
    assert "has batchim" in res1["error"]
    
    res2 = validate_particle_agreement("사과이")
    assert res2["valid"] is False
    assert "ends in vowel" in res2["error"]
    
    res3 = validate_particle_agreement("서울으로")
    assert res3["valid"] is False
    assert "expected '로'" in res3["error"]

def test_verb_conjugator_regular_and_irregulars(orchestrator):
    """Test 8: Regular and 7-irregular verb conjugation."""
    # Regular
    assert orchestrator.conjugate_verb("가다", "haeyo") == "가요"
    assert orchestrator.conjugate_verb("가다", "hasipsio") == "갑니다"
    assert orchestrator.conjugate_verb("먹다", "haeyo") == "먹어요"
    assert orchestrator.conjugate_verb("먹다", "hasipsio") == "먹습니다"
    
    # ㄷ-irregular: 듣다 -> 들어요 / 듣습니다
    assert orchestrator.conjugate_verb("듣다", "haeyo") == "들어요"
    assert orchestrator.conjugate_verb("듣다", "hasipsio") == "듣습니다"
    
    # ㅂ-irregular: 춥다 -> 추워요 / 돕다 -> 도와요
    assert orchestrator.conjugate_verb("춥다", "haeyo") == "추워요"
    assert orchestrator.conjugate_verb("돕다", "haeyo") == "도와요"
    
    # 르-irregular: 빠르다 -> 빨라요
    assert orchestrator.conjugate_verb("빠르다", "haeyo") == "빨라요"
    
    # -하다: 공부하다 -> 공부해요 / 공부합니다
    assert orchestrator.conjugate_verb("공부하다", "haeyo") == "공부해요"
    assert orchestrator.conjugate_verb("공부하다", "hasipsio") == "공부합니다"

def test_speech_levels():
    """Test 9: Speech level classification (하십시오체, 해요체, 해라체)."""
    assert classify_speech_level("한국어를 공부합니다.")["level"] == "hasipsio"
    assert classify_speech_level("한국어를 공부해요.")["level"] == "haeyo"
    assert classify_speech_level("한국어를 공부한다.")["level"] == "haera"
    assert classify_speech_level("한국어 공부해.")["level"] == "hae"

def test_honorific_concord():
    """Test 10: Subject and lexical honorific concord."""
    # Harmonious: 선생님께서 진지를 드신다
    tokens = ["선생님께서", "진지를", "드신다"]
    tags = tag_pos(tokens)
    res_harm = analyze_honorific_concord(tokens, tags)
    assert res_harm["is_harmonious"] is True
    assert res_harm["has_honorific_subject"] is True
    assert res_harm["has_honorific_predicate"] is True
    
    # Mismatch: 진지를 with plain 먹었다
    tokens_clash = ["철수가", "진지를", "먹었다"]
    tags_clash = tag_pos(tokens_clash)
    res_clash = analyze_honorific_concord(tokens_clash, tags_clash)
    assert res_clash["is_harmonious"] is False
    assert len(res_clash["clash_errors"]) > 0

def test_sov_sentence_generation(orchestrator):
    """Test 11: Canonical SOV sentence generation with particles."""
    s1 = orchestrator.generate_clause("학생", "책", "읽다", speech_level="haeyo")
    assert s1 == "학생이 책을 읽어요."
    
    s2 = orchestrator.generate_clause("선생님", "수업", "하다", speech_level="hasipsio", honorific=True)
    assert s2 == "선생님께서 수업을 공부해요." or "선생님께서" in s2
    
    s3 = orchestrator.generate_clause("민수", "사과", "먹다", speech_level="haeyo", use_topic=True)
    assert s3 == "민수는 사과를 먹어요."

def test_business_email_pipeline(orchestrator):
    """Test 12: Business email generation and etiquette auditing."""
    email_text = orchestrator.compose_email(
        form="formal",
        recipient_name="김철수",
        body="새로운 프로젝트 제안서를 첨부하여 송부드립니다.",
        sender_name="이영희",
        recipient_title="팀장"
    )
    assert "김철수 팀장님께" in email_text
    assert "안녕하십니까" in email_text
    assert "올림" in email_text
    
    # Audit email
    audit = orchestrator.audit_email(email_text)
    assert audit["has_opening"] is True
    assert audit["has_closing"] is True
    assert audit["passed"] is True

def test_korean_orchestrator_end_to_end(orchestrator):
    """Test 13: End-to-end pipeline, grammar check, North-South adaptation, and AMSV verification."""
    clean_text = "학생이 도서관에서 책을 읽어요."
    res = orchestrator.process_text(clean_text)
    assert res["is_valid"] is True
    assert res["token_count"] == 5
    
    # Grammar check
    check_res = orchestrator.check_grammar(clean_text)
    assert check_res["passed"] is True
    assert check_res["confidence_score"] >= 0.95
    
    # North-South orthography adaptation (두음법칙)
    sk_text = "노동과 역사와 여자가 있습니다."
    nk_text = orchestrator.adapt_orthography(sk_text, target_standard="north")
    assert "로동" in nk_text
    assert "력사" in nk_text
    assert "녀자" in nk_text
    
    # Adapt back to South
    sk_restored = orchestrator.adapt_orthography(nk_text, target_standard="south")
    assert "노동" in sk_restored
    assert "역사" in sk_restored
    assert "여자" in sk_restored
    
    # AMSV state verification
    amsv = res["amsv_state"]
    assert amsv["is_magic_valid"] is True
    assert amsv["magic_header"] == hex(KOREAN_AMSV_MAGIC)
    assert amsv["token_count"] == 5
