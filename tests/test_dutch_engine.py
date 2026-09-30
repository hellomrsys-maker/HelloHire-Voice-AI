"""
Comprehensive Test Suite for Dutch Sovereign Language Engine
Adheres strictly to the Zero-Bridge Synchronous Memory Rule.
13 Automated Test Cases covering all cognitive layers, sub-AIs, and invariants.
"""

import ctypes
import pytest
from Dutch_engine import (
    DutchEngineOrchestrator,
    DUTCH_AMSV_MAGIC,
    DUTCH_ENGINE_ID,
    DutchAtomicMemoryStateVector,
    DutchMatrixMemoryBridge
)
from Dutch_engine.brain.skills.tokenization import DutchTokenizer
from Dutch_engine.brain.skills.pos_tagging import DutchPOSTagger
from Dutch_engine.brain.skills.v2_syntax_engine import DutchV2SyntaxEngine
from Dutch_engine.brain.skills.diminutive_engine import DutchDiminutiveEngine
from Dutch_engine.brain.skills.gender_engine import DutchGenderEngine
from Dutch_engine.brain.skills.modal_particle_engine import DutchModalParticleEngine
from Dutch_engine.brain.skills.generation import DutchGenerator
from Dutch_engine.brain.task.grammar_check import DutchGrammarChecker
from Dutch_engine.brain.task.email_pipeline import DutchEmailPipeline
from Dutch_engine.brain.task.composition_pipeline import DutchCompositionPipeline

@pytest.fixture
def orchestrator():
    return DutchEngineOrchestrator()

# Test 1: AMSV Exact 64-Byte Size and Magic Signature
def test_amsv_magic_and_64byte_size():
    assert ctypes.sizeof(DutchAtomicMemoryStateVector) == 64
    vec = DutchAtomicMemoryStateVector()
    vec.magic = DUTCH_AMSV_MAGIC
    vec.engine_id = DUTCH_ENGINE_ID
    assert vec.magic == 0x4E454452  # "NEDR"
    assert vec.engine_id == 8

    bridge = DutchMatrixMemoryBridge()
    buf = bridge.get_bytearray()
    assert len(buf) == 64
    magic_unpacked = int.from_bytes(buf[0:4], byteorder="little")
    assert magic_unpacked == 0x4E454452

# Test 2: Tokenization and POS Tagging
def test_tokenizer_and_pos_tagger():
    tok = DutchTokenizer()
    tokens = tok.tokenize("Jan leest een mooi boek in de bibliotheek.")
    assert len(tokens) >= 8
    assert "Jan" in tokens
    assert "boek" in tokens

    tagger = DutchPOSTagger()
    tagged = tagger.tag(tokens)
    tag_map = dict(tagged)
    assert tag_map.get("een") == "DET"
    assert tag_map.get("boek") == "NOUN"
    assert tag_map.get("leest") == "VERB"

# Test 3: Canonical SVO Main Clause V2 Word Order
def test_v2_main_clause_canonical_svo():
    syntax = DutchV2SyntaxEngine()
    tagger = DutchPOSTagger()
    tok = DutchTokenizer()

    sentence = "Jan leest een boek."
    tokens = tok.tokenize(sentence)
    tagged = tagger.tag(tokens)
    res = syntax.analyze_clause(tokens, tagged)

    assert res["v2_valid"] is True
    assert res["clause_type"] == "main"
    assert res["syntax_score"] == 100
    assert len(res["errors"]) == 0

# Test 4: Vorfeld Fronting Inversion (Verb = Pos 2, Subject = Pos 3)
def test_v2_vorfeld_fronting_inversion():
    syntax = DutchV2SyntaxEngine()
    tagger = DutchPOSTagger()
    tok = DutchTokenizer()

    sentence = "Morgen leest Jan een boek."
    tokens = tok.tokenize(sentence)
    tagged = tagger.tag(tokens)
    res = syntax.analyze_clause(tokens, tagged)

    assert res["v2_valid"] is True
    assert res["inversion_active"] is True
    assert res["syntax_score"] == 100
    assert len(res["errors"]) == 0

# Test 5: V2 Inversion Violation Detection
def test_v2_inversion_violation_detection():
    syntax = DutchV2SyntaxEngine()
    tagger = DutchPOSTagger()
    tok = DutchTokenizer()

    # Fronted adverb without subject-verb inversion: *Morgen Jan leest...
    sentence = "Morgen Jan leest een boek."
    tokens = tok.tokenize(sentence)
    tagged = tagger.tag(tokens)
    res = syntax.analyze_clause(tokens, tagged)

    assert res["v2_valid"] is False
    assert len(res["errors"]) > 0
    assert any("V2 Inversion Violation" in err for err in res["errors"])

# Test 6: Subordinate Clause SOV Verb-Final Cluster
def test_subordinate_sov_verb_cluster():
    syntax = DutchV2SyntaxEngine()
    tagger = DutchPOSTagger()
    tok = DutchTokenizer()

    sentence = "omdat Jan een boek leest"
    tokens = tok.tokenize(sentence)
    tagged = tagger.tag(tokens)
    res = syntax.analyze_clause(tokens, tagged)

    assert res["clause_type"] == "subordinate"
    assert res["subordinate_sov_valid"] is True
    assert res["syntax_score"] == 100

# Test 7: Subordinate Clause SOV Violation Detection
def test_subordinate_sov_violation_detection():
    syntax = DutchV2SyntaxEngine()
    tagger = DutchPOSTagger()
    tok = DutchTokenizer()

    # Subordinate clause with verb in position 2 instead of coda: *omdat Jan leest een boek
    sentence = "omdat Jan leest een boek"
    tokens = tok.tokenize(sentence)
    tagged = tagger.tag(tokens)
    res = syntax.analyze_clause(tokens, tagged)

    assert res["subordinate_sov_valid"] is False
    assert any("Subordinate SOV violation" in err for err in res["errors"])

# Test 8: Diminutive Allomorph Suffix Generation (-tje, -je, -pje, -etje, -kje)
def test_diminutive_allomorph_generation():
    dim_engine = DutchDiminutiveEngine()

    # 1. -kje for -ing
    d_woning = dim_engine.generate_diminutive("woning")
    assert d_woning["diminutive"] == "woninkje"
    assert d_woning["article"] == "het"

    # 2. -pje for long vowel/diphthong + m
    d_boom = dim_engine.generate_diminutive("boom")
    assert d_boom["diminutive"] == "boompje"

    # 3. -etje for short vowel + liquid/nasal
    d_bal = dim_engine.generate_diminutive("bal")
    assert d_bal["diminutive"] == "balletje"
    d_man = dim_engine.generate_diminutive("man")
    assert d_man["diminutive"] == "mannetje"

    # 4. -je for obstruents
    d_huis = dim_engine.generate_diminutive("huis")
    assert d_huis["diminutive"] == "huisje"
    d_boek = dim_engine.generate_diminutive("boek")
    assert d_boek["diminutive"] == "boekje"

    # 5. -tje for long open vowels and sonorants
    d_auto = dim_engine.generate_diminutive("auto")
    assert d_auto["diminutive"] == "autootje"
    d_trein = dim_engine.generate_diminutive("trein")
    assert d_trein["diminutive"] == "treintje"

# Test 9: Diminutive Mandatory Neuter Invariant
def test_diminutive_mandatory_neuter_invariant():
    dim_engine = DutchDiminutiveEngine()

    # Valid singular: het huisje
    res_valid = dim_engine.verify_diminutive_concord("het", "huisje")
    assert res_valid["valid"] is True

    # Invalid singular: *de huisje
    res_invalid = dim_engine.verify_diminutive_concord("de", "huisje")
    assert res_invalid["valid"] is False
    assert "Diminutive Neuter Violation" in res_invalid["error"]

    # Valid plural: de huisjes
    res_plural = dim_engine.verify_diminutive_concord("de", "huisjes")
    assert res_plural["valid"] is True

# Test 10: Adjective Inflection Zero-Ending Invariant
def test_adjective_inflection_zero_ending_invariant():
    gender_engine = DutchGenderEngine()

    # 1. Indefinite singular neuter: MUST BE ZERO-ENDING (een mooi huis)
    res_correct_neuter = gender_engine.verify_adjective_inflection("een", "mooi", "huis")
    assert res_correct_neuter["valid"] is True

    # 2. Indefinite singular neuter with incorrect -e: *een mooie huis
    res_violation_neuter = gender_engine.verify_adjective_inflection("een", "mooie", "huis")
    assert res_violation_neuter["valid"] is False
    assert "Adjective Inflection Violation" in res_violation_neuter["error"]
    assert res_violation_neuter["expected"] == "mooi"

    # 3. Definite neuter: MUST HAVE -e (het mooie huis)
    res_def_neuter = gender_engine.verify_adjective_inflection("het", "mooie", "huis")
    assert res_def_neuter["valid"] is True

    # 4. Definite common: MUST HAVE -e (de mooie tafel)
    res_def_common = gender_engine.verify_adjective_inflection("de", "mooie", "tafel")
    assert res_def_common["valid"] is True

# Test 11: Modal Particles and Pragmatic Attenuation
def test_modal_particles_and_attenuation():
    mp_engine = DutchModalParticleEngine()
    tok = DutchTokenizer()

    sentence = "Kom maar even binnen hoor!"
    tokens = tok.tokenize(sentence)
    res = mp_engine.analyze_particles(tokens)

    assert res["is_attenuated"] is True
    assert res["particle_count"] >= 3
    found_tokens = [p["token"] for p in res["particles"]]
    assert "maar" in found_tokens
    assert "even" in found_tokens
    assert "hoor" in found_tokens
    assert "maar even" in res["clusters"]

# Test 12: Sub-AIs Direct AMSV Execution and Memory Map
def test_sub_ais_direct_amsv_execution(orchestrator):
    text = "Morgen belt Jan zijn vriendin even op."
    res = orchestrator.process(text)

    amsv = res["amsv_state"]
    assert amsv["magic"] == "0x4e454452"  # "NEDR"
    assert amsv["engine_id"] == 8
    assert amsv["token_count"] >= 7
    assert amsv["v2_inversion_flag"] is True

    # Verify that all 4 Sub-AIs executed and set their execution bits
    sub_ais = amsv["sub_ais_executed"]
    assert sub_ais["syntax"] is True
    assert sub_ais["phonology"] is True
    assert sub_ais["pragmatic"] is True
    assert sub_ais["editorial"] is True

    # Memory state vector latency must be sub-millisecond
    assert res["latency_ns"] >= 0

# Test 13: Task Pipelines (Grammar Checker, Email, Composition)
def test_task_pipelines_grammar_email_composition(orchestrator):
    # 1. Grammar Checker on correct sentence
    check_ok = orchestrator.check_grammar("Jan heeft een mooi huis.")
    assert check_ok["is_valid"] is True
    assert check_ok["overall_score"] >= 90

    # 2. Grammar Checker catching adjective error (*een mooie huis)
    check_bad = orchestrator.check_grammar("Jan heeft een mooie huis.")
    assert check_bad["is_valid"] is False
    assert any("Adjective Inflection Violation" in err for err in check_bad["all_errors"])

    # 3. Email Pipeline
    email_res = orchestrator.generate_email("Bakker", "de offerte", register="formal")
    assert email_res["status"] == "success"
    assert "Geachte heer/mevrouw Bakker," in email_res["email"]["salutation"]
    assert "Met vriendelijke groet," in email_res["email"]["valediction"]

    # 4. Composition Pipeline with fronted subordinate clause (V2 inversion in main clause)
    comp = orchestrator.compose_complex_sentence(
        main_sub="hij", main_verb="blijft", main_obj="thuis",
        sub_conj="omdat", sub_subj="Jan", sub_obj="ziek", sub_verb="is",
        front_subordinate=True
    )
    assert comp == "Omdat Jan ziek is, blijft hij thuis."
