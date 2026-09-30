"""
Lingua Sapiens — Interactive Terminal REPL & Command-Line Shell.

Provides an interactive CLI interface for querying and exercising all modules:
  1. Deep Thinking & Ambiguity Resolution
  2. Grammar Knowledge Base Query
  3. Sentence Analysis & Typology Synthesis
  4. Writing Generation & Critique
  5. Error Detection & Correction
  6. Pronunciation & Phonology
  7. Reading Comprehension Analysis
  8. Spoken Discourse Analysis
  9. Multilingual Contrastive Analysis
 10. Creative Generation & Style Transfer
 11. CEFR Diagnostic Quiz & Progress Tracking
 12. Export Full Educational Grammar Compendium
 13. Pragmatic, Discourse, Historical & SLA Analyses
"""

import sys
import os

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gra_voi.orchestrator import UniversalGrammarAI
from gra_voi.common.models import WordOrder, SentenceType, WritingFormat


def print_menu():
    print("\n" + "=" * 65)
    print("      LINGUA SAPIENS — INTERACTIVE COMMAND-LINE CONSOLE")
    print("=" * 65)
    print(" [1]  Deep Thinking & Ambiguity Resolver")
    print(" [2]  Universal Grammar Knowledge Base Lookup")
    print(" [3]  Sentence Syntactic Parser & ASCII Tree")
    print(" [4]  Sentence Synthesizer (SVO, SOV, VSO, VOS, OVS, OSV)")
    print(" [5]  Sentence Transformer (Active/Passive, Cleft, Inversion)")
    print(" [6]  Writing Document Generator & Critique")
    print(" [7]  Error Detector & Full Correction Review")
    print(" [8]  Pronunciation, IPA & Stress Shift Analysis")
    print(" [9]  Reading Comprehension Deconstruction")
    print(" [10] Spoken Discourse & Disfluency Analyzer")
    print(" [11] Multilingual Cross-Linguistic Contrastive Analysis")
    print(" [12] Creative Language Generator & Style Transfer")
    print(" [13] CEFR Diagnostic Quiz & Learner Roadmap")
    print(" [14] Export Full Educational Grammar Compendium to File")
    print(" [15] Proactive Enhancements (Pragmatics, Discourse, Diachronic, SLA)")
    print(" [0]  Exit")
    print("=" * 65)


def interactive_loop():
    ai = UniversalGrammarAI()
    print("\nInitializing Lingua Sapiens Universal AI Engine...")

    while True:
        print_menu()
        choice = input("Select an option (0-15): ").strip()

        if choice == "0":
            print("\nExiting Lingua Sapiens. Farewell!")
            break

        elif choice == "1":
            text = input("\nEnter sentence to analyze deeply: ").strip()
            if not text: text = "I saw the astronomer with binoculars."
            ctx = input("Enter optional pragmatic context: ").strip()
            trace = ai.think(text, context=ctx or None)
            print("\n--- DEEP THINKING THOUGHT CHAIN ---")
            for s in trace.step_by_step_thought_chain:
                print(f"• {s}")
            if trace.ambiguities_detected:
                print("\n--- AMBIGUITIES DETECTED ---")
                for a in trace.ambiguities_detected:
                    print(f"[{a.interpretation_id}] {a.parse_description} (Score: {a.contextual_plausibility_score:.2f})")
            print(f"\nPreferred Meaning: {trace.selected_interpretation.semantic_meaning if trace.selected_interpretation else 'Direct canonical meaning'}")

        elif choice == "2":
            concept = input("\nEnter grammar concept to lookup (e.g., Noun, Verb, Tense, Aspect, Case, Pronoun): ").strip()
            if not concept: concept = "Noun"
            c = ai.query_grammar(concept)
            if c:
                print(f"\n=== {c.name.upper()} ({c.category}) ===")
                print(f"Definition: {c.definition}")
                print(f"Role: {c.functional_role}")
                print(f"Universal Principle: {c.universal_principle}")
                print("\nAnnotated Multi-Language Examples:")
                for ex in c.annotated_examples:
                    print(f"  [{ex.language}] \"{ex.target_sentence}\" — {ex.translation}")
                    print(f"     Breakdown: {ex.grammatical_breakdown}")
            else:
                print(f"Concept '{concept}' not found. Available: {', '.join(ai.list_grammar_concepts()[:10])}...")

        elif choice == "3":
            text = input("\nEnter sentence to parse: ").strip()
            if not text: text = "The diligent scientist discovered an ancient star in the galaxy."
            res = ai.analyze_sentence(text)
            print(f"\nSentence Type: {res.sentence_type.value.upper()} | Word Order: {res.word_order_typology.value}")
            print("\nASCII Syntactic Parse Tree:")
            print(res.syntactic_tree_ascii)

        elif choice == "4":
            subj = input("Subject: ").strip() or "The scholar"
            verb = input("Verb: ").strip() or "wrote"
            obj = input("Direct Object: ").strip() or "the book"
            print("\nSynthesizing across world typologies:")
            for order in [WordOrder.SVO, WordOrder.SOV, WordOrder.VSO, WordOrder.VOS, WordOrder.OVS, WordOrder.OSV]:
                s = ai.construct_sentence(subject=subj, verb=verb, direct_object=obj, word_order=order)
                print(f"  [{order.value}]: {s['sentence']}")

        elif choice == "5":
            sent = input("\nEnter sentence to transform: ").strip() or "The cat chased the mouse."
            print("Transformations: active_to_passive, affirmative_to_negative, declarative_to_interrogative, canonical_to_cleft, canonical_to_inverted, nominalize")
            target = input("Target transformation: ").strip() or "active_to_passive"
            res = ai.transform_sentence(sent, target)
            print(f"\nTransformed: \"{res['transformed_sentence']}\"")
            print(f"Explanation: {res['explanation']}")

        elif choice == "6":
            print("\nFormats: essay_argumentative, business_email, academic_abstract, executive_report")
            fmt = input("Select format: ").strip() or "academic_abstract"
            topic = input("Topic: ").strip() or "Cognitive Linguistics"
            doc = ai.generate_writing_model(fmt, topic)
            print(f"\n{doc[:800]}...\n")

        elif choice == "7":
            text = input("\nEnter text with errors to scan: ").strip()
            if not text:
                text = "The list of participants were delayed, and he don't care because their going to see if it will effect them."
            corr = ai.correct_text(text)
            print(f"\nDetected {len(corr.errors)} Error(s):")
            for e in corr.errors:
                print(f"  • [{e.rule_violated}] '{e.problematic_text}' -> '{e.suggested_fix}': {e.explanation}")
            print(f"\nFully Corrected:\n  \"{corr.corrected_text}\"")

        elif choice == "8":
            w = input("\nEnter word for phonological stress analysis (e.g., record, present, object): ").strip() or "record"
            np = ai.analyze_pronunciation(w, grammatical_role="noun")
            vp = ai.analyze_pronunciation(w, grammatical_role="verb")
            print(f"\nNoun form: {np.ipa} | Stress: {np.stress_pattern}")
            print(f"Verb form: {vp.ipa} | Stress: {vp.stress_pattern}")
            if np.grammatical_stress_shift_note:
                print(f"Stress Shift Principle: {np.grammatical_stress_shift_note}")

        elif choice == "9":
            passage = input("\nEnter reading passage: ").strip()
            if not passage:
                passage = "Although early researchers faced skepticism, they published their breakthrough. The scientific community realized that the discovery was sound."
            res = ai.analyze_reading_passage(passage)
            print("\nReading Analysis Breakdown:")
            for b in res.sentence_breakdowns:
                print(f"  Sentence {b.sentence_index} Spine: '{b.core_informational_spine}' (Cues: {b.grammatical_cues_for_reader[0]})")
            print("\nGuided Comprehension Question:")
            q = res.guided_comprehension_exercises[0]
            print(f"  Q: {q['question']}\n  Answer: {q['correct_answer']}\n  Proof: {q['grammatical_reasoning']}")

        elif choice == "10":
            transcript = input("\nEnter spoken transcript: ").strip()
            if not transcript:
                transcript = "Well, um, that ancient manuscript, I studied it, you know, but my friend, he had doubts."
            s = ai.analyze_spoken_discourse(transcript)
            print(f"\nCleaned Syntax: \"{s.cleaned_canonical_syntax}\"")
            print(f"Fillers Detected: {[d['token'] for d in s.detected_disfluencies]}")
            print(f"Discourse Markers: {[m['marker'] for m in s.discourse_markers]}")
            print(f"Listening Strategy: {s.listening_comprehension_guidance}")

        elif choice == "11":
            l1 = input("Native Language (L1): ").strip() or "Spanish"
            l2 = input("Target Language (L2): ").strip() or "English"
            c = ai.compare_languages(l1, l2)
            print(f"\nContrast Summary: {c.typological_contrast}")
            print(f"Negative Transfer Risks:\n  • " + "\n  • ".join(c.negative_interference_risks))
            print(f"Pedagogical Blueprint:\n{c.pedagogical_remediation_strategy}")

        elif choice == "12":
            genre = input("Creative Genre (sonnet, haiku, fiction, dialogue, oration): ").strip() or "sonnet"
            prompt = input("Prompt / Theme: ").strip() or "The living power of universal language"
            cr = ai.generate_creative(genre, prompt)
            print(f"\n--- {genre.upper()} OUTPUT ---")
            print(cr.generated_text)
            print(f"\nStylistic Choices: {cr.grammatical_and_stylistic_explanation}")

        elif choice == "13":
            lvl = input("CEFR Level (A1, A2, B1, B2, C1, C2): ").strip() or "B1"
            quiz = ai.create_quiz(lvl)
            print(f"\nGenerated Quiz ({len(quiz.questions)} questions):")
            for i, q in enumerate(quiz.questions, 1):
                print(f"\nQuestion {i}: {q.prompt}")
                for opt in q.options:
                    print(f"  [ ] {opt}")
                print(f"  * Correct Answer: {q.correct_answer}")
                print(f"  * Rule Reference: {q.grammar_rule_reference}")

        elif choice == "14":
            default_path = os.path.join(os.path.dirname(__file__), "UNIVERSAL_GRAMMAR_COMPENDIUM.md")
            path = input(f"Enter file path to export compendium (Default: {default_path}): ").strip() or default_path
            msg = ai.export_compendium(path)
            print(f"\n{msg}")

        elif choice == "15":
            print("\n--- PROACTIVE ENHANCEMENTS DEMO ---")
            prag = ai.analyze_pragmatics("Could you please open the window?")
            print(f"1. Pragmatics: \"{prag.utterance}\" -> Force: {prag.illocutionary_force}, Politeness: {prag.politeness_strategy}")
            disc = ai.analyze_discourse("The theory was tested. Consequently, new protocols were established.")
            print(f"2. Discourse: Cohesion ties = {[t.cohesive_item for t in disc.cohesion_ties]}")
            dia = ai.analyze_diachronic_evolution("knight")
            print(f"3. Diachronic: {dia.target_item_or_pattern} -> {dia.explanation_of_modern_irregularity}")
            sla = ai.diagnose_sla(["Subject-Verb Agreement violation"], l1="Spanish", l2="English")
            print(f"4. SLA Modeling: Interlanguage stage = {sla.interlanguage_stage}, Fossilization risk = {sla.fossilization_risk_score}")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    interactive_loop()
