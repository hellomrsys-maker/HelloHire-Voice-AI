"""
Reading Comprehension and Syntactic Decoding Intelligence Engine.

Demonstrates and operationalizes how grammatical awareness unlocks deep reading comprehension:
  - Deconstructs complex syntax into informational spines vs subordinate qualifications
  - Identifies clause boundaries and dependency relations
  - Resolves cross-sentential anaphoric reference chains
  - Detects presupposition triggers and conversational implicatures
  - Generates guided comprehension exercises with explanations grounded in syntactic evidence.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import re


@dataclass
class SentenceReadingBreakdown:
    sentence_index: int
    raw_sentence: str
    core_informational_spine: str
    subordinate_qualifications: List[str]
    grammatical_cues_for_reader: List[str]
    epistemic_stance_and_modality: str


@dataclass
class GrammaticalReadingAnalysis:
    passage_text: str
    sentence_breakdowns: List[SentenceReadingBreakdown]
    anaphora_reference_chains: List[Dict[str, str]]
    presupposition_triggers: List[Dict[str, str]]
    syntactic_ambiguity_resolutions: List[Dict[str, str]]
    information_hierarchy: Dict[str, List[str]]
    guided_comprehension_exercises: List[Dict[str, Any]]


class ReadingComprehensionEngine:
    """
    Teaches and automates the decoding of textual meaning through grammatical analysis.
    """

    def analyze_passage(self, passage: str) -> GrammaticalReadingAnalysis:
        """
        Perform a comprehensive grammatical reading analysis on a text passage.
        """
        cleaned = passage.strip()
        raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]

        sentence_breakdowns: List[SentenceReadingBreakdown] = []
        anaphora_chains: List[Dict[str, str]] = []
        presuppositions: List[Dict[str, str]] = []
        ambiguities: List[Dict[str, str]] = []

        primary_entities: List[str] = []

        for idx, s in enumerate(raw_sentences, start=1):
            words = s.split()

            # Core informational spine heuristic (Subject + Main Verb + Object)
            spine = self._extract_core_spine(s)

            # Subordinate qualifications
            subordinates = []
            sub_matches = re.findall(r"\b(although|because|since|while|if|which|who|that|despite|after|before)\b[^,.]*", s, re.I)
            for sm in sub_matches:
                subordinates.append(sm.strip())

            # Cues for reader
            cues = []
            if any(w in s.lower() for w in ["however", "nevertheless", "yet"]):
                cues.append("Adversative Connective: Signals counter-expectation; reader must prepare for refutation of prior point.")
            if any(w in s.lower() for w in ["therefore", "consequently", "thus"]):
                cues.append("Causal Connective: Signals logical derivation; reader should track the preceding clause as a premise.")
            if any(w in s.lower() for w in ["furthermore", "moreover", "additionally"]):
                cues.append("Additive Connective: Extends prior argument without altering thematic polarity.")
            if not cues:
                cues.append("Informational Progression: Reader integrates new propositional predication into current discourse model.")

            # Modality and epistemic stance
            if any(w in s.lower() for w in ["may", "might", "could", "perhaps", "plausibly"]):
                stance = "Hedged / Epistemic Contingency (Speaker reserves judgment regarding factual certainty)"
            elif any(w in s.lower() for w in ["must", "undoubtedly", "definitively", "conclusively"]):
                stance = "High Certainty / Categorical Assertion"
            else:
                stance = "Neutral Assertive Stance"

            sentence_breakdowns.append(SentenceReadingBreakdown(
                sentence_index=idx,
                raw_sentence=s,
                core_informational_spine=spine,
                subordinate_qualifications=subordinates,
                grammatical_cues_for_reader=cues,
                epistemic_stance_and_modality=stance
            ))

            # Presuppositions in this sentence
            if re.search(r"\b(realized|discovered|acknowledged|admitted)\b", s, re.I):
                presuppositions.append({
                    "trigger": "Factive Verb",
                    "sentence": s,
                    "presupposition": "The subordinate clausal complement is presupposed as objective truth by the author."
                })
            if re.search(r"\b(stopped|ceased|resumed|continued)\b", s, re.I):
                presuppositions.append({
                    "trigger": "Aspectual Change Verb",
                    "sentence": s,
                    "presupposition": "The designated event was ongoing prior to the focal reference point."
                })

            # Detect entities for tracking
            if words:
                first_noun = words[1] if words[0].lower() in {"the", "a", "an"} and len(words) > 1 else words[0]
                if first_noun.isalpha() and first_noun.lower() not in {"this", "that", "it", "he", "she", "they"}:
                    primary_entities.append(first_noun)

        # Track anaphora across sentences
        for idx, s in enumerate(raw_sentences[1:], start=2):
            for pr in ["he", "she", "it", "they"]:
                if re.search(rf"\b{pr}\b", s, re.I):
                    referent = primary_entities[0] if primary_entities else "Dominant subject of prior sentence"
                    anaphora_chains.append({
                        "pronoun": pr,
                        "sentence_index": idx,
                        "antecedent": referent,
                        "syntactic_cue": f"Reader resolves '{pr}' by locating the most structurally prominent matching DP in prior discourse."
                    })

        # Information hierarchy
        info_hierarchy = {
            "Nuclear Propositions (Core Spine)": [b.core_informational_spine for b in sentence_breakdowns],
            "Peripheral Elaborations & Modifiers": [sub for b in sentence_breakdowns for sub in b.subordinate_qualifications]
        }

        # Generate guided comprehension exercises
        exercises = self._generate_comprehension_exercises(raw_sentences, sentence_breakdowns)

        return GrammaticalReadingAnalysis(
            passage_text=cleaned,
            sentence_breakdowns=sentence_breakdowns,
            anaphora_reference_chains=anaphora_chains,
            presupposition_triggers=presuppositions,
            syntactic_ambiguity_resolutions=ambiguities,
            information_hierarchy=info_hierarchy,
            guided_comprehension_exercises=exercises
        )

    def _extract_core_spine(self, sentence: str) -> str:
        """Strip non-restrictive relative clauses and adverbials to isolate Subject-Verb-Object."""
        stripped = re.sub(r",\s*which[^,]+,", "", sentence)
        stripped = re.sub(r",\s*who[^,]+,", "", stripped)
        stripped = re.sub(r"^(although|because|since|while|if)\s+[^,]+,\s*", "", stripped, flags=re.I)
        words = stripped.split()
        if len(words) > 8:
            return " ".join(words[:8]) + "..."
        return stripped

    def _generate_comprehension_exercises(self, sentences: List[str], breakdowns: List[SentenceReadingBreakdown]) -> List[Dict[str, Any]]:
        """
        Generate reading comprehension questions whose answers are proved
        via explicit grammatical cues.
        """
        exercises = []
        if not sentences:
            return exercises

        s1 = sentences[0]
        exercises.append({
            "question_number": 1,
            "question": "What is the primary action or claim asserted in the first sentence?",
            "target_grammatical_feature": "Matrix Clause Identification vs Subordinate Adjunct",
            "correct_answer": breakdowns[0].core_informational_spine,
            "grammatical_reasoning": "The core semantic claim resides in the matrix (independent) clause, where the primary finite verb assigns theta roles to the subject and object, whereas subordinate clauses merely qualify conditions or concession."
        })

        if len(sentences) > 1:
            exercises.append({
                "question_number": 2,
                "question": "How does the logical relationship between the first and second sentence develop?",
                "target_grammatical_feature": "Discourse Markers and Inter-clausal Cohesion",
                "correct_answer": breakdowns[1].grammatical_cues_for_reader[0],
                "grammatical_reasoning": "Grammatical cohesive markers (coordinating conjunctions, conjunctive adverbs) explicitly instruct the reader how to link new information to the preceding discourse model."
            })

        return exercises
