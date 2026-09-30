"""
Italian Engine — Comprehensive Test Suite
Validates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
Six-Language Matrix, and Zero-Bridge Synchronous Memory State Vector (AMSV: 0x4954414C).
"""

import pytest
import struct
from Italian_engine import (
    ItalianEngineOrchestrator,
    ItalianMatrixBridge,
    ITALIAN_AMSV_MAGIC,
    ITALIAN_AMSV_SIZE
)
from Italian_engine.brain.skills.tokenization import tokenize_words, split_sentences, split_elision
from Italian_engine.brain.skills.verb_conjugator import conjugate_verb
from Italian_engine.brain.skills.auxiliary_selector import (
    select_auxiliary,
    compute_participle_concord,
    validate_passato_prossimo
)
from Italian_engine.brain.skills.clitic_engine import combine_clitics, attach_enclitic
from Italian_engine.brain.skills.articulated_prep_engine import fuse_preposition, select_article
from Italian_engine.brain.skills.subjunctive_engine import detect_subjunctive_triggers
from Italian_engine.brain.skills.pragmatics_engine import classify_register, format_salutation, format_closing
from Italian_engine.brain.skills.generation import generate_sentence
from Italian_engine.brain.analysis.auxiliary_agreement_analyzer import AuxiliaryAgreementAnalyzer
from Italian_engine.brain.analysis.clitic_placement_analyzer import CliticPlacementAnalyzer
from Italian_engine.brain.analysis.subjunctive_concord_analyzer import SubjunctiveConcordAnalyzer
from Italian_engine.brain.sub_ais.syntax_sub_ai import ItalianSyntaxSubAI
from Italian_engine.brain.sub_ais.phonology_sub_ai import ItalianPhonologySubAI
from Italian_engine.brain.sub_ais.pragmatic_sub_ai import ItalianPragmaticSubAI
from Italian_engine.brain.sub_ais.editorial_sub_ai import ItalianEditorialSubAI
from Italian_engine.brain.task.grammar_check import ItalianGrammarChecker
from Italian_engine.brain.task.email_pipeline import ItalianEmailPipeline
from Italian_engine.brain.task.composition_pipeline import ItalianCompositionPipeline


def test_amsv_physical_layout_and_magic():
    """Test 1: Verify 64-byte AMSV layout, magic header 0x4954414C ('ITAL'), and sub-AI active bytes."""
    bridge = ItalianMatrixBridge()
    buf = bridge.buffer
    assert len(buf) == ITALIAN_AMSV_SIZE == 64
    
    magic = struct.unpack_from("<I", buf, 0)[0]
    assert magic == ITALIAN_AMSV_MAGIC == 0x4954414C
    
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
    bridge = ItalianMatrixBridge(raw_memory)
    assert bridge.buffer is raw_memory # Exact physical address identity
    
    bridge.update_metrics(
        token_count=12,
        sentence_count=2,
        clause_type_mask=0x0001,
        syntax_flags=0x05,
        auxiliary_flags=0x02,
        phonology_flags=0x01,
        morphology_flags=0x08,
        register_tier=1, # Formal Lei
        pragmatic_flags=0x03,
        confidence=0.98
    )
    
    metrics = bridge.read_metrics()
    assert metrics["is_magic_valid"] is True
    assert metrics["token_count"] == 12
    assert metrics["sentence_count"] == 2
    assert metrics["register_tier"] == 1
    assert metrics["confidence"] == 0.98
    assert raw_memory[22] == 1 # Physical byte directly updated in-place


def test_tokenization_and_elision_splitting():
    """Test 3: Tokenization preserving elisions, apostrophes, and abbreviation boundaries."""
    text = "L'amico ha detto che c'è un'altra possibilità. Dott. Rossi è d'accordo."
    tokens = tokenize_words(text)
    assert "L'amico" in tokens or ("L'" in tokens and "amico" in tokens)
    assert "c'è" in tokens or ("c'" in tokens and "è" in tokens)
    assert "d'accordo" in tokens or ("d'" in tokens and "accordo" in tokens)
    
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert "Dott. Rossi" in sentences[1]
    
    elided = split_elision("l'amica")
    assert elided == ["l'", "amica"]


def test_verb_conjugation_regular_and_irregular():
    """Test 4: Verb conjugation across regular (-are, -ere, -ire) and irregular paradigms."""
    # Regular 1st conj: parlare
    assert conjugate_verb("parlare", "presente", "1sg") == "parlo"
    assert conjugate_verb("parlare", "futuro", "3sg") == "parlerà"
    assert conjugate_verb("parlare", "participio_passato") == "parlato"
    
    # Regular 2nd conj: credere
    assert conjugate_verb("credere", "presente", "2sg") == "credi"
    assert conjugate_verb("credere", "imperfetto", "1pl") == "credevamo"
    
    # Regular 3rd conj: dormire
    assert conjugate_verb("dormire", "presente", "3pl") == "dormono"
    
    # Irregulars: essere, avere, andare, fare, dire, venire
    assert conjugate_verb("essere", "presente", "1sg") == "sono"
    assert conjugate_verb("essere", "presente", "3sg") == "è"
    assert conjugate_verb("avere", "presente", "1sg") == "ho"
    assert conjugate_verb("andare", "presente", "1sg") == "vado"
    assert conjugate_verb("fare", "presente", "1sg") == "faccio"
    assert conjugate_verb("dire", "presente", "1sg") == "dico"
    assert conjugate_verb("venire", "presente", "3pl") == "vengono"


def test_auxiliary_selection_essere_vs_avere():
    """Test 5: Auxiliary selection invariants (unaccusatives -> essere, transitives -> avere)."""
    # Motion and unaccusative change of state: essere
    assert select_auxiliary("andare") == "essere"
    assert select_auxiliary("venire") == "essere"
    assert select_auxiliary("partire") == "essere"
    assert select_auxiliary("arrivare") == "essere"
    assert select_auxiliary("uscire") == "essere"
    assert select_auxiliary("nascere") == "essere"
    
    # Transitive / unergative: avere
    assert select_auxiliary("leggere") == "avere"
    assert select_auxiliary("mangiare") == "avere"
    assert select_auxiliary("scrivere") == "avere"
    assert select_auxiliary("lavorare") == "avere"
    
    # Reflexive and passive take essere
    assert select_auxiliary("lavare", is_reflexive=True) == "essere"
    assert select_auxiliary("costruire", is_passive=True) == "essere"


def test_past_participle_gender_number_concord():
    """Test 6: Past participle concord with essere vs invariability with avere."""
    # With essere: concord is mandatory
    assert compute_participle_concord("andato", "essere", subject_gender="m", subject_number="sg") == "andato"
    assert compute_participle_concord("andato", "essere", subject_gender="f", subject_number="sg") == "andata"
    assert compute_participle_concord("andato", "essere", subject_gender="m", subject_number="pl") == "andati"
    assert compute_participle_concord("andato", "essere", subject_gender="f", subject_number="pl") == "andate"
    
    # With avere: invariable masculine singular -o by default
    assert compute_participle_concord("mangiato", "avere", subject_gender="f", subject_number="sg") == "mangiato"
    
    # Diagnostic validation
    res_valid = validate_passato_prossimo("è", "andata", "andare", subject_gender="f", subject_number="sg")
    assert res_valid["valid"] is True
    
    # Invalid: wrong auxiliary (ha andata)
    res_wrong_aux = validate_passato_prossimo("ha", "andato", "andare")
    assert res_wrong_aux["valid"] is False
    assert any(v["rule"] == "auxiliary_choice" for v in res_wrong_aux["violations"])
    
    # Invalid: discordant participle with essere (lei è andato)
    res_bad_concord = validate_passato_prossimo("è", "andato", "andare", subject_gender="f", subject_number="sg")
    assert res_bad_concord["valid"] is False
    assert any(v["rule"] == "participle_concord" for v in res_bad_concord["violations"])


def test_clitic_clusters_and_vowel_shifts():
    """Test 7: Clitic cluster fusion and vowel shift (-i -> -e)."""
    # Indirect mi/ti/ci/vi/si + direct lo/la/li/le/ne
    assert combine_clitics("mi", "lo") == "me lo"
    assert combine_clitics("ti", "la") == "te la"
    assert combine_clitics("ci", "ne") == "ce ne"
    assert combine_clitics("si", "lo") == "se lo"
    
    # 3rd person indirect gli/le + lo/la/li/le/ne -> glielo/gliela...
    assert combine_clitics("gli", "lo") == "glielo"
    assert combine_clitics("le", "lo") == "glielo"
    assert combine_clitics("gli", "ne") == "gliene"
    
    # Cognitive Analyzer catches unshifted chains
    analyzer = CliticPlacementAnalyzer()
    res_bad = analyzer.analyze("Lui mi lo dice sempre.")
    assert res_bad["is_valid"] is False
    assert any(v["rule"] == "clitic_cluster_vowel_shift" for v in res_bad["violations"])
    
    res_good = analyzer.analyze("Lui me lo dice sempre.")
    assert res_good["is_valid"] is True


def test_imperative_and_infinitive_enclisis():
    """Test 8: Enclisis on infinitives and consonant doubling on monosyllabic imperatives."""
    # Infinitive drops terminal -e
    assert attach_enclitic("parlare", "lo") == "parlarlo"
    assert attach_enclitic("vedere", "la") == "vederla"
    assert attach_enclitic("sentire", "ci") == "sentirci"
    
    # Monosyllabic imperative doubling
    assert attach_enclitic("di", "mi") == "dimmi"
    assert attach_enclitic("da", "mi") == "dammi"
    assert attach_enclitic("fa", "lo") == "fallo"
    assert attach_enclitic("da", "lo") == "dallo"


def test_articulated_prepositions():
    """Test 9: Preposizioni articolate contractions and article selection."""
    # Fusions
    assert fuse_preposition("di", "il") == "del"
    assert fuse_preposition("di", "la") == "della"
    assert fuse_preposition("a", "il") == "al"
    assert fuse_preposition("a", "gli") == "agli"
    assert fuse_preposition("da", "lo") == "dallo"
    assert fuse_preposition("in", "la") == "nella"
    assert fuse_preposition("su", "i") == "sui"
    
    # Article selection based on onset
    assert select_article("libro", gender="m", number="sg") == "il"
    assert select_article("studente", gender="m", number="sg") == "lo"
    assert select_article("amico", gender="m", number="sg") == "l'"
    assert select_article("studenti", gender="m", number="pl") == "gli"
    assert select_article("casa", gender="f", number="sg") == "la"


def test_subjunctive_triggers_and_mood_audit():
    """Test 10: Subjunctive trigger detection and subordinate mood checking."""
    # Trigger detection
    res1 = detect_subjunctive_triggers("Credo che tu abbia ragione.")
    assert res1["requires_subjunctive"] is True
    
    res2 = detect_subjunctive_triggers("Benché piova, usciamo.")
    assert res2["requires_subjunctive"] is True
    
    # Indicative error detection
    sub_analyzer = SubjunctiveConcordAnalyzer()
    res_err = sub_analyzer.analyze("Voglio che tu vieni a Roma.")
    assert res_err["is_valid"] is False
    assert any(v["rule"] == "subjunctive_mood_required" for v in res_err["violations"])
    
    res_corr = sub_analyzer.analyze("Voglio che tu venga a Roma.")
    assert res_corr["is_valid"] is True


def test_pragmatic_deference_and_address_tiers():
    """Test 11: Register classification (tu vs Lei) and formal epistolary formulas."""
    formal_text = "Gentile Dottor Rossi, Le scrivo per ringraziarLa della Sua cortese attenzione. Cordiali saluti."
    reg_formal = classify_register(formal_text)
    assert reg_formal["register"] == "formal"
    
    informal_text = "Ciao Marco, ti scrivo per farti sapere le novità. A presto!"
    reg_informal = classify_register(informal_text)
    assert reg_informal["register"] == "informal"
    
    # Formal salutation generator
    assert format_salutation("Dottore", "Bianchi", formal=True) == "Gentile Dottor Bianchi,"
    assert format_salutation("Professore", "Verdi", formal=True) == "Chiarissimo Professor Verdi,"
    assert format_salutation("", "Luca", formal=False) == "Caro Luca,"


def test_sub_ais_direct_amsv_execution():
    """Test 12: Direct physical AMSV buffer modification by the 4 dedicated Sub-AIs."""
    buf = bytearray(64)
    bridge = ItalianMatrixBridge(buf)
    
    syntax_ai = ItalianSyntaxSubAI()
    phonology_ai = ItalianPhonologySubAI()
    pragmatic_ai = ItalianPragmaticSubAI()
    editorial_ai = ItalianEditorialSubAI()
    
    text = "Marco è andato a Roma e me lo ha detto."
    
    s_res = syntax_ai.process(text, buf)
    assert s_res["status"] == "success"
    assert buf[52] == 1 # Syntax Sub-AI active
    assert buf[18] & 0x01 # SVO valid
    assert buf[18] & 0x04 # Clitic cluster verified
    
    p_res = phonology_ai.process(text, buf)
    assert p_res["status"] == "success"
    assert buf[53] == 1 # Phonology Sub-AI active
    
    pr_res = pragmatic_ai.process(text, buf)
    assert pr_res["status"] == "success"
    assert buf[54] == 1 # Pragmatic Sub-AI active
    
    ed_res = editorial_ai.process(text, buf)
    assert ed_res["status"] == "success"
    assert buf[55] == 1 # Editorial Sub-AI active
    assert ed_res["is_valid"] is True
    
    conf = struct.unpack_from("<f", buf, 24)[0]
    assert conf >= 0.95


def test_orchestrator_end_to_end_and_task_pipelines():
    """Test 13: Master Orchestrator end-to-end processing, email pipeline, and dialect adaptation."""
    orchestrator = ItalianEngineOrchestrator()
    
    # 1. Process text
    res = orchestrator.process_text("Chiara è andata a Milano.")
    assert res["token_count"] == 6 # Chiara + è + andata + a + Milano + .
    assert res["sentence_count"] == 1
    assert res["is_valid"] is True
    assert res["amsv_state"]["is_magic_valid"] is True
    assert res["amsv_state"]["sub_ai_statuses"]["syntax"] is True
    assert res["amsv_state"]["sub_ai_statuses"]["editorial"] is True
    
    # 2. Formal email generation & audit
    email = orchestrator.compose_email(
        form="formal",
        recipient_surname="Moretti",
        recipient_title="Dottoressa",
        body="Le invio il resoconto completo dello sviluppo del modulo.",
        sender_name="Ing. Giovanni Ferrari",
        organization="Solo Rock"
    )
    assert "Gentile Dottoressa Moretti," in email
    assert "Cordiali saluti" in email
    
    audit = orchestrator.audit_email(email)
    assert audit["passed"] is True
    assert audit["is_consistent"] is True
    
    # 3. Dialect adaptation
    dialect_text = "Ho visto la Chiara e poi noi si va insieme."
    adapted = orchestrator.adapt_dialect(dialect_text, target="standard")
    assert "Ho visto Chiara" in adapted
    assert "noi andiamo" in adapted
    
    # 4. Rhetorical style analysis
    rhetorical_text = "Non vedo l'ora di presentare questo progetto in bocca al lupo a tutti."
    style_res = orchestrator.analyze_style(rhetorical_text)
    assert style_res["style"] == "classical_rhetorical"
    assert "non vedere l'ora" in style_res["idioms_found"]
