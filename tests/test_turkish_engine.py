"""Unit and Integration Test Suite for the Turkish Language Engine (Türkçe).

Tests all 9 layers, 9 computational skills, 3 cognitive analyzers,
3 task pipelines, 4 dedicated Sub-AIs, 6-language matrix, and Zero-Bridge AMSV sync.
"""

import pytest
from amsv.python.amsv_embedded import AMSVEmbeddedView

from Turkish_engine.brain.skills.tokenization import TurkishTokenizer
from Turkish_engine.brain.skills.vowel_harmony_engine import TurkishVowelHarmonyEngine
from Turkish_engine.brain.skills.consonant_mutation_engine import TurkishConsonantMutationEngine
from Turkish_engine.brain.skills.pos_tagging import TurkishPOSTagger
from Turkish_engine.brain.skills.case_engine import TurkishCaseEngine
from Turkish_engine.brain.skills.verb_conjugator import TurkishVerbConjugator
from Turkish_engine.brain.skills.pragmatics_engine import TurkishPragmaticsEngine
from Turkish_engine.brain.skills.parsing import TurkishDependencyParser
from Turkish_engine.brain.skills.generation import TurkishSentenceGenerator

from Turkish_engine.brain.analysis.vowel_harmony_analyzer import TurkishVowelHarmonyAnalyzer
from Turkish_engine.brain.analysis.case_postposition_analyzer import TurkishCasePostpositionAnalyzer
from Turkish_engine.brain.analysis.evidentiality_analyzer import TurkishEvidentialityAnalyzer

from Turkish_engine.brain.task.grammar_check import TurkishGrammarChecker
from Turkish_engine.brain.task.email_pipeline import TurkishEmailPipeline
from Turkish_engine.brain.task.composition_pipeline import TurkishCompositionPipeline

from Turkish_engine.brain.sub_ais.syntax_sub_ai import TurkishSyntaxSubAI
from Turkish_engine.brain.sub_ais.phonology_sub_ai import TurkishPhonologySubAI
from Turkish_engine.brain.sub_ais.pragmatic_sub_ai import TurkishPragmaticSubAI
from Turkish_engine.brain.sub_ais.editorial_sub_ai import TurkishEditorialSubAI

from Turkish_engine.six_language_matrix.python.turkish_matrix_bridge import TurkishMatrixBridge
from Turkish_engine.turkish_engine_orchestrator import TurkishEngineOrchestrator


def test_turkish_tokenizer_and_proper_noun_apostrophes():
    tokenizer = TurkishTokenizer()
    text = "Ahmet'in kitabı dün Ankara'da bulundu."
    tokens = tokenizer.tokenize(text)

    assert "Ahmet'in" in tokens
    assert "kitabı" in tokens
    assert "Ankara'da" in tokens
    assert "bulundu" in tokens
    assert "." in tokens

    # Locale-aware dotted/dotless casing
    assert TurkishTokenizer.turkish_lower("İSTANBUL") == "istanbul"
    assert TurkishTokenizer.turkish_lower("IŞIK") == "ışık"
    assert TurkishTokenizer.turkish_upper("istanbul") == "İSTANBUL"
    assert TurkishTokenizer.turkish_upper("ışık") == "IŞIK"

    # Split apostrophe
    stem, sfx = tokenizer.split_apostrophe("Ahmet'in")
    assert stem == "Ahmet"
    assert sfx == "in"


def test_turkish_vowel_harmony():
    harmony = TurkishVowelHarmonyEngine()

    # Two-way harmony: Front vowels -> e, Back vowels -> a
    assert harmony.get_two_way_harmonic_vowel("ev") == "e"
    assert harmony.get_two_way_harmonic_vowel("göz") == "e"
    assert harmony.get_two_way_harmonic_vowel("okul") == "a"
    assert harmony.get_two_way_harmonic_vowel("kapı") == "a"

    # Four-way harmony: e,i -> i; a,ı -> ı; ö,ü -> ü; o,u -> u
    assert harmony.get_four_way_harmonic_vowel("ev") == "i"
    assert harmony.get_four_way_harmonic_vowel("dil") == "i"
    assert harmony.get_four_way_harmonic_vowel("kapı") == "ı"
    assert harmony.get_four_way_harmonic_vowel("göz") == "ü"
    assert harmony.get_four_way_harmonic_vowel("okul") == "u"

    # Internal harmony check
    assert harmony.check_internal_harmony("kelebek")["is_harmonic"] is True
    assert harmony.check_internal_harmony("çocuklar")["is_harmonic"] is True


def test_turkish_consonant_mutation():
    mutation = TurkishConsonantMutationEngine()

    # Lenition / Softening (p->b, ç->c, t->d, k->ğ)
    assert mutation.apply_lenition("kitap") == "kitab"
    assert mutation.apply_lenition("ağaç") == "ağac"
    assert mutation.apply_lenition("kanat") == "kanad"
    assert mutation.apply_lenition("çocuk") == "çocuğ"

    # Exceptions (monosyllabic / foreign loans do not soften)
    assert mutation.apply_lenition("top") == "top"
    assert mutation.apply_lenition("ip") == "ip"
    assert mutation.apply_lenition("hukuk") == "hukuk"
    assert mutation.apply_lenition("devlet") == "devlet"

    # Consonant assimilation (d->t, c->ç after voiceless)
    assert mutation.assimilate_suffix("kitap", "da") == "ta"
    assert mutation.assimilate_suffix("sınıf", "dan") == "tan"
    assert mutation.assimilate_suffix("ev", "de") == "de"


def test_turkish_pos_tagging():
    tagger = TurkishPOSTagger()
    tokens = ["Öğrenci", "yeni", "kitabı", "dikkatle", "okudu", "ve", "çıktı", "."]
    tagged = tagger.tag(tokens)

    tag_map = {item["token"]: item["pos"] for item in tagged}
    assert tag_map["Öğrenci"] == "NOUN"
    assert tag_map["yeni"] == "ADJ"
    assert tag_map["kitabı"] == "NOUN"
    assert tag_map["dikkatle"] == "ADV"
    assert tag_map["okudu"] == "VERB"
    assert tag_map["ve"] == "CCONJ"
    assert tag_map["çıktı"] == "VERB"

    # Postpositions and pronouns
    postp_tagged = tagger.tag(["bizim", "için", "onun", "gibi"])
    p_map = {item["token"]: item["pos"] for item in postp_tagged}
    assert p_map["bizim"] == "PRON"
    assert p_map["için"] == "ADP"
    assert p_map["gibi"] == "ADP"


def test_turkish_case_engine_and_dom():
    case_engine = TurkishCaseEngine()

    # Accusative (definite direct object with buffer y and lenition)
    assert case_engine.inflect_noun("ev", "acc") == "evi"
    assert case_engine.inflect_noun("araba", "acc") == "arabayı"
    assert case_engine.inflect_noun("kitap", "acc") == "kitabı"
    assert case_engine.inflect_noun("göz", "acc") == "gözü"

    # Dative (-(y)e / -(y)a)
    assert case_engine.inflect_noun("ev", "dat") == "eve"
    assert case_engine.inflect_noun("araba", "dat") == "arabaya"
    assert case_engine.inflect_noun("çocuk", "dat") == "çocuğa"

    # Locative (-de / -te)
    assert case_engine.inflect_noun("ev", "loc") == "evde"
    assert case_engine.inflect_noun("kitap", "loc") == "kitapta"

    # Ablative (-den / -ten)
    assert case_engine.inflect_noun("okul", "abl") == "okuldan"
    assert case_engine.inflect_noun("sınıf", "abl") == "sınıftan"

    # Genitive (-(n)in)
    assert case_engine.inflect_noun("ev", "gen") == "evin"
    assert case_engine.inflect_noun("araba", "gen") == "arabanın"

    # Proper nouns with apostrophe
    assert case_engine.inflect_noun("Ankara", "dat", is_proper=True) == "Ankara'ya"
    assert case_engine.inflect_noun("Ahmet", "gen", is_proper=True) == "Ahmet'in"


def test_turkish_verb_conjugator():
    conj = TurkishVerbConjugator()

    # Past tense (-di / -ti)
    assert conj.conjugate("yazmak", tense="past", person="3sg") == "yazdı"
    assert conj.conjugate("gelmek", tense="past", person="1sg") == "geldim"
    assert conj.conjugate("bakmak", tense="past", person="3sg") == "baktı"
    assert conj.conjugate("gitmek", tense="past", person="1pl") == "gittik"

    # Evidential past (-miş)
    assert conj.conjugate("yazmak", tense="evidential", person="3sg") == "yazmış"
    assert conj.conjugate("gelmek", tense="evidential", person="2sg") == "gelmişsin"

    # Present continuous (-iyor)
    assert conj.conjugate("yazmak", tense="progressive", person="3sg") == "yazıyor"
    assert conj.conjugate("gelmek", tense="progressive", person="1sg") == "geliyorum"

    # Future (-ecek / -acak)
    assert conj.conjugate("yazmak", tense="future", person="3sg") == "yazacak"
    assert conj.conjugate("gelmek", tense="future", person="1sg") == "geleceğim"

    # Negation
    assert conj.conjugate("yazmak", tense="past", person="3sg", negative=True) == "yazmadı"
    assert conj.conjugate("gelmek", tense="past", person="3sg", negative=True) == "gelmedi"


def test_turkish_pragmatics_and_honorifics():
    prag = TurkishPragmaticsEngine()

    # Postpositive honorific titles
    assert prag.format_honorific_name("Ahmet", "Bey") == "Ahmet Bey"
    assert prag.format_honorific_name("Ayşe", "Hanım") == "Ayşe Hanım"
    assert prag.format_honorific_name("Mehmet", "Hocam") == "Mehmet Hocam"

    # Register detection
    assert prag.detect_register("Sayın Yetkili, bilgilerinize sunarım.") == "formal_business"
    assert prag.detect_register("Değerli Hocam, makalenizi inceledim.") == "academic"
    assert prag.detect_register("Selam, sen yarın geliyor musun?") == "informal"


def test_turkish_dependency_parsing():
    parser = TurkishDependencyParser()
    parsed = parser.parse("Öğrenci kitabı okudu.")

    assert parsed["root_index"] == 2
    deprels = [n["deprel"] for n in parsed["nodes"]]
    assert "root" in deprels
    assert "nsubj" in deprels
    assert "obj" in deprels


def test_turkish_sentence_generation():
    generator = TurkishSentenceGenerator()

    # Canonical SOV generation
    sent1 = generator.generate_transitive_sov(
        subject="öğrenci",
        verb_lemma="okumak",
        object_noun="kitap",
        is_definite_object=True,
        tense="past",
        person="3sg"
    )
    assert sent1 == "Öğrenci kitabı okudu."

    # Postpositional clause generation
    sent2 = generator.generate_postpositional_clause(
        subject="ali",
        noun="akşam",
        postposition="kadar",
        verb_lemma="çalışmak",
        tense="past"
    )
    assert "akşama kadar" in sent2

    # Polite request generation
    req = generator.generate_polite_request("açmak")
    assert req == "Açar mısınız?"


def test_turkish_cognitive_analyzers():
    harmony_analyzer = TurkishVowelHarmonyAnalyzer()
    case_analyzer = TurkishCasePostpositionAnalyzer()
    evidential_analyzer = TurkishEvidentialityAnalyzer()

    # Vowel harmony audit
    harm_res = harmony_analyzer.analyze("Çocuklar okulda güzel çiçekler gördüler.")
    assert harm_res["compliance_score"] == 100
    assert harm_res["is_valid"] is True

    # Postposition case valency check
    case_res = case_analyzer.analyze("Biz akşama kadar çalıştık ve sonra yemekten önce konuştuk.")
    assert case_res["case_bitfield"] > 0
    assert len(case_res["postposition_checks"]) >= 2
    assert case_res["is_valid"] is True

    # Evidentiality stance audit
    evid_res = evidential_analyzer.analyze("Dün Ali gelmiş, ancak Mehmet hemen gitti.")
    assert evid_res["evidential_past_count"] == 1
    assert evid_res["direct_past_count"] == 1


def test_turkish_tasks():
    grammar_checker = TurkishGrammarChecker()
    email_pipeline = TurkishEmailPipeline()
    comp_pipeline = TurkishCompositionPipeline()

    # 1. Grammar check
    g_res = grammar_checker.check("Öğrenci kütüphanede yeni kitabı dikkatle okudu.")
    assert g_res["is_clean"] is True
    assert g_res["quality_score"] == 100

    # 2. Email pipeline
    email = email_pipeline.compose_email(
        recipient_name="Kemal",
        sender_name="Deniz",
        recipient_gender="masc",
        register="formal_business"
    )
    assert "Sayın Kemal Bey," in email["salutation"]
    assert "Saygılarımla," in email["valediction"]
    assert "Deniz" in email["full_email"]

    # 3. Composition pipeline
    comp = comp_pipeline.compose_report(
        engineer_name="Selim",
        task_count=3,
        system_name="bellek"
    )
    assert "Mühendis Selim 3 önemli görevi" in comp["full_text"]


def test_turkish_sub_ais_and_amsv_bit_isolation():
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))

    syntax_ai = TurkishSyntaxSubAI(amsv_view=amsv)
    phonology_ai = TurkishPhonologySubAI(amsv_view=amsv)
    pragmatic_ai = TurkishPragmaticSubAI(amsv_view=amsv)
    editorial_ai = TurkishEditorialSubAI(amsv_view=amsv)

    initial_bytes = bytes(amsv.get_raw_bytes())
    assert len(initial_bytes) == 64
    assert all(b == 0 for b in initial_bytes)

    test_sentence = "Müdür Bey raporu dikkatle inceledi."

    # 1. Syntax Sub-AI: writes to Byte 18 (0x12) and Byte 52 (0x34)
    syn_eval = syntax_ai.evaluate(test_sentence)
    assert syn_eval.amsv_synced is True
    b_syntax = bytes(amsv.get_raw_bytes())
    assert b_syntax[18] > 0, "Syntax Sub-AI must write to Byte 18"
    assert b_syntax[52] > 0, "Syntax Sub-AI must write to Byte 52"
    assert all(b == 0 for b in b_syntax[0:16]), "Bytes 0..15 must remain pristine"
    assert all(b == 0 for b in b_syntax[20:28]), "Bytes 20..27 must remain pristine"

    # 2. Phonology Sub-AI: writes to Bytes 0..15 and Byte 24 (0x18)
    ph_eval = phonology_ai.evaluate(test_sentence)
    assert ph_eval.amsv_synced is True
    b_phono = bytes(amsv.get_raw_bytes())
    assert any(b > 0 for b in b_phono[0:8]), "Phonology Sub-AI must write to Bytes 0..7"
    assert any(b > 0 for b in b_phono[8:16]), "Phonology Sub-AI must write to Bytes 8..15"
    assert b_phono[24] > 0, "Phonology Sub-AI must write to Byte 24"
    assert b_phono[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_phono[52] == b_syntax[52], "Byte 52 must be preserved"

    # 3. Pragmatic Sub-AI: writes to Byte 22 (0x16) and Byte 54 (0x36)
    prag_eval = pragmatic_ai.evaluate("Sayın Ahmet Bey, bilgilerinize arz ederim.")
    assert prag_eval.amsv_synced is True
    b_prag = bytes(amsv.get_raw_bytes())
    assert b_prag[22] > 0, "Pragmatic Sub-AI must write to Byte 22"
    assert b_prag[54] > 0, "Pragmatic Sub-AI must write to Byte 54"
    assert b_prag[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_prag[24] == b_phono[24], "Byte 24 must be preserved"

    # 4. Editorial Sub-AI: writes to Byte 20 (0x14) and Byte 26 (0x1A)
    edit_eval = editorial_ai.evaluate(test_sentence)
    assert edit_eval.amsv_synced is True
    b_edit = bytes(amsv.get_raw_bytes())
    assert b_edit[20] > 0, "Editorial Sub-AI must write to Byte 20"
    assert b_edit[26] > 0, "Editorial Sub-AI must write to Byte 26"

    # Bit Isolation Check: Bytes 30 and 31 must remain untouched (0)
    assert b_edit[30] == 0
    assert b_edit[31] == 0


def test_turkish_six_language_matrix_and_orchestrator():
    amsv = AMSVEmbeddedView()
    bridge = TurkishMatrixBridge(amsv_view=amsv)

    res = bridge.execute_matrix_pipeline("Mühendis görevi tamamladı.")
    assert res["rust_safety"]["is_safe"] is True
    assert res["cuda_acceleration"]["parallel_batch_supported"] is True
    assert res["java_loom_service"]["direct_byte_buffer_capacity"] == 64
    assert res["amsv_synchronization"]["synced"] is True

    # Master Orchestrator End-to-End
    orchestrator = TurkishEngineOrchestrator()
    sentence = "Öğrenci kütüphanede yeni kitabı dikkatle okudu."
    analysis = orchestrator.analyze(sentence)

    assert analysis.input_text == sentence
    assert len(analysis.tokens) > 0
    assert analysis.syntax_eval.syntactic_integrity_score > 0.6
    assert analysis.overall_linguistic_score > 0.6
    assert analysis.amsv_synced is True

    # Convenience wrappers
    proof = orchestrator.proofread(sentence)
    assert proof["is_clean"] is True

    email = orchestrator.compose_email(
        recipient_name="Ayşe",
        sender_name="Merve",
        recipient_gender="fem",
        register="formal_business"
    )
    assert "Sayın Ayşe Hanım," in email["salutation"]

    prose = orchestrator.compose_prose(author_name="Can", task_count=2)
    assert "Mühendis Can" in prose["full_text"]

    gen_sent = orchestrator.generate_sentence(
        subject="öğretmen",
        verb_lemma="yazmak",
        object_noun="mektup",
        is_definite_object=True,
        tense="past",
        person="3sg"
    )
    assert "Öğretmen mektubu yazdı." == gen_sent
