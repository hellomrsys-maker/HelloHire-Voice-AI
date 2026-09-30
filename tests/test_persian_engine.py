"""
Dedicated Automated Test Suite for Persian Language Engine (Persian_engine/)
Verifies the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
Six-Language Matrix, and The Zero-Bridge Synchronous Memory Rule (0x46415253 'FARS').
"""

import os
import struct
import pytest
from Persian_engine import (
    PersianEngineOrchestrator,
    PersianMatrixBridge,
    PERSIAN_MAGIC_BYTES,
    PERSIAN_MAGIC_INT,
    AMSV_TOTAL_SIZE
)
from Persian_engine.brain.skills.tokenization import PersianTokenizer, ZWNJ
from Persian_engine.brain.skills.pos_tagging import PersianPOSTagger
from Persian_engine.brain.skills.ezafe_engine import PersianEzafeEngine
from Persian_engine.brain.skills.dom_marker_engine import PersianDOMEngine
from Persian_engine.brain.skills.light_verb_engine import PersianLightVerbEngine
from Persian_engine.brain.skills.verb_conjugator import PersianVerbConjugator
from Persian_engine.brain.skills.pragmatics_engine import PersianPragmaticsEngine
from Persian_engine.brain.sub_ais.syntax_sub_ai import PersianSyntaxSubAI
from Persian_engine.brain.sub_ais.phonology_sub_ai import PersianPhonologySubAI
from Persian_engine.brain.sub_ais.pragmatic_sub_ai import PersianPragmaticSubAI
from Persian_engine.brain.sub_ais.editorial_sub_ai import PersianEditorialSubAI
from Persian_engine.brain.task.grammar_check import PersianGrammarChecker
from Persian_engine.brain.task.email_pipeline import PersianEmailPipeline
from Persian_engine.brain.task.composition_pipeline import PersianCompositionPipeline

# 1. AMSV Physical Layout & Magic
def test_amsv_physical_layout_and_magic():
    bridge = PersianMatrixBridge()
    assert len(bridge.buffer) == AMSV_TOTAL_SIZE == 64
    assert bridge.verify_magic() is True
    assert bytes(bridge.buffer[0:4]) == PERSIAN_MAGIC_BYTES == b"FARS"
    assert bridge.get_magic_uint32() == PERSIAN_MAGIC_INT == 0x46415253
    assert bridge.buffer[4] == 0x01  # Major version
    assert bridge.buffer[5] == 0x00  # Minor version
    assert bridge.buffer[7] == 0x01  # Perso-Arabic RTL

# 2. Zero-Bridge Memory Synchronization
def test_zero_bridge_memory_synchronization():
    shared_buf = bytearray(64)
    bridge = PersianMatrixBridge(shared_buf)
    orchestrator = PersianEngineOrchestrator(shared_buf)
    
    # Process text and verify that shared_buf has been updated directly in-place
    res = orchestrator.process_text("کتابِ خوب را خواندم")
    
    # Check Magic
    assert bytes(shared_buf[0:4]) == b"FARS"
    # Check that Sub-AIs activated their active bytes directly in shared_buf
    assert shared_buf[52] == 0x01  # Syntax active
    assert shared_buf[53] == 0x01  # Phonology active
    assert shared_buf[54] == 0x01  # Pragmatic active
    assert shared_buf[55] == 0x01  # Editorial active
    
    # Read back float score from shared_buf bytes 24..28
    score = struct.unpack("<f", shared_buf[24:28])[0]
    assert 0.0 <= score <= 1.0

# 3. Tokenization and ZWNJ
def test_tokenization_and_zwnj():
    tokenizer = PersianTokenizer()
    # Arabic kaf and yeh should be normalized to Persian
    raw_text = "كتاب دوستي" # Arabic kaf U+0643, Arabic yeh U+064A
    normalized = tokenizer.normalize_script(raw_text)
    assert 'ک' in normalized # Persian Keheh
    assert 'ی' in normalized # Persian Yeh
    
    # Word with ZWNJ (نیم‌فاصله)
    zwnj_word = f"می{ZWNJ}خورم"
    tokens = tokenizer.tokenize_words(f"من {zwnj_word} .")
    assert zwnj_word in tokens
    assert "." in tokens
    
    spans = tokenizer.tokenize_with_spans(f"من {zwnj_word} .")
    zwnj_spans = [s for s in spans if s["has_zwnj"]]
    assert len(zwnj_spans) == 1
    assert zwnj_spans[0]["token"] == zwnj_word

# 4. POS Tagging
def test_pos_tagging():
    tagger = PersianPOSTagger()
    sentence = "من کتاب را خواندم"
    tagged = tagger.tag_sentence(sentence)
    tags = {tok: pos for tok, pos in tagged}
    
    assert tags.get("من") == "PRON"
    assert tags.get("کتاب") == "NOUN"
    assert tags.get("را") == "PART"
    assert tags.get("خواندم") == "VERB"

# 5. Ezafe Engine and Phonetic Realization
def test_ezafe_engine_and_phonetic_realization():
    engine = PersianEzafeEngine()
    
    # Consonant ending (کتاب)
    res_c = engine.determine_ezafe_suffix("کتاب")
    assert res_c["phonetic"] == "-e"
    assert res_c["type"] == "consonant"
    
    # Vowel ending alif (هوا)
    res_v = engine.determine_ezafe_suffix("هوا")
    assert res_v["phonetic"] == "-ye"
    assert res_v["type"] == "vowel_alif_vav"
    
    # Silent heh ending (خانه)
    res_h = engine.determine_ezafe_suffix("خانه")
    assert res_h["phonetic"] == "-ye"
    assert res_h["type"] == "silent_heh"
    
    # Constructing phrases
    phrase_c = engine.construct_ezafe_phrase("کتاب", "بزرگ", explicit_diacritic=True)
    assert "ِ" in phrase_c
    phrase_h = engine.construct_ezafe_phrase("خانه", "زیبا")
    assert "ٔ" in phrase_h or "ی" in phrase_h

# 6. DOM Marker 'rā' and Definiteness
def test_dom_marker_ra_and_definiteness():
    dom = PersianDOMEngine()
    
    # Personal pronoun requires rā
    eval_pron = dom.evaluate_object_definiteness("او")
    assert eval_pron["requires_ra"] is True
    
    # Proper noun requires rā
    eval_proper = dom.evaluate_object_definiteness("علی")
    assert eval_proper["requires_ra"] is True
    
    # Demonstrative requires rā
    eval_dem = dom.evaluate_object_definiteness("این کتاب")
    assert eval_dem["requires_ra"] is True
    
    # Bare noun does not require rā
    eval_bare = dom.evaluate_object_definiteness("سیب")
    assert eval_bare["requires_ra"] is False
    
    # Attach marker
    attached = dom.attach_dom_marker("کتاب")
    assert attached == "کتاب را"

# 7. Light Verb Constructions and Voice
def test_light_verb_constructions_and_voice():
    lve = PersianLightVerbEngine()
    assert lve.is_light_verb_compound("کار", "کردن") is True
    assert lve.is_light_verb_compound("حرف", "زدن") is True
    assert lve.is_light_verb_compound("پیدا", "شدن") is True
    
    # Extraction
    words = ["ما", "دیروز", "کار", "کردیم"]
    compounds = lve.extract_compound_predicate(words)
    assert len(compounds) == 1
    assert compounds[0]["non_verbal"] == "کار"
    
    # Active to passive/inchoative transformation
    passive = lve.transform_voice("پیدا", "کردن")
    assert passive == "پیدا شدن"

# 8. Verb Conjugation Dual Stems
def test_verb_conjugation_dual_stems():
    conjugator = PersianVerbConjugator()
    
    # رفتن (past: رفت, present: رو)
    past_1sg = conjugator.conjugate("رفتن", "past_simple", person=1)
    assert past_1sg == "رفتم"
    
    pres_1sg = conjugator.conjugate("رفتن", "present_continuous", person=1)
    assert pres_1sg.startswith("می")
    assert pres_1sg.endswith("روم")
    
    past_neg = conjugator.conjugate("خوردن", "past_simple", person=3, negative=True)
    assert past_neg == "نخورد"
    
    subj_2sg = conjugator.conjugate("دیدن", "subjunctive", person=2)
    assert subj_2sg.startswith("ب")
    assert subj_2sg.endswith("بینی")

# 9. Pragmatics and Ta'arof Deference
def test_pragmatics_and_taarof_deference():
    pragmatics = PersianPragmaticsEngine()
    
    # Register detection
    high_text = "جناب آقای دکتر، با سلام و تجدید احترام، فرمودید که بررسی شود."
    det = pragmatics.detect_register(high_text)
    assert det["dominant_register"] == "high_taarof"
    assert det["tier_level"] == 3
    
    # Honorific elevation and self-lowering
    elevated = pragmatics.elevate_verb_for_interlocutor("گفتن")
    assert elevated == "فرمودن"
    
    lowered = pragmatics.lower_verb_for_self("گفتن")
    assert lowered == "عرض کردن"
    
    # Letter formatting
    letter = pragmatics.format_formal_letter(
        addressee="احمدی",
        title="مدیرکل",
        body="گزارش پروژه تقدیم می‌گردد.",
        sender="رضایی",
        is_high_taarof=True
    )
    assert "جناب آقای احمدی" in letter
    assert "تجدید احترام" in letter

# 10. Sub-AIs Direct AMSV Execution
def test_sub_ais_direct_amsv_execution():
    buf = bytearray(64)
    bridge = PersianMatrixBridge(buf)
    
    syn_ai = PersianSyntaxSubAI(buf)
    phon_ai = PersianPhonologySubAI(buf)
    prag_ai = PersianPragmaticSubAI(buf)
    edit_ai = PersianEditorialSubAI(buf)
    
    text = f"من کتابِ خوب را دیروز خواندم."
    
    syn_ai.process(text, buf)
    assert buf[52] == 0x01 # Syntax active
    assert buf[18] > 0     # Syntax score
    
    phon_ai.process(text, buf)
    assert buf[53] == 0x01 # Phonology active
    
    prag_ai.process(text, buf)
    assert buf[54] == 0x01 # Pragmatic active
    assert buf[22] in {1, 2, 3}
    
    edit_ai.process(text, buf)
    assert buf[55] == 0x01 # Editorial active
    assert buf[19] == 0x01 # DOM accuracy
    
    # Verify zero-bleed in untouched bytes (e.g. byte 28..31 reserved hardware)
    assert buf[28] == 0x00
    assert buf[29] == 0x00

# 11. Orchestrator End-to-End and Pipeline
def test_orchestrator_end_to_end_and_pipeline():
    orch = PersianEngineOrchestrator()
    res = orch.process_text("علی نامهٔ رسمی را برای مدیریت فرستاد.")
    
    assert res["text"].startswith("علی")
    assert res["phonology"]["token_count"] > 0
    assert res["syntax"]["sub_ai"] == "PersianSyntaxSubAI"
    assert res["amsv_state"]["magic"] == "FARS"
    assert res["amsv_state"]["sub_ais_active"]["syntax"] is True
    assert res["amsv_state"]["sub_ais_active"]["editorial"] is True
    
    # Sentence synthesis
    sov_sent = orch.synthesize_sov_sentence(
        subject="من",
        direct_object="این کتاب",
        verb_infinitive="خواندن",
        tense="past_simple",
        person=1,
        is_definite_object=True
    )
    assert sov_sent == "من این کتاب را خواندم"

# 12. Task Pipelines and Colloquial Normalization
def test_task_pipelines_and_colloquial_normalization():
    orch = PersianEngineOrchestrator()
    
    # 1. Grammar check
    valid_text = "ما کتاب را خواندیم."
    check = orch.check_grammar(valid_text)
    assert check["is_valid"] is True
    assert check["confidence_score"] >= 0.85
    
    # 2. Colloquial normalization
    colloquial = "من توی تهرون نون خریدم و به خونه رفتم."
    normalized = orch.compose_prose(colloquial)
    assert "تهران" in normalized
    assert "نان" in normalized
    assert "خانه" in normalized
    
    # 3. Proverb injection
    proverb_prose = orch.compose_prose("نتیجه کار تلاش مداوم است.", theme="patience_results")
    assert "پاییز" in proverb_prose

# 13. Six-Language Matrix Nodes
def test_six_language_matrix_nodes():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    matrix_dir = os.path.join(base_dir, "Persian_engine", "six_language_matrix")
    
    expected_files = [
        "persian_syntax_safety.rs",
        "persian_core_engine.hpp",
        "persian_core_engine.cpp",
        "persian_gpu_kernels.cu",
        "PersianEngineService.java",
        "PersianGrammarDynamics.jl",
        "persian_matrix_bridge.py",
        "__init__.py"
    ]
    
    for filename in expected_files:
        path = os.path.join(matrix_dir, filename)
        assert os.path.exists(path), f"Missing matrix node: {filename}"
        assert os.path.getsize(path) > 50, f"Matrix node too small: {filename}"
