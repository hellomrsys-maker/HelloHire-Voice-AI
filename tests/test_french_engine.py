"""
Unit and Integration Test Suite for French Language Engine (French_engine).
Validates 9-layer compliance, 4 dedicated Sub-AIs, Six-Language Matrix nodes,
and strict Zero-Bridge 64-byte AMSV memory isolation.
"""

import pytest
from amsv.python.amsv_embedded import AMSVEmbeddedView

from French_engine.brain.skills.tokenization import FrenchTokenizer
from French_engine.brain.skills.pos_tagging import FrenchPOSTagger
from French_engine.brain.skills.verb_conjugator import FrenchVerbConjugator
from French_engine.brain.skills.liaison_elision_engine import LiaisonElisionEngine
from French_engine.brain.skills.agreement_engine import FrenchAgreementEngine
from French_engine.brain.skills.clitic_engine import FrenchCliticEngine
from French_engine.brain.skills.pragmatics_engine import FrenchPragmaticsEngine
from French_engine.brain.skills.parsing import FrenchParser
from French_engine.brain.skills.generation import FrenchGenerator

from French_engine.brain.analysis.non_pro_drop_analyzer import NonProDropAnalyzer
from French_engine.brain.analysis.auxiliary_agreement_analyzer import AuxiliaryAgreementAnalyzer
from French_engine.brain.analysis.subjunctive_trigger_evaluator import SubjunctiveTriggerEvaluator

from French_engine.brain.task.grammar_check import FrenchGrammarChecker
from French_engine.brain.task.email_pipeline import FrenchEmailPipeline
from French_engine.brain.task.composition_pipeline import FrenchCompositionPipeline

from French_engine.brain.sub_ais.syntax_sub_ai import FrenchSyntaxSubAI
from French_engine.brain.sub_ais.phonology_sub_ai import FrenchPhonologySubAI
from French_engine.brain.sub_ais.pragmatic_sub_ai import FrenchPragmaticSubAI
from French_engine.brain.sub_ais.editorial_sub_ai import FrenchEditorialSubAI

from French_engine.six_language_matrix.python.french_matrix_bridge import FrenchMatrixBridge
from French_engine.french_engine_orchestrator import FrenchEngineOrchestrator


def test_french_tokenizer_and_elision():
    tokenizer = FrenchTokenizer()
    text = "L'étudiant lit attentivement le livre de l'enseignant."
    tokens = tokenizer.tokenize(text)

    # Elision tokens should be isolated
    assert "l'" in tokens
    assert "étudiant" in tokens
    assert "livre" in tokens

    spans = tokenizer.get_token_spans(text)
    assert len(spans) == len(tokens)
    for tok, start, end in spans:
        assert text[start:end] == tok


def test_french_pos_tagging():
    tagger = FrenchPOSTagger()
    tokens = ["le", "professeur", "explique", "la", "règle", "aux", "étudiants", "."]
    tagged = tagger.tag(tokens)

    tag_dict = dict(tagged)
    assert tag_dict["le"] == "DET"
    assert tag_dict["la"] == "DET"
    assert tag_dict["aux"] == "ADP"
    assert tag_dict["."] == "PUNCT"
    assert tag_dict["explique"] == "VERB"


def test_french_verb_conjugation_and_auxiliaries():
    conjugator = FrenchVerbConjugator()

    # Regular -er verb (parler)
    pres_parler = conjugator.conjugate("parler", "present")
    assert pres_parler == ["parle", "parles", "parle", "parlons", "parlez", "parlent"]

    # Auxiliary classification: DR MRS VANDERTRAMP motion verbs take être
    assert conjugator.get_auxiliary("aller") == "être"
    assert conjugator.get_auxiliary("venir") == "être"
    assert conjugator.get_auxiliary("partir") == "être"
    assert conjugator.get_auxiliary("parler") == "avoir"
    assert conjugator.get_auxiliary("manger") == "avoir"

    # Passé composé with agreement
    pc_aller_fem_pl = conjugator.conjugate_passe_compose("aller", subject_gender="F", subject_number="PL")
    assert "sont allées" in pc_aller_fem_pl[5]

    # Lemmatization
    lem_res = conjugator.lemmatize("suis")
    assert lem_res["lemma"] == "être"
    assert lem_res["is_irregular"] is True


def test_french_liaison_and_elision_engine():
    engine = LiaisonElisionEngine()

    # Valid elision
    v1 = engine.evaluate_elision("l'", "homme")
    assert v1["is_valid"] is True

    # Missing elision: "le ami"
    v2 = engine.evaluate_elision("le", "ami")
    assert v2["is_valid"] is False
    assert v2["error_type"] == "missing_elision"

    # Forbidden elision before h aspiré: "l'héros"
    v3 = engine.evaluate_elision("l'", "héros")
    assert v3["is_valid"] is False
    assert v3["error_type"] == "illicit_elision_h_aspire"

    # Valid non-elision before h aspiré: "le héros"
    v4 = engine.evaluate_elision("le", "héros")
    assert v4["is_valid"] is True

    # Liaison realization: "les amis" -> /z/
    l1 = engine.evaluate_liaison("les", "amis")
    assert l1["has_liaison"] is True
    assert l1["phonetic_realization"] == "z"

    # Forbidden liaison after "et"
    l2 = engine.evaluate_liaison("et", "un")
    assert l2["has_liaison"] is False
    assert l2["is_forbidden"] is True


def test_french_agreement_engine():
    engine = FrenchAgreementEngine()

    # Noun-Adjective agreement: "fille intelligente" (F SG)
    a1 = engine.evaluate_noun_adjective_agreement("F", "SG", "intelligent", "intelligente")
    assert a1["is_valid"] is True

    a2 = engine.evaluate_noun_adjective_agreement("F", "PL", "intelligent", "intelligentes")
    assert a2["is_valid"] is True

    # Participle agreement with être (agrees with subject)
    p1 = engine.evaluate_participle_with_etre("F", "SG", "parti", "partie")
    assert p1["is_valid"] is True

    # Participle agreement with avoir (preceding COD)
    p2 = engine.evaluate_participle_with_avoir(
        cod_precedes=True,
        cod_gender="F",
        cod_number="PL",
        participle_base="mangé",
        participle_surface="mangées"
    )
    assert p2["is_valid"] is True

    # Participle agreement with avoir (following COD: no agreement)
    p3 = engine.evaluate_participle_with_avoir(
        cod_precedes=False,
        participle_base="mangé",
        participle_surface="mangé"
    )
    assert p3["is_valid"] is True


def test_french_clitic_sequencing():
    engine = FrenchCliticEngine()

    # Valid pre-verbal clitic order: me (1) before le (2)
    s1 = engine.evaluate_clitic_sequence(["me", "le"])
    assert s1["is_valid"] is True

    # Valid: le (2) before lui (3)
    s2 = engine.evaluate_clitic_sequence(["le", "lui"])
    assert s2["is_valid"] is True

    # Invalid order: lui (3) before le (2)
    s3 = engine.evaluate_clitic_sequence(["lui", "le"])
    assert s3["is_valid"] is False

    # Imperative postposed order: donne-le-moi
    imp1 = engine.evaluate_imperative_clitics("donne-le-moi")
    assert imp1["is_valid"] is True


def test_french_pragmatics_and_t_v_register():
    engine = FrenchPragmaticsEngine()

    # Vouvoiement
    r1 = engine.evaluate_register("Bonjour Madame, pourriez-vous m'accorder un rendez-vous s'il vous plaît ?")
    assert r1["assigned_register"] == "vouvoiement"
    assert r1["is_formal"] is True
    assert r1["politeness_score"] >= 0.85

    # Tutoiement
    r2 = engine.evaluate_register("Salut, tu viens au cinéma ce soir avec ton frère ?")
    assert r2["assigned_register"] == "tutoiement"
    assert r2["is_informal"] is True

    # Register clash (tu mixed with vous)
    r3 = engine.evaluate_register("Tu pourrais me donner votre avis sur ce document ?")
    assert r3["has_register_clash"] is True


def test_french_sentence_generation():
    generator = FrenchGenerator()

    # Declarative statement with non-pro-drop subject
    s1 = generator.generate_statement("nous", "finir", "le projet", tense="present")
    assert s1 == "Nous finissons le projet."

    # Negative statement with ne...pas
    s2 = generator.generate_statement("il", "manger", "la pomme", negative=True)
    assert s2 == "Il ne mange pas la pomme."

    # Interrogative with inversion
    q1 = generator.generate_question("vous", "parler", "français", method="inversion")
    assert q1 == "Parlez-vous français ?"

    # Interrogative with est-ce que
    q2 = generator.generate_question("tu", "comprendre", method="est_ce_que")
    assert "Est-ce que" in q2


def test_french_cognitive_analyzers():
    non_pro_drop = NonProDropAnalyzer()
    aux_analyzer = AuxiliaryAgreementAnalyzer()
    subj_evaluator = SubjunctiveTriggerEvaluator()

    # Non-pro-drop: overt subject present
    r1 = non_pro_drop.analyze("Elle étudie la linguistique moderne.")
    assert r1["conforms_to_non_pro_drop"] is True
    assert r1["has_overt_subject"] is True

    # Non-pro-drop: dummy expletive subject (il faut)
    r2 = non_pro_drop.analyze("Il faut partir maintenant.")
    assert r2["is_expletive"] is True
    assert r2["conforms_to_non_pro_drop"] is True

    # Compound tense analysis: elle est allée
    r3 = aux_analyzer.analyze_construction(
        verb_lemma="aller",
        auxiliary_used="est",
        participle_surface="allée",
        subject_gender="F",
        subject_number="SG"
    )
    assert r3["is_grammatically_sound"] is True
    assert r3["expected_auxiliary"] == "être"

    # Subjunctive trigger evaluation: il faut que
    r4 = subj_evaluator.evaluate_clause("Il faut que tu fasses attention.")
    assert r4["requires_subjunctive"] is True
    assert "il faut que" in r4["triggers_detected"]


def test_french_tasks():
    grammar_checker = FrenchGrammarChecker()
    email_pipeline = FrenchEmailPipeline()
    comp_pipeline = FrenchCompositionPipeline()

    # Grammar check clean sentence
    res1 = grammar_checker.check("Nous travaillons ensemble avec enthousiasme.")
    assert res1["is_valid"] is True
    assert res1["score"] == 1.0

    # Grammar check sentence with missing elision ("le ami")
    res2 = grammar_checker.check("Je vois le ami de Marie.")
    assert res2["is_valid"] is False
    assert any(iss["type"] == "missing_elision" for iss in res2["issues"])

    # Email generation
    email_res = email_pipeline.generate_email(
        recipient_name="Dupont",
        recipient_title="Professeur",
        topic="Projet Linguistique",
        body_content="Je vous transmets ci-joint le compte rendu architectural.",
        sender_name="Jean-Luc Martin",
        formal=True
    )
    assert "Professeur Dupont," in email_res["full_email"]
    assert "salutations distinguées" in email_res["full_email"]
    assert email_res["is_formal"] is True

    # Composition statement
    comp_res = comp_pipeline.compose_statement(
        subject="ils",
        verb_lemma="parler",
        obj="français couramment"
    )
    assert comp_res["composed_text"] == "Ils parlent français couramment."


def test_french_sub_ais_and_amsv_bit_isolation():
    """
    CRITICAL ZERO-BRIDGE TEST:
    Validates that each Sub-AI updates strictly its designated byte offsets in the 64-byte AMSV
    with zero unintended bit contamination or cross-subsystem bleeding.
    """
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))

    syntax_ai = FrenchSyntaxSubAI(amsv_view=amsv)
    phonology_ai = FrenchPhonologySubAI(amsv_view=amsv)
    pragmatic_ai = FrenchPragmaticSubAI(amsv_view=amsv)
    editorial_ai = FrenchEditorialSubAI(amsv_view=amsv)

    initial_bytes = bytes(amsv.get_raw_bytes())
    assert len(initial_bytes) == 64
    assert all(b == 0 for b in initial_bytes)

    # 1. Syntax Sub-AI: writes to Byte 18 (0x12) and Byte 52 (0x34)
    syntax_eval = syntax_ai.evaluate("Le professeur explique la théorie aux étudiants attentifs.")
    assert syntax_eval.has_overt_subject is True
    b_syntax = bytes(amsv.get_raw_bytes())

    assert b_syntax[18] > 0, "Syntax Sub-AI must write to Byte 18"
    assert b_syntax[52] > 0, "Syntax Sub-AI must write to Byte 52"
    assert all(b == 0 for b in b_syntax[0:16]), "Bytes 0..15 must remain pristine"
    assert all(b == 0 for b in b_syntax[20:28]), "Bytes 20..27 must remain pristine"
    assert all(b == 0 for b in b_syntax[54:64]), "Bytes 54..63 must remain pristine"

    # 2. Phonology Sub-AI: writes to Bytes 0..15 and Byte 24 (0x18)
    phonology_eval = phonology_ai.evaluate("Les anciens amis ont chanté ensemble dans la grande maison.")
    assert phonology_eval.syllable_count >= 10
    b_phono = bytes(amsv.get_raw_bytes())

    assert any(b > 0 for b in b_phono[0:8]), "Phonology Sub-AI must write to Bytes 0..7"
    assert any(b > 0 for b in b_phono[8:16]), "Phonology Sub-AI must write to Bytes 8..15"
    assert b_phono[24] > 0, "Phonology Sub-AI must write to Byte 24"
    assert b_phono[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_phono[52] == b_syntax[52], "Byte 52 must be preserved"

    # 3. Pragmatic Sub-AI: writes to Byte 22 (0x16) and Byte 54 (0x36)
    pragmatic_eval = pragmatic_ai.evaluate("Veuillez agréer, Monsieur, l'expression de mes salutations distinguées.")
    assert pragmatic_eval.is_formal is True
    b_prag = bytes(amsv.get_raw_bytes())

    assert b_prag[22] > 0, "Pragmatic Sub-AI must write to Byte 22"
    assert b_prag[54] > 0, "Pragmatic Sub-AI must write to Byte 54"
    assert b_prag[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_prag[24] == b_phono[24], "Byte 24 must be preserved"

    # 4. Editorial Sub-AI: writes to Byte 20 (0x14) and Byte 26 (0x1A)
    editorial_eval = editorial_ai.evaluate("L'architecture cognitive démontre une remarquable rigueur scientifique.")
    assert editorial_eval.is_clean is True
    b_edit = bytes(amsv.get_raw_bytes())

    assert b_edit[20] > 0, "Editorial Sub-AI must write to Byte 20"
    assert b_edit[26] > 0, "Editorial Sub-AI must write to Byte 26"
    assert b_edit[18] == b_syntax[18], "Byte 18 must be preserved"
    assert b_edit[22] == b_prag[22], "Byte 22 must be preserved"
    assert b_edit[24] == b_phono[24], "Byte 24 must be preserved"
    assert b_edit[52] == b_syntax[52], "Byte 52 must be preserved"
    assert b_edit[54] == b_prag[54], "Byte 54 must be preserved"


def test_french_six_language_matrix():
    clean_buf = bytearray(64)
    amsv = AMSVEmbeddedView(raw_buffer=memoryview(clean_buf))
    bridge = FrenchMatrixBridge(amsv_view=amsv)

    res = bridge.execute_matrix_pipeline(
        text="« Nous sommes arrivés à Paris », dit-il.",
        syntax_score=0.96,
        phonology_score=0.92,
        register_score=0.88
    )

    assert res["rust_safety"]["is_safe"] is True
    assert res["rust_safety"]["guillemets_balanced"] is True
    assert res["cpp_engine"]["has_etre_motion_verb"] is True
    assert res["cuda_kernel"]["batch_acceleration"] is True
    assert res["java_service"]["loom_virtual_threads"] is True
    assert res["julia_dynamics"]["entropy_model"] == "syllabic_duration"
    assert res["amsv_zero_bridge_synced"] is True

    # Verify AMSV direct write
    raw = bytes(amsv.get_raw_bytes())
    assert raw[18] > 0
    assert raw[22] > 0
    assert raw[24] > 0
    assert raw[52] > 0
    assert raw[54] > 0


def test_french_engine_orchestrator_end_to_end():
    orchestrator = FrenchEngineOrchestrator()
    sample = "Le chercheur présente ses travaux devant l'académie des sciences."
    result = orchestrator.analyze(sample)

    assert len(result.tokens) > 5
    assert result.sentence_structure.has_overt_subject is True
    assert result.non_pro_drop_analysis["conforms_to_non_pro_drop"] is True
    assert result.syntax_eval.is_valid_sentence is True
    assert result.phonology_eval.syllable_count > 5
    assert result.editorial_eval.is_clean is True
    assert result.overall_linguistic_score >= 0.70
    assert result.amsv_synced is True
