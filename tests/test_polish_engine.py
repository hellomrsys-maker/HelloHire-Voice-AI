"""
Comprehensive Test Suite for Polish Sovereign Language Engine
Adheres strictly to the Zero-Bridge Synchronous Memory Rule.
17 Automated Test Cases covering all cognitive layers, sub-AIs, invariants,
prefix semantics, AMSV Resonance Protocol, Stage 3 Network, and AHN binding.
"""

import ctypes
import pytest
from Polish_engine import (
    PolishEngineOrchestrator,
    POLISH_AMSV_MAGIC,
    POLISH_ENGINE_ID,
    PolishAtomicMemoryStateVector,
    PolishMatrixMemoryBridge
)
from Polish_engine.brain.skills.genitive_negation_engine import PolishGenitiveNegationEngine
from Polish_engine.brain.skills.aspect_engine import PolishAspectEngine
from Polish_engine.brain.skills.honorific_deixis_engine import PolishHonorificDeixisEngine
from Polish_engine.brain.skills.phonology_sibilant_engine import PolishPhonologySibilantEngine
from Polish_engine.brain.skills.generation import PolishGenerator
from Polish_engine.brain.skills.tokenization import PolishTokenizer
from Polish_engine.brain.skills.pos_tagging import PolishPOSTagger
from Polish_engine.brain.skills.prefix_semantic_engine import PolishPrefixSemanticEngine
from Polish_engine.brain.skills.morpheme_generator import PolishMorphemeGenerator, PolishOpenVocabClassifier
from Polish_engine.brain.task.grammar_check import PolishGrammarChecker
from Polish_engine.brain.task.email_pipeline import PolishEmailPipeline
from Polish_engine.brain.task.composition_pipeline import PolishCompositionPipeline
from amsv.amsv_namespace import (
    AMSVHierarchicalNamespace,
    COGNITIVE_PROFILES,
    compute_verbal_reasoning_bonus,
    decode_cognitive_difficulty_vector,
)

@pytest.fixture
def orchestrator():
    return PolishEngineOrchestrator()

# Test 1: AMSV Exact 64-Byte Size and Magic Signature
def test_amsv_magic_and_64byte_size():
    assert ctypes.sizeof(PolishAtomicMemoryStateVector) == 64
    vec = PolishAtomicMemoryStateVector()
    vec.magic = POLISH_AMSV_MAGIC
    vec.engine_id = POLISH_ENGINE_ID
    assert vec.magic == 0x504F4C53  # "POLS"
    assert vec.engine_id == 9

    bridge = PolishMatrixMemoryBridge()
    buf = bridge.get_bytearray()
    assert len(buf) == 64
    magic_unpacked = int.from_bytes(buf[0:4], byteorder="little")
    assert magic_unpacked == 0x504F4C53

# Test 2: Tokenization and POS Tagging
def test_tokenizer_and_pos_tagger():
    tok = PolishTokenizer()
    text = "Jan czyta nową książkę w pokoju."
    tokens = tok.tokenize(text)
    assert len(tokens) >= 6
    assert "książkę" in tokens

    tagger = PolishPOSTagger()
    tagged = tagger.tag(tokens)
    tag_map = dict(tagged)
    assert tag_map.get("czyta") == "VERB"
    assert tag_map.get("w") == "ADP"

# Test 3: Genitive of Negation - Affirmative Takes Accusative
def test_genitive_of_negation_affirmative_accusative():
    neg_engine = PolishGenitiveNegationEngine()
    tok = PolishTokenizer()

    tokens = tok.tokenize("Czytam książkę.")
    res = neg_engine.verify_sentence(tokens)
    assert res["is_negated"] is False
    assert res["genitive_of_negation_valid"] is True
    assert len(res["errors"]) == 0

# Test 4: Genitive of Negation - Negative Takes Mandatory Genitive
def test_genitive_of_negation_mandatory_shift():
    neg_engine = PolishGenitiveNegationEngine()
    tok = PolishTokenizer()

    # Correct: Nie czytam książki (GEN)
    tokens_ksiazki = tok.tokenize("Nie czytam książki.")
    res1 = neg_engine.verify_sentence(tokens_ksiazki)
    assert res1["is_negated"] is True
    assert res1["genitive_of_negation_valid"] is True
    assert res1["genitive_verified"] is True
    assert len(res1["errors"]) == 0

    # Correct: Nie mam czasu (GEN)
    tokens_czasu = tok.tokenize("Nie mam czasu.")
    res2 = neg_engine.verify_sentence(tokens_czasu)
    assert res2["is_negated"] is True
    assert res2["genitive_of_negation_valid"] is True
    assert res2["genitive_verified"] is True

# Test 5: Genitive of Negation - Violation Detection
def test_genitive_of_negation_violation_detection():
    neg_engine = PolishGenitiveNegationEngine()
    tok = PolishTokenizer()

    # Incorrect: *Nie czytam książkę (ACC under negation)
    tokens_bad1 = tok.tokenize("Nie czytam książkę.")
    res1 = neg_engine.verify_sentence(tokens_bad1)
    assert res1["is_negated"] is True
    assert res1["genitive_of_negation_valid"] is False
    assert any("Genitive of Negation Violation" in err for err in res1["errors"])

    # Incorrect: *Nie mam czas (ACC under negation)
    tokens_bad2 = tok.tokenize("Nie mam czas.")
    res2 = neg_engine.verify_sentence(tokens_bad2)
    assert res2["is_negated"] is True
    assert res2["genitive_of_negation_valid"] is False
    assert any("Genitive of Negation Violation" in err for err in res2["errors"])

# Test 6: Verbal Aspect Classification (Imperfective vs Perfective)
def test_verbal_aspect_classification():
    aspect_engine = PolishAspectEngine()

    assert aspect_engine.classify_aspect("pisać") == "imperfective"
    assert aspect_engine.classify_aspect("napisać") == "perfective"
    assert aspect_engine.classify_aspect("czytam") == "imperfective"
    assert aspect_engine.classify_aspect("przeczytam") == "perfective"
    assert aspect_engine.classify_aspect("robić") == "imperfective"
    assert aspect_engine.classify_aspect("zrobić") == "perfective"

# Test 7: Verbal Aspect Pairs
def test_verbal_aspect_pairs():
    aspect_engine = PolishAspectEngine()

    pair_pisac = aspect_engine.get_aspect_pair("pisać")
    assert pair_pisac is not None
    assert pair_pisac["perfective"] == "napisać"

    pair_napisac = aspect_engine.get_aspect_pair("napisać")
    assert pair_napisac is not None
    assert pair_napisac["imperfective"] == "pisać"

    pair_kupowac = aspect_engine.get_aspect_pair("kupować")
    assert pair_kupowac["perfective"] == "kupić"

# Test 8: Honorific Deixis Third-Person Concord
def test_honorific_deixis_third_person_concord():
    hon_engine = PolishHonorificDeixisEngine()
    tok = PolishTokenizer()

    # Valid: Czy Pan wie? (3SG)
    tokens1 = tok.tokenize("Czy Pan wie, gdzie jest biblioteka?")
    res1 = hon_engine.verify_honorific_agreement(tokens1)
    assert res1["is_formal"] is True
    assert res1["honorific_concord_valid"] is True
    assert len(res1["errors"]) == 0

    # Valid: Czy Pani czytała raport? (3SG)
    tokens2 = tok.tokenize("Czy Pani czytała raport?")
    res2 = hon_engine.verify_honorific_agreement(tokens2)
    assert res2["is_formal"] is True
    assert res2["honorific_concord_valid"] is True

# Test 9: Honorific Deixis Violation Detection (2nd-person discord)
def test_honorific_deixis_violation_detection():
    hon_engine = PolishHonorificDeixisEngine()
    tok = PolishTokenizer()

    # Violation: *Czy Pan wiesz? (2SG verb with formal Pan)
    tokens1 = tok.tokenize("Czy Pan wiesz?")
    res1 = hon_engine.verify_honorific_agreement(tokens1)
    assert res1["is_formal"] is True
    assert res1["honorific_concord_valid"] is False
    assert any("Honorific Concord Violation" in err for err in res1["errors"])

    # Violation: *Czy Pani czytałaś? (2SG past with formal Pani)
    tokens2 = tok.tokenize("Czy Pani czytałaś raport?")
    res2 = hon_engine.verify_honorific_agreement(tokens2)
    assert res2["is_formal"] is True
    assert res2["honorific_concord_valid"] is False

# Test 10: Phonology Sibilant and Homophone Check
def test_phonology_sibilant_and_homophone_check():
    phon_engine = PolishPhonologySibilantEngine()
    tok = PolishTokenizer()

    # Valid sentence with nasal vowels and sibilants
    tokens = tok.tokenize("Wierzę, że wszystko się ułoży.")
    res = phon_engine.check_orthography(tokens)
    assert res["has_nasal_vowels"] is True
    assert res["has_sibilants"] is True
    assert res["is_valid"] is True

    # Homophone confusion: *może Bałtyckie instead of morze Bałtyckie
    tokens_bad = tok.tokenize("Płyniemy przez może bałtyckie.")
    res_bad = phon_engine.check_orthography(tokens_bad)
    assert res_bad["is_valid"] is False
    assert any("Homophone Confusion" in w for w in res_bad["warnings"])

# Test 11: Prepositional Case Government
def test_prepositional_case_government():
    import json
    with open("Polish_engine/brain/rules/preposition_case_matrix.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    gov_map = {item["preposition"]: item["case"] for item in data["preposition_government"]}
    assert gov_map["do"] == "genitive"
    assert gov_map["dzięki"] == "dative"
    assert gov_map["przez"] == "accusative"
    assert gov_map["z"] == "instrumental"
    assert gov_map["o"] == "locative"

# Test 12: Sub-AIs Direct AMSV Execution and Memory Map
def test_sub_ais_direct_amsv_execution(orchestrator):
    text = "Czy Pan wie, że nie mam czasu?"
    res = orchestrator.process(text)

    amsv = res["amsv_state"]
    assert amsv["magic"] == "0x504f4c53"  # "POLS"
    assert amsv["engine_id"] == 9
    assert amsv["token_count"] >= 7
    assert amsv["genitive_neg_flag"] is True

    # Verify that all 4 Sub-AIs executed and set their execution bits
    sub_ais = amsv["sub_ais_executed"]
    assert sub_ais["syntax"] is True
    assert sub_ais["phonology"] is True
    assert sub_ais["pragmatic"] is True
    assert sub_ais["editorial"] is True

    # Latency must be recorded
    assert res["latency_ns"] >= 0

# Test 13: Task Pipelines (Grammar Checker, Email, Composition)
def test_task_pipelines_grammar_email_composition(orchestrator):
    # 1. Grammar Checker on correct sentence
    check_ok = orchestrator.check_grammar("Jan nie ma czasu.")
    assert check_ok["is_valid"] is True
    assert check_ok["overall_score"] >= 90

    # 2. Grammar Checker catching Genitive of Negation violation (*Jan nie ma czas)
    check_bad = orchestrator.check_grammar("Jan nie ma czas.")
    assert check_bad["is_valid"] is False
    assert any("Genitive of Negation Violation" in err for err in check_bad["all_errors"])

    # 3. Email Pipeline
    email_res = orchestrator.generate_email("Kowalski", "male", "nowy projekt", register="formal")
    assert email_res["status"] == "success"
    assert "Szanowny Panie Kowalski," in email_res["email"]["salutation"]
    assert "Z poważaniem," in email_res["email"]["valediction"]

    # 4. Composition Pipeline
    contrast = orchestrator.compose_aspectual_contrast("Jan", "czytać", "książka")
    assert "książkę" in contrast["imperfective_affirmative"]
    assert "książki" in contrast["genitive_of_negation"]


# Test 14: Polish Prefix Semantic Engine — Frames, Aspect-Tense, and Misuse Detection (Tier 8)
def test_prefix_semantic_engine():
    engine = PolishPrefixSemanticEngine()

    # 14a: Semantic frame lookup for na- (accumulation/saturation)
    frame = engine.get_semantic_frame("napisać")
    assert frame is not None, "napisać must have a semantic frame"
    assert frame["prefix"] == "na"
    assert frame["frame_name"] == "ACCUMULATION_OR_SATURATION"
    assert "write" in frame["meaning"].lower()

    # 14b: Semantic frame for od- (reversal/response) — odpisać = write back
    frame_od = engine.get_semantic_frame("odpisać")
    assert frame_od is not None
    assert frame_od["prefix"] == "od"
    assert frame_od["frame_name"] == "REVERSAL_OR_RETURN"

    # 14c: Aspect-tense violation — perfective future form with present-continuity adverb
    res_violation = engine.analyze("Napiszę teraz ten raport.")
    assert len(res_violation["aspect_tense_violations"]) > 0, (
        "Should detect: 'Napiszę' is perfective future, cannot express present continuity with 'teraz'"
    )
    assert "perfective future" in res_violation["aspect_tense_violations"][0].lower()

    # 14d: Clean sentence — no violations
    res_clean = engine.analyze("Jan czyta teraz ten raport.")
    assert res_clean["prefix_semantics_ok"] is True

    # 14e: prze- frame explanation
    prze = engine.explain_prefix("prze")
    assert prze is not None
    assert prze["spatial_frame"] == "THROUGH_OR_ACROSS"
    assert len(prze["prototypical_verbs"]) > 0


# Test 15: Open-Vocabulary Morpheme Generator — Loanword Classification (Tier 4)
def test_open_vocab_morpheme_generator():
    oc = PolishOpenVocabClassifier()
    gen = PolishMorphemeGenerator()

    # 15a: streamowac (ASCII approx of loanword verb) → classified as VERB
    r1 = oc.classify("streamowac")
    assert r1["classification"] == "VERB"
    assert r1["aspect"] == "imperfective"
    assert r1.get("is_loanword") is True

    # 15b: Present tense loanword form → inferred infinitive available
    r2 = oc.classify("streamuje")
    assert r2["classification"] == "VERB"
    inferred = r2.get("inferred_infinitive") or r2.get("paradigm", {}).get("infinitive_impf", "")
    assert "stream" in inferred.lower(), f"Expected stream in infinitive, got: {inferred}"

    # 15c: marketing (-ing suffix) → masculine noun
    r3 = oc.classify("marketing")
    assert r3["classification"] == "NOUN"
    assert r3["gender"] == "masculine"

    # 15d: instalacja (-acja suffix) → feminine noun
    r4 = oc.classify("instalacja")
    assert r4["classification"] == "NOUN"
    assert r4["gender"] == "feminine"

    # 15e: is_verb / is_noun helpers
    assert oc.is_verb("streamowac") is True
    assert oc.is_noun("marketing") is True
    assert oc.is_verb("marketing") is False


# Test 16: AMSV Hierarchical Namespace — Tier 1 / Tier 2 Isolation (Tier 9)
def test_amsv_hierarchical_namespace():
    master_buf = bytearray(64)
    ahn = AMSVHierarchicalNamespace(master_buf)

    # 16a: Polish profile has correct cognitive difficulty vector
    polish_byte = COGNITIVE_PROFILES["Polish"]
    fields = decode_cognitive_difficulty_vector(polish_byte)
    assert fields["morphological_tier"] == 3, "Polish is fusional (tier 3)"
    assert fields["case_depth"] == 2,         "Polish has 5-7 cases (depth 2)"
    assert fields["tonal_load"] == 0,          "Polish has no tones"

    # 16b: Polish gets higher verbal reasoning bonus than English
    polish_bonus  = compute_verbal_reasoning_bonus(COGNITIVE_PROFILES["Polish"])
    english_bonus = compute_verbal_reasoning_bonus(COGNITIVE_PROFILES["English"])
    assert polish_bonus > english_bonus, (
        f"Polish bonus {polish_bonus} must be > English bonus {english_bonus}"
    )

    # 16c: publish_engine_result writes ONLY to 0x1C-0x1F (not to VCE or MAIO fields)
    master_buf[:] = bytearray(64)  # zero out
    ahn.publish_engine_result("Polish", 0.90, polish_byte, resonance_conflict=False)

    # VCE fields (0x00-0x0F) must be untouched
    assert master_buf[0x00:0x10] == bytearray(16), "VCE fields must not be modified by language engine"
    # RSSE/AEEE/MAIO fields (0x20-0x3F) must be untouched
    assert master_buf[0x20:0x40] == bytearray(32), "MAIO fields must not be modified by language engine"

    # Verbal Reasoning must be written correctly
    verbal_q16 = ahn.read_verbal_reasoning_q16()
    assert verbal_q16 > 0, "Verbal Reasoning Q16 must be written after publish"
    normalized = ahn.read_verbal_reasoning_normalized()
    assert 0.0 < normalized <= 1.0

    # 16d: resonance_conflict flag is correctly written
    ahn.publish_engine_result("Polish", 0.70, polish_byte, resonance_conflict=True)
    assert ahn.has_resonance_conflict() is True
    ahn.publish_engine_result("Polish", 0.70, polish_byte, resonance_conflict=False)
    assert ahn.has_resonance_conflict() is False


# Test 17: Stage 3 Network + Stage 4 Verifier — Full Four-Stage Pipeline (Tier 5)
def test_stage3_network_and_stage4_verifier():
    from Polish_engine.brain.stage3_network import Stage3Network
    from Polish_engine.brain.stage4_verifier import Stage4Verifier
    from Polish_engine.brain.sub_ais.syntax_sub_ai import PolishSyntaxSubAI
    from Polish_engine.brain.sub_ais.phonology_sub_ai import PolishPhonologySubAI
    from Polish_engine.brain.sub_ais.pragmatic_sub_ai import PolishPragmaticSubAI
    from Polish_engine.brain.sub_ais.editorial_sub_ai import PolishEditorialSubAI

    net = Stage3Network(
        syntax_sub_ai=PolishSyntaxSubAI(),
        editorial_sub_ai=PolishEditorialSubAI(),
        phonology_sub_ai=PolishPhonologySubAI(),
        pragmatic_sub_ai=PolishPragmaticSubAI(),
    )
    verifier = Stage4Verifier()

    buf = bytearray(64)
    text = "Jan czyta teraz tę książkę."

    # 17a: Stage 3 runs all 4 sub-AIs and returns hub result
    s3 = net.execute(text, buf)
    assert s3["stage"] == 3
    assert "group_a" in s3 and "group_b" in s3
    assert "hub" in s3
    assert isinstance(s3["hub"]["conflict_detected"], bool)
    assert "hub_composite_score" in s3["hub"]

    # 17b: Hub composite is in valid range
    composite = s3["hub"]["hub_composite_score"]
    assert 0 <= composite <= 100, f"Hub composite must be 0-100, got {composite}"

    # 17c: Stage 4 verifier runs and produces final verdict
    s4 = verifier.execute(s3, buf, text)
    assert s4["stage"] == 4
    assert "final_quality" in s4
    assert "verdict" in s4
    assert s4["final_quality"] >= 0
    assert isinstance(s4["recursive_feedback_fired"], bool)

    # 17d: AMSV Resonance Protocol — Editorial Sub-AI reads Syntax flags
    # Inject a genitive_neg_flag = 0 (negation violation signal from Syntax)
    buf2 = bytearray(64)
    buf2[0x10] = 0   # genitive_neg_flag = 0 (violation)
    buf2[0x12] = 90  # syntax_score high
    buf2[0x16] = 1   # pragmatic register = informal

    editorial = PolishEditorialSubAI()
    ed_res = editorial.execute("Nic nie.", buf2)

    # Editorial should detect resonance conflict (high syntax score + informal register)
    assert ed_res["resonance_protocol"] == "active"
    # Resonance flag should have been picked up
    assert "resonance_conflict" in ed_res
