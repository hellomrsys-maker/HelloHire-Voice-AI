"""Unit and Integration Test Suite for the Russian Language Engine (Русский язык).

Tests all 9 layers, 9 computational skills, 3 cognitive analyzers,
3 task pipelines, 4 dedicated Sub-AIs, 6-language matrix, and Zero-Bridge AMSV sync.
"""

import pytest
from amsv.python.amsv_embedded import AMSVEmbeddedView

from Russian_engine.brain.skills.tokenization import RussianTokenizer
from Russian_engine.brain.skills.pos_tagging import RussianPOSTagger
from Russian_engine.brain.skills.verb_aspect_conjugator import RussianVerbAspectConjugator
from Russian_engine.brain.skills.case_engine import RussianCaseEngine
from Russian_engine.brain.skills.motion_verb_engine import RussianMotionVerbEngine
from Russian_engine.brain.skills.numeral_concord_engine import RussianNumeralConcordEngine
from Russian_engine.brain.skills.pragmatics_engine import RussianPragmaticsEngine
from Russian_engine.brain.skills.parsing import RussianDependencyParser
from Russian_engine.brain.skills.generation import RussianSentenceGenerator

from Russian_engine.brain.analysis.case_government_analyzer import RussianCaseGovernmentAnalyzer
from Russian_engine.brain.analysis.aspect_choice_analyzer import RussianAspectChoiceAnalyzer
from Russian_engine.brain.analysis.numeral_concord_analyzer import RussianNumeralConcordAnalyzer

from Russian_engine.brain.task.grammar_check import RussianGrammarChecker
from Russian_engine.brain.task.email_pipeline import RussianEmailPipeline
from Russian_engine.brain.task.composition_pipeline import RussianCompositionPipeline

from Russian_engine.brain.sub_ais.syntax_sub_ai import RussianSyntaxSubAI
from Russian_engine.brain.sub_ais.phonology_sub_ai import RussianPhonologySubAI
from Russian_engine.brain.sub_ais.pragmatic_sub_ai import RussianPragmaticSubAI
from Russian_engine.brain.sub_ais.editorial_sub_ai import RussianEditorialSubAI

from Russian_engine.six_language_matrix.python.russian_matrix_bridge import RussianMatrixBridge
from Russian_engine.russian_engine_orchestrator import RussianEngineOrchestrator


def test_russian_tokenizer_and_hyphenated_particles():
    tokenizer = RussianTokenizer()
    text = "Кое-кто из-за непогоды всё-таки опоздал на поезд."
    tokens = tokenizer.tokenize(text)

    assert "Кое-кто" in tokens
    assert "из-за" in tokens
    assert "всё-таки" in tokens
    assert "поезд" in tokens
    assert "." in tokens

    meta = tokenizer.analyze_tokens(text)
    compounds = [m["text"] for m in meta if m["is_hyphenated_compound"]]
    assert "Кое-кто" in compounds
    assert "из-за" in compounds


def test_russian_pos_tagging():
    tagger = RussianPOSTagger()
    tokens = ["Студент", "внимательно", "прочитал", "новую", "книгу", "и", "вышел", "."]
    tagged = tagger.tag(tokens)

    tag_map = {item["token"]: item["pos"] for item in tagged}
    assert tag_map["Студент"] == "NOUN"
    assert tag_map["внимательно"] == "ADV"
    assert tag_map["прочитал"] == "VERB"
    assert tag_map["новую"] == "ADJ"
    assert tag_map["книгу"] == "NOUN"
    assert tag_map["и"] == "CCONJ"
    assert tag_map["вышел"] == "VERB"


def test_russian_verb_aspect_and_conjugator():
    conj = RussianVerbAspectConjugator()

    # Aspect detection & pair lookup
    asp1 = conj.get_aspect("делать")
    assert asp1["aspect"] == "impf"
    assert asp1["partner"] == "сделать"

    asp2 = conj.get_aspect("прочитать")
    assert asp2["aspect"] == "perf"
    assert asp2["partner"] == "читать"

    asp3 = conj.get_aspect("сказать")
    assert asp3["aspect"] == "perf"
    assert asp3["partner"] == "говорить"

    # Past tense gender/number conjugation
    assert conj.conjugate_past("читать", gender="masc") == "читал"
    assert conj.conjugate_past("читать", gender="fem") == "читала"
    assert conj.conjugate_past("читать", gender="neut") == "читало"
    assert conj.conjugate_past("читать", number="plur") == "читали"


def test_russian_case_engine_and_animacy():
    case_engine = RussianCaseEngine()

    # Preposition government
    assert case_engine.get_expected_case_for_prep("без") == "gen"
    assert case_engine.get_expected_case_for_prep("к") == "dat"
    assert case_engine.get_expected_case_for_prep("о") == "prep"

    # Verb government
    assert case_engine.get_expected_case_for_verb("помогать") == "dat"
    assert case_engine.get_expected_case_for_verb("управлять") == "inst"
    assert case_engine.get_expected_case_for_verb("бояться") == "gen"

    # Declension 1st (книга)
    assert case_engine.inflect_noun("книга", case="acc", gender="fem", declension="1st") == "книгу"
    assert case_engine.inflect_noun("книга", case="gen", gender="fem", declension="1st") == "книги"

    # Declension 2nd (стол vs студент - animacy split in accusative)
    # Inanimate: Accusative = Nominative
    assert case_engine.inflect_noun("стол", case="acc", gender="masc", declension="2nd", animacy=False) == "стол"
    # Animate: Accusative = Genitive
    assert case_engine.inflect_noun("студент", case="acc", gender="masc", declension="2nd", animacy=True) == "студента"

    # Animacy check helper
    anim_check = case_engine.check_accusative_animacy("студент", is_animate=True, gender="masc", number="sing")
    assert anim_check["accusative_takes_genitive_form"] is True


def test_russian_motion_verbs():
    motion_engine = RussianMotionVerbEngine()

    # Base determinate vs indeterminate
    m1 = motion_engine.analyze_motion_verb("идти")
    assert m1["is_motion_verb"] is True
    assert m1["type"] == "determinate"
    assert m1["partner"] == "ходить"

    m2 = motion_engine.analyze_motion_verb("ходить")
    assert m2["is_motion_verb"] is True
    assert m2["type"] == "indeterminate"
    assert m2["partner"] == "идти"

    # Prefixed forms
    m3 = motion_engine.analyze_motion_verb("уйти")
    assert m3["is_motion_verb"] is True
    assert m3["type"] == "prefixed_determinate"
    assert m3["prefix"] == "у"
    assert m3["aspect"] == "perf"


def test_russian_numeral_paucal_concord():
    num_engine = RussianNumeralConcordEngine()

    # Ending in 1 -> Nom Sing
    assert num_engine.get_noun_form_requirements(1) == ("nom", "sing")
    assert num_engine.get_noun_form_requirements(21) == ("nom", "sing")

    # Ending in 2, 3, 4 -> Gen Sing
    assert num_engine.get_noun_form_requirements(2) == ("gen", "sing")
    assert num_engine.get_noun_form_requirements(34) == ("gen", "sing")

    # Ending in 5..20, 11..14 -> Gen Plur
    assert num_engine.get_noun_form_requirements(5) == ("gen", "plur")
    assert num_engine.get_noun_form_requirements(12) == ("gen", "plur")
    assert num_engine.get_noun_form_requirements(14) == ("gen", "plur")
    assert num_engine.get_noun_form_requirements(20) == ("gen", "plur")

    # Full phrase synthesis
    phrase2 = num_engine.combine(2, lemma="стол", gender="masc", declension="2nd")
    assert phrase2 == "2 стола"

    # Concord verification
    ver1 = num_engine.verify_concord(2, observed_noun="стола", lemma="стол", gender="masc", declension="2nd")
    assert ver1["is_valid"] is True


def test_russian_pragmatics_and_patronymics():
    prag = RussianPragmaticsEngine()

    # Patronymic generation
    # Hard consonant -> -ович / -овна
    assert prag.generate_patronymic("Иван", gender="masc") == "Иванович"
    assert prag.generate_patronymic("Иван", gender="fem") == "Ивановна"
    assert prag.generate_patronymic("Пётр", gender="masc") == "Петрович"

    # Soft / j -> -евич / -евна
    assert prag.generate_patronymic("Сергей", gender="masc") == "Сергеевич"
    assert prag.generate_patronymic("Сергей", gender="fem") == "Сергеевна"

    # Historical exceptions
    assert prag.generate_patronymic("Илья", gender="masc") == "Ильич"
    assert prag.generate_patronymic("Илья", gender="fem") == "Ильинична"

    # Respectful full name
    assert prag.format_full_respectful_name("Александр", "Сергей", gender="masc") == "Александр Сергеевич"

    # Register detection
    assert prag.detect_register("Здравствуйте, уважаемый коллега!") == "formal_business"
    assert prag.detect_register("Привет, ты пойдёшь с нами?") == "informal_friendly"


def test_russian_dependency_parsing():
    parser = RussianDependencyParser()
    parsed = parser.parse("Студент прочитал книгу.")

    assert parsed["root_index"] == 1
    deprels = [n["deprel"] for n in parsed["nodes"]]
    assert "root" in deprels
    assert "nsubj" in deprels
    assert "obj" in deprels


def test_russian_sentence_generation():
    generator = RussianSentenceGenerator()

    # SVO Generation with Inanimate Object: Студент прочитал стол.
    sent1 = generator.generate_transitive_svo(
        subj_lemma="студент",
        subj_gender="masc",
        verb_lemma="прочитать",
        obj_lemma="стол",
        obj_gender="masc",
        obj_declension="2nd",
        obj_animacy=False,
        tense="past"
    )
    assert sent1 == "Студент прочитал стол."

    # SVO Generation with Animate Object: Преподаватель встретил студента.
    sent2 = generator.generate_transitive_svo(
        subj_lemma="преподаватель",
        subj_gender="masc",
        verb_lemma="встретить",
        obj_lemma="студент",
        obj_gender="masc",
        obj_declension="2nd",
        obj_animacy=True,
        tense="past"
    )
    assert "студента." in sent2


def test_russian_cognitive_analyzers():
    case_analyzer = RussianCaseGovernmentAnalyzer()
    aspect_analyzer = RussianAspectChoiceAnalyzer()
    numeral_analyzer = RussianNumeralConcordAnalyzer()

    # Case government analysis
    case_res = case_analyzer.analyze("Мы идём к директору.")
    assert case_res["case_bitfield"] > 0
    assert len(case_res["preposition_checks"]) > 0

    # Aspect analysis
    aspect_res = aspect_analyzer.analyze("Он часто читал и вдруг встал.")
    assert aspect_res["total_verbs"] == 2
    assert aspect_res["imperfective_count"] >= 1
    assert aspect_res["perfective_count"] >= 1

    # Numeral concord audit
    num_res = numeral_analyzer.analyze("В проекте участвуют 2 инженера и 5 разработчиков.")
    assert len(num_res["pairs_audited"]) == 2
    assert num_res["is_valid"] is True


def test_russian_tasks():
    grammar_checker = RussianGrammarChecker()
    email_pipeline = RussianEmailPipeline()
    comp_pipeline = RussianCompositionPipeline()

    # 1. Grammar check
    g_res = grammar_checker.check("Студент прочитал интересную книгу.")
    assert g_res["is_clean"] is True
    assert g_res["quality_score"] == 100

    # 2. Email pipeline
    email = email_pipeline.compose_email(
        recipient_first_name="Иван",
        recipient_father_name="Петр",
        recipient_gender="masc",
        sender_name="Алексей",
        subject="План работ",
        register="formal_business"
    )
    assert "Иван Петрович" in email["recipient"]
    assert "С уважением," in email["valediction"]
    assert "Алексей" in email["full_email"]

    # 3. Composition pipeline
    comp = comp_pipeline.compose_report(
        engineer_name="Иван",
        task_count=3,
        component_lemma="модуль"
    )
    assert "3 задачи" in comp["full_text"]
    assert "3 модуля" in comp["full_text"]


def test_russian_sub_ais_and_amsv_bit_isolation():
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))

    syntax_ai = RussianSyntaxSubAI(amsv_view=amsv)
    phonology_ai = RussianPhonologySubAI(amsv_view=amsv)
    pragmatic_ai = RussianPragmaticSubAI(amsv_view=amsv)
    editorial_ai = RussianEditorialSubAI(amsv_view=amsv)

    initial_bytes = bytes(amsv.get_raw_bytes())
    assert len(initial_bytes) == 64
    assert all(b == 0 for b in initial_bytes)

    test_sentence = "Уважаемый директор внимательно прочитал официальный отчет."

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
    prag_eval = pragmatic_ai.evaluate("Здравствуйте, уважаемый Иван Сергеевич!")
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


def test_russian_six_language_matrix_and_orchestrator():
    amsv = AMSVEmbeddedView()
    bridge = RussianMatrixBridge(amsv_view=amsv)

    res = bridge.execute_matrix_pipeline("Инженер завершил задачу.")
    assert res["rust_safety"]["is_safe"] is True
    assert res["cuda_acceleration"]["parallel_batch_supported"] is True
    assert res["java_loom_service"]["direct_byte_buffer_capacity"] == 64
    assert res["amsv_synchronization"]["synced"] is True

    # Master Orchestrator End-to-End
    orchestrator = RussianEngineOrchestrator()
    sentence = "Инженер успешно завершил сложную задачу."
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
        recipient_first_name="Мария",
        recipient_father_name="Иван",
        recipient_gender="fem",
        sender_name="Константин",
        register="formal_business"
    )
    assert "Мария Ивановна" in email["recipient"]

    prose = orchestrator.compose_prose(author_name="Дмитрий", task_count=2)
    assert "2 задачи" in prose["full_text"]

    gen_sent = orchestrator.generate_sentence(
        subj_lemma="учитель",
        subj_gender="masc",
        verb_lemma="прочитать",
        obj_lemma="книга",
        obj_gender="fem",
        obj_declension="1st",
        tense="past"
    )
    assert "Учитель прочитал книгу." == gen_sent
