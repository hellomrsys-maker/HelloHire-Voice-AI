"""
Indonesian Engine — Comprehensive Test Suite
Validates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
Six-Language Matrix, and Zero-Bridge Synchronous Memory State Vector (AMSV: 0x494E444F).
"""

import pytest
import struct
from Indonesian_engine import (
    IndonesianEngineOrchestrator,
    IndonesianMatrixBridge,
    INDONESIAN_AMSV_MAGIC,
    INDONESIAN_AMSV_SIZE
)
from Indonesian_engine.brain.skills.tokenization import tokenize_words, split_sentences, is_reduplicated
from Indonesian_engine.brain.skills.nasal_assimilation_engine import apply_men_prefix, verify_men_derivation
from Indonesian_engine.brain.skills.voice_affix_engine import derive_verb, derive_circumfix
from Indonesian_engine.brain.skills.reduplication_engine import reduplicate_word, analyze_reduplication
from Indonesian_engine.brain.skills.classifier_engine import select_classifier, format_numeral_classifier, validate_classifier_phrase
from Indonesian_engine.brain.skills.aspect_negation_engine import validate_negation, detect_aspect
from Indonesian_engine.brain.skills.pragmatics_engine import classify_register, format_salutation, format_closing, adapt_gaul_to_baku
from Indonesian_engine.brain.skills.generation import generate_sentence
from Indonesian_engine.brain.analysis.voice_symmetry_analyzer import VoiceSymmetryAnalyzer
from Indonesian_engine.brain.analysis.reduplication_analyzer import ReduplicationAnalyzer
from Indonesian_engine.brain.analysis.classifier_concord_analyzer import ClassifierConcordAnalyzer
from Indonesian_engine.brain.sub_ais.syntax_sub_ai import IndonesianSyntaxSubAI
from Indonesian_engine.brain.sub_ais.phonology_sub_ai import IndonesianPhonologySubAI
from Indonesian_engine.brain.sub_ais.pragmatic_sub_ai import IndonesianPragmaticSubAI
from Indonesian_engine.brain.sub_ais.editorial_sub_ai import IndonesianEditorialSubAI
from Indonesian_engine.brain.task.grammar_check import IndonesianGrammarChecker
from Indonesian_engine.brain.task.email_pipeline import IndonesianEmailPipeline
from Indonesian_engine.brain.task.composition_pipeline import IndonesianCompositionPipeline


def test_amsv_physical_layout_and_magic():
    """Test 1: Verify 64-byte AMSV layout, magic header 0x494E444F ('INDO'), and sub-AI active bytes."""
    bridge = IndonesianMatrixBridge()
    buf = bridge.buffer
    assert len(buf) == INDONESIAN_AMSV_SIZE == 64
    
    magic = struct.unpack_from("<I", buf, 0)[0]
    assert magic == INDONESIAN_AMSV_MAGIC == 0x494E444F
    
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
    bridge = IndonesianMatrixBridge(raw_memory)
    assert bridge.buffer is raw_memory # Exact physical address identity
    
    bridge.update_metrics(
        token_count=14,
        sentence_count=2,
        clause_type_mask=0x0001,
        syntax_flags=0x07,
        morphology_flags=0x05,
        phonology_flags=0x03,
        aspect_flags=0x01, # sudah
        register_tier=1,   # Formal Baku
        pragmatic_flags=0x03,
        confidence=0.98
    )
    
    metrics = bridge.read_metrics()
    assert metrics["is_magic_valid"] is True
    assert metrics["token_count"] == 14
    assert metrics["sentence_count"] == 2
    assert metrics["register_tier"] == 1
    assert metrics["confidence"] == 0.98
    assert raw_memory[22] == 1 # Physical byte directly updated in-place


def test_tokenization_and_hyphenated_reduplication():
    """Test 3: Tokenization preserving hyphenated reduplication and official abbreviations."""
    text = "Anak-anak membaca buku-buku di perpustakaan. Yth. Bapak Santoso menyambut mereka."
    tokens = tokenize_words(text)
    assert "Anak-anak" in tokens
    assert "buku-buku" in tokens
    assert is_reduplicated("anak-anak") is True
    assert is_reduplicated("buku-buku") is True
    
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert "Yth. Bapak Santoso" in sentences[1]


def test_nasal_assimilation_rules():
    """Test 4: Morphophonemic nasal assimilation for meN- with p/t/s/k deletion and homorganic insertion."""
    # Voiceless stops / sibilant deletion (p -> m, t -> n, s -> ny, k -> ng)
    assert apply_men_prefix("tulis") == "menulis"
    assert apply_men_prefix("pakai") == "memakai"
    assert apply_men_prefix("sapu") == "menyapu"
    assert apply_men_prefix("kirim") == "mengirim"
    
    # Voiced stops retention (b -> mem-b, d -> men-d, j -> men-j, g -> meng-g)
    assert apply_men_prefix("baca") == "membaca"
    assert apply_men_prefix("dengar") == "mendengar"
    assert apply_men_prefix("jual") == "menjual"
    assert apply_men_prefix("goreng") == "menggoreng"
    
    # Vowels & glottal h -> meng-
    assert apply_men_prefix("ambil") == "mengambil"
    assert apply_men_prefix("hitung") == "menghitung"
    
    # Liquids & nasals -> me-
    assert apply_men_prefix("lihat") == "melihat"
    assert apply_men_prefix("masak") == "memasak"
    
    # Monosyllabic root -> menge-
    assert apply_men_prefix("cat") == "mengecat"
    assert apply_men_prefix("bom") == "mengebom"


def test_voice_symmetry_active_and_passive():
    """Test 5: Voice derivation across active (meN-), passive (di-), accidental (ter-), and intransitive (ber-)."""
    # Active vs Passive
    assert derive_verb("tulis", voice="active") == "menulis"
    assert derive_verb("tulis", voice="passive") == "ditulis"
    assert derive_verb("baca", voice="passive") == "dibaca"
    
    # Accidental / stative ter-
    assert derive_verb("buka", voice="accidental") == "terbuka"
    assert derive_verb("tidur", voice="accidental") == "tertidur"
    
    # ber- with r-dropping rules
    assert derive_verb("jalan", voice="intransitive") == "berjalan"
    assert derive_verb("kerja", voice="intransitive") == "bekerja" # r-drop before -er-
    assert derive_verb("renang", voice="intransitive") == "berenang"
    assert derive_verb("ajar", voice="intransitive") == "belajar"
    
    # Circumfixes
    assert derive_circumfix("adil", "ke_an") == "keadilan"
    assert derive_circumfix("didik", "pen_an") == "pendidikan"


def test_reduplication_typology():
    """Test 6: Full dwilingga, imitative sound-shift, partial collective, and lexicalized reduplication."""
    # Full dwilingga
    assert reduplicate_word("buku") == "buku-buku"
    assert reduplicate_word("rumah") == "rumah-rumah"
    
    # Imitative sound-shift
    assert reduplicate_word("sayur", redup_type="imitative") == "sayur-mayur"
    assert reduplicate_word("balik", redup_type="imitative") == "bolak-balik"
    
    # Partial collective
    assert reduplicate_word("pohon", redup_type="partial") == "pepohonan"
    assert reduplicate_word("daun", redup_type="partial") == "dedaunan"
    
    # Lexicalized recognition
    res_kupu = analyze_reduplication("kupu-kupu")
    assert res_kupu["is_reduplicated"] is True
    assert res_kupu["type"] == "lexicalized_invariable"


def test_reduplication_analyzer_catches_numeric_shorthand():
    """Test 7: Reduplication analyzer flags informal numeric abbreviation (*buku2 -> buku-buku)."""
    analyzer = ReduplicationAnalyzer()
    
    res_bad = analyzer.analyze("Saya membeli buku2 di toko.")
    assert res_bad["is_valid"] is False
    assert any(v["rule"] == "informal_numeric_reduplication" for v in res_bad["violations"])
    
    res_good = analyzer.analyze("Saya membeli buku-buku di toko.")
    assert res_good["is_valid"] is True


def test_numeral_classifier_selection_and_synthesis():
    """Test 8: Numeral classifier selection and phrase synthesis across semantic domains."""
    # Humans: orang
    assert select_classifier("guru") == "orang"
    assert select_classifier("dokter") == "orang"
    assert format_numeral_classifier("satu", "guru") == "seorang guru"
    
    # Animals: ekor
    assert select_classifier("kucing") == "ekor"
    assert select_classifier("burung") == "ekor"
    assert format_numeral_classifier("dua", "kucing") == "dua ekor kucing"
    
    # Inanimates / general: buah
    assert select_classifier("buku") == "buah"
    assert select_classifier("mobil") == "buah"
    assert format_numeral_classifier("tiga", "buku") == "tiga buah buku"
    
    # Sheets: lembar
    assert select_classifier("kertas") == "lembar"
    assert format_numeral_classifier("satu", "kertas") == "selembar kertas"


def test_classifier_concord_analyzer_violations():
    """Test 9: Classifier concord analyzer detects semantic clashes (e.g. *sebuah guru)."""
    clf_analyzer = ClassifierConcordAnalyzer()
    
    # Valid phrases
    res_valid = clf_analyzer.analyze("Di sana ada seorang guru dan dua ekor kucing.")
    assert res_valid["is_valid"] is True
    assert len(res_valid["checked_phrases"]) >= 2
    
    # Semantic clash: *sebuah guru (inanimate classifier on human)
    res_clash = clf_analyzer.analyze("Di sana ada sebuah guru.")
    assert res_clash["is_valid"] is False
    assert any(v["rule"] == "classifier_semantic_clash" for v in res_clash["violations"])


def test_negation_distribution_tidak_vs_bukan():
    """Test 10: Negation distribution (tidak for verbs/adjectives vs bukan for nouns)."""
    # Valid: tidak makan (verb), bukan dokter (noun)
    assert validate_negation("tidak", "VERB", "makan")["valid"] is True
    assert validate_negation("bukan", "NOUN", "dokter")["valid"] is True
    
    # Invalid: tidak dokter (noun negated with tidak)
    res_err1 = validate_negation("tidak", "NOUN", "dokter")
    assert res_err1["valid"] is False
    assert any(v["rule"] == "negation_tidak_with_noun" for v in res_err1["violations"])
    
    # Invalid: bukan makan (verb negated with bukan)
    res_err2 = validate_negation("bukan", "VERB", "makan")
    assert res_err2["valid"] is False
    assert any(v["rule"] == "negation_bukan_with_verb" for v in res_err2["violations"])


def test_pragmatic_registers_and_epistolary_protocol():
    """Test 11: Register classification (Baku vs Gaul), formal surat resmi formatting, and peribahasa."""
    formal_text = "Dengan hormat, sehubungan dengan surat Bapak, kami mengucapkan terima kasih. Hormat kami."
    reg_formal = classify_register(formal_text)
    assert reg_formal["register"] == "formal"
    
    informal_text = "Gue nggak mau pergi, lu aja yang ke sana ya dong."
    reg_informal = classify_register(informal_text)
    assert reg_informal["register"] == "informal"
    
    # Salutation & closing formatting
    assert format_salutation("Direktur Utama", "Santoso", formal=True) == "Yang terhormat Direktur Utama Santoso,"
    assert "Hormat kami," in format_closing(formal=True)


def test_sub_ais_direct_amsv_execution():
    """Test 12: Direct physical AMSV buffer modification by the 4 dedicated Sub-AIs."""
    buf = bytearray(64)
    bridge = IndonesianMatrixBridge(buf)
    
    syntax_ai = IndonesianSyntaxSubAI()
    phonology_ai = IndonesianPhonologySubAI()
    pragmatic_ai = IndonesianPragmaticSubAI()
    editorial_ai = IndonesianEditorialSubAI()
    
    text = "Budi sudah membaca buku-buku itu dengan baik."
    
    s_res = syntax_ai.process(text, buf)
    assert s_res["status"] == "success"
    assert buf[52] == 1 # Syntax Sub-AI active
    assert buf[18] & 0x01 # SVO valid
    assert buf[18] & 0x02 # Active meN- voice
    
    p_res = phonology_ai.process(text, buf)
    assert p_res["status"] == "success"
    assert buf[53] == 1 # Phonology Sub-AI active
    assert buf[20] & 0x01 # Nasal assimilation verified
    
    pr_res = pragmatic_ai.process(text, buf)
    assert pr_res["status"] == "success"
    assert buf[54] == 1 # Pragmatic Sub-AI active
    
    ed_res = editorial_ai.process(text, buf)
    assert ed_res["status"] == "success"
    assert buf[55] == 1 # Editorial Sub-AI active
    assert ed_res["is_valid"] is True
    assert buf[19] & 0x04 # Reduplication flag
    assert buf[21] & 0x01 # Sudah aspect flag
    
    conf = struct.unpack_from("<f", buf, 24)[0]
    assert conf >= 0.95


def test_orchestrator_end_to_end_and_task_pipelines():
    """Test 13: Master Orchestrator end-to-end processing, email pipeline, and dialect adaptation."""
    orchestrator = IndonesianEngineOrchestrator()
    
    # 1. Process text
    res = orchestrator.process_text("Guru itu sudah menulis tiga buah buku.")
    assert res["token_count"] == 8 # Guru + itu + sudah + menulis + tiga + buah + buku + .
    assert res["sentence_count"] == 1
    assert res["is_valid"] is True
    assert res["amsv_state"]["is_magic_valid"] is True
    assert res["amsv_state"]["sub_ai_statuses"]["syntax"] is True
    assert res["amsv_state"]["sub_ai_statuses"]["phonology"] is True
    assert res["amsv_state"]["sub_ai_statuses"]["editorial"] is True
    
    # 2. Formal email generation & audit
    email = orchestrator.compose_email(
        form="formal",
        recipient_name="Santoso",
        recipient_title="Direktur Utama",
        body="Bersama ini kami lampirkan dokumen spesifikasi teknis Solo Rock.",
        sender_name="Budi Wijaya",
        organization="Solo Rock"
    )
    assert "Yang terhormat Direktur Utama Santoso," in email
    assert "Hormat kami," in email
    
    audit = orchestrator.audit_email(email)
    assert audit["passed"] is True
    assert audit["is_consistent"] is True
    
    # 3. Dialect adaptation (Bahasa Gaul -> Bahasa Baku)
    gaul_text = "Saya nggak bisa datang karena udah capek banget."
    baku_text = orchestrator.adapt_dialect(gaul_text, target="baku")
    assert "tidak" in baku_text
    assert "sudah" in baku_text
    assert "sangat" in baku_text
    
    # 4. Rhetorical style analysis
    rhetorical_text = "Kita bekerja keras karena ada udang di balik batu dalam proyek ini."
    style_res = orchestrator.analyze_style(rhetorical_text)
    assert style_res["style"] == "classical_rhetorical"
    assert "ada udang di balik batu" in style_res["proverbs_found"]
