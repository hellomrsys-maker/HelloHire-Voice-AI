"""
Unit and Integration Test Suite for the Bengali Language Engine (বাংলা).
Tests all 9 layers, 9 computational skills, 3 cognitive analyzers,
3 task pipelines, 4 dedicated Sub-AIs, 6-language matrix, and Zero-Bridge AMSV sync.
"""

import pytest
from amsv.python.amsv_embedded import AMSVEmbeddedView

from Bengali_engine.brain.skills.tokenization import BengaliTokenizer
from Bengali_engine.brain.skills.pos_tagging import BengaliPOSTagger
from Bengali_engine.brain.skills.verb_conjugator import BengaliVerbConjugator
from Bengali_engine.brain.skills.classifier_engine import BengaliClassifierEngine
from Bengali_engine.brain.skills.case_engine import BengaliCaseEngine
from Bengali_engine.brain.skills.compound_verb_engine import BengaliCompoundVerbEngine
from Bengali_engine.brain.skills.pragmatics_engine import BengaliPragmaticsEngine
from Bengali_engine.brain.skills.parsing import BengaliParser
from Bengali_engine.brain.skills.generation import BengaliGenerator

from Bengali_engine.brain.analysis.classifier_concord_analyzer import ClassifierConcordAnalyzer
from Bengali_engine.brain.analysis.case_postposition_analyzer import CasePostpositionAnalyzer
from Bengali_engine.brain.analysis.honorific_register_analyzer import HonorificRegisterAnalyzer

from Bengali_engine.brain.task.grammar_check import BengaliGrammarCheckTask
from Bengali_engine.brain.task.email_pipeline import BengaliEmailPipelineTask
from Bengali_engine.brain.task.composition_pipeline import BengaliCompositionPipelineTask

from Bengali_engine.brain.sub_ais.syntax_sub_ai import BengaliSyntaxSubAI
from Bengali_engine.brain.sub_ais.phonology_sub_ai import BengaliPhonologySubAI
from Bengali_engine.brain.sub_ais.pragmatic_sub_ai import BengaliPragmaticSubAI
from Bengali_engine.brain.sub_ais.editorial_sub_ai import BengaliEditorialSubAI

from Bengali_engine.six_language_matrix.python.bengali_matrix_bridge import BengaliMatrixBridge
from Bengali_engine.bengali_engine_orchestrator import BengaliEngineOrchestrator


def test_bengali_tokenizer_and_classifier_detachment():
    tokenizer = BengaliTokenizer()
    text = "আমি বইটি পড়ছি। তিনি পাঁচজন ছাত্রকে দেখলেন।"
    tokens = tokenizer.tokenize(text)

    assert "আমি" in tokens
    assert "বইটি" in tokens
    assert "পড়ছি" in tokens
    assert "।" in tokens
    assert "পাঁচজন" in tokens

    # Test classifier detachment
    stem, clf = tokenizer.split_classifier("বইটা")
    assert stem == "বই"
    assert clf == "টা"

    stem, clf = tokenizer.split_classifier("ছাত্রজন")
    assert stem == "ছাত্র"
    assert clf == "জন"

    # Test token spans
    spans = tokenizer.tokenize_with_spans(text)
    assert len(spans) > 0
    assert spans[0]["token"] == "আমি"
    assert spans[0]["start"] == 0


def test_bengali_pos_tagging():
    tagger = BengaliPOSTagger()
    tokens = ["তিনি", "একটি", "ভালো", "বই", "পড়ছেন", "।"]
    tagged = tagger.tag_tokens(tokens)

    tag_map = {item["token"]: item["pos"] for item in tagged}
    assert tag_map["তিনি"] == "PRON"
    assert tag_map["একটি"] == "NUM"
    assert tag_map["ভালো"] == "ADJ"
    assert tag_map["।"] == "PUNCT"


def test_bengali_verb_conjugator_and_classes():
    conj = BengaliVerbConjugator()

    # Class 1: করা (kora)
    assert conj.conjugate("করা", "present_simple", "1st") == "করি"
    assert conj.conjugate("করা", "present_simple", "2nd_fam") == "করো"
    assert conj.conjugate("করা", "present_simple", "hon") == "করেন"
    assert conj.conjugate("করা", "past_simple", "1st") == "করলাম"
    assert conj.conjugate("করা", "future_simple", "hon") == "করবেন"

    # Non-finite participles
    assert conj.get_non_finite("করা", "conjunctive") == "করে"
    assert conj.get_non_finite("করা", "infinitive") == "করতে"
    assert conj.get_non_finite("করা", "conditional") == "করলে"

    # Class 4: যাওয়া (jawa)
    assert conj.conjugate("যাওয়া", "past_simple", "hon") == "গেলেন"
    assert conj.get_non_finite("যাওয়া", "conjunctive") == "গিয়ে"

    # Lemmatization
    lem_info = conj.lemmatize("করেছেন")
    assert lem_info is not None
    lemma, tense, tier = lem_info
    assert lemma == "করা"
    assert tier == "hon"


def test_bengali_classifier_engine_and_animacy():
    clf_engine = BengaliClassifierEngine()

    # Test attach classifier
    res1 = clf_engine.attach_classifier("বই", "টা")
    assert res1 == "বইটা"

    res2 = clf_engine.attach_classifier("ছাত্র", "জন", count=5)
    assert res2 == "পাঁচজন ছাত্র"

    # Test analysis
    analysis = clf_engine.analyze_classifier("বইখানা")
    assert analysis["has_classifier"] is True
    assert analysis["base_noun"] == "বই"
    assert analysis["classifier"] == "খানা"

    # Test animacy validation
    valid_human, _ = clf_engine.validate_animacy("ছাত্র", "জন")
    assert valid_human is True

    invalid_inanimate, reason = clf_engine.validate_animacy("বই", "জন")
    assert invalid_inanimate is False
    assert "strictly reserved for human" in reason


def test_bengali_case_engine_and_postpositions():
    case_engine = BengaliCaseEngine()

    # Noun inflection: vowel stem vs consonant stem
    # Vowel stem: ছেলে -> ছেলের, বাড়িতে
    assert case_engine.inflect_case("ছেলে", "genitive") == " ছেলের" or case_engine.inflect_case("ছেলে", "genitive") == "ছেলের"
    assert case_engine.inflect_case("বাড়ি", "locative") == "বাড়িতে"

    # Consonant stem: ঘর -> ঘরের, ঘরে
    assert case_engine.inflect_case("ঘর", "genitive") == "ঘরের"
    assert case_engine.inflect_case("ঘর", "locative") == "ঘরে"

    # Pronoun cases
    assert case_engine.inflect_case("আমি", "objective") == "আমাকে"
    assert case_engine.inflect_case("আমি", "genitive") == "আমার"
    assert case_engine.inflect_case("তিনি", "genitive") == "তাঁর"

    # Differential Object Marking
    valid_dom, _ = case_engine.validate_differential_object_marking("রাহুল", is_animate=True, has_ke=True)
    assert valid_dom is True

    invalid_dom, _ = case_engine.validate_differential_object_marking("বই", is_animate=False, has_ke=True)
    assert invalid_dom is False

    # Postposition governance
    valid_gov, _ = case_engine.validate_postposition_governor("আমার", "জন্য")
    assert valid_gov is True

    invalid_gov, _ = case_engine.validate_postposition_governor("বই", "জন্য")
    assert invalid_gov is False


def test_bengali_compound_verbs():
    compound_engine = BengaliCompoundVerbEngine()

    assert compound_engine.is_vector_verb("ফেলা") is True
    assert compound_engine.is_vector_verb("রাখা") is True
    assert compound_engine.is_vector_verb("দেওয়া") is True

    # Compose compound verb: করা + ফেলা -> করে ফেলে
    compound_str = compound_engine.compose_compound("করা", "ফেলা", tense="present_simple", tier="3rd_ord")
    assert compound_str == "করে ফেলে"

    # Analyze compound
    analysis = compound_engine.analyze_compound("লিখে", "রাখলেন")
    assert analysis["is_compound"] is True
    assert analysis["v2_vector_lemma"] == "রাখা"
    assert analysis["semantic_nuance"] == "preparatory_retentive"


def test_bengali_pragmatics_and_guru_chondali():
    prag = BengaliPragmaticsEngine()

    # Superior register
    tokens_sup = ["আপনি", "দয়া", "করে", "বলুন", "।"]
    res_sup = prag.evaluate_pragmatics(tokens_sup)
    assert res_sup["tier"] == "superior"
    assert res_sup["politeness_score"] >= 0.90

    # Intimate register
    tokens_int = ["তুই", "আয়", "রে", "।"]
    res_int = prag.evaluate_pragmatics(tokens_int)
    assert res_int["tier"] == "intimate"

    # Guru-Chondali detection: mixing Sadhu and Cholito
    mixed_tokens = ["তিনি", "তাহাকে", "করছেন", "।"]
    violations = prag.detect_guru_chondali(mixed_tokens)
    assert len(violations) > 0
    assert violations[0]["rule"] == "GURU_CHONDALI_DOSH"


def test_bengali_sentence_generation():
    generator = BengaliGenerator()

    # Generate canonical SOV sentence
    sent = generator.generate_clause(
        verb_lemma="পড়া",
        subject="আমি",
        direct_object="বই",
        classifier="টি",
        tense="present_continuous",
        punctuation="।"
    )
    assert "আমি" in sent
    assert "বইটি" in sent
    assert "পড়ছি" in sent
    assert sent.endswith("।")

    # Generate negative sentence (negation na at the end)
    neg_sent = generator.generate_clause(
        verb_lemma="যাওয়া",
        subject="সে",
        tense="present_simple",
        negative=True,
        punctuation="।"
    )
    assert "যায় না" in neg_sent or "না" in neg_sent
    assert neg_sent.endswith("।")


def test_bengali_cognitive_analyzers():
    clf_analyzer = ClassifierConcordAnalyzer()
    case_analyzer = CasePostpositionAnalyzer()
    hon_analyzer = HonorificRegisterAnalyzer()

    # Test classifier mismatch
    clf_res = clf_analyzer.analyze_sentence("আমি বইটি পড়ছি।")
    assert clf_res["is_valid"] is True

    # Test postposition governance
    case_res = case_analyzer.analyze_sentence("আমার জন্য একটি বই আনো।")
    assert case_res["is_valid"] is True

    # Test honorific mismatch
    hon_res = hon_analyzer.analyze_sentence("আপনি কাল যাস।")
    assert hon_res["is_valid"] is False
    assert len(hon_res["diagnostics"]) > 0


def test_bengali_tasks():
    grammar_task = BengaliGrammarCheckTask()
    email_task = BengaliEmailPipelineTask()
    comp_task = BengaliCompositionPipelineTask()

    # 1. Grammar check
    g_res = grammar_task.run("তিনি একটি বই পড়ছেন।")
    assert g_res["overall_score"] >= 0.80

    # 2. Email pipeline
    email_res = email_task.compose_email(
        recipient_name="অমিত",
        sender_name="রাহুল",
        purpose="meeting",
        tier="superior"
    )
    assert "শ্রদ্ধেয় অমিত মহাশয়," in email_res["full_email"]
    assert "আপনার বিশ্বস্ত" in email_res["full_email"]

    # 3. Composition pipeline
    comp_res = comp_task.compose_narrative(topic="study")
    assert len(comp_res["clauses"]) == 3
    assert "বইটি" in comp_res["composed_prose"]


def test_bengali_sub_ais_and_amsv_bit_isolation():
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))

    syntax_ai = BengaliSyntaxSubAI(amsv_view=amsv)
    phonology_ai = BengaliPhonologySubAI(amsv_view=amsv)
    pragmatic_ai = BengaliPragmaticSubAI(amsv_view=amsv)
    editorial_ai = BengaliEditorialSubAI(amsv_view=amsv)

    initial_bytes = bytes(amsv.get_raw_bytes())
    assert len(initial_bytes) == 64
    assert all(b == 0 for b in initial_bytes)

    # 1. Syntax Sub-AI: writes to Byte 18 (0x12) and Byte 52 (0x34)
    syntax_eval = syntax_ai.evaluate("তিনি একটি চমৎকার বই লিখেছেন।")
    assert syntax_eval.amsv_synced is True
    b_syntax = bytes(amsv.get_raw_bytes())
    assert b_syntax[18] > 0, "Syntax Sub-AI must write to Byte 18"
    assert b_syntax[52] > 0, "Syntax Sub-AI must write to Byte 52"
    assert all(b == 0 for b in b_syntax[0:16]), "Bytes 0..15 must remain pristine"
    assert all(b == 0 for b in b_syntax[20:28]), "Bytes 20..27 must remain pristine"

    # 2. Phonology Sub-AI: writes to Bytes 0..15 and Byte 24 (0x18)
    phono_eval = phonology_ai.evaluate("তিনি একটি চমৎকার বই লিখেছেন।")
    assert phono_eval.amsv_synced is True
    b_phono = bytes(amsv.get_raw_bytes())
    assert any(b > 0 for b in b_phono[0:8]), "Phonology Sub-AI must write to Bytes 0..7"
    assert any(b > 0 for b in b_phono[8:16]), "Phonology Sub-AI must write to Bytes 8..15"
    assert b_phono[24] > 0, "Phonology Sub-AI must write to Byte 24"
    assert b_phono[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_phono[52] == b_syntax[52], "Byte 52 must be preserved"

    # 3. Pragmatic Sub-AI: writes to Byte 22 (0x16) and Byte 54 (0x36)
    prag_eval = pragmatic_ai.evaluate("আপনি দয়া করে বলুন।")
    assert prag_eval.amsv_synced is True
    b_prag = bytes(amsv.get_raw_bytes())
    assert b_prag[22] > 0, "Pragmatic Sub-AI must write to Byte 22"
    assert b_prag[54] > 0, "Pragmatic Sub-AI must write to Byte 54"
    assert b_prag[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_prag[24] == b_phono[24], "Byte 24 must be preserved"

    # 4. Editorial Sub-AI: writes to Byte 20 (0x14) and Byte 26 (0x1A)
    edit_eval = editorial_ai.evaluate("তিনি একটি চমৎকার বই লিখেছেন।")
    assert edit_eval.amsv_synced is True
    b_edit = bytes(amsv.get_raw_bytes())
    assert b_edit[20] > 0, "Editorial Sub-AI must write to Byte 20"
    assert b_edit[26] > 0, "Editorial Sub-AI must write to Byte 26"

    # Bit Isolation Check: Byte 30 and 31 must remain 0
    assert b_edit[30] == 0
    assert b_edit[31] == 0


def test_bengali_six_language_matrix():
    amsv = AMSVEmbeddedView()
    bridge = BengaliMatrixBridge(amsv_view=amsv)

    res = bridge.execute_matrix_pipeline("আমি বইটি পড়েছি।")
    assert res["rust_safety"]["is_safe"] is True
    assert res["cpp_engine"]["has_classifier"] is True
    assert res["cuda_acceleration"]["parallel_batch_supported"] is True
    assert res["java_loom_service"]["direct_byte_buffer_capacity"] == 64
    assert res["amsv_synchronization"]["synced"] is True


def test_bengali_engine_orchestrator_end_to_end():
    orchestrator = BengaliEngineOrchestrator()

    test_sentence = "তিনি পাঁচজন ছাত্রকে একটি নতুন পাঠ শেখালেন।"
    analysis = orchestrator.analyze(test_sentence)

    assert analysis.input_text == test_sentence
    assert len(analysis.tokens) > 0
    assert analysis.syntax_eval.syntactic_integrity_score > 0.6
    assert analysis.overall_linguistic_score > 0.6
    assert analysis.amsv_synced is True

    # Orchestrator convenience wrappers
    proof = orchestrator.proofread(test_sentence)
    assert "overall_score" in proof

    email = orchestrator.compose_email(recipient_name="রহিম", sender_name="করিম", tier="familiar")
    assert "প্রিয় রহিম," in email["full_email"]

    prose = orchestrator.compose_prose()
    assert len(prose["clauses"]) > 0

    gen_sent = orchestrator.generate_sentence(verb_lemma="পড়া", subject="আমি", direct_object="বই", classifier="টি")
    assert gen_sent.endswith("।")
