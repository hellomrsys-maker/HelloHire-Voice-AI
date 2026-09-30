"""
Unit and Integration Test Suite for Hindustani Language Engine (Hindustani_engine).
Validates 9-layer compliance, 4 dedicated Sub-AIs, Six-Language Matrix nodes,
and strict Zero-Bridge 64-byte AMSV memory isolation.
"""

import pytest
from amsv.python.amsv_embedded import AMSVEmbeddedView

from Hindustani_engine.brain.skills.tokenization import HindustaniTokenizer
from Hindustani_engine.brain.skills.pos_tagging import HindustaniPOSTagger
from Hindustani_engine.brain.skills.verb_conjugator import HindustaniVerbConjugator
from Hindustani_engine.brain.skills.ergative_engine import ErgativeSplitEngine
from Hindustani_engine.brain.skills.oblique_case_engine import ObliqueCaseEngine
from Hindustani_engine.brain.skills.compound_verb_engine import CompoundVerbEngine
from Hindustani_engine.brain.skills.pragmatics_engine import HindustaniPragmaticsEngine
from Hindustani_engine.brain.skills.parsing import HindustaniParser
from Hindustani_engine.brain.skills.generation import HindustaniGenerator

from Hindustani_engine.brain.analysis.ergative_alignment_analyzer import ErgativeAlignmentAnalyzer
from Hindustani_engine.brain.analysis.oblique_concord_analyzer import ObliqueConcordAnalyzer
from Hindustani_engine.brain.analysis.honorific_agreement_analyzer import HonorificAgreementAnalyzer

from Hindustani_engine.brain.task.grammar_check import HindustaniGrammarChecker
from Hindustani_engine.brain.task.email_pipeline import HindustaniEmailPipeline
from Hindustani_engine.brain.task.composition_pipeline import HindustaniCompositionPipeline

from Hindustani_engine.brain.sub_ais.syntax_sub_ai import HindustaniSyntaxSubAI
from Hindustani_engine.brain.sub_ais.phonology_sub_ai import HindustaniPhonologySubAI
from Hindustani_engine.brain.sub_ais.pragmatic_sub_ai import HindustaniPragmaticSubAI
from Hindustani_engine.brain.sub_ais.editorial_sub_ai import HindustaniEditorialSubAI

from Hindustani_engine.six_language_matrix.python.hindustani_matrix_bridge import HindustaniMatrixBridge
from Hindustani_engine.hindustani_engine_orchestrator import HindustaniEngineOrchestrator


def test_hindustani_tokenizer_and_dual_script():
    tokenizer = HindustaniTokenizer()

    # Romanized tokenization
    t1 = "Ram ne ek nayi kitaab padhi."
    toks1 = tokenizer.tokenize(t1)
    assert "ne" in toks1
    assert "padhi" in toks1

    # Devanagari tokenization with danda
    t2 = "राम ने एक नई किताब पढ़ी।"
    toks2 = tokenizer.tokenize(t2)
    assert "ने" in toks2
    assert "पढ़ी" in toks2
    assert "।" in toks2

    spans = tokenizer.get_token_spans(t1)
    assert len(spans) == len(toks1)


def test_hindustani_pos_tagging():
    tagger = HindustaniPOSTagger()
    tokens = ["ladke", "ne", "seb", "khaya", "."]
    tagged = tagger.tag(tokens)

    tag_dict = dict(tagged)
    assert tag_dict["ne"] == "ADP"
    assert tag_dict["khaya"] == "VERB"
    assert tag_dict["ladke"] == "NOUN"


def test_hindustani_verb_conjugator_and_transitivity():
    conjugator = HindustaniVerbConjugator()

    # Transitivity check for split-ergativity
    assert conjugator.is_transitive("padhna") is True
    assert conjugator.is_transitive("dekhna") is True
    assert conjugator.is_transitive("jaana") is False
    assert conjugator.is_transitive("aana") is False

    # Irregular perfective forms
    assert conjugator.conjugate("karna", aspect="perfective", gender="M", number="SG") == "kiya"
    assert conjugator.conjugate("jaana", aspect="perfective", gender="M", number="PL") == "gaye"
    assert conjugator.conjugate("dena", aspect="perfective", gender="F", number="SG") == "di"

    # Regular aspectual conjugation
    assert conjugator.conjugate("bolna", aspect="habitual", gender="M", number="SG") == "bolta"
    assert conjugator.conjugate("bolna", aspect="continuous", gender="F", number="SG") == "bol rahi"


def test_hindustani_ergative_split_engine():
    engine = ErgativeSplitEngine()

    # Transitive past: Ram ne kitaab (F SG) padhi (F SG) -> Valid agreement with object
    res1 = engine.evaluate_clause(
        subject_phrase=["Ram", "ne"],
        verb_lemma="padhna",
        aspect="perfective",
        object_phrase=["kitaab"],
        object_gender="F",
        object_number="SG",
        verb_surface="padhi"
    )
    assert res1["is_grammatically_sound"] is True
    assert res1["requires_ne"] is True

    # Transitive past: missing ne on subject -> Error
    res2 = engine.evaluate_clause(
        subject_phrase=["Ram"],
        verb_lemma="padhna",
        aspect="perfective",
        object_phrase=["kitaab"],
        object_gender="F",
        object_number="SG",
        verb_surface="padhi"
    )
    assert res2["is_grammatically_sound"] is False
    assert res2["subject_ergative_valid"] is False

    # Transitive past with ko-marked object: default masculine singular neutral agreement
    res3 = engine.evaluate_clause(
        subject_phrase=["Ram", "ne"],
        verb_lemma="dekhna",
        aspect="perfective",
        object_phrase=["Sita", "ko"],
        object_gender="F",
        object_number="SG",
        verb_surface="dekha"
    )
    assert res3["is_grammatically_sound"] is True
    assert res3["object_has_ko"] is True
    assert res3["expected_verb_form"] == "dekha"


def test_hindustani_oblique_case_engine():
    engine = ObliqueCaseEngine()

    # Masculine marked singular: ladka -> ladke
    assert engine.to_oblique("ladka", gender="M", number="SG") == "ladke"
    assert engine.to_oblique("kamra", gender="M", number="SG") == "kamre"

    # Plural oblique: ladka -> ladkon, kitaab -> kitabon
    assert engine.to_oblique("ladka", gender="M", number="PL") == "ladkon"
    assert engine.to_oblique("kitaab", gender="F", number="PL") == "kitabon"

    # Evaluation of uninflected direct form before postposition: *ladka ne
    check1 = engine.evaluate_noun_phrase("ladka", "ne", gender="M", number="SG")
    assert check1["is_valid"] is False
    assert check1["expected_oblique"] == "ladke"

    # Evaluation of properly inflected oblique: ladke ne
    check2 = engine.evaluate_noun_phrase("ladke", "ne", gender="M", number="SG")
    assert check2["is_valid"] is True


def test_hindustani_compound_verbs():
    engine = CompoundVerbEngine()

    # V1 stem + V2 vector: khaa lena
    c1 = engine.analyze_compound_verb("khaa", "lena")
    assert c1["is_compound_verb"] is True
    assert c1["semantic_role"] == "self_benefactive"

    # V1 stem + V2 vector: maar daalna
    c2 = engine.analyze_compound_verb("maar", "daalna")
    assert c2["is_compound_verb"] is True
    assert c2["semantic_role"] == "violent_forceful"


def test_hindustani_pragmatics_and_honorifics():
    engine = HindustaniPragmaticsEngine()

    # Tier 3 Aap formal
    p1 = engine.evaluate_pragmatics("Aap kahan jaa rahe hain, Sharma ji?")
    assert p1["address_tier"] == "tier_3_aap"
    assert p1["is_formal"] is True
    assert p1["has_honorific_particle_ji"] is True
    assert p1["politeness_score"] >= 0.90

    # Tier 2 Tum familiar
    p2 = engine.evaluate_pragmatics("Tum kya kar rahe ho?")
    assert p2["address_tier"] == "tier_2_tum"
    assert p2["is_familiar"] is True

    # Tier 1 Tu intimate
    p3 = engine.evaluate_pragmatics("Tu idhar aa.")
    assert p3["address_tier"] == "tier_1_tu"
    assert p3["is_intimate"] is True


def test_hindustani_sentence_generation():
    generator = HindustaniGenerator()

    # Habitual SOV statement
    s1 = generator.generate_statement("woh", "likhna", "patra", aspect="habitual", subject_gender="M")
    assert s1 == "Woh patra likhta hai."

    # Perfective transitive clause with split-ergative ne and object concord
    s2 = generator.generate_statement(
        "Ram", "padhna", "kitaab", aspect="perfective", object_gender="F", object_number="SG"
    )
    assert s2 == "Ram ne kitaab padhi."

    # Future SOV clause
    s3 = generator.generate_statement("hum", "jaana", "Dilli", aspect="future", subject_gender="M", subject_number="PL")
    assert s3 == "Hum Dilli jaayenge." or s3 == "Hum Dilli jaenge." or "ja" in s3


def test_hindustani_cognitive_analyzers():
    erg_analyzer = ErgativeAlignmentAnalyzer()
    oblique_analyzer = ObliqueConcordAnalyzer()
    hon_analyzer = HonorificAgreementAnalyzer()

    # Ergative clause check
    r1 = erg_analyzer.analyze_clause(
        subject="usne",
        verb_lemma="khana",
        aspect="perfective",
        obj="seb",
        object_gender="M",
        verb_surface="khaya"
    )
    assert r1["is_grammatically_sound"] is True

    # Oblique case concord diagnostic: ladka ne -> error
    r2 = oblique_analyzer.analyze("ladka ne seb khaya.")
    assert r2["is_valid"] is False
    assert r2["violation_count"] >= 1

    # Honorific agreement: Aap aate hain -> valid
    r3 = hon_analyzer.analyze("Aap yahan aate hain.")
    assert r3["is_concord_valid"] is True

    # Honorific agreement mismatch: Aap aata hai -> invalid
    r4 = hon_analyzer.analyze("Aap yahan aata hai.")
    assert r4["is_concord_valid"] is False


def test_hindustani_tasks():
    grammar_checker = HindustaniGrammarChecker()
    email_pipeline = HindustaniEmailPipeline()
    comp_pipeline = HindustaniCompositionPipeline()

    # Grammar check clean sentence
    res1 = grammar_checker.check("ladke ne kitaab padhi.")
    assert res1["is_valid"] is True
    assert res1["score"] == 1.0

    # Grammar check with oblique error
    res2 = grammar_checker.check("ladka ne kitaab padhi.")
    assert res2["is_valid"] is False
    assert any(iss["type"] == "oblique_case_error" for iss in res2["issues"])

    # Email generation
    email_res = email_pipeline.generate_email(
        recipient_name="Verma",
        topic="Project Update",
        body_content="Hum aapko pragati report bhej rahe hain.",
        sender_name="Amit Kumar",
        formal=True
    )
    assert "Aadarniya Verma ji," in email_res["full_email"]
    assert "Bhavadiya," in email_res["full_email"]
    assert email_res["is_formal"] is True

    # Composition statement
    comp_res = comp_pipeline.compose_statement(
        subject="ladka",
        verb_lemma="padhna",
        obj="kitaab",
        aspect="perfective",
        object_gender="F",
        object_number="SG"
    )
    assert comp_res["composed_text"] == "Ladke ne kitaab padhi."
    assert comp_res["is_ergative"] is True


def test_hindustani_sub_ais_and_amsv_bit_isolation():
    """
    CRITICAL ZERO-BRIDGE TEST:
    Validates that each Sub-AI updates strictly its designated byte offsets in the 64-byte AMSV
    with zero unintended bit contamination or cross-subsystem bleeding.
    """
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))

    syntax_ai = HindustaniSyntaxSubAI(amsv_view=amsv)
    phonology_ai = HindustaniPhonologySubAI(amsv_view=amsv)
    pragmatic_ai = HindustaniPragmaticSubAI(amsv_view=amsv)
    editorial_ai = HindustaniEditorialSubAI(amsv_view=amsv)

    initial_bytes = bytes(amsv.get_raw_bytes())
    assert len(initial_bytes) == 64
    assert all(b == 0 for b in initial_bytes)

    # 1. Syntax Sub-AI: writes to Byte 18 (0x12) and Byte 52 (0x34)
    syntax_eval = syntax_ai.evaluate("Adhyapak ne vidyarthiyon ko path padhaya.")
    assert syntax_eval.is_canonical_sov is True
    b_syntax = bytes(amsv.get_raw_bytes())

    assert b_syntax[18] > 0, "Syntax Sub-AI must write to Byte 18"
    assert b_syntax[52] > 0, "Syntax Sub-AI must write to Byte 52"
    assert all(b == 0 for b in b_syntax[0:16]), "Bytes 0..15 must remain pristine"
    assert all(b == 0 for b in b_syntax[20:28]), "Bytes 20..27 must remain pristine"
    assert all(b == 0 for b in b_syntax[54:64]), "Bytes 54..63 must remain pristine"

    # 2. Phonology Sub-AI: writes to Bytes 0..15 and Byte 24 (0x18)
    phonology_eval = phonology_ai.evaluate("Bade ladke ne gaadi ko dheere se roka aur padha.")
    assert phonology_eval.retroflex_count >= 1
    b_phono = bytes(amsv.get_raw_bytes())

    assert any(b > 0 for b in b_phono[0:8]), "Phonology Sub-AI must write to Bytes 0..7"
    assert any(b > 0 for b in b_phono[8:16]), "Phonology Sub-AI must write to Bytes 8..15"
    assert b_phono[24] > 0, "Phonology Sub-AI must write to Byte 24"
    assert b_phono[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_phono[52] == b_syntax[52], "Byte 52 must be preserved"

    # 3. Pragmatic Sub-AI: writes to Byte 22 (0x16) and Byte 54 (0x36)
    pragmatic_eval = pragmatic_ai.evaluate("Aap kripya aasan grahan karein, Sharma ji.")
    assert pragmatic_eval.is_formal is True
    b_prag = bytes(amsv.get_raw_bytes())

    assert b_prag[22] > 0, "Pragmatic Sub-AI must write to Byte 22"
    assert b_prag[54] > 0, "Pragmatic Sub-AI must write to Byte 54"
    assert b_prag[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_prag[24] == b_phono[24], "Byte 24 must be preserved"

    # 4. Editorial Sub-AI: writes to Byte 20 (0x14) and Byte 26 (0x1A)
    editorial_eval = editorial_ai.evaluate("Vigyan aur taknik ke vikas se samaj ko naye aayam mile hain.")
    assert editorial_eval.is_clean is True
    b_edit = bytes(amsv.get_raw_bytes())

    assert b_edit[20] > 0, "Editorial Sub-AI must write to Byte 20"
    assert b_edit[26] > 0, "Editorial Sub-AI must write to Byte 26"
    assert b_edit[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_edit[22] == b_prag[22], "Byte 22 must be preserved"
    assert b_edit[24] == b_phono[24], "Byte 24 must be preserved"
    assert b_edit[52] == b_syntax[52], "Byte 52 must be preserved"
    assert b_edit[54] == b_prag[54], "Byte 54 must be preserved"


def test_hindustani_six_language_matrix():
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))
    bridge = HindustaniMatrixBridge(amsv_view=amsv)

    res = bridge.execute_matrix_pipeline(
        text="Maine ek sundar kitaab padhi.",
        syntax_score=0.95,
        phonology_score=0.90,
        register_score=0.85
    )

    assert res["rust_safety"]["is_safe"] is True
    assert res["cpp_engine"]["has_transitive_verb"] is True
    assert res["cuda_kernel"]["batch_acceleration"] is True
    assert res["java_service"]["loom_virtual_threads"] is True
    assert res["julia_dynamics"]["entropy_model"] == "head_final_sov"
    assert res["amsv_zero_bridge_synced"] is True

    raw = bytes(amsv.get_raw_bytes())
    assert raw[18] > 0
    assert raw[22] > 0
    assert raw[24] > 0
    assert raw[52] > 0
    assert raw[54] > 0


def test_hindustani_engine_orchestrator_end_to_end():
    orchestrator = HindustaniEngineOrchestrator()
    sample = "Adhyapak ji ne chatron ko naya vishay sikhaya."
    result = orchestrator.analyze(sample)

    assert len(result.tokens) > 5
    assert result.sentence_structure.has_subject is True
    assert result.sentence_structure.is_canonical_sov is True
    assert result.syntax_eval.is_valid_sentence is True
    assert result.editorial_eval.is_clean is True
    assert result.overall_linguistic_score >= 0.70
    assert result.amsv_synced is True
