"""
Comprehensive Test Suite for the Mandarin Engine Ecosystem
==========================================================
Validates:
1. All Mandarin Computational Skills (Tokenization, POS, Parsing, Pinyin/Tone, Chengyu, Classifiers, Mianzi, Generation)
2. Cognitive Analysis Modules (Topic-Comment, Tone Sandhi, Classifier Agreement)
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
from Mandarin_engine.brain.skills.tokenization import MandarinTokenizer, MandarinToken
from Mandarin_engine.brain.skills.pos_tagging import MandarinPOSTagger
from Mandarin_engine.brain.skills.parsing import MandarinParser
from Mandarin_engine.brain.skills.pinyin_tone import PinyinToneEngine
from Mandarin_engine.brain.skills.chengyu_engine import ChengyuEngine
from Mandarin_engine.brain.skills.classifier_engine import ClassifierEngine
from Mandarin_engine.brain.skills.sentiment_mianzi import MianziPragmaticSkill
from Mandarin_engine.brain.skills.generation import MandarinGenerator

from Mandarin_engine.brain.analysis.topic_comment_analyzer import TopicCommentAnalyzer
from Mandarin_engine.brain.analysis.tone_sandhi_verifier import ToneSandhiVerifier
from Mandarin_engine.brain.analysis.classifier_agreement_checker import ClassifierAgreementChecker

from Mandarin_engine.brain.task.grammar_check import MandarinGrammarChecker
from Mandarin_engine.brain.task.email_pipeline import MandarinEmailPipeline
from Mandarin_engine.brain.task.composition_pipeline import MandarinCompositionPipeline

from Mandarin_engine.brain.sub_ais.syntax_sub_ai import MandarinSyntaxSubAI
from Mandarin_engine.brain.sub_ais.phonology_sub_ai import MandarinPhonologySubAI
from Mandarin_engine.brain.sub_ais.pragmatic_sub_ai import MandarinPragmaticSubAI
from Mandarin_engine.brain.sub_ais.editorial_sub_ai import MandarinEditorialSubAI

from Mandarin_engine.six_language_matrix.python.mandarin_matrix_bridge import (
    MandarinSixLanguageMatrixBridge,
    MandarinSixLanguageExecutionResult,
)
from Mandarin_engine.mandarin_engine_orchestrator import MandarinEngineOrchestrator


def test_mandarin_tokenizer_and_token_spans():
    tokenizer = MandarinTokenizer()
    text = "我把作业写完了。"
    tokens = tokenizer.tokenize(text)

    assert len(tokens) >= 5
    surfaces = [t.text for t in tokens]
    assert "我" in surfaces
    assert "把" in surfaces
    assert "作业" in surfaces
    assert "写" in surfaces
    assert "完了" in surfaces or ("完" in surfaces and "了" in surfaces)

    # Check MandarinToken dataclass spans & types
    for tok in tokens:
        assert isinstance(tok, MandarinToken)
        assert tok.char_start < tok.char_end
        assert tok.char_end <= len(text)
        assert tok.script_type in {"HANZI", "PUNCT", "ASCII", "OTHER"}

    stats = tokenizer.get_character_stats(text)
    assert stats["cjk_character_count"] >= 7
    assert stats["cjk_ratio"] > 0.8


def test_mandarin_pos_tagging():
    tokenizer = MandarinTokenizer()
    tagger = MandarinPOSTagger()
    text = "老师在教室里看书"
    tokens = tokenizer.segment(text)
    tagged = tagger.tag(tokens)

    assert len(tagged) == len(tokens)
    tag_map = dict(tagged)
    assert tag_map.get("老师") == "NN"
    assert tag_map.get("在") in {"P", "VV"}
    assert tag_map.get("看") == "VV"
    assert tag_map.get("书") == "NN"


def test_mandarin_parsing_ba_and_bei():
    parser = MandarinParser()

    # Test 把 (disposal) construction
    ba_tags = [("我", "PN"), ("把", "BA"), ("作业", "NN"), ("写", "VV"), ("了", "AS")]
    ba_parsed = parser.parse(ba_tags)
    assert ba_parsed.is_ba_construction is True
    assert ba_parsed.ba_disposed_object == "作业"
    assert ba_parsed.aspect_markers == ["了"]

    # Test 被 (passive) construction
    bei_tags = [("苹果", "NN"), ("被", "LB"), ("他", "PN"), ("吃", "VV"), ("了", "AS")]
    bei_parsed = parser.parse(bei_tags)
    assert bei_parsed.is_bei_construction is True
    assert bei_parsed.bei_agent == "他"


def test_mandarin_pinyin_and_tone_sandhi():
    engine = PinyinToneEngine()

    # Test 3rd tone sandhi: 你好 (3 + 3 -> 2 + 3: nǐ hǎo -> ní hǎo)
    raw = engine.text_to_pinyin_string("你好", apply_sandhi=False)
    sandhi = engine.text_to_pinyin_string("你好", apply_sandhi=True)
    assert "nǐ" in raw
    assert "ní" in sandhi
    assert "hǎo" in sandhi

    # Test 一 sandhi before 4th tone (e.g., 一个 -> yí gè)
    yi_sandhi = engine.text_to_pinyin_string("一个", apply_sandhi=True)
    assert "yí" in yi_sandhi

    # Test 不 sandhi before 4th tone (e.g., 不是 -> bú shì)
    bu_sandhi = engine.text_to_pinyin_string("不是", apply_sandhi=True)
    assert "bú" in bu_sandhi


def test_mandarin_chengyu_engine():
    engine = ChengyuEngine()
    text = "做事不能半途而废，要循序渐进才能水到渠成。"
    res = engine.evaluate_density(text)

    assert res["idiom_count"] == 3
    assert "半途而废" in res["detected_idioms"]
    assert "循序渐进" in res["detected_idioms"]
    assert "水到渠成" in res["detected_idioms"]
    assert res["stylistic_level"] in {"Wenyan-Influenced", "Classical/Scholarly", "Highly Literary / Scholarly (典雅)"}


def test_mandarin_classifier_engine():
    clf_engine = ClassifierEngine()

    # Valid collocations
    v1 = clf_engine.verify_collocation("本", "书")
    assert v1["is_valid"] is True

    v2 = clf_engine.verify_collocation("张", "桌子")
    assert v2["is_valid"] is True

    v3 = clf_engine.verify_collocation("只", "猫")
    assert v3["is_valid"] is True

    # Invalid collocation
    v4 = clf_engine.verify_collocation("条", "书")
    assert v4["is_valid"] is False
    assert "本" in v4["recommended_classifiers"]


def test_mandarin_mianzi_and_pragmatics():
    skill = MianziPragmaticSkill()

    # High politeness with honorific 您 and indirect refusal
    polite_text = "您好，非常感谢您的邀请，但是我们目前可能不太方便。"
    p_res = skill.evaluate_mianzi(polite_text)
    assert p_res["politeness_level"] == "High"
    assert p_res["has_indirect_refusal"] is True
    assert p_res["face_preservation_score"] >= 0.85

    # Plain text
    plain_text = "我去看书。"
    pl_res = skill.evaluate_mianzi(plain_text)
    assert pl_res["politeness_level"] == "Neutral"
    assert pl_res["has_indirect_refusal"] is False


def test_mandarin_generation():
    gen = MandarinGenerator()

    # SVO with aspect marker 了
    s1 = gen.generate(subject="他", verb="写", obj="作业", aspect="了")
    assert s1 == "他写了作业。"

    # 把 construction
    s2 = gen.generate(subject="我", verb="做", obj="报告", is_ba=True)
    assert "把报告" in s2

    # Polite request with 请
    s3 = gen.generate(subject="您", verb="看", obj="书", polite=True)
    assert s3.startswith("请")


def test_mandarin_cognitive_analysis():
    tc_analyzer = TopicCommentAnalyzer()
    sandhi_verifier = ToneSandhiVerifier()
    clf_checker = ClassifierAgreementChecker()

    # Topic-Comment analysis
    tc_res = tc_analyzer.analyze("北京，我很喜欢去旅游。")
    assert tc_res["is_topic_comment"] is True
    assert tc_res["topic"] == "北京"
    assert tc_res["syntactic_harmony"] == "Topic-Prominent"

    # Tone Sandhi verification
    sandhi_res = sandhi_verifier.verify_sandhi("你好，我也很好。")
    assert sandhi_res["has_sandhi"] is True
    assert sandhi_res["sandhi_count"] >= 1

    # Classifier Agreement check
    c_res = clf_checker.check_phrase("两", "只", "书")
    assert c_res["is_correct"] is False
    assert c_res["suggested_correction"] == "两本书"


def test_mandarin_tasks():
    grammar_checker = MandarinGrammarChecker()
    email_pipeline = MandarinEmailPipeline()
    composition_pipeline = MandarinCompositionPipeline()

    # Grammar check on valid text
    g_res = grammar_checker.check_text("我把报告完成了。")
    assert g_res["is_grammatically_sound"] is True
    assert g_res["is_ba"] is True

    # Email generator
    email_res = email_pipeline.generate_email(
        recipient_name="李",
        recipient_title="教授",
        topic="项目合作方案",
        body_content="请审阅附件中的初步大纲。",
        sender_name="张三",
        formal=True
    )
    assert "李教授" in email_res["full_email"]
    assert "顺祝商祺" in email_res["full_email"]
    assert email_res["is_formal"] is True

    # Composition generator
    comp_res = composition_pipeline.compose_statement(
        subject="我们",
        verb="学",
        obj="汉语",
        aspect="了",
        chengyu_focus="水到渠成",
        polite=False
    )
    assert "水到渠成" in comp_res["composed_text"]
    assert len(comp_res["tokens"]) >= 3


def test_mandarin_sub_ais_and_amsv_bit_isolation():
    """
    CRITICAL ZERO-BRIDGE TEST:
    Validates that each Sub-AI updates strictly its designated byte offsets in the 64-byte AMSV
    with zero unintended bit contamination or cross-subsystem bleeding.
    """
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))

    syntax_ai = MandarinSyntaxSubAI(amsv_view=amsv)
    phonology_ai = MandarinPhonologySubAI(amsv_view=amsv)
    pragmatic_ai = MandarinPragmaticSubAI(amsv_view=amsv)
    editorial_ai = MandarinEditorialSubAI(amsv_view=amsv)

    # Initial state: clean 64 zeros
    initial_bytes = bytes(amsv.get_raw_bytes())
    assert len(initial_bytes) == 64
    assert all(b == 0 for b in initial_bytes)

    # 1. Execute Syntax Sub-AI:
    # Must write to Byte 18 (0x12, Cognitive Capability 1) and Byte 52 (0x34, Global Structural Score).
    # Must NOT touch Bytes 0..15, Bytes 20..26, or Bytes 56..63.
    syntax_eval = syntax_ai.evaluate("我把作业写完了。")
    assert syntax_eval.has_ba_construction is True
    b_syntax = bytes(amsv.get_raw_bytes())

    assert b_syntax[18] > 0, "Syntax Sub-AI must write to Byte 18"
    assert b_syntax[52] > 0, "Syntax Sub-AI must write to Byte 52"
    # Verify non-target bytes remain 0
    assert all(b == 0 for b in b_syntax[0:16]), "Bytes 0..15 must remain pristine"
    assert all(b == 0 for b in b_syntax[20:28]), "Bytes 20..27 must remain pristine"
    assert all(b == 0 for b in b_syntax[54:64]), "Bytes 54..63 must remain pristine"

    # 2. Execute Phonology Sub-AI:
    # Must write to Bytes 0..7 (Phonemes), Bytes 8..15 (Prosody), and Byte 24 (Capability 4).
    # Must NOT touch Byte 18, Byte 52, or Bytes 54..63.
    phonology_eval = phonology_ai.evaluate("塞翁失马，焉知非福。")
    assert phonology_eval.syllable_count >= 8
    b_phono = bytes(amsv.get_raw_bytes())

    assert any(b > 0 for b in b_phono[0:8]), "Phonology Sub-AI must write to Bytes 0..7"
    assert any(b > 0 for b in b_phono[8:16]), "Phonology Sub-AI must write to Bytes 8..15"
    assert b_phono[24] > 0, "Phonology Sub-AI must write to Byte 24"
    # Ensure syntax bytes were NOT clobbered
    assert b_phono[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_phono[52] == b_syntax[52], "Byte 52 must be preserved"

    # 3. Execute Pragmatic Sub-AI:
    # Must write to Byte 22 (Capability 3) and Byte 54 (Register Score).
    pragmatic_eval = pragmatic_ai.evaluate("您好，请问您有什么需要帮助的吗？")
    assert pragmatic_eval.is_formal is True
    b_prag = bytes(amsv.get_raw_bytes())

    assert b_prag[22] > 0, "Pragmatic Sub-AI must write to Byte 22"
    assert b_prag[54] > 0, "Pragmatic Sub-AI must write to Byte 54"
    # Ensure syntax and phonology bytes were preserved
    assert b_prag[18] == b_syntax[18]
    assert b_prag[24] == b_phono[24]

    # 4. Execute Editorial Sub-AI:
    # Must write to Byte 20 (Capability 2) and Byte 26 (Capability 5).
    # Must NOT overwrite Byte 56 (Attention directives).
    editorial_eval = editorial_ai.evaluate("这篇文章写得非常好，条理清晰，水到渠成。")
    assert editorial_eval.editorial_verdict in {"PASSED_FOR_PUBLICATION", "NEEDS_REVISION"}
    b_edit = bytes(amsv.get_raw_bytes())

    assert b_edit[20] > 0, "Editorial Sub-AI must write to Byte 20"
    assert b_edit[26] > 0, "Editorial Sub-AI must write to Byte 26"
    assert b_edit[56] == 0, "Byte 56 attention directive must remain decoupled"


def test_mandarin_six_language_matrix():
    amsv = AMSVEmbeddedView()
    bridge = MandarinSixLanguageMatrixBridge(amsv_view=amsv)
    text = "“北京欢迎你”，我把这本书送给您。"
    res = bridge.coordinate(text, request_id="req-zh-test-01")

    assert isinstance(res, MandarinSixLanguageExecutionResult)
    assert set(res.language_nodes) == {"Rust", "Python", "C++20", "CUDA", "Java 21", "Julia"}
    assert res.rust_safety_passed is True
    assert res.cpp_trie_lookup_count > 0
    assert res.cuda_attention_flops > 0
    assert res.java_virtual_thread_dispatched is True
    assert res.julia_tone_trajectory_steps > 0
    assert res.amsv_synced is True
    assert 0.0 < res.composite_linguistic_score <= 1.0


def test_mandarin_engine_orchestrator_end_to_end():
    """
    Validates complete end-to-end processing of the MandarinEngineOrchestrator.
    """
    orchestrator = MandarinEngineOrchestrator()
    sample_text = "尊敬的李教授，您好！我把毕业论文的最终报告已经写完了，可谓是胸有成竹。请您审阅。"

    output = orchestrator.process(sample_text, request_id="zh-orchestrator-eval-001")

    # 1. Output structure assertions
    assert output.input_text == sample_text
    assert len(output.tokens) >= 10
    assert len(output.pos_tags) == len(output.tokens)
    assert output.sentence_structure is not None
    assert output.sentence_structure.is_ba_construction is True
    assert len(output.pinyin_surface) > 0
    assert output.chengyu_density["idiom_count"] >= 1
    assert "胸有成竹" in output.chengyu_density["detected_idioms"]

    # 2. Pragmatic & Face Preservation assertions
    assert output.mianzi_evaluation["politeness_level"] == "High"
    assert output.mianzi_evaluation["face_preservation_score"] >= 0.85

    # 3. Cognitive Analysis assertions
    assert output.topic_comment_analysis is not None
    assert output.tone_sandhi_analysis["has_sandhi"] is True

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
    # Ensure cognitive score bytes are populated
    assert any(b > 0 for b in raw_bytes[16:32])

    # 8. Performance latency assertion
    assert output.latency_ms < 500.0, f"Latency exceeded expectation: {output.latency_ms}ms"
