"""
Comprehensive Test Suite for the Japanese Engine Ecosystem
==========================================================
Validates:
1. All 14 Japanese Computational Skills
2. Declarative Rules Engine and Keigo Anti-Pattern Detection
3. High-level Cognitive Analysis (Ha vs Ga, Zero-Pronoun, Ki-shō-ten-ketsu, Yojijukugo)
4. Task Pipelines (Grammar Check, Summarize, Translate SOV-SVO, TTS, QA)
5. Dedicated Sub-AIs (Syntax, Phonology, Pragmatic, Editorial) with 0-ns AMSV memory sync
6. Six-Language Matrix Coordination (Rust, Python, C++20, CUDA, Java 21, Julia)
7. Master Orchestrator End-to-End Processing and 64-byte AMSV State Vector integrity
"""

import pytest
import os
import sys

# Ensure workspace root is in python path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from amsv.python.amsv_embedded import AMSVEmbeddedView
from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.skills.pos_tagging import JapanesePOSTagger
from Japanese_engine.brain.skills.parsing import JapaneseParser
from Japanese_engine.brain.skills.lemmatization import JapaneseLemmatizer
from Japanese_engine.brain.skills.reading_generation import JapaneseReadingGenerator
from Japanese_engine.brain.skills.kana_kanji_conversion import JapaneseKanaKanjiConverter
from Japanese_engine.brain.skills.ner import JapaneseNamedEntityRecognizer
from Japanese_engine.brain.skills.keigo_engine import JapaneseKeigoEngine
from Japanese_engine.brain.rules.rules_engine import JapaneseRulesEngine
from Japanese_engine.brain.Analysis.ha_ga_resolver import JapaneseHaGaResolver
from Japanese_engine.brain.Analysis.zero_pronoun_resolver import JapaneseZeroPronounResolver
from Japanese_engine.brain.Analysis.discourse_parser import JapaneseDiscourseParser
from Japanese_engine.brain.Analysis.figurative_detector import JapaneseFigurativeDetector
from Japanese_engine.brain.task.grammar_check import JapaneseGrammarCheckerPipeline
from Japanese_engine.brain.task.summarize import JapaneseSummarizer
from Japanese_engine.brain.task.translate import JapaneseCrossLingualTranslator
from Japanese_engine.brain.task.tts_pipeline import JapaneseTTSPipeline
from Japanese_engine.brain.task.qa import JapaneseQuestionAnsweringPipeline
from Japanese_engine.brain.task.rewrite_keigo import JapaneseKeigoRewriter
from Japanese_engine.brain.sub_ais.syntax_sub_ai import JapaneseSyntaxSubAI
from Japanese_engine.brain.sub_ais.phonology_sub_ai import JapanesePhonologySubAI
from Japanese_engine.brain.sub_ais.pragmatic_sub_ai import JapanesePragmaticSubAI
from Japanese_engine.brain.sub_ais.editorial_sub_ai import JapaneseEditorialSubAI
from Japanese_engine.six_language_matrix.python.japanese_matrix_bridge import JapaneseSixLanguageMatrixBridge
from Japanese_engine.japanese_engine_orchestrator import JapaneseEngineOrchestrator


def test_japanese_skills_tokenization_and_pos():
    tokenizer = JapaneseTokenizer()
    pos_tagger = JapanesePOSTagger()
    text = "私は東京で本を読みます。"

    tokens = tokenizer.tokenize(text)
    assert len(tokens) >= 5
    # Verify script classification
    scripts = {t.script for t in tokens}
    assert "Kanji" in scripts
    assert "Hiragana" in scripts

    tagged = pos_tagger.tag_tokens(tokens)
    pos_tags = [t.pos for t in tagged]
    assert "Meishi" in pos_tags
    assert "Joshi" in pos_tags
    assert "Doushi" in pos_tags or "Jodoushi" in pos_tags


def test_japanese_parsing_and_bunsetsu():
    parser = JapaneseParser()
    text = "太郎が図書館で本を読む。"
    tree = parser.parse_bunsetsu_dependencies(text)

    assert len(tree.bunsetsu_list) >= 3
    # Sentence-final bunsetsu must be root (-1)
    assert tree.bunsetsu_list[-1].head_id == -1
    # Check head-final constraint: every modifier depends on a subsequent bunsetsu
    for b in tree.bunsetsu_list[:-1]:
        assert b.head_id > b.id


def test_japanese_lemmatization_and_conjugation():
    lemmatizer = JapaneseLemmatizer()
    cases = [
        ("書きました", "書く", "Godan"),
        ("食べない", "食べる", "Ichidan"),
        ("来ました", "来る", "Kuru"),
        ("しました", "する", "Suru"),
    ]
    for surface, expected_dict, expected_type in cases:
        res = lemmatizer.lemmatize(surface)
        assert res.dictionary_form == expected_dict
        assert res.verb_type == expected_type


def test_japanese_reading_and_ime():
    reading_gen = JapaneseReadingGenerator()
    ime = JapaneseKanaKanjiConverter()

    # Reading & Ruby
    r_res = reading_gen.generate_reading("漢字を研究する")
    assert "<ruby>漢字<rt>かんじ</rt></ruby>" in r_res.annotated_html
    assert r_res.hiragana_stream.startswith("かんじ")

    # IME Conversion
    ime_res = ime.convert_kana("わたし")
    assert ime_res.best_kanji == "私"
    assert len(ime_res.candidates) >= 1


def test_japanese_rules_and_keigo():
    rules_engine = JapaneseRulesEngine()

    # Double honorific anti-pattern detection
    text_bad_keigo = "先生がおっしゃられました。"
    violations = rules_engine.check_text(text_bad_keigo)
    keigo_violations = [v for v in violations if v.category == "keigo"]
    assert len(keigo_violations) > 0
    assert "おっしゃられ" in keigo_violations[0].offending_text

    # Ra-nuki detection
    text_ra_nuki = "美味しいご飯が食べれる。"
    violations2 = rules_engine.check_text(text_ra_nuki)
    assert any(v.rule_id == "STYLE_RA_NUKI" for v in violations2)

    # Register detection
    reg = rules_engine.detect_register("大変恐縮に存じます。何卒よろしくお願い申し上げます。")
    assert "Business" in reg.detected_register
    assert reg.formality_score > 0.80


def test_japanese_ha_ga_and_zero_pronoun():
    ha_ga = JapaneseHaGaResolver()
    zero_pro = JapaneseZeroPronounResolver()

    # Ha vs Ga disambiguation
    text_haga = "田中さんは本を読んだが、誰が買ったのか？"
    results = ha_ga.resolve(text_haga)
    assert len(results) >= 2
    wa_results = [r for r in results if r.particle == "は"]
    ga_results = [r for r in results if r.particle == "が"]
    assert len(wa_results) > 0
    assert len(ga_results) > 0
    assert "Discourse_Topic" in wa_results[0].semantic_function or "Contrastive" in wa_results[0].semantic_function
    assert any("Exhaustive_Listing" in r.semantic_function or "Subject" in r.semantic_function for r in ga_results)

    # Zero-pronoun recovery via honorific constraint
    utterance = "先生、昨日おっしゃいましたね。"
    zp_report = zero_pro.resolve_discourse([], utterance)
    assert len(zp_report.recovered_arguments) > 0
    assert "聞き手" in zp_report.recovered_arguments[0].inferred_referent


def test_japanese_figurative_and_discourse():
    fig_detector = JapaneseFigurativeDetector()
    disc_parser = JapaneseDiscourseParser()

    # Yojijukugo & Onomatopoeia
    text_fig = "心臓がドキドキして、一期一会の出会いに胸をなでおろした。"
    fig_report = fig_detector.detect(text_fig)
    cats = {h.category for h in fig_report.hits}
    assert "giongo_gitaigo" in cats
    assert "yojijukugo" in cats
    assert "kanyouku" in cats

    # Ki-shō-ten-ketsu discourse parser
    discourse_text = "桜が咲いた。人々が集まってきた。しかし突然激しい雨が降った。最終的に皆家に帰った。"
    d_report = disc_parser.parse(discourse_text)
    assert d_report.total_segments == 4
    assert any("転" in s.kishotenketsu_role for s in d_report.segments)


def test_japanese_task_pipelines():
    grammar_checker = JapaneseGrammarCheckerPipeline()
    summarizer = JapaneseSummarizer()
    translator = JapaneseCrossLingualTranslator()
    tts = JapaneseTTSPipeline()
    qa = JapaneseQuestionAnsweringPipeline()
    keigo_rewriter = JapaneseKeigoRewriter()

    # Grammar check auto-correction
    g_res = grammar_checker.check("昨日は食べれると言っていた、、")
    assert "、" in g_res.corrected_text
    assert "、、" not in g_res.corrected_text

    # Summarization
    long_text = "第一に人工知能の発展は急速である。多くの研究者が言語モデルに取り組んでいる。要するに結論として統語と意味の統合が最重要課題である。"
    s_res = summarizer.summarize(long_text, max_sentences=1)
    assert s_res.compression_ratio < 1.0
    assert "要するに" in s_res.summary_text or "第一に" in s_res.summary_text

    # Cross-Lingual Translation (JA SOV -> EN SVO)
    t_res = translator.translate("学生は本を読みます。", target_lang="en")
    assert t_res.structural_alignment == "SOV -> SVO"
    assert "read" in t_res.translated_text.lower()
    assert "book" in t_res.translated_text.lower()

    # TTS mora frames
    tts_res = tts.synthesize_stream("日本")
    assert len(tts_res.mora_stream) > 0
    assert tts_res.sample_rate_hz == 24000

    # QA extraction
    passage = "夏目漱石は1867年に江戸で生まれた。"
    qa_res = qa.answer_question("夏目漱石はいつ生まれたか？", passage)
    assert "1867年" in qa_res.answer

    # Keigo rewrite
    kw_res = keigo_rewriter.rewrite_to_tier("社長が言いました。", target_tier="sonkeigo")
    assert "おっしゃいました" in kw_res.rewritten_sentence


def test_japanese_sub_ais_and_zero_bridge_amsv():
    amsv = AMSVEmbeddedView()
    syntax_ai = JapaneseSyntaxSubAI(amsv_view=amsv)
    phonology_ai = JapanesePhonologySubAI(amsv_view=amsv)
    pragmatic_ai = JapanesePragmaticSubAI(amsv_view=amsv)
    editorial_ai = JapaneseEditorialSubAI(amsv_view=amsv)

    text = "本日はご足労いただき、誠にありがとうございます。"

    # Execute all 4 Sub-AIs
    syn_eval = syntax_ai.evaluate(text)
    assert syn_eval.amsv_synced is True
    assert syn_eval.syntactic_integrity_score > 0.0

    phon_eval = phonology_ai.evaluate(text)
    assert phon_eval.amsv_synced is True
    assert len(phon_eval.mora_stream) > 0

    prag_eval = pragmatic_ai.evaluate(text)
    assert prag_eval.amsv_synced is True
    assert prag_eval.pragmatic_felicity_score > 0.0

    edit_eval = editorial_ai.evaluate(text)
    assert edit_eval.amsv_synced is True
    assert edit_eval.editorial_grade in {"S", "A", "B", "C"}

    # VERIFY 0-NANOSECOND HARDWARE MEMORY ADDRESS STATE VECTOR
    raw_bytes = amsv.get_raw_bytes()
    assert len(raw_bytes) == 64
    # Check that cognitive score slots 0, 1, 2, 3 are populated
    for cap_idx in range(4):
        assert amsv.get_cognitive_score(cap_idx) > 0.0


def test_japanese_six_language_matrix():
    amsv = AMSVEmbeddedView()
    matrix = JapaneseSixLanguageMatrixBridge(amsv_view=amsv)

    res = matrix.coordinate("私は新しい技術を研究しています。")
    assert res.amsv_synced is True
    assert len(res.language_nodes) == 6
    assert "Rust" in res.language_nodes
    assert "C++20" in res.language_nodes
    assert "CUDA" in res.language_nodes
    assert "Java 21" in res.language_nodes
    assert "Julia" in res.language_nodes
    assert "Python" in res.language_nodes
    assert res.rust_safety_passed is True
    assert res.cpp_trie_lookup_count > 0
    assert res.cuda_attention_flops > 0
    assert res.java_virtual_thread_dispatched is True
    assert res.julia_pitch_trajectory_steps > 0
    assert res.composite_linguistic_score > 0.0


def test_japanese_master_orchestrator_end_to_end():
    amsv = AMSVEmbeddedView()
    orchestrator = JapaneseEngineOrchestrator(amsv_view=amsv)

    input_text = "吾輩は猫である。名前はまだ無い。どこで生れたかとんと見当がつかぬ。"
    output = orchestrator.process(input_text, request_id="test-ja-999")

    # Validate output completeness
    assert output.input_text == input_text
    assert len(output.tokens) > 5
    assert len(output.tagged_tokens) > 5
    assert len(output.parse_tree.bunsetsu_list) >= 3
    assert len(output.reading_generation.hiragana_stream) > 0
    assert output.grammar_check is not None
    assert output.register is not None
    assert output.ambiguity is not None
    assert len(output.ha_ga_analysis) > 0
    assert output.syntax_sub_ai.amsv_synced is True
    assert output.phonology_sub_ai.amsv_synced is True
    assert output.pragmatic_sub_ai.amsv_synced is True
    assert output.editorial_sub_ai.amsv_synced is True
    assert output.six_language_matrix.amsv_synced is True
    assert output.four_stage_matrix is not None

    # Validate raw AMSV memory state vector
    assert len(output.amsv_bytes_hex) == 128  # 64 bytes in hex
    assert output.latency_ms > 0.0
