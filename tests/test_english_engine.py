"""
Unit and Integration Test Suite for the English Engine Ecosystem.
Validates:
1. All 11 Cognitive and Linguistic Skills
2. Declarative Rules and Register Detection
3. High-level Cognitive Analysis Modules (Ambiguity, RST, Figurative, Speech Acts, Presupposition, Drift)
4. Task Pipelines (Grammar check, Summarize, Translate, TTS, STT, QA, Rewrite)
5. Dedicated Sub-AIs with 0-nanosecond AMSV physical memory writes
6. Six-Language Matrix Bridge (Rust, Python, C++, CUDA, Java, Julia)
7. Master Orchestrator with Reusable Four-Stage Pattern execution
8. Layers 1 through 9 structural artifacts integrity
"""

import os
import json
import yaml
import pytest
from typing import Dict, Any

from amsv.python.amsv_embedded import AMSVEmbeddedView
from English_engine import EnglishEngineOrchestrator, EnglishEngineComprehensiveOutput
from English_engine.brain.skills import (
    EnglishTokenizer,
    EnglishPOSTagger,
    EnglishParser,
    EnglishLemmatizer,
    EnglishNamedEntityRecognizer,
    EnglishCoreferenceResolver,
    EnglishSemanticRoleLabeler,
    EnglishSentimentClassifier,
    EnglishG2PConverter,
    EnglishSTTDecoder,
    EnglishTextGenerator,
)
from English_engine.brain.rules import RulesEngine
from English_engine.brain.Analysis import (
    AmbiguityRanker,
    DiscourseParser,
    FigurativeDetector,
    IntentMapper,
    PresuppositionChecker,
    DriftMonitor,
)
from English_engine.brain.task import (
    GrammarCheckerPipeline,
    Summarizer,
    CrossLingualTranslator,
    TTSPipeline,
    STTPipeline,
    QuestionAnsweringEngine,
    RegisterRewriter,
)
from English_engine.brain.sub_ais import (
    EnglishSyntaxSubAI,
    EnglishPhonologySubAI,
    EnglishPragmaticSubAI,
    EnglishEditorialSubAI,
)
from English_engine.six_language_matrix import EnglishSixLanguageMatrixBridge


@pytest.fixture
def amsv_fixture():
    buf = bytearray(64)
    return AMSVEmbeddedView(memoryview(buf))


@pytest.fixture
def orchestrator(amsv_fixture):
    return EnglishEngineOrchestrator(amsv_view=amsv_fixture)


# ---------------------------------------------------------------------------
# 1. Test Skills Layer
# ---------------------------------------------------------------------------
def test_tokenization_and_pos_tagging():
    tokenizer = EnglishTokenizer()
    tagger = EnglishPOSTagger()
    tokens = tokenizer.tokenize("The quick brown fox jumps over the lazy dog.")
    assert len(tokens) >= 9
    tagged = tagger.tag_tokens(tokens)
    assert len(tagged) == len(tokens)
    assert any(t.penn_tag.startswith("NN") for t in tagged)
    assert any(t.penn_tag.startswith("VB") for t in tagged)


def test_parser_and_lemmatization():
    tokenizer = EnglishTokenizer()
    tagger = EnglishPOSTagger()
    parser = EnglishParser()
    lemmatizer = EnglishLemmatizer()

    tokens = tokenizer.tokenize("She is running fast.")
    tagged = tagger.tag_tokens(tokens)
    dep_tree = parser.parse_dependencies(tagged)
    assert dep_tree.root is not None
    const_tree = parser.parse_constituency(tagged)
    assert const_tree.category == "S"

    lemma = lemmatizer.lemmatize("running", pos="v")
    assert lemma.lemma == "run"


def test_ner_srl_coreference_sentiment():
    ner = EnglishNamedEntityRecognizer()
    entities = ner.recognize("Alan Turing founded computer science in London in 1936.")
    assert any(e.entity_type == "PERSON" and "Turing" in e.text for e in entities)
    assert any(e.entity_type == "GPE" and "London" in e.text for e in entities)

    srl = EnglishSemanticRoleLabeler()
    frames = srl.label_roles("The engineer built the compiler.")
    assert len(frames) > 0
    assert frames[0].predicate == "built"

    coref = EnglishCoreferenceResolver()
    chains = coref.resolve("Marie Curie was a scientist. She won two Nobel prizes.")
    assert len(chains) > 0

    sentiment = EnglishSentimentClassifier()
    res = sentiment.classify("This grammar engine is exceptionally accurate and fast.")
    assert res.sentiment == "POSITIVE"
    assert res.valence > 0.6


def test_g2p_stt_generation():
    g2p = EnglishG2PConverter()
    res = g2p.convert_word("thought")
    assert "TH" in res.phonemes

    decoder = EnglishSTTDecoder()
    stt_res = decoder.decode(["DH", "AH0", "K", "AE1", "T"])
    assert "the cat" in stt_res.decoded_text.lower()

    gen = EnglishTextGenerator()
    out = gen.generate(subject="The model", verb="converged", form="interrogative")
    assert out.endswith("?")


# ---------------------------------------------------------------------------
# 2. Test Rules & Analysis Layer
# ---------------------------------------------------------------------------
def test_rules_engine_and_register():
    rules_engine = RulesEngine()
    violations = rules_engine.check_text("In order to achieve implementation, he do not care.")
    assert len(violations) > 0
    assert any(v.category == "style" for v in violations)

    reg = rules_engine.detect_register("Furthermore, we hypothesize that the empirical results substantiate our thesis.")
    assert reg.detected_register == "Formal Academic"
    assert reg.formality_score > 0.75


def test_cognitive_analysis_modules():
    ambig_ranker = AmbiguityRanker()
    ambig_rep = ambig_ranker.analyze("The scientist observed the star with a telescope.")
    assert ambig_rep.total_ambiguities >= 1

    disc_parser = DiscourseParser()
    tree = disc_parser.parse("Because latency was low, throughput doubled. However, power draw increased.")
    assert len(tree.edus) >= 2
    assert len(tree.relations) >= 1

    fig_det = FigurativeDetector()
    fig_rep = fig_det.analyze("Time is money, so don't spill the beans.")
    assert fig_rep.figurative_count >= 2

    intent_map = IntentMapper()
    intent = intent_map.classify("Could you please analyze this dataset?")
    assert intent.primary_speech_act == "Directive"

    presupp_checker = PresuppositionChecker()
    presupp = presupp_checker.analyze("He realized that the experiment was flawed.")
    assert len(presupp.triggers) >= 1

    drift = DriftMonitor()
    d_res = drift.compute_metrics("The quick brown fox jumps over the lazy dog.")
    assert d_res.status == "stable"


# ---------------------------------------------------------------------------
# 3. Test Task Pipelines
# ---------------------------------------------------------------------------
def test_task_pipelines():
    grammar = GrammarCheckerPipeline()
    g_res = grammar.check("He have a problem at this point in time.")
    assert g_res.total_issues > 0

    summarizer = Summarizer()
    text = (
        "Artificial intelligence is transforming linguistics. "
        "State vectors provide 0-nanosecond physical memory synchronization. "
        "High-performance parsers execute with deterministic precision. "
        "Consequently, language models achieve extraordinary coherence."
    )
    s_res = summarizer.summarize(text, max_words=15)
    assert s_res.summary_word_count <= 25
    assert len(s_res.selected_sentence_indices) >= 1

    translator = CrossLingualTranslator()
    t_res = translator.translate("the student read book", target_lang="hi")
    assert t_res.target_language == "hi"

    tts = TTSPipeline()
    tts_res = tts.synthesize_stream("Hello world.")
    assert "<speak" in tts_res.ssml
    assert len(tts_res.phoneme_stream) > 0

    stt = STTPipeline()
    stt_res = stt.process_phonemes(["DH", "AH0", "B", "UH1", "K"])
    assert len(stt_res.transcription) > 0

    qa = QuestionAnsweringEngine()
    passage = "Alan Turing was born in London. He designed the Turing machine."
    qa_res = qa.answer_question(passage, "Where was Alan Turing born?")
    assert "London" in qa_res.best_answer

    rewriter = RegisterRewriter()
    rw_res = rewriter.rewrite("He gonna figure out what's up.", target_register="formal_academic")
    assert "going to" in rw_res.rewritten_text


# ---------------------------------------------------------------------------
# 4. Test Sub-AIs & Zero-Bridge Synchronous Memory (AMSV)
# ---------------------------------------------------------------------------
def test_sub_ais_and_amsv_memory(amsv_fixture):
    syntax_ai = EnglishSyntaxSubAI(amsv_view=amsv_fixture)
    phonology_ai = EnglishPhonologySubAI(amsv_view=amsv_fixture)
    pragmatic_ai = EnglishPragmaticSubAI(amsv_view=amsv_fixture)
    editorial_ai = EnglishEditorialSubAI(amsv_view=amsv_fixture)

    text = "The architect designed a scalable distributed system."
    syn_eval = syntax_ai.evaluate(text)
    assert syn_eval.amsv_synced
    assert amsv_fixture.get_global_structural_score() > 0.0

    phon_eval = phonology_ai.evaluate(text)
    assert phon_eval.amsv_synced
    assert amsv_fixture.get_phoneme_state() != 0
    assert amsv_fixture.get_prosody_state() != 0

    prag_eval = pragmatic_ai.evaluate(text)
    assert prag_eval.amsv_synced
    assert amsv_fixture.get_global_register_score() > 0.0

    edit_eval = editorial_ai.evaluate(text)
    assert edit_eval.amsv_synced
    assert amsv_fixture.get_cognitive_score(2) > 0.0
    assert amsv_fixture.get_cognitive_score(5) > 0.0

    raw_bytes = amsv_fixture.get_raw_bytes()
    assert len(raw_bytes) == 64
    assert any(b != 0 for b in raw_bytes)


# ---------------------------------------------------------------------------
# 5. Test Six-Language Matrix Bridge
# ---------------------------------------------------------------------------
def test_six_language_matrix_bridge(amsv_fixture):
    bridge = EnglishSixLanguageMatrixBridge(amsv_view=amsv_fixture)
    res = bridge.coordinate("The system executes with maximum efficiency.", request_id="req-test-99")
    assert len(res.language_nodes) == 6
    assert "Rust" in res.language_nodes
    assert "Julia" in res.language_nodes
    assert "C++20" in res.language_nodes
    assert "CUDA" in res.language_nodes
    assert "Java 21" in res.language_nodes
    assert "Python" in res.language_nodes
    assert res.rust_safety_passed
    assert res.amsv_synced
    assert res.composite_linguistic_score > 0.0


# ---------------------------------------------------------------------------
# 6. Test Master Orchestrator and Four-Stage Reusable Matrix
# ---------------------------------------------------------------------------
def test_master_orchestrator(orchestrator):
    text = (
        "Furthermore, the transformer architecture utilizes self-attention to capture "
        "long-range dependencies in textual sequences. It was introduced in 2017."
    )
    result = orchestrator.process(text, request_id="orchestrator-test-01")

    assert isinstance(result, EnglishEngineComprehensiveOutput)
    assert len(result.tokens) > 10
    assert result.parse_tree is not None
    assert result.grammar_check.grammar_score > 70.0
    assert result.syntax_sub_ai.amsv_synced
    assert result.phonology_sub_ai.amsv_synced
    assert result.pragmatic_sub_ai.amsv_synced
    assert result.editorial_sub_ai.amsv_synced
    assert result.six_language_matrix.amsv_synced

    # Four-stage matrix check
    fsm = result.four_stage_matrix
    assert fsm["status"] == "COMPLETED"
    assert len(fsm["stage3_connected_groups"]["cyclic_feedback_loop_history"]) > 0
    assert len(fsm["stage4_execution_pipeline"]["recursive_feedback_history"]) > 0
    assert fsm["amsv_synchronized"] is True

    # Check 64-byte AMSV state
    assert len(result.amsv_bytes_hex) == 128  # 64 bytes in hex string is 128 chars


# ---------------------------------------------------------------------------
# 7. Test Structural Concrete Layers 1 to 9 Files
# ---------------------------------------------------------------------------
def test_layers_1_to_9_structural_files():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "English_engine")

    # Layer 1
    ptb_path = os.path.join(base_dir, "1_SYNTACTIC_STRUCTURE_(Sentence_Layer)", "1.1_PARTS_OF_SPEECH", "penn_treebank_tagset.json")
    assert os.path.exists(ptb_path)
    with open(ptb_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "tags" in data

    # Layer 2
    roots_path = os.path.join(base_dir, "2_MORPHOLOGICAL_ANALYSIS_(Word_Layer)", "2.2_MORPHEME_LEXICON", "roots_latin_greek_anglosaxon.json")
    assert os.path.exists(roots_path)

    # Layer 3
    ipa_path = os.path.join(base_dir, "3_PHONOLOGICAL_ORTHOGRAPHIC_(Text_Sound_Layer)", "3.1_PHONEMES", "ipa_to_arpabet_mapping.json")
    assert os.path.exists(ipa_path)

    # Layer 4
    wordnet_path = os.path.join(base_dir, "4_SEMANTIC_REPRESENTATION_(Meaning_Layer)", "4.1_LEXICAL_SEMANTICS", "wordnet_synsets_core.json")
    assert os.path.exists(wordnet_path)

    # Layer 5
    metaphor_path = os.path.join(base_dir, "5_PRAGMATIC_(Use_Layer)", "5.3_FIGURATIVE_LANGUAGE", "conceptual_metaphor_inventory.json")
    assert os.path.exists(metaphor_path)

    # Layer 6
    corpus_path = os.path.join(base_dir, "6_DATA_REQUIREMENTS", "6.1_CORPORA", "corpus_manifest.json")
    assert os.path.exists(corpus_path)

    # Layer 7
    pipeline_path = os.path.join(base_dir, "7_ALGORITHMS", "7.1_PARSING_PIPELINE", "pipeline_architecture.json")
    assert os.path.exists(pipeline_path)

    # Layer 8
    dialect_path = os.path.join(base_dir, "8_EVOLUTION_VARIATION", "8.1_DIALECT_PROFILES", "dialect_matrices.json")
    assert os.path.exists(dialect_path)

    # Layer 9
    config_path = os.path.join(base_dir, "9_CONFIG", "three_questions.yaml")
    assert os.path.exists(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
        assert "three_questions" in cfg
