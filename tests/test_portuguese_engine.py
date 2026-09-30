"""
Unit and Integration Test Suite for the Portuguese Language Engine (Português).
Tests all 9 layers, 9 computational skills, 3 cognitive analyzers,
3 task pipelines, 4 dedicated Sub-AIs, 6-language matrix, and Zero-Bridge AMSV sync.
"""

import pytest
from amsv.python.amsv_embedded import AMSVEmbeddedView

from Portuguese_engine.brain.skills.tokenization import PortugueseTokenizer
from Portuguese_engine.brain.skills.pos_tagging import PortuguesePOSTagger
from Portuguese_engine.brain.skills.verb_conjugator import PortugueseVerbConjugator
from Portuguese_engine.brain.skills.clitic_engine import PortugueseCliticEngine
from Portuguese_engine.brain.skills.contraction_engine import PortugueseContractionEngine
from Portuguese_engine.brain.skills.ser_estar_engine import PortugueseSerEstarEngine
from Portuguese_engine.brain.skills.pragmatics_engine import PortuguesePragmaticsEngine
from Portuguese_engine.brain.skills.parsing import PortugueseParser
from Portuguese_engine.brain.skills.generation import PortugueseGenerator

from Portuguese_engine.brain.analysis.clitic_placement_analyzer import CliticPlacementAnalyzer
from Portuguese_engine.brain.analysis.crase_contraction_analyzer import CraseContractionAnalyzer
from Portuguese_engine.brain.analysis.subjunctive_concord_analyzer import SubjunctiveConcordAnalyzer

from Portuguese_engine.brain.task.grammar_check import PortugueseGrammarCheckTask
from Portuguese_engine.brain.task.email_pipeline import PortugueseEmailPipelineTask
from Portuguese_engine.brain.task.composition_pipeline import PortugueseCompositionPipelineTask

from Portuguese_engine.brain.sub_ais.syntax_sub_ai import PortugueseSyntaxSubAI
from Portuguese_engine.brain.sub_ais.phonology_sub_ai import PortuguesePhonologySubAI
from Portuguese_engine.brain.sub_ais.pragmatic_sub_ai import PortuguesePragmaticSubAI
from Portuguese_engine.brain.sub_ais.editorial_sub_ai import PortugueseEditorialSubAI

from Portuguese_engine.six_language_matrix.python.portuguese_matrix_bridge import PortugueseMatrixBridge
from Portuguese_engine.portuguese_engine_orchestrator import PortugueseEngineOrchestrator


def test_portuguese_tokenizer_and_clitic_contractions():
    tokenizer = PortugueseTokenizer()
    text = "O professor disse-me que o trabalho estava no arquivo."
    tokens = tokenizer.tokenize(text)

    assert "O" in tokens
    assert "professor" in tokens
    assert "disse-me" in tokens
    assert "no" in tokens

    # Clitic detachment
    stem, clitic = tokenizer.split_clitic("disse-me")
    assert stem == "disse"
    assert clitic == "me"

    stem2, clitic2 = tokenizer.split_clitic("fazê-lo")
    assert stem2 == "fazê"
    assert clitic2 == "lo"

    # Contraction expansion
    expansion = tokenizer.expand_contraction("no")
    assert expansion == ("em", "o")

    expansion_da = tokenizer.expand_contraction("da")
    assert expansion_da == ("de", "a")


def test_portuguese_pos_tagging():
    tagger = PortuguesePOSTagger()
    tokens = ["Ele", "não", "comeu", "a", "maçã", "ontem", "."]
    tagged = tagger.tag_tokens(tokens)

    tag_map = {item["token"]: item["pos"] for item in tagged}
    assert tag_map["Ele"] == "PRON"
    assert tag_map["não"] == "ADV"
    assert tag_map["comeu"] == "VERB"
    assert tag_map["a"] == "DET"
    assert tag_map["ontem"] == "ADV"


def test_portuguese_verb_conjugator_and_personal_infinitive():
    conj = PortugueseVerbConjugator()

    # Regular verb: falar
    assert conj.conjugate("falar", "indicativo", "presente", "eu") == "falo"
    assert conj.conjugate("falar", "indicativo", "perfeito", "ele") == "falou"
    assert conj.conjugate("falar", "subjuntivo", "futuro", "tu") == "falares"

    # Personal infinitive (infinitivo pessoal)
    assert conj.conjugate_personal_infinitive("fazer", "nos") == "fazermos"
    assert conj.conjugate_personal_infinitive("fazer", "tu") == "fazeres"
    assert conj.conjugate_personal_infinitive("comer", "eles") == "comerem"

    # Irregular verbs
    assert conj.conjugate("fazer", "indicativo", "presente", "eu") == "faço"
    assert conj.conjugate("fazer", "indicativo", "perfeito", "ele") == "fez"
    assert conj.conjugate("dizer", "indicativo", "futuro", "eu") == "direi"

    # Lemmatization
    lem_info = conj.lemmatize("fazemos")
    assert lem_info is not None
    lemma, mood, tense, person = lem_info
    assert lemma == "fazer"
    assert person == "nos"


def test_portuguese_clitic_engine_and_allomorphy():
    clitic_engine = PortugueseCliticEngine()

    # Rule 1: dropped -r/-s/-z -> -lo/-la
    res1 = clitic_engine.apply_enclisis("fazer", "o")
    assert res1 == "fazê-lo"

    res2 = clitic_engine.apply_enclisis("comer", "as")
    assert res2 == "comê-las"

    # Rule 2: nasal endings -> -no/-na
    res3 = clitic_engine.apply_enclisis("fazem", "o")
    assert res3 == "fazem-no"

    res4 = clitic_engine.apply_enclisis("dão", "as")
    assert res4 == "dão-nas"

    # Mesoclisis
    meso = clitic_engine.apply_mesoclisis("dir", "te", "ei")
    assert meso == "dir-te-ei"

    # Proclisis attractor validation: "não" triggers proclisis
    valid_proc, _ = clitic_engine.validate_placement(["não"], "disse", "me", is_enclitic=False)
    assert valid_proc is True

    invalid_enc, msg = clitic_engine.validate_placement(["não"], "disse", "me", is_enclitic=True)
    assert invalid_enc is False
    assert "demands proclisis" in msg


def test_portuguese_contraction_and_crase():
    contraction_engine = PortugueseContractionEngine()

    assert contraction_engine.contract("de", "o") == "do"
    assert contraction_engine.contract("em", "a") == "na"
    assert contraction_engine.contract("a", "a") == "à"
    assert contraction_engine.contract("por", "o") == "pelo"

    # Crase validation:
    # Valid before feminine noun
    valid_crase, _ = contraction_engine.validate_crase("praia", has_crase=True)
    assert valid_crase is True

    # Prohibited before verb: "à partir"
    invalid_verb, _ = contraction_engine.validate_crase("partir", has_crase=True)
    assert invalid_verb is False

    # Prohibited before masculine noun: "à pé"
    invalid_masc, _ = contraction_engine.validate_crase("pé", has_crase=True)
    assert invalid_masc is False


def test_portuguese_ser_vs_estar():
    ser_estar = PortugueseSerEstarEngine()

    assert ser_estar.select_copula("identity") == "ser"
    assert ser_estar.select_copula("profession") == "ser"
    assert ser_estar.select_copula("temporary_state") == "estar"
    assert ser_estar.select_copula("location") == "estar"

    # Semantic shift
    shift_info = ser_estar.analyze_semantic_shift("bom", "estar")
    assert shift_info["has_shift"] is True
    assert "tasty" in shift_info["meaning"] or "health" in shift_info["meaning"]

    # Continuous aspect dialect validation
    v_pt, _ = ser_estar.validate_progressive_aspect("estou a fazer", dialect="pt_pt")
    assert v_pt is True

    v_br, _ = ser_estar.validate_progressive_aspect("estou fazendo", dialect="pt_br")
    assert v_br is True


def test_portuguese_pragmatics_and_address_tiers():
    prag = PortuguesePragmaticsEngine()

    # Formal register
    tokens_form = ["Prezado", "Senhor", "atenciosamente", "."]
    res_form = prag.evaluate_pragmatics(tokens_form)
    assert res_form["tier"] == "formal"
    assert res_form["politeness_score"] >= 0.90

    # Familiar register
    tokens_fam = ["Você", "vai", "ao", "cinema", ",", "amigo", "?"]
    res_fam = prag.evaluate_pragmatics(tokens_fam)
    assert res_fam["tier"] == "familiar"

    assert prag.get_epistolary_closing("formal") == "Atenciosamente,"


def test_portuguese_sentence_generation():
    generator = PortugueseGenerator()

    # Generate affirmative SVO with enclisis
    sent1 = generator.generate_clause(
        verb_lemma="dizer",
        subject="Ele",
        clitic="me",
        direct_object="a verdade",
        tense="presente",
        person="ele"
    )
    assert "Ele" in sent1
    assert "diz-me" in sent1
    assert "a verdade." in sent1

    # Generate negative sentence triggering proclisis
    sent2 = generator.generate_clause(
        verb_lemma="dizer",
        subject="Ele",
        clitic="me",
        direct_object="a verdade",
        negative=True,
        tense="presente",
        person="ele"
    )
    assert "Ele não me diz a verdade." == sent2


def test_portuguese_cognitive_analyzers():
    clitic_analyzer = CliticPlacementAnalyzer()
    crase_analyzer = CraseContractionAnalyzer()
    subj_analyzer = SubjunctiveConcordAnalyzer()

    # Clitic error detection: "não disse-me"
    clitic_res = clitic_analyzer.analyze_sentence("Ele não disse-me a verdade.")
    assert clitic_res["is_valid"] is False
    assert len(clitic_res["diagnostics"]) > 0

    # Crase error detection: "à pé"
    crase_res = crase_analyzer.analyze_sentence("Fui à pé até lá.")
    assert crase_res["is_valid"] is False
    assert any(d["error_type"] == "PROHIBITED_CRASE" for d in crase_res["diagnostics"])

    # Subjunctive trigger check
    subj_res = subj_analyzer.analyze_sentence("Quando você chegar, começaremos.")
    assert subj_res["has_subjunctive_trigger"] is True


def test_portuguese_tasks():
    grammar_task = PortugueseGrammarCheckTask()
    email_task = PortugueseEmailPipelineTask()
    comp_task = PortugueseCompositionPipelineTask()

    # 1. Proofreading clean sentence
    g_res = grammar_task.run("Ele me disse a verdade ontem.")
    assert g_res["overall_score"] >= 0.85

    # 2. Email composition
    email_res = email_task.compose_email(
        recipient_name="Carlos",
        sender_name="Mariana",
        purpose="meeting",
        tier="formal"
    )
    assert "Prezado(a) Carlos," in email_res["full_email"]
    assert "Atenciosamente," in email_res["full_email"]

    # 3. Prose composition with personal infinitive
    comp_res = comp_task.compose_narrative(topic="project", dialect="pt_br")
    assert len(comp_res["clauses"]) == 3
    assert "Para nós fazermos" in comp_res["composed_prose"]


def test_portuguese_sub_ais_and_amsv_bit_isolation():
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))

    syntax_ai = PortugueseSyntaxSubAI(amsv_view=amsv)
    phonology_ai = PortuguesePhonologySubAI(amsv_view=amsv)
    pragmatic_ai = PortuguesePragmaticSubAI(amsv_view=amsv)
    editorial_ai = PortugueseEditorialSubAI(amsv_view=amsv)

    initial_bytes = bytes(amsv.get_raw_bytes())
    assert len(initial_bytes) == 64
    assert all(b == 0 for b in initial_bytes)

    test_sentence = "O professor entregou-lhe o livro com atenção."

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
    prag_eval = pragmatic_ai.evaluate("Prezado Senhor, agradeço pela atenção.")
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

    # Bit Isolation Check: Byte 30 and 31 must remain 0
    assert b_edit[30] == 0
    assert b_edit[31] == 0


def test_portuguese_six_language_matrix():
    amsv = AMSVEmbeddedView()
    bridge = PortugueseMatrixBridge(amsv_view=amsv)

    res = bridge.execute_matrix_pipeline("O aluno entregou-me o relatório.")
    assert res["rust_safety"]["is_safe"] is True
    assert res["cpp_engine"]["has_clitic"] is True
    assert res["cuda_acceleration"]["parallel_batch_supported"] is True
    assert res["java_loom_service"]["direct_byte_buffer_capacity"] == 64
    assert res["amsv_synchronization"]["synced"] is True


def test_portuguese_engine_orchestrator_end_to_end():
    orchestrator = PortugueseEngineOrchestrator()

    test_sentence = "O diretor entregou-lhe o documento com satisfação."
    analysis = orchestrator.analyze(test_sentence)

    assert analysis.input_text == test_sentence
    assert len(analysis.tokens) > 0
    assert analysis.syntax_eval.syntactic_integrity_score > 0.6
    assert analysis.overall_linguistic_score > 0.6
    assert analysis.amsv_synced is True

    # Orchestrator convenience wrappers
    proof = orchestrator.proofread(test_sentence)
    assert "overall_score" in proof

    email = orchestrator.compose_email(recipient_name="Beatriz", sender_name="Leonardo", tier="familiar")
    assert "Olá, Beatriz," in email["full_email"]

    prose = orchestrator.compose_prose(topic="project")
    assert len(prose["clauses"]) == 3

    gen_sent = orchestrator.generate_sentence(
        verb_lemma="falar",
        subject="Nós",
        direct_object="com o professor",
        tense="presente",
        person="nos"
    )
    assert "Nós falamos com o professor." == gen_sent
