"""
German Engine Test Suite
Validates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
the six-language matrix bridge, and Zero-Bridge AMSV physical synchronization.
"""

import pytest
from German_engine.german_engine_orchestrator import GermanEngineOrchestrator
from German_engine.six_language_matrix.german_matrix_bridge import (
    GermanMatrixBridge,
    GERMAN_AMSV_MAGIC,
    GERMAN_AMSV_SIZE
)
from German_engine.brain.skills.tokenization import tokenize_words, split_sentences, normalize_orthography
from German_engine.brain.skills.pos_tagging import tag_pos
from German_engine.brain.skills.parsing import parse_topological_fields
from German_engine.brain.skills.separable_verb_engine import detect_clause_separable_verb, split_infinitive
from German_engine.brain.skills.adjective_declension_engine import (
    inflect_adjective,
    validate_adjective_agreement
)
from German_engine.brain.skills.case_engine import (
    validate_prepositional_phrase,
    get_preposition_governed_case
)
from German_engine.brain.skills.verb_conjugator import conjugate_present, form_participle_ii
from German_engine.brain.skills.modal_particle_engine import analyze_modal_particles
from German_engine.brain.skills.pragmatics_engine import analyze_register

@pytest.fixture
def orchestrator():
    return GermanEngineOrchestrator()

def test_amsv_magic_and_size(orchestrator):
    """Test 1: Validate 64-byte AMSV length, magic header, and physical vector layout."""
    buf = orchestrator.amsv_buffer
    assert len(buf) == GERMAN_AMSV_SIZE == 64
    state = orchestrator.bridge.read_metrics()
    assert state["is_magic_valid"] is True
    assert state["magic_header"] == hex(GERMAN_AMSV_MAGIC)
    assert state["version"] == "0x10000"

def test_sub_ai_zero_bridge_sync(orchestrator):
    """Test 2: Verify zero-bridge physical memory writes across all 4 Sub-AIs."""
    buf = orchestrator.amsv_buffer
    text = "Der kluge Mann liest heute ein Buch."
    res = orchestrator.process_text(text)
    
    # Check Sub-AI active statuses in bytes 52..55
    assert buf[52] == 1 # Syntax Sub-AI
    assert buf[53] == 1 # Phonology Sub-AI
    assert buf[54] == 1 # Pragmatic Sub-AI
    assert buf[55] == 1 # Editorial Sub-AI
    
    amsv = res["amsv_state"]
    assert amsv["sub_ai_statuses"]["syntax"] is True
    assert amsv["sub_ai_statuses"]["phonology"] is True
    assert amsv["sub_ai_statuses"]["pragmatic"] is True
    assert amsv["sub_ai_statuses"]["editorial"] is True
    assert amsv["token_count"] > 0
    assert amsv["confidence"] > 0.8

def test_tokenization_and_compounds():
    """Test 3: Tokenization, sentence splitting, and compound word handling."""
    text = "Dr. Müller arbeitet heute. Er liest das Wirtschaftsministerium-Dokument."
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert "Dr. Müller arbeitet heute." in sentences[0]
    
    tokens = tokenize_words(sentences[0])
    assert "Dr." in tokens or "Dr" in tokens
    assert "Müller" in tokens
    assert "arbeitet" in tokens

def test_pos_tagging():
    """Test 4: Accurate UPOS / STTS tagging of German tokens."""
    tokens = ["Der", "fleißige", "Student", "liest", "ein", "Buch", "."]
    tags = tag_pos(tokens)
    assert tags[0]["upos"] == "DET"
    assert tags[1]["upos"] == "ADJ"
    assert tags[2]["upos"] == "NOUN"
    assert tags[3]["upos"] == "VERB"
    assert tags[4]["upos"] == "DET"
    assert tags[5]["upos"] == "NOUN"
    assert tags[6]["upos"] == "PUNCT"

def test_topological_fields_v2():
    """Test 5: Satzklammer parsing for V2 main clauses."""
    tokens = ["Heute", "liest", "der", "Student", "den", "Bericht", "."]
    tags = tag_pos(tokens)
    parsed = parse_topological_fields(tokens, tags)
    
    assert parsed["clause_type"] == "main_v2"
    assert parsed["verb_second"] is True
    fields = parsed["fields"]
    assert fields["vorfeld"] == ["Heute"]
    assert fields["linke_klammer"] == ["liest"]
    assert "Student" in fields["mittelfeld"]

def test_topological_fields_vend():
    """Test 6: Satzklammer parsing for subordinate V-End clauses."""
    tokens = ["weil", "er", "den", "Bericht", "liest"]
    tags = tag_pos(tokens)
    parsed = parse_topological_fields(tokens, tags)
    
    assert parsed["clause_type"] == "subordinate_v_end"
    assert parsed["verb_second"] is False
    assert parsed["fields"]["linke_klammer"] == ["weil"]
    assert parsed["fields"]["rechte_klammer"] == ["liest"]

def test_separable_verbs():
    """Test 7: Identification and re-attachment of separable verbs."""
    infinitive_split = split_infinitive("aufstehen")
    assert infinitive_split is not None
    assert infinitive_split[0] == "auf"
    assert infinitive_split[1] == "stehen"
    
    tokens = ["Er", "steht", "jeden", "Morgen", "früh", "auf", "."]
    sep_info = detect_clause_separable_verb(tokens)
    assert sep_info is not None
    assert sep_info["has_separable_verb"] is True
    assert sep_info["prefix"] == "auf"
    assert sep_info["verb_stem"] == "steht"

def test_adjective_declension_triad(orchestrator):
    """Test 8: Triad of German adjective declensions (Weak, Mixed, Strong)."""
    # 1. Weak: der gute Mann
    assert inflect_adjective("gut", "masculine", "nominative", "der") == "gute"
    # Weak masc accusative: den guten Mann
    assert inflect_adjective("gut", "masculine", "accusative", "den") == "guten"
    
    # 2. Mixed: ein guter Mann
    assert inflect_adjective("gut", "masculine", "nominative", "ein") == "guter"
    # Mixed masc accusative: einen guten Mann
    assert inflect_adjective("gut", "masculine", "accusative", "einen") == "guten"
    
    # 3. Strong: guter Wein
    assert inflect_adjective("gut", "masculine", "nominative", None) == "guter"
    
    # Test orchestrator noun phrase generator
    np_weak = orchestrator.inflect_noun_phrase("der", "gut", "Mann", "masculine", "accusative")
    assert np_weak == "den guten Mann"
    
    np_mixed = orchestrator.inflect_noun_phrase("ein", "schön", "Haus", "neuter", "nominative")
    assert np_mixed == "ein schönes Haus"

def test_case_government():
    """Test 9: Preposition case government and validation."""
    assert get_preposition_governed_case("für") == "accusative"
    assert get_preposition_governed_case("mit") == "dative"
    assert get_preposition_governed_case("während") == "genitive"
    assert get_preposition_governed_case("in") == "two_way"
    
    # Valid: für den Hund (Accusative)
    assert validate_prepositional_phrase("für", "den")["valid"] is True
    # Invalid: für dem Hund (Dative with für)
    assert validate_prepositional_phrase("für", "dem")["valid"] is False
    # Valid: mit dem Bus (Dative)
    assert validate_prepositional_phrase("mit", "dem")["valid"] is True

def test_verb_conjugation(orchestrator):
    """Test 10: Verb conjugation across regular, strong, modal, and auxiliary paradigms."""
    # Regular weak
    assert orchestrator.conjugate_verb("machen", "ich") == "mache"
    assert orchestrator.conjugate_verb("machen", "du") == "machst"
    assert orchestrator.conjugate_verb("machen", "er") == "macht"
    
    # Strong with vowel change: geben
    assert orchestrator.conjugate_verb("geben", "du") == "gibst"
    assert orchestrator.conjugate_verb("geben", "er") == "gibt"
    
    # Modal: können
    assert orchestrator.conjugate_verb("können", "ich") == "kann"
    assert orchestrator.conjugate_verb("können", "wir") == "können"
    
    # Auxiliary: sein
    assert orchestrator.conjugate_verb("sein", "ich") == "bin"
    assert orchestrator.conjugate_verb("sein", "wir") == "sind"
    
    # Participle II
    assert form_participle_ii("machen") == "gemacht"
    assert form_participle_ii("studieren") == "studiert"

def test_modal_particles_and_pragmatics():
    """Test 11: Abtönungspartikeln (modal particles) detection and pragmatic analysis."""
    tokens = ["Das", "ist", "ja", "eine", "Überraschung", "!"]
    res = analyze_modal_particles(tokens)
    assert res["particle_count"] == 1
    assert res["particles"][0]["particle"] == "ja"
    assert res["particles"][0]["category"] == "shared_knowledge"
    
    tokens2 = ["Komm", "doch", "mal", "her", "!"]
    res2 = analyze_modal_particles(tokens2)
    assert res2["particle_count"] == 2
    particles_found = {p["particle"] for p in res2["particles"]}
    assert "doch" in particles_found
    assert "mal" in particles_found

def test_duzen_siezen_register(orchestrator):
    """Test 12: Duzen vs Siezen classification and epistolary email auditing."""
    # Formal letter
    formal_text = "Sehr geehrte Damen und Herren,\nwie Sie wissen, möchten wir den Vertrag verlängern.\nMit freundlichen Grüßen\nDr. Schmidt"
    audit_formal = orchestrator.audit_email(formal_text)
    assert audit_formal["register"] == "siezen"
    assert audit_formal["is_register_consistent"] is True
    assert audit_formal["has_proper_closing"] is True
    
    # Informal letter
    informal_text = "Hallo Anna,\nkannst du mir bitte dein Buch leihen?\nLiebe Grüße\nMax"
    audit_informal = orchestrator.audit_email(informal_text)
    assert audit_informal["register"] == "duzen"
    assert audit_informal["is_register_consistent"] is True
    
    # Mixed clash: du and Sie in the same text
    mixed_text = "Hallo Peter, können Sie mir bitte dein Buch leihen?"
    res_mixed = analyze_register(mixed_text, tokenize_words(mixed_text))
    assert res_mixed["register"] == "mixed_clash"
    assert res_mixed["is_consistent"] is False

def test_full_orchestrator_pipeline(orchestrator):
    """Test 13: Full end-to-end pipeline with grammar checking, Swiss orthography, and AMSV verification."""
    clean_text = "Der fleißige Student liest heute das wichtige Buch."
    res = orchestrator.process_text(clean_text)
    assert res["is_valid"] is True
    assert res["token_count"] == 9
    
    # Grammar check
    check_res = orchestrator.check_grammar(clean_text)
    assert check_res["passed"] is True
    assert check_res["confidence_score"] >= 0.95
    
    # Swiss orthography adaptation (converting 'ß' to 'ss')
    standard_text = "Die weiße Straße ist groß."
    swiss_text = orchestrator.adapt_to_swiss(standard_text)
    assert "weisse" in swiss_text
    assert "Strasse" in swiss_text
    assert "gross" in swiss_text
    assert "ß" not in swiss_text
    
    # Verify AMSV state
    amsv = res["amsv_state"]
    assert amsv["is_magic_valid"] is True
    assert amsv["token_count"] == 9
    assert amsv["sentence_count"] == 1
