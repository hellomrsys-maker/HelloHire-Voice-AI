"""
Comprehensive Test Suite for the Spanish Engine Ecosystem
=========================================================
Validates:
1. All Spanish Computational Skills (Tokenization, POS, Conjugation, Ser/Estar, Por/Para, Clitics, Pragmatics, Generation)
2. Cognitive Analysis Modules (Pro-Drop, Subjunctive Evaluator, Agreement Checker)
3. Task Pipelines (Grammar Checker, Email Generator, Composition)
4. Dedicated Sub-AIs (Syntax, Phonology, Pragmatic, Editorial) with 0-ns AMSV memory sync and bit isolation
5. Six-Language Matrix Coordination (Rust, Python, C++20, CUDA, Java 21, Julia)
6. Master Orchestrator End-to-End Processing and 64-byte AMSV State Vector integrity
"""

import pytest
import os
import sys

# Ensure workspace root is in python path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from amsv.python.amsv_embedded import AMSVEmbeddedView
from Spanish_engine.brain.skills.tokenization import SpanishTokenizer, SpanishToken
from Spanish_engine.brain.skills.pos_tagging import SpanishPOSTagger
from Spanish_engine.brain.skills.verb_conjugator import SpanishVerbConjugator
from Spanish_engine.brain.skills.ser_estar_engine import SerEstarEngine
from Spanish_engine.brain.skills.por_para_engine import PorParaEngine
from Spanish_engine.brain.skills.clitic_engine import CliticEngine
from Spanish_engine.brain.skills.pragmatics_engine import SpanishPragmaticsEngine
from Spanish_engine.brain.skills.parsing import SpanishParser
from Spanish_engine.brain.skills.generation import SpanishGenerator

from Spanish_engine.brain.analysis.pro_drop_analyzer import ProDropAnalyzer
from Spanish_engine.brain.analysis.subjunctive_evaluator import SubjunctiveEvaluator
from Spanish_engine.brain.analysis.agreement_checker import SpanishAgreementChecker

from Spanish_engine.brain.task.grammar_check import SpanishGrammarChecker
from Spanish_engine.brain.task.email_pipeline import SpanishEmailPipeline
from Spanish_engine.brain.task.composition_pipeline import SpanishCompositionPipeline

from Spanish_engine.brain.sub_ais.syntax_sub_ai import SpanishSyntaxSubAI
from Spanish_engine.brain.sub_ais.phonology_sub_ai import SpanishPhonologySubAI
from Spanish_engine.brain.sub_ais.pragmatic_sub_ai import SpanishPragmaticSubAI
from Spanish_engine.brain.sub_ais.editorial_sub_ai import SpanishEditorialSubAI

from Spanish_engine.six_language_matrix.python.spanish_matrix_bridge import (
    SpanishSixLanguageMatrixBridge,
    SpanishSixLanguageExecutionResult,
)
from Spanish_engine.spanish_engine_orchestrator import SpanishEngineOrchestrator


def test_spanish_tokenizer_and_inverted_punctuation():
    tokenizer = SpanishTokenizer()
    text = "¡Hola! ¿Cómo estás? Vamos al mercado del centro."
    tokens = tokenizer.tokenize(text)

    assert len(tokens) >= 8
    surfaces = [t.text for t in tokens]
    assert "¡" in surfaces
    assert "!" in surfaces
    assert "¿" in surfaces
    assert "?" in surfaces
    assert "Hola" in surfaces
    assert "al" in surfaces
    assert "del" in surfaces

    stats = tokenizer.get_token_stats(text)
    assert stats["has_inverted_question"] is True
    assert stats["has_inverted_exclamation"] is True
    assert stats["accented_vowel_count"] >= 2


def test_spanish_pos_tagging():
    tokenizer = SpanishTokenizer()
    tagger = SpanishPOSTagger()
    text = "El estudiante lee un libro en la biblioteca"
    tokens = tokenizer.segment(text)
    tagged = tagger.tag(tokens)

    assert len(tagged) == len(tokens)
    tag_map = dict(tagged)
    assert tag_map.get("El") == "DET"
    assert tag_map.get("estudiante") == "NOUN"
    assert tag_map.get("lee") == "VERB"
    assert tag_map.get("un") == "DET"
    assert tag_map.get("libro") == "NOUN"
    assert tag_map.get("en") == "ADP"
    assert tag_map.get("la") == "DET"


def test_spanish_verb_conjugation_and_lemmatization():
    conjugator = SpanishVerbConjugator()

    # Regular -ar verb
    hablar_pres = conjugator.conjugate("hablar", "presente_indicativo")
    assert hablar_pres == ["hablo", "hablas", "habla", "hablamos", "habláis", "hablan"]

    # Irregular ser
    ser_pres = conjugator.conjugate("ser", "presente_indicativo")
    assert ser_pres == ["soy", "eres", "es", "somos", "sois", "son"]

    # Specific person lookup
    assert conjugator.get_conjugation_for_person("vivir", 3, "presente_indicativo") == "vivimos"
    assert conjugator.get_conjugation_for_person("tener", 0, "presente_indicativo") == "tengo"

    # Lemmatization
    res = conjugator.lemmatize("fuiste")
    assert res["lemma"] == "ser" or res["lemma"] == "ir"
    assert res["is_irregular"] is True


def test_spanish_ser_vs_estar_copula_disambiguation():
    engine = SerEstarEngine()

    # Identity -> Ser
    e1 = engine.evaluate_copula("es", "médico")
    assert e1["chosen_copula"] == "ser"
    assert e1["is_appropriate"] is True

    # State -> Estar
    e2 = engine.evaluate_copula("está", "cansado")
    assert e2["chosen_copula"] == "estar"
    assert e2["is_appropriate"] is True

    # Semantic shift adjective: listo
    e3 = engine.evaluate_copula("es", "listo")
    assert e3["has_semantic_shift"] is True
    assert "Inteligente" in e3["contextual_meaning"]

    e4 = engine.evaluate_copula("está", "listo")
    assert e4["has_semantic_shift"] is True
    assert "Preparado" in e4["contextual_meaning"]


def test_spanish_por_vs_para():
    engine = PorParaEngine()

    # Purpose with infinitive -> Para
    v1 = engine.evaluate_preposition("para", "estudiar en la universidad")
    assert v1["recommended_preposition"] == "para"
    assert v1["is_valid"] is True

    # Recipient -> Para
    v2 = engine.evaluate_preposition("para", "ti con mucho cariño")
    assert v2["recommended_preposition"] == "para"

    # Cause -> Por
    v3 = engine.evaluate_preposition("por", "la lluvia torrencial")
    assert v3["recommended_preposition"] == "por"

    # Gratitude -> Por
    v4 = engine.evaluate_preposition("por", "tu ayuda y gracias")
    assert v4["recommended_preposition"] == "por"


def test_spanish_clitic_engine():
    clitic_engine = CliticEngine()

    # Spurious 'se' rule: le + lo -> se lo
    cluster = clitic_engine.resolve_clitic_cluster("le", "lo")
    assert cluster["spurious_se_applied"] is True
    assert cluster["proclitic_cluster"] == "se lo"
    assert cluster["enclitic_cluster"] == "selo"

    # Non-spurious: te + la -> te la
    c2 = clitic_engine.resolve_clitic_cluster("te", "la")
    assert c2["spurious_se_applied"] is False
    assert c2["proclitic_cluster"] == "te la"

    # Enclisis on infinitive
    placement = clitic_engine.analyze_placement("cantar", ["lo"])
    assert placement["placement"] == "enclitic"
    assert placement["surface_verb"] == "cantarlo"


def test_spanish_pragmatics_and_address_tiers():
    engine = SpanishPragmaticsEngine()

    # Formal ustedeo with courtesy markers
    formal_text = "Estimado señor, ¿podría usted indicarme la hora, por favor? Muchas gracias."
    p1 = engine.evaluate_pragmatics(formal_text)
    assert p1["is_formal"] is True
    assert "Ustedeo" in p1["address_tier"]
    assert p1["politeness_score"] >= 0.85
    assert len(p1["detected_courtesy_markers"]) >= 2
    assert p1["has_pragmatic_mitigation"] is True

    # Informal tuteo
    informal_text = "Hola, ¿cómo estás tú? ¿Tienes tiempo?"
    p2 = engine.evaluate_pragmatics(informal_text)
    assert p2["is_formal"] is False
    assert "Tuteo" in p2["address_tier"]


def test_spanish_sentence_generation():
    gen = SpanishGenerator()

    # Canonical SVO
    s1 = gen.generate(subject="yo", verb_lemma="hablar", obj="español")
    assert s1 == "Yo hablo español."

    # Pro-drop
    s2 = gen.generate(subject="nosotros", verb_lemma="vivir", obj="en Madrid", pro_drop=True)
    assert s2 == "Vivimos en Madrid."

    # Interrogative
    s3 = gen.generate(subject="tú", verb_lemma="estudiar", obj="lingüística", is_question=True)
    assert s3 == "¿Tú estudias lingüística?"


def test_spanish_cognitive_analysis():
    pro_drop = ProDropAnalyzer()
    subjunctive = SubjunctiveEvaluator()
    agreement = SpanishAgreementChecker()

    # Pro-drop analysis
    pd_res = pro_drop.analyze("Estudiamos en la biblioteca por la tarde.")
    assert pd_res["is_pro_drop"] is True
    assert pd_res["has_overt_subject"] is False

    # Subjunctive clause analysis
    sub_res = subjunctive.evaluate_clause("Quiero que estudies mucho para el examen.")
    assert sub_res["requires_subjunctive"] is True
    assert "quiero que" in sub_res["detected_triggers"]

    # Noun phrase agreement
    ag1 = agreement.check_noun_phrase_agreement("la", "casa", "blanca")
    assert ag1["is_valid"] is True

    ag2 = agreement.check_noun_phrase_agreement("la", "casa", "blanco")
    assert ag2["is_valid"] is False
    assert ag2["gender_concord"] is False


def test_spanish_tasks():
    grammar_checker = SpanishGrammarChecker()
    email_pipeline = SpanishEmailPipeline()
    composition_pipeline = SpanishCompositionPipeline()

    # Grammar check on valid text
    g_res = grammar_checker.check_text("¿Cómo estás? Espero que estés muy bien.")
    assert g_res["is_grammatically_sound"] is True
    assert g_res["error_count"] == 0

    # Grammar check on unclosed question mark
    g_err = grammar_checker.check_text("Cómo estás? No sé.")
    assert g_err["is_grammatically_sound"] is False
    assert g_err["error_count"] >= 1

    # Email generation
    email_res = email_pipeline.generate_email(
        recipient_name="García",
        recipient_title="Profesor",
        topic="Propuesta de Colaboración",
        body_content="Le presento el informe sobre la arquitectura lingüística.",
        sender_name="Carlos Ruiz",
        formal=True
    )
    assert "Estimado/a Profesor García:" in email_res["full_email"]
    assert "Atentamente," in email_res["full_email"]
    assert email_res["is_formal"] is True

    # Composition statement
    comp_res = composition_pipeline.compose_statement(
        subject="ellos",
        verb_lemma="comer",
        obj="frutas frescas",
        pro_drop=True
    )
    assert comp_res["composed_text"] == "Comen frutas frescas."
    assert comp_res["pro_drop_applied"] is True


def test_spanish_sub_ais_and_amsv_bit_isolation():
    """
    CRITICAL ZERO-BRIDGE TEST:
    Validates that each Sub-AI updates strictly its designated byte offsets in the 64-byte AMSV
    with zero unintended bit contamination or cross-subsystem bleeding.
    """
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))

    syntax_ai = SpanishSyntaxSubAI(amsv_view=amsv)
    phonology_ai = SpanishPhonologySubAI(amsv_view=amsv)
    pragmatic_ai = SpanishPragmaticSubAI(amsv_view=amsv)
    editorial_ai = SpanishEditorialSubAI(amsv_view=amsv)

    initial_bytes = bytes(amsv.get_raw_bytes())
    assert len(initial_bytes) == 64
    assert all(b == 0 for b in initial_bytes)

    # 1. Syntax Sub-AI: writes to Byte 18 (0x12) and Byte 52 (0x34)
    syntax_eval = syntax_ai.evaluate("El profesor explica la lección a los estudiantes.")
    assert syntax_eval.has_personal_a is True
    b_syntax = bytes(amsv.get_raw_bytes())

    assert b_syntax[18] > 0, "Syntax Sub-AI must write to Byte 18"
    assert b_syntax[52] > 0, "Syntax Sub-AI must write to Byte 52"
    assert all(b == 0 for b in b_syntax[0:16]), "Bytes 0..15 must remain pristine"
    assert all(b == 0 for b in b_syntax[20:28]), "Bytes 20..27 must remain pristine"
    assert all(b == 0 for b in b_syntax[54:64]), "Bytes 54..63 must remain pristine"

    # 2. Phonology Sub-AI: writes to Bytes 0..15 and Byte 24 (0x18)
    phonology_eval = phonology_ai.evaluate("La lingüística española es una disciplina fascinante.")
    assert phonology_eval.syllable_count >= 10
    b_phono = bytes(amsv.get_raw_bytes())

    assert any(b > 0 for b in b_phono[0:8]), "Phonology Sub-AI must write to Bytes 0..7"
    assert any(b > 0 for b in b_phono[8:16]), "Phonology Sub-AI must write to Bytes 8..15"
    assert b_phono[24] > 0, "Phonology Sub-AI must write to Byte 24"
    assert b_phono[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_phono[52] == b_syntax[52], "Byte 52 must be preserved"

    # 3. Pragmatic Sub-AI: writes to Byte 22 (0x16) and Byte 54 (0x36)
    pragmatic_eval = pragmatic_ai.evaluate("Estimado señor, ¿podría usted atenderme por favor?")
    assert pragmatic_eval.is_formal is True
    b_prag = bytes(amsv.get_raw_bytes())

    assert b_prag[22] > 0, "Pragmatic Sub-AI must write to Byte 22"
    assert b_prag[54] > 0, "Pragmatic Sub-AI must write to Byte 54"
    assert b_prag[18] == b_syntax[18]
    assert b_prag[24] == b_phono[24]

    # 4. Editorial Sub-AI: writes to Byte 20 (0x14) and Byte 26 (0x1A)
    editorial_eval = editorial_ai.evaluate("En primer lugar, el proyecto es viable; sin embargo, requiere mayor inversión.")
    assert editorial_eval.editorial_verdict in {"PASSED_FOR_PUBLICATION", "NEEDS_REVISION"}
    b_edit = bytes(amsv.get_raw_bytes())

    assert b_edit[20] > 0, "Editorial Sub-AI must write to Byte 20"
    assert b_edit[26] > 0, "Editorial Sub-AI must write to Byte 26"
    assert b_edit[56] == 0, "Byte 56 attention directive must remain decoupled"


def test_spanish_six_language_matrix():
    amsv = AMSVEmbeddedView()
    bridge = SpanishSixLanguageMatrixBridge(amsv_view=amsv)
    text = "«Buenos días», ¿podría usted explicarme el ejercicio por favor?"
    res = bridge.coordinate(text, request_id="req-es-test-01")

    assert isinstance(res, SpanishSixLanguageExecutionResult)
    assert set(res.language_nodes) == {"Rust", "Python", "C++20", "CUDA", "Java 21", "Julia"}
    assert res.rust_safety_passed is True
    assert res.cpp_trie_lookup_count > 0
    assert res.cuda_attention_flops > 0
    assert res.java_virtual_thread_dispatched is True
    assert res.julia_stress_trajectory_steps > 0
    assert res.amsv_synced is True
    assert 0.0 < res.composite_linguistic_score <= 1.0


def test_spanish_engine_orchestrator_end_to_end():
    """
    Validates complete end-to-end processing of the SpanishEngineOrchestrator.
    """
    orchestrator = SpanishEngineOrchestrator()
    sample_text = "Estimado profesor, le escribo para informarle que he completado el proyecto con éxito."

    output = orchestrator.process(sample_text, request_id="es-orchestrator-eval-001")

    # 1. Output structure assertions
    assert output.input_text == sample_text
    assert len(output.tokens) >= 10
    assert len(output.pos_tags) == len(output.tokens)
    assert output.sentence_structure is not None
    assert output.grammar_check["is_grammatically_sound"] is True

    # 2. Pragmatics assertions
    assert output.pragmatics["is_formal"] is True
    assert output.pragmatics["politeness_score"] >= 0.80

    # 3. Cognitive Analysis assertions
    assert output.pro_drop_analysis is not None
    assert output.subjunctive_evaluation is not None

    # 4. Sub-AIs assertions
    assert output.syntax_sub_ai.syntax_score > 0.70
    assert output.phonology_sub_ai.syllable_count > 10
    assert output.pragmatic_sub_ai.is_formal is True
    assert output.editorial_sub_ai.readability_score > 0.0

    # 5. Six-Language Matrix assertions
    assert output.six_language_matrix.rust_safety_passed is True
    assert output.six_language_matrix.cpp_trie_lookup_count >= 5

    # 6. Four-Stage Matrix assertions
    assert "stage1_entry" in output.four_stage_matrix
    assert "stage2_base_ai_pair" in output.four_stage_matrix
    assert "stage3_connected_groups" in output.four_stage_matrix
    assert "stage4_execution_pipeline" in output.four_stage_matrix
    assert "out_result" in output.four_stage_matrix
    assert output.four_stage_matrix["status"] == "COMPLETED"

    # 7. Hardware AMSV 64-byte State Vector assertions
    assert len(output.amsv_bytes_hex) == 128  # 64 bytes = 128 hex chars
    raw_bytes = bytes.fromhex(output.amsv_bytes_hex)
    assert len(raw_bytes) == 64
    assert any(b > 0 for b in raw_bytes[16:32])

    # 8. Performance latency assertion
    assert output.latency_ms < 500.0, f"Latency exceeded expectation: {output.latency_ms}ms"
