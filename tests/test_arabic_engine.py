"""
Arabic Engine — Comprehensive Test Suite
Validates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
Six-Language Matrix, and Zero-Bridge Synchronous Memory State Vector (AMSV: 0x41524142).
"""

import pytest
import struct
from Arabic_engine import ArabicEngineOrchestrator, ArabicMatrixBridge, ARABIC_AMSV_MAGIC, ARABIC_AMSV_SIZE
from Arabic_engine.brain.skills.root_pattern_engine import derive_form, extract_root_heuristic
from Arabic_engine.brain.skills.broken_plural_engine import get_plural, analyze_plural
from Arabic_engine.brain.skills.concord_agreement_engine import (
    validate_vso_agreement,
    validate_svo_agreement,
    validate_noun_adjective_agreement
)
from Arabic_engine.brain.skills.idafa_engine import validate_idafa, synthesize_idafa
from Arabic_engine.brain.skills.sun_moon_engine import apply_sun_moon_article, is_sun_letter
from Arabic_engine.brain.skills.pragmatics_engine import validate_greeting_turn
from Arabic_engine.brain.analysis.vso_svo_agreement_analyzer import VsoSvoAgreementAnalyzer
from Arabic_engine.brain.analysis.deflected_agreement_analyzer import DeflectedAgreementAnalyzer
from Arabic_engine.brain.analysis.idafa_construct_analyzer import IdafaConstructAnalyzer
from Arabic_engine.brain.sub_ais.syntax_sub_ai import ArabicSyntaxSubAI
from Arabic_engine.brain.sub_ais.phonology_sub_ai import ArabicPhonologySubAI
from Arabic_engine.brain.sub_ais.pragmatic_sub_ai import ArabicPragmaticSubAI
from Arabic_engine.brain.sub_ais.editorial_sub_ai import ArabicEditorialSubAI
from Arabic_engine.brain.task.grammar_check import ArabicGrammarChecker
from Arabic_engine.brain.task.email_pipeline import ArabicEmailPipeline
from Arabic_engine.brain.task.composition_pipeline import ArabicCompositionPipeline


def test_amsv_physical_layout_and_magic():
    """Test 1: Verify 64-byte AMSV layout, magic header 0x41524142 ('ARAB'), and sub-AI active bytes."""
    bridge = ArabicMatrixBridge()
    buf = bridge.buffer
    assert len(buf) == ARABIC_AMSV_SIZE == 64
    
    magic = struct.unpack_from("<I", buf, 0)[0]
    assert magic == ARABIC_AMSV_MAGIC == 0x41524142
    
    version = struct.unpack_from("<I", buf, 4)[0]
    assert version == 0x00010000
    
    # Check Sub-AI active bytes (52..55)
    assert buf[52] == 1 # Syntax Sub-AI
    assert buf[53] == 1 # Phonology Sub-AI
    assert buf[54] == 1 # Pragmatic Sub-AI
    assert buf[55] == 1 # Editorial Sub-AI


def test_zero_bridge_memory_synchronization():
    """Test 2: Adherence to The Zero-Bridge Synchronous Memory Rule with zero serialization."""
    raw_memory = bytearray(64)
    bridge = ArabicMatrixBridge(raw_memory)
    assert bridge.buffer is raw_memory # Exact physical address identity
    
    bridge.update_metrics(
        token_count=15,
        sentence_count=2,
        clause_type_mask=0x0001, # VSO
        syntax_flags=0x07,
        case_error_flags=0x00,
        phonology_flags=0x05,
        morphology_flags=0x11,
        root_class=1, # ktb
        pragmatic_flags=0x02,
        confidence=0.98
    )
    
    metrics = bridge.read_metrics()
    assert metrics["is_magic_valid"] is True
    assert metrics["token_count"] == 15
    assert metrics["sentence_count"] == 2
    assert metrics["root_class"] == 1
    assert metrics["confidence"] == 0.98
    assert raw_memory[22] == 1 # Physical byte directly updated in-place


def test_root_pattern_derivation_forms_i_to_x():
    """Test 3: Non-concatenative root-and-pattern derivation across Forms I..X."""
    # Root ktb Form I
    ktb_i = derive_form("ktb", "I")
    assert ktb_i["past"] == "kataba"
    assert ktb_i["present"] == "yaktubu"
    assert ktb_i["active_participle"] == "kātib"
    assert ktb_i["passive_participle"] == "maktūb"
    
    # Root ktb Form II (causative / intensive)
    ktb_ii = derive_form("ktb", "II")
    assert ktb_ii["past"] == "kattaba"
    assert ktb_ii["present"] == "yukattibu"
    
    # Root slm Form IV (causative / transitive)
    slm_iv = derive_form("slm", "IV")
    assert slm_iv["past"] == "aslama"
    assert slm_iv["present"] == "yuslimu"
    
    # Root slm Form X (requestive / reflexive)
    slm_x = derive_form("slm", "X")
    assert slm_x["past"] == "istaslama"
    assert slm_x["present"] == "yastaslimu"


def test_broken_plural_resolution_and_animacy():
    """Test 4: Broken plural resolution and human vs non-human animacy discrimination."""
    # Non-human plurals (must trigger deflected agreement)
    res_kitab = analyze_plural("kutub")
    assert res_kitab["is_plural"] is True
    assert res_kitab["singular"] == "kitab"
    assert res_kitab["is_human"] is False
    assert res_kitab["requires_deflected_agreement"] is True
    
    res_qalam = analyze_plural("aqlam")
    assert res_qalam["is_plural"] is True
    assert res_qalam["is_human"] is False
    assert res_qalam["requires_deflected_agreement"] is True
    
    # Human plurals (must NOT trigger deflected agreement)
    res_walad = analyze_plural("awlad")
    assert res_walad["is_plural"] is True
    assert res_walad["is_human"] is True
    assert res_walad["requires_deflected_agreement"] is False
    
    res_rajul = analyze_plural("rijal")
    assert res_rajul["is_plural"] is True
    assert res_rajul["is_human"] is True
    assert res_rajul["requires_deflected_agreement"] is False


def test_vso_singular_verb_agreement_rule():
    """Test 5: VSO order enforces singular verb before post-verbal overt subjects."""
    # Valid: Singular verb 'kataba' preceding plural subject 'al-awlad'
    res_valid = validate_vso_agreement("kataba", "al-awlad")
    assert res_valid["valid"] is True
    
    # Invalid: Plural verb 'katabu' preceding post-verbal subject 'al-awlad'
    res_invalid = validate_vso_agreement("katabu", "al-awlad")
    assert res_invalid["valid"] is False
    assert "VSO order violation" in res_invalid["error"]


def test_svo_full_concord_rule():
    """Test 6: SVO order mandates full number/gender concord for human subjects."""
    # Valid: Human plural subject 'al-awlad' followed by plural verb 'katabu'
    res_valid = validate_svo_agreement("al-awlad", "katabu")
    assert res_valid["valid"] is True
    
    # Invalid: Human plural subject 'al-awlad' followed by singular verb 'kataba'
    res_invalid = validate_svo_agreement("al-awlad", "kataba")
    assert res_invalid["valid"] is False
    assert "Human plural" in res_invalid["error"]


def test_deflected_agreement_non_human_plural():
    """Test 7: Deflected Agreement mandates Feminine Singular concord for non-human plurals."""
    # Valid: Non-human plural 'al-kutub' with feminine singular adjective 'al-jadida'
    res_valid = validate_noun_adjective_agreement("al-kutub", "al-jadida")
    assert res_valid["valid"] is True
    
    # Invalid: Non-human plural 'al-kutub' with human plural demonstrative 'ha'ula'i'
    res_dem = validate_noun_adjective_agreement("al-kutub", "ha'ula'i")
    assert res_dem["valid"] is False
    assert "strictly for human plurals" in res_dem["error"]
    
    # Invalid: Non-human plural 'al-kutub' with masculine adjective 'al-jadid'
    res_masc = validate_noun_adjective_agreement("al-kutub", "al-jadid")
    assert res_masc["valid"] is False
    assert "Deflected agreement violation" in res_masc["error"]


def test_idafa_construct_state_rules():
    """Test 8: Idafa construct constraints (Mudaf lacks al- and tanwin)."""
    # Valid: Mudaf lacks al- and tanwin
    res_valid = validate_idafa("kitab", "ar-rajul")
    assert res_valid["valid"] is True
    assert len(res_valid["violations"]) == 0
    
    # Invalid: Mudaf has illegal definite article 'al-'
    res_al = validate_idafa("al-kitab", "ar-rajul")
    assert res_al["valid"] is False
    assert any(v["rule"] == "mudaf_no_al" for v in res_al["violations"])
    
    # Invalid: Mudaf has illegal tanwin 'kitabun'
    res_tanwin = validate_idafa("kitabun", "ar-rajul")
    assert res_tanwin["valid"] is False
    assert any(v["rule"] == "mudaf_no_tanwin" for v in res_tanwin["violations"])


def test_sun_and_moon_letter_assimilation():
    """Test 9: Coronal assimilation for Sun letters and preservation for Moon letters."""
    # Sun letters (coronal: sh, r, s, t, etc.)
    assert apply_sun_moon_article("shams") == "ash-shams"
    assert apply_sun_moon_article("rajul") == "ar-rajul"
    assert apply_sun_moon_article("nūr") == "an-nūr" or apply_sun_moon_article("nur") == "an-nur"
    
    # Moon letters (non-coronal: q, k, b, m, etc.)
    assert apply_sun_moon_article("qamar") == "al-qamar"
    assert apply_sun_moon_article("kitab") == "al-kitab"
    assert apply_sun_moon_article("bab") == "al-bab"


def test_pragmatic_greetings_and_social_etiquette():
    """Test 10: Islamic greeting adjacency pairs and clash detection."""
    # Islamic Salam pair
    res_salam = validate_greeting_turn("As-salamu 'alaykum wa-rahmatullah", "Wa-'alaykum as-salam wa-rahmatullah")
    assert res_salam["valid"] is True
    assert res_salam["protocol"] == "islamic_salam"
    
    # Diurnal morning greeting
    res_sabah = validate_greeting_turn("Sabah al-khayr", "Sabah an-nur")
    assert res_sabah["valid"] is True
    assert res_sabah["protocol"] == "sabah_greeting"
    
    # Clash: Islamic Salam answered with morning greeting
    res_clash = validate_greeting_turn("As-salamu 'alaykum", "Sabah an-nur")
    assert res_clash["valid"] is False


def test_sub_ais_direct_amsv_execution():
    """Test 11: Direct physical AMSV buffer modification by the 4 dedicated Sub-AIs."""
    buf = bytearray(64)
    bridge = ArabicMatrixBridge(buf)
    
    syntax_ai = ArabicSyntaxSubAI()
    phonology_ai = ArabicPhonologySubAI()
    pragmatic_ai = ArabicPragmaticSubAI()
    editorial_ai = ArabicEditorialSubAI()
    
    text = "Kataba al-awlad ad-dars."
    
    s_res = syntax_ai.process(text, buf)
    assert s_res["status"] == "success"
    assert buf[52] == 1 # Syntax Sub-AI active
    assert buf[18] & 0x01 # VSO valid bit
    
    p_res = phonology_ai.process(text, buf)
    assert p_res["status"] == "success"
    assert buf[53] == 1 # Phonology Sub-AI active
    
    pr_res = pragmatic_ai.process(text, buf)
    assert pr_res["status"] == "success"
    assert buf[54] == 1 # Pragmatic Sub-AI active
    assert buf[22] == 1 # Root ktb identified
    assert buf[23] & 0x02 # Pure MSA flag
    
    ed_res = editorial_ai.process(text, buf)
    assert ed_res["status"] == "success"
    assert buf[55] == 1 # Editorial Sub-AI active
    assert ed_res["is_valid"] is True
    
    conf = struct.unpack_from("<f", buf, 24)[0]
    assert conf >= 0.95


def test_orchestrator_process_text_pipeline():
    """Test 12: Master Orchestrator end-to-end processing and AMSV state validation."""
    orchestrator = ArabicEngineOrchestrator()
    result = orchestrator.process_text("Kataba al-awlad ad-dars.")
    
    assert result["token_count"] == 4 # 3 words + punctuation
    assert result["sentence_count"] == 1
    assert result["is_valid"] is True
    assert result["amsv_state"]["is_magic_valid"] is True
    assert result["amsv_state"]["sub_ai_statuses"]["syntax"] is True
    assert result["amsv_state"]["sub_ai_statuses"]["phonology"] is True
    assert result["amsv_state"]["sub_ai_statuses"]["pragmatic"] is True
    assert result["amsv_state"]["sub_ai_statuses"]["editorial"] is True


def test_email_and_composition_task_pipelines():
    """Test 13: Diplomatic email composition, audit, and dialect adaptation."""
    orchestrator = ArabicEngineOrchestrator()
    
    # Formal diplomatic email
    email = orchestrator.compose_email(
        form="formal",
        recipient_name="Tariq Hasan",
        recipient_title="المدير العام",
        body="يسرنا تقديم التقرير الفني النهائي لمشروع سولو روك.",
        sender_name="المهندسة فاطمة",
        organization="Solo Rock"
    )
    assert "سعادة المدير العام / Tariq Hasan المحترم،" in email
    assert "تحية طيبة وبعد،" in email
    assert "وتفضلوا بقبول فائق الاحترام والتقدير،" in email
    
    audit = orchestrator.audit_email(email)
    assert audit["passed"] is True
    assert audit["is_pure_msa"] is True
    
    # Dialect adaptation: Colloquial -> MSA
    dialect_text = "Hada kwayyis biddi al-an."
    msa_text = orchestrator.adapt_dialect(dialect_text, target="msa")
    assert "jayyid" in msa_text
    assert "uridu" in msa_text
    
    # Style analysis with classical rhetorical idiom
    rhetorical_text = "Hada al-mashru' fi ghayati al-ahammiyya lin-najah."
    style_res = orchestrator.analyze_style(rhetorical_text)
    assert style_res["style"] == "classical_rhetorical"
    assert "fi ghayati al-ahammiyya" in style_res["idioms_found"]
