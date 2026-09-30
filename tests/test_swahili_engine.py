"""
Swahili Engine — Comprehensive Test Suite
Validates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
Six-Language Matrix, and Zero-Bridge Synchronous Memory State Vector (AMSV: 0x53574148).
"""

import pytest
import struct
from Swahili_engine import SwahiliEngineOrchestrator, SwahiliMatrixBridge, SWAHILI_AMSV_MAGIC, SWAHILI_AMSV_SIZE
from Swahili_engine.brain.skills.noun_class_engine import identify_noun_class
from Swahili_engine.brain.skills.concord_engine import generate_concordial_np, validate_concord
from Swahili_engine.brain.analysis.concord_agreement_analyzer import ConcordAgreementAnalyzer
from Swahili_engine.brain.skills.verbal_template_engine import synthesize_verb, parse_verbal_template
from Swahili_engine.brain.skills.monosyllabic_verb_engine import check_monosyllabic_ku
from Swahili_engine.brain.skills.verbal_extensions_engine import derive_extension
from Swahili_engine.brain.skills.pragmatics_engine import validate_greeting_turn
from Swahili_engine.brain.sub_ais.syntax_sub_ai import SwahiliSyntaxSubAI
from Swahili_engine.brain.sub_ais.phonology_sub_ai import SwahiliPhonologySubAI
from Swahili_engine.brain.sub_ais.pragmatic_sub_ai import SwahiliPragmaticSubAI
from Swahili_engine.brain.sub_ais.editorial_sub_ai import SwahiliEditorialSubAI
from Swahili_engine.brain.task.grammar_check import SwahiliGrammarChecker
from Swahili_engine.brain.task.email_pipeline import SwahiliEmailPipeline
from Swahili_engine.brain.task.composition_pipeline import SwahiliCompositionPipeline


def test_amsv_physical_layout_and_magic():
    """Test 1: Verify 64-byte AMSV layout, magic header 0x53574148 ('SWAH'), and sub-AI active bytes."""
    bridge = SwahiliMatrixBridge()
    buf = bridge.buffer
    assert len(buf) == SWAHILI_AMSV_SIZE == 64
    
    magic = struct.unpack_from("<I", buf, 0)[0]
    assert magic == SWAHILI_AMSV_MAGIC == 0x53574148
    
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
    bridge = SwahiliMatrixBridge(raw_memory)
    assert bridge.buffer is raw_memory # Exact physical address identity
    
    bridge.update_metrics(
        token_count=12,
        sentence_count=2,
        clause_type_mask=0x0001,
        syntax_flags=0x05,
        concord_error_flags=0x00,
        phonology_flags=0x02,
        verbal_extension_flags=0x01,
        noun_class_head=7,
        pragmatic_flags=0x01,
        confidence=0.95
    )
    
    metrics = bridge.read_metrics()
    assert metrics["is_magic_valid"] is True
    assert metrics["token_count"] == 12
    assert metrics["sentence_count"] == 2
    assert metrics["noun_class_head"] == 7
    assert metrics["confidence"] == 0.95
    assert raw_memory[22] == 7 # Physical byte directly updated


def test_noun_class_identification():
    """Test 3: Noun class (Ngeli 1..18) identification across Bantu genders."""
    assert identify_noun_class("mtoto") == 1
    assert identify_noun_class("watoto") == 2
    assert identify_noun_class("mti") == 3
    assert identify_noun_class("miti") == 4
    assert identify_noun_class("jina") == 5
    assert identify_noun_class("majina") == 6
    assert identify_noun_class("kitabu") == 7
    assert identify_noun_class("vitabu") == 8
    assert identify_noun_class("nyumba") == 9
    assert identify_noun_class("uhuru") == 11
    assert identify_noun_class("kusoma") == 15


def test_concordial_agreement_generation():
    """Test 4: Modifier hierarchy and alliterative concord generation."""
    # Class 7
    np7 = generate_concordial_np("kitabu", dem_type="proximal", adj_stem="zuri")
    assert np7 == "kitabu hiki kizuri"
    
    # Class 8
    np8 = generate_concordial_np("vitabu", dem_type="proximal", adj_stem="zuri")
    assert np8 == "vitabu hivi vizuri"
    
    # Class 1
    np1 = generate_concordial_np("mtoto", dem_type="proximal", adj_stem="zuri")
    assert np1 == "mtoto huyu mzuri"
    
    # Class 2
    np2 = generate_concordial_np("watoto", dem_type="proximal", adj_stem="zuri")
    assert np2 == "watoto hawa wazuri"


def test_concordial_agreement_analyzer_and_violations():
    """Test 5: Concord Agreement Analyzer identifies valid agreement and catches cross-class violations."""
    analyzer = ConcordAgreementAnalyzer()
    
    # Valid concord
    valid_res = analyzer.analyze("Watoto wazuri wanasoma vitabu.")
    assert valid_res["is_valid"] is True
    assert len(valid_res["violations"]) == 0
    
    # Invalid concord (Class 2 noun 'watoto' with Class 7 adjective 'kizuri')
    invalid_res = analyzer.analyze("Watoto kizuri wanasoma vitabu.")
    assert invalid_res["is_valid"] is False
    assert len(invalid_res["violations"]) > 0


def test_verbal_template_synthesis_and_parsing():
    """Test 6: 8-slot agglutinative finite verb synthesis and decomposition."""
    # Affirmative present
    v_pres = synthesize_verb(subject="cl2", root="soma", tense="present")
    assert v_pres == "wanasoma"
    
    # Affirmative past
    v_past = synthesize_verb(subject="cl2", root="soma", tense="past")
    assert v_past == "walisoma"
    
    # Affirmative future
    v_fut = synthesize_verb(subject="cl2", root="soma", tense="future")
    assert v_fut == "watasoma"
    
    # Negative present (FV shifts to -i, tense prefix drops)
    v_neg = synthesize_verb(subject="cl2", root="soma", tense="present", negative=True)
    assert v_neg == "hawasomi"
    
    # Template parsing
    parsed = parse_verbal_template("wanasoma")
    assert parsed["sp"] == "wa"
    assert parsed["tam"] == "na"
    assert parsed["root"] == "soma"
    assert parsed["fv"] == "a"


def test_monosyllabic_verb_ku_preservation():
    """Test 7: Monosyllabic verb dummy 'ku-' retention and drop conditions."""
    # Affirmative present: retains ku- to maintain penultimate stress
    res1 = check_monosyllabic_ku("anakula")
    assert res1["is_monosyllabic"] is True
    assert res1["retains_ku"] is True
    
    # With object prefix: drops ku- because OP adds a syllable
    res2 = check_monosyllabic_ku("alikila")
    assert res2["is_monosyllabic"] is True
    assert res2["retains_ku"] is False
    
    # Negative present: drops ku-
    res3 = check_monosyllabic_ku("hali")
    assert res3["is_monosyllabic"] is True
    assert res3["retains_ku"] is False


def test_verbal_extensions_vowel_harmony():
    """Test 8: Verbal extension derivation obeying Bantu height vowel harmony (/a, i, u/ vs /e, o/)."""
    # Applicative: -ia after high/low vowels, -ea after mid vowels
    assert derive_extension("kupika", "applicative") == "kupikia"  # 'i' -> -ia
    assert derive_extension("kusoma", "applicative") == "kusomea"  # 'o' -> -ea
    
    # Causative: -isha after high/low, -esha after mid
    assert derive_extension("kufika", "causative") == "kufikisha"  # 'i' -> -isha
    assert derive_extension("kuona", "causative") == "kuonesha"   # 'o' -> -esha
    
    # Passive: -wa
    assert derive_extension("kupika", "passive") == "kupikwa"
    
    # Reciprocal: -ana
    assert derive_extension("kupenda", "reciprocal") == "kupendana"


def test_pragmatic_greetings_and_social_deixis():
    """Test 9: Swahili greetings protocol, deference deixis, and clash detection."""
    # Shikamoo / Marahaba
    res1 = validate_greeting_turn("Shikamoo mwalimu", "Marahaba mtoto wangu")
    assert res1["valid"] is True
    assert res1["protocol"] == "shikamoo_marahaba"
    
    # Hujambo / Sijambo
    res2 = validate_greeting_turn("Hujambo rafiki", "Sijambo")
    assert res2["valid"] is True
    assert res2["protocol"] == "jambo_salutation"
    
    # Clash: Shikamoo responded to with informal greeting
    res3 = validate_greeting_turn("Shikamoo", "Mambo")
    assert res3["valid"] is False


def test_sub_ais_direct_amsv_execution():
    """Test 10: Direct physical AMSV buffer modification by the 4 dedicated Sub-AIs."""
    buf = bytearray(64)
    bridge = SwahiliMatrixBridge(buf)
    
    syntax_ai = SwahiliSyntaxSubAI()
    phonology_ai = SwahiliPhonologySubAI()
    pragmatic_ai = SwahiliPragmaticSubAI()
    editorial_ai = SwahiliEditorialSubAI()
    
    text = "Watoto wanakula chakula."
    
    s_res = syntax_ai.process(text, buf)
    assert s_res["status"] == "success"
    assert buf[52] == 1 # Syntax Sub-AI active
    assert buf[18] & 0x01 # SVO order bit
    
    p_res = phonology_ai.process(text, buf)
    assert p_res["status"] == "success"
    assert buf[53] == 1 # Phonology Sub-AI active
    assert buf[20] & 0x01 # Monosyllabic ku- active in 'wanakula'
    
    pr_res = pragmatic_ai.process(text, buf)
    assert pr_res["status"] == "success"
    assert buf[54] == 1 # Pragmatic Sub-AI active
    assert buf[22] == 2 # Head noun 'Watoto' is Class 2
    
    ed_res = editorial_ai.process(text, buf)
    assert ed_res["status"] == "success"
    assert buf[55] == 1 # Editorial Sub-AI active
    assert ed_res["is_valid"] is True
    
    conf = struct.unpack_from("<f", buf, 24)[0]
    assert conf >= 0.9


def test_orchestrator_process_text_pipeline():
    """Test 11: Master Orchestrator end-to-end processing and AMSV state validation."""
    orchestrator = SwahiliEngineOrchestrator()
    result = orchestrator.process_text("Watoto wanasoma vitabu vizuri.")
    
    assert result["token_count"] == 5  # 4 words + terminal punctuation
    assert result["sentence_count"] == 1

    assert result["is_valid"] is True
    assert result["amsv_state"]["is_magic_valid"] is True
    assert result["amsv_state"]["sub_ai_statuses"]["syntax"] is True
    assert result["amsv_state"]["sub_ai_statuses"]["phonology"] is True
    assert result["amsv_state"]["sub_ai_statuses"]["pragmatic"] is True
    assert result["amsv_state"]["sub_ai_statuses"]["editorial"] is True


def test_grammar_checker_task_pipeline():
    """Test 12: Comprehensive SwahiliGrammarChecker task pipeline."""
    checker = SwahiliGrammarChecker()
    
    # Valid sentence
    res_valid = checker.check("Watoto wazuri wanasoma vitabu.")
    assert res_valid["passed"] is True
    assert res_valid["total_errors"] == 0
    assert res_valid["confidence_score"] == 1.0
    
    # Concord error sentence (Watoto [Cl 2] with kizuri [Cl 7])
    res_invalid = checker.check("Watoto kizuri wanasoma vitabu.")
    assert res_invalid["passed"] is False
    assert res_invalid["total_errors"] > 0
    assert len(res_invalid["concord_errors"]) > 0


def test_email_and_composition_task_pipelines():
    """Test 13: Email and composition pipelines with Methali and Sheng dialect adaptation."""
    orchestrator = SwahiliEngineOrchestrator()
    
    # Formal email composition & audit
    email = orchestrator.compose_email(
        form="formal",
        recipient_name="Amani Juma",
        recipient_title="Mkurugenzi Mkuu",
        body="Tunapenda kuwasilisha ripoti ya mradi wa Solo Rock.",
        sender_name="Mhandisi Neema",
        organization="Solo Rock"
    )
    assert "Kwa Mheshimiwa Mkurugenzi Mkuu Amani Juma," in email
    assert "Wasalaam," in email
    
    audit = orchestrator.audit_email(email)
    assert audit["passed"] is True
    assert audit["is_formal"] is True
    
    # Dialect adaptation: Sheng -> Standard Kiunguja
    sheng_text = "Nahitaji chapaa nyingi morio wangu."
    std_text = orchestrator.adapt_dialect(sheng_text, target="standard")
    assert "pesa" in std_text
    assert "rafiki" in std_text
    
    # Style analysis with Methali proverb
    proverb_text = "Mwanangu kumbuka kwamba haraka haraka haina baraka maishani."
    style_res = orchestrator.analyze_style(proverb_text)
    assert style_res["style"] == "proverbial_bantu"
    assert "haraka haraka haina baraka" in style_res["proverbs"]
