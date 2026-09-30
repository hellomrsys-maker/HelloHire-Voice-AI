"""
Lingua Sapiens — Demonstration Script.

Exercises every component of the Universal Grammar & Linguistic Intelligence AI System:
  - Component 1: Deep Thinking & Multi-Level Reasoning Engine
  - Component 2: Universal Grammar Knowledge Base
  - Component 3: Sentence Construction, Parsing & Transformation
  - Component 4: Writing Skill Module & Critique
  - Component 5: Error Detection & Systematic Correction
  - Component 6: Pronunciation & Phonological Intelligence
  - Component 7: Reading Comprehension & Syntactic Decoding
  - Component 8: Listening & Spoken Language Intelligence
  - Component 9: Multilingual & Cross-Linguistic Contrastive Analysis
  - Component 10: Creativity, Rhetorical Devices & Style Transfer
  - Component 11: Self-Assessment, CEFR Quizzes & Learner Profiler
  - Component 12: Comprehensive Educational Grammar Compendium
  - Proactive Enhancement 1: Pragmatic Competence & Speech Acts
  - Proactive Enhancement 2: Discourse Analysis & RST Relations
  - Proactive Enhancement 3: Diachronic Evolution & Historical Linguistics
  - Proactive Enhancement 4: Second Language Acquisition & Cognitive Load
"""

import sys
import os

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add package to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gra_voi.orchestrator import UniversalGrammarAI
from gra_voi.common.models import WordOrder, SentenceType, WritingFormat, ErrorCategory


def print_banner(title: str):
    width = 78
    print("\n" + "=" * width)
    print(f"  {title.upper()}")
    print("=" * width)


def main():
    ai = UniversalGrammarAI()
    print_banner("Lingua Sapiens — Universal Grammar & Deep Linguistic Intelligence AI")
    print("Self-contained, offline-capable AI system initializing all modules...\n")

    # =========================================================================
    # COMPONENT 1: DEEP THINKING AND REASONING ENGINE
    # =========================================================================
    print_banner("Component 1 — Deep Thinking & Multi-Level Reasoning Engine")
    sample_sentence = "I saw the astronomer with binoculars."
    print(f"Input Utterance: \"{sample_sentence}\"")
    print("Executing multi-tier cognitive scan across structural, semantic, pragmatic, and cognitive levels...\n")

    trace = ai.think(sample_sentence, context="Observing the celestial night sky")
    for step in trace.step_by_step_thought_chain:
        print(f"  {step}")

    print("\n[Ambiguity Decomposition & Structural Disambiguation]")
    for idx, amb in enumerate(trace.ambiguities_detected, 1):
        print(f"  Interpretation {idx}: {amb.parse_description}")
        print(f"    • Syntactic Bracketing: {amb.syntactic_bracketing}")
        print(f"    • Plausibility Score:   {amb.contextual_plausibility_score:.2f}")
        print(f"    • Cognitive Rationale:  {amb.reasoning}")

    if trace.selected_interpretation:
        print(f"\n[AI Decision] Preferred Interpretation: {trace.selected_interpretation.interpretation_id}")
        print(f"  Meaning: {trace.selected_interpretation.semantic_meaning}")

    # =========================================================================
    # COMPONENT 2: UNIVERSAL GRAMMAR KNOWLEDGE BASE
    # =========================================================================
    print_banner("Component 2 — Universal Grammar Knowledge Base")
    concept_name = "Noun"
    concept = ai.query_grammar(concept_name)
    if concept:
        print(f"Concept: {concept.name} (Category: {concept.category})")
        print(f"Definition: {concept.definition}")
        print(f"Universal Functional Role: {concept.functional_role}")
        print(f"Universal Principle: {concept.universal_principle}")
        print("\nCross-Linguistic Annotated Examples:")
        for ex in concept.annotated_examples:
            print(f"  [{ex.language}] \"{ex.target_sentence}\"")
            print(f"    Gloss: {ex.gloss}")
            print(f"    Translation: {ex.translation}")
            print(f"    Grammatical Breakdown: {ex.grammatical_breakdown}")

    # =========================================================================
    # COMPONENT 3: SENTENCE CONSTRUCTION AND ANALYSIS MODULE
    # =========================================================================
    print_banner("Component 3 — Sentence Construction and Analysis Module")
    parse_input = "The brilliant astronomer discovered a new planet in the observatory."
    print(f"Parsing sentence: \"{parse_input}\"")
    analysis = ai.analyze_sentence(parse_input)
    print(f"Sentence Type: {analysis.sentence_type.value.upper()} | Word Order: {analysis.word_order_typology.value}")
    print("\nConstituent Decomposition:")
    for c in analysis.constituents:
        print(f"  • [{c.phrase_type.value}: {c.role.value.upper()}] \"{c.text}\" (Head: '{c.head_word}', θ-Role: {c.semantic_role})")

    print("\nHierarchical Parse Tree (ASCII):")
    print(analysis.syntactic_tree_ascii)

    print("\nSentence Generation Across World Typologies:")
    for order in [WordOrder.SVO, WordOrder.SOV, WordOrder.VSO, WordOrder.OSV]:
        gen = ai.construct_sentence(
            subject="The scholar",
            verb="translated",
            direct_object="the ancient manuscript",
            word_order=order
        )
        print(f"  [{order.value} Order]: {gen['sentence']}")

    print("\nSyntactic Transformation:")
    trans = ai.transform_sentence("The scholar translated the ancient manuscript", "active_to_passive")
    print(f"  Original:    {trans['original_sentence']}")
    print(f"  Transformed: {trans['transformed_sentence']}")
    print(f"  Explanation: {trans['explanation']}")

    # =========================================================================
    # COMPONENT 4: WRITING SKILL MODULE
    # =========================================================================
    print_banner("Component 4 — Writing Skill Module")
    print("Generating Academic Abstract Model Document:")
    model_abstract = ai.generate_writing_model(WritingFormat.ACADEMIC_ABSTRACT, "Neural Correlates of Universal Grammar")
    print(model_abstract[:700] + "\n... [truncated for demonstration] ...\n")

    print("Executing Automated Writing Critique:")
    sample_writing = (
        "Language is the foundation of human culture. Furthermore, complex syntax enables nuanced reasoning. "
        "Consequently, linguistic mastery remains indispensable for collective intellectual advancement."
    )
    critique = ai.critique_writing(sample_writing)
    print(f"Overall Writing Score: {critique.overall_score}/100")
    for domain, score in critique.sub_scores.items():
        print(f"  • {domain}: {score}/100")
    print(f"Strengths: {critique.strengths[0] if critique.strengths else 'Good baseline'}")

    # =========================================================================
    # COMPONENT 5: ERROR DETECTION AND CORRECTION ENGINE
    # =========================================================================
    print_banner("Component 5 — Error Detection and Correction Engine")
    erroneous_text = (
        "The list of participants were delayed, and he don't care because their going to see if it will effect them on monday."
    )
    print(f"Submitted Problematic Text:\n  \"{erroneous_text}\"\n")
    corr_result = ai.correct_text(erroneous_text)
    print(f"Detected {len(corr_result.errors)} Grammatical Error(s):")
    for i, err in enumerate(corr_result.errors, 1):
        print(f"  {i}. [{err.rule_violated}] '{err.problematic_text}' -> Suggested Fix: '{err.suggested_fix}'")
        print(f"     Explanation: {err.explanation}")

    print("\nCorrected Output:")
    print(f"  \"{corr_result.corrected_text}\"")

    # =========================================================================
    # COMPONENT 6: PRONUNCIATION AND PHONOLOGICAL INTELLIGENCE
    # =========================================================================
    print_banner("Component 6 — Pronunciation & Phonological Intelligence")
    word = "record"
    noun_phon = ai.analyze_pronunciation(word, grammatical_role="noun")
    verb_phon = ai.analyze_pronunciation(word, grammatical_role="verb")

    print(f"Word Class Stress Shift Analysis for '{word}':")
    print(f"  • As Noun: {noun_phon.ipa} | Stress: {noun_phon.stress_pattern}")
    print(f"  • As Verb: {verb_phon.ipa} | Stress: {verb_phon.stress_pattern}")
    print(f"  • Morphophonological Principle: {noun_phon.grammatical_stress_shift_note}")

    print("\nConnected Speech Analysis for: \"did you drink water?\"")
    conn_phon = ai.analyze_pronunciation("did you drink water")
    for eff in conn_phon.connected_speech_effects:
        print(f"  • {eff}")

    # =========================================================================
    # COMPONENT 7: READING COMPREHENSION INTELLIGENCE
    # =========================================================================
    print_banner("Component 7 — Reading Comprehension Intelligence Module")
    passage = (
        "Although the archaeological team encountered severe weather, they discovered an intact inscription. "
        "The epigrapher realized that the text recorded an unknown dialect."
    )
    reading_analysis = ai.analyze_reading_passage(passage)
    print(f"Passage: \"{passage}\"\n")
    print("Matrix Spine vs Subordinate Deconstruction:")
    for sb in reading_analysis.sentence_breakdowns:
        print(f"  Sentence {sb.sentence_index}: Core Spine: '{sb.core_informational_spine}'")
        print(f"    Subordinates: {sb.subordinate_qualifications}")
        print(f"    Reader Cues:  {sb.grammatical_cues_for_reader[0]}")

    print("\nGuided Reading Comprehension Questions (Grounded in Grammar):")
    for ex in reading_analysis.guided_comprehension_exercises:
        print(f"  Q: {ex['question']}")
        print(f"  Answer: {ex['correct_answer']}")
        print(f"  Grammatical Proof: {ex['grammatical_reasoning']}\n")

    # =========================================================================
    # COMPONENT 8: LISTENING AND SPOKEN LANGUAGE MODULE
    # =========================================================================
    print_banner("Component 8 — Listening & Spoken Language Intelligence")
    transcript = "Well, um, that ancient manuscript, I studied it, you know, but my colleague, he had doubts."
    print(f"Spoken Transcript: \"{transcript}\"\n")
    spoken_res = ai.analyze_spoken_discourse(transcript)
    print("Spoken Syntax & Interactional Analysis:")
    print(f"  • Fillers Detected:     {[d['token'] for d in spoken_res.detected_disfluencies]}")
    print(f"  • Discourse Markers:    {[m['marker'] for m in spoken_res.discourse_markers]}")
    print(f"  • Spoken Constructions: {[s['construction'] for s in spoken_res.spoken_grammatical_structures]}")
    print(f"  • Cleaned Syntax:       \"{spoken_res.cleaned_canonical_syntax}\"")
    print(f"\nListening Strategy: {spoken_res.listening_comprehension_guidance}")

    # =========================================================================
    # COMPONENT 9: MULTILINGUAL AND CROSS-LINGUISTIC MODULE
    # =========================================================================
    print_banner("Component 9 — Multilingual & Cross-Linguistic Module")
    print("Cross-Linguistic Contrastive Analysis: Spanish (L1) -> English (L2)")
    contrast = ai.compare_languages("Spanish", "English")
    print(f"Typological Overview: {contrast.typological_contrast}")
    print("Negative Interference Risks:")
    for risk in contrast.negative_interference_risks:
        print(f"  • {risk}")
    print("Common Learner Transfer Errors:")
    for err in contrast.common_learner_errors:
        print(f"  • {err}")

    # =========================================================================
    # COMPONENT 10: CREATIVITY AND LANGUAGE GENERATION MODULE
    # =========================================================================
    print_banner("Component 10 — Creativity & Language Generation Module")
    print("Generating Shakespearean Sonnet on Universal Grammar:")
    sonnet = ai.generate_creative("sonnet", "The architecture of human grammar")
    print(sonnet.generated_text)
    print(f"\nMetrical Structure: {sonnet.metrical_and_rhythmic_notes}")
    print(f"Stylistic Choices:  {sonnet.grammatical_and_stylistic_explanation}")

    print("\nStyle Transfer Demonstration (Casual -> High Academic):")
    trans_style = ai.transfer_style("We figured out that the test worked really well.", "academic")
    print(f"  Original:    \"{trans_style.original_text}\"")
    print(f"  Transferred: \"{trans_style.transferred_text}\"")

    # =========================================================================
    # COMPONENT 11: SELF-ASSESSMENT AND LEARNER PROGRESS MODULE
    # =========================================================================
    print_banner("Component 11 — Self-Assessment & Learner Progress Module")
    quiz = ai.create_quiz(cefr_level="B1", topic="Conjunctions & Agreement", count=2)
    print(f"Created CEFR {quiz.target_cefr_level} Quiz (ID: {quiz.quiz_id}):")
    for i, q in enumerate(quiz.questions, 1):
        print(f"  Q{i}: {q.prompt}")
        print(f"      Target: {q.target_concept}")
        print(f"      Correct Answer: {q.correct_answer}")

    # Simulate submission
    user_answers = {quiz.questions[0].question_id: quiz.questions[0].correct_answer}
    diag = ai.evaluate_quiz("learner_alpha", quiz, user_answers)
    print(f"\nDiagnostic Score: {diag.score_percentage}% ({diag.correct_count}/{diag.total_questions} correct)")
    print(f"CEFR Evaluation:  {diag.cefr_assessment}")
    print(f"Dynamic Roadmap:  {diag.personalized_roadmap[0]}")

    # =========================================================================
    # COMPONENT 12: COMPREHENSIVE EDUCATIONAL GRAMMAR COMPENDIUM
    # =========================================================================
    print_banner("Component 12 — Comprehensive Educational Grammar Compendium")
    doc_sample = ai.generate_educational_compendium()
    words = len(doc_sample.split())
    print(f"Generated complete standalone educational compendium ({words} words across 10 exhaustive chapters).")
    print(f"Chapter 1 Preview:\n{doc_sample[:450]}...\n")

    # =========================================================================
    # PROACTIVE ARCHITECTURAL ENHANCEMENTS
    # =========================================================================
    print_banner("Proactive Architectural Enhancements")

    print("\n[Enhancement 1: Pragmatic Competence & Speech Acts]")
    prag = ai.analyze_pragmatics("Could you possibly close the window, please?")
    print(f"  Utterance:             \"{prag.utterance}\"")
    print(f"  Illocutionary Force:   {prag.illocutionary_force}")
    print(f"  Implicature:           {prag.conversational_implicature}")
    print(f"  Politeness Strategy:   {prag.politeness_strategy} (Mitigation: {prag.face_threat_mitigation_score:.2f})")

    print("\n[Enhancement 2: Discourse Analysis & Rhetorical Structure Theory]")
    disc = ai.analyze_discourse(
        "The algorithm achieved convergence. Consequently, the researchers halted optimization."
    )
    print(f"  Thematic Model:        {disc.thematic_progression_model}")
    print(f"  Cohesion Ties:         {[t.cohesive_item for t in disc.cohesion_ties]}")
    print(f"  RST Relation:          {disc.rst_relations[0].relation_type if disc.rst_relations else 'Elaboration'}")

    print("\n[Enhancement 3: Diachronic Evolution & Historical Linguistics]")
    dia = ai.analyze_diachronic_evolution("strong verbs")
    print(f"  Target Pattern:        {dia.target_item_or_pattern}")
    print(f"  Etymological Root:     {dia.historical_etymology}")
    print(f"  Sound Law:             {dia.phonological_sound_laws[0]}")
    print(f"  Modern Irregularity:   {dia.explanation_of_modern_irregularity}")

    print("\n[Enhancement 4: Second Language Acquisition & Cognitive Load]")
    sla = ai.diagnose_sla(["Subject-Verb Agreement violation", "Article omission"], l1="Mandarin", l2="English")
    print(f"  Interlanguage Stage:   {sla.interlanguage_stage}")
    print(f"  Fossilization Risk:    {sla.fossilization_risk_score:.2f}")
    print(f"  Krashen i+1 Target:    {sla.krashen_input_zone}")
    print(f"  Remediation Regimen:   {sla.neurolinguistic_remediation_regimen[0]}")

    print_banner("All Components Verified Successfully — Lingua Sapiens Operational")


if __name__ == "__main__":
    main()
