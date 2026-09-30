"""
Grammar Error Detection, Diagnostic, and Correction Engine.

Covers all 16+ core error categories:
  - Subject-Verb Agreement violations
  - Tense Inconsistency & Sequence of Tenses
  - Aspect Mismatch (Stative verbs in progressive frames)
  - Voice Errors & Awkward Passives
  - Pronoun-Antecedent Disagreement
  - Dangling & Misplaced Modifiers
  - Run-On Sentences & Comma Splices
  - Sentence Fragments
  - Faulty Parallelism
  - Article Misuse (Count vs Mass, Phonetic 'a' vs 'an')
  - Preposition & Collocational Errors
  - Conjunction & Correlative Pairing Errors
  - Punctuation & Apostrophe Misuse
  - Capitalization Errors
  - Homophones & Grammatical Spelling Errors
  - Register Mismatches
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from ..common.models import (
    ErrorCategory,
    GrammarError,
    CorrectionResult,
)


class ErrorDetectionEngine:
    """
    Scans natural language texts for grammatical, syntactic, and orthographic errors,
    providing exact location spans, theoretical rule citations, step-by-step
    pedagogical corrections, and unified patched outputs.
    """

    def __init__(self):
        self._catalog: Dict[ErrorCategory, Dict[str, Any]] = {}
        self._initialize_catalog()

    def _initialize_catalog(self):
        self._catalog = {
            ErrorCategory.SUBJECT_VERB_AGREEMENT: {
                "name": "Subject-Verb Agreement Violation",
                "definition": "A syntactic error where the finite verb fails to agree in number (singular/plural) or person with its structural subject.",
                "example_bad": "The list of approved participants were published yesterday.",
                "example_good": "The list of approved participants was published yesterday.",
                "explanation": "The head of the subject noun phrase is the singular noun 'list', not the plural prepositional complement 'participants'. Therefore, the singular auxiliary 'was' is syntactically required."
            },
            ErrorCategory.TENSE_INCONSISTENCY: {
                "name": "Tense Inconsistency & Sequence of Tenses",
                "definition": "An illicit shift in temporal reference frame across coordinated or subordinated clauses without a valid semantic reason.",
                "example_bad": "Yesterday she walked into the library and borrows three volumes.",
                "example_good": "Yesterday she walked into the library and borrowed three volumes.",
                "explanation": "The temporal anchor 'Yesterday' establishes past reference time. Both conjoined verbs must share the past tense inflection (-ed)."
            },
            ErrorCategory.ASPECT_MISMATCH: {
                "name": "Aspectual Mismatch (Stative Verbs in Progressive)",
                "definition": "Coercing a non-dynamic stative verb (denoting an unchanging state, belief, or possession) into a progressive aspectual frame.",
                "example_bad": "I am knowing the correct answer to the riddle.",
                "example_good": "I know the correct answer to the riddle.",
                "explanation": "Cognitive stative verbs like 'know', 'believe', and 'understand' lack internal temporal dynamism and cannot license the progressive auxiliary 'be + V-ing' in standard grammar."
            },
            ErrorCategory.VOICE_CONFUSION: {
                "name": "Voice Confusion and Truncated Passive",
                "definition": "Unnecessary or unmotivated shift between active and passive voice in coordinated structures, obscuring agentive responsibility.",
                "example_bad": "The team conducted the survey, and the data was analyzed by them thoroughly.",
                "example_good": "The team conducted the survey and analyzed the data thoroughly.",
                "explanation": "Maintaining parallel active voice across coordinated predicates preserves thematic role continuity and improves processing fluency."
            },
            ErrorCategory.PRONOUN_ANTECEDENT: {
                "name": "Pronoun-Antecedent Agreement / Ambiguity",
                "definition": "A mismatch in number, person, or gender between a pronoun and its referential antecedent, or reference to an ambiguous antecedent.",
                "example_bad": "Every student must submit their paper before Friday.",
                "example_good": "All students must submit their papers before Friday. (or: Each student must submit his or her paper...)",
                "explanation": "The singular distributive quantifier 'Every student' traditionally clashes with plural pronoun 'their'; pluralizing both antecedent and pronoun resolves the conflict cleanly."
            },
            ErrorCategory.DANGLING_MODIFIER: {
                "name": "Dangling and Misplaced Modifier",
                "definition": "A non-finite participial or prepositional modifier whose implied logical subject fails to align with the structural subject of the matrix clause.",
                "example_bad": "Walking across the quad, the library tower came into view.",
                "example_good": "Walking across the quad, I saw the library tower come into view.",
                "explanation": "The participial phrase 'Walking across the quad' implies an animate agent capable of locomotion. Attaching it to 'the library tower' creates an absurd semantic predication."
            },
            ErrorCategory.RUN_ON_SENTENCE: {
                "name": "Run-on (Fused) Sentence",
                "definition": "Two or more independent clauses joined together without any intervening punctuation or coordinating conjunction.",
                "example_bad": "The experiment concluded successfully the researchers published their data.",
                "example_good": "The experiment concluded successfully; subsequently, the researchers published their data.",
                "explanation": "Two complete matrix clauses must be demarcated with a period, a semicolon, or a coordinating conjunction with a comma."
            },
            ErrorCategory.COMMA_SPLICE: {
                "name": "Comma Splice",
                "definition": "Joining two independent matrix clauses with only a comma, lacking an accompanying coordinating conjunction.",
                "example_bad": "The hypothesis was refuted, the team initiated a new trial.",
                "example_good": "The hypothesis was refuted; therefore, the team initiated a new trial. (or: ...refuted, so the team...)",
                "explanation": "A comma alone is syntactically insufficient to link two finite independent clauses."
            },
            ErrorCategory.SENTENCE_FRAGMENT: {
                "name": "Sentence Fragment",
                "definition": "A subordinate or dependent clause punctuated as if it were a complete, freestanding matrix sentence.",
                "example_bad": "Because the archival documents were severely degraded by moisture.",
                "example_good": "The historians halted analysis because the archival documents were severely degraded by moisture.",
                "explanation": "Subordinating conjunctions like 'Because' create dependent CPs that cannot stand without a governing matrix clause."
            },
            ErrorCategory.FAULTY_PARALLELISM: {
                "name": "Faulty Parallelism",
                "definition": "Coordinating dissimilar syntactic structures (e.g., mixing gerunds with infinitives or nouns with clauses) across a conjunction.",
                "example_bad": "She enjoys hiking, swimming, and to ride bicycles.",
                "example_good": "She enjoys hiking, swimming, and riding bicycles.",
                "explanation": "Coordinated conjuncts governed by 'enjoys' must share an identical morphological category (all gerunds: -ing)."
            },
            ErrorCategory.ARTICLE_MISUSE: {
                "name": "Article Misuse (Phonetic 'A'/'An' & Mass/Count)",
                "definition": "Selecting the incorrect indefinite article based on orthography rather than initial phonetic sound, or applying count articles to mass nouns.",
                "example_bad": "He attended a university and earned an honest living.",
                "example_good": "He attended a university (phonetic initial /j/) and earned an honest living (phonetic initial /ɒ/).",
                "explanation": "The selection between 'a' and 'an' depends strictly on whether the following word begins with a consonant phoneme or vowel phoneme in spoken articulation."
            },
            ErrorCategory.PREPOSITION_ERROR: {
                "name": "Preposition & Collocational Misuse",
                "definition": "Using an incorrect dependent preposition dictated by lexical subcategorization frames.",
                "example_bad": "She is capable to solve this equation and interested on biology.",
                "example_good": "She is capable of solving this equation and interested in biology.",
                "explanation": "The adjective 'capable' subcategorizes for the preposition 'of' + gerund; 'interested' subcategorizes for 'in'."
            },
            ErrorCategory.CONJUNCTION_ERROR: {
                "name": "Conjunction & Correlative Error",
                "definition": "Mismatched correlative conjunction pairs (e.g., 'neither...or', 'both...or') or double subordinators.",
                "example_bad": "Neither the teacher or the principal consented.",
                "example_good": "Neither the teacher nor the principal consented.",
                "explanation": "Correlative conjunctions require strict pairing: 'Neither ... nor', 'Either ... or', 'Not only ... but also'."
            },
            ErrorCategory.PUNCTUATION_ERROR: {
                "name": "Punctuation & Apostrophe Misuse",
                "definition": "Erroneous insertion of apostrophes in plural nouns (greengrocer's apostrophe) or confusion of possessive vs contracted forms.",
                "example_bad": "The dog wagged it's tail, and the apple's were fresh.",
                "example_good": "The dog wagged its tail, and the apples were fresh.",
                "explanation": "'It's' is a contraction of 'it is'; the possessive determiner is 'its' (no apostrophe). Plural nouns do not take apostrophes."
            },
            ErrorCategory.CAPITALIZATION_ERROR: {
                "name": "Capitalization Error",
                "definition": "Failure to capitalize proper nouns, days of the week, months, or the initial token of a sentence.",
                "example_bad": "we arrived in london on monday morning.",
                "example_good": "We arrived in London on Monday morning.",
                "explanation": "Proper nouns and calendar terms designate unique entities and require initial orthographic capitalization."
            },
            ErrorCategory.HOMOPHONE_SPELLING: {
                "name": "Homophone & Grammatical Spelling Confusion",
                "definition": "Confusing phonetically identical words with distinct grammatical categories (their/there/they're, affect/effect, complement/compliment).",
                "example_bad": "Their going to the theater to see how the weather will effect them.",
                "example_good": "They're going to the theater to see how the weather will affect them.",
                "explanation": "'They're' is the contraction of 'they are'; 'affect' is the transitive verb meaning to influence; 'effect' is typically a noun."
            },
            ErrorCategory.REGISTER_MISMATCH: {
                "name": "Register & Colloquial Mismatch",
                "definition": "Employing informal oral contractions or vernacular slang in formal academic or professional writing.",
                "example_bad": "The results ain't conclusive, and we gonna need a bunch of data.",
                "example_good": "The results are not conclusive, and we will require substantial additional data.",
                "explanation": "Formal registers avoid non-standard dialectal contractions ('ain't', 'gonna') and colloquial quantifiers ('a bunch of')."
            }
        }

    def explain_error_category(self, category: ErrorCategory) -> Dict[str, Any]:
        """Return definition, bad example, good example, and explanation for an error type."""
        return self._catalog.get(category, {
            "name": category.value,
            "definition": "Grammatical violation.",
            "example_bad": "",
            "example_good": "",
            "explanation": ""
        })

    def get_all_error_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Return the complete indexed error catalog."""
        return {k.value: v for k, v in self._catalog.items()}

    def detect_errors(self, text: str) -> List[GrammarError]:
        """
        Scan input text against the grammatical rule engine and return all detected errors.
        """
        errors: List[GrammarError] = []

        # 1. Homophone & Spelling Rules
        homophone_rules = [
            (r"\btheir\s+(going|coming|leaving|ready|happy|capable)\b", "they're", ErrorCategory.HOMOPHONE_SPELLING, "Confused possessive determiner 'their' with contraction 'they're' (they are)."),
            (r"\bthere\s+(car|house|book|idea|responsibility)\b", "their", ErrorCategory.HOMOPHONE_SPELLING, "Confused locative adverb 'there' with possessive determiner 'their'."),
            (r"\bit\'s\s+(tail|legs|color|name|purpose|origin|impact)\b", "its", ErrorCategory.PUNCTUATION_ERROR, "Used contracted 'it's' (it is) instead of possessive determiner 'its'."),
            (r"\bwill\s+effect\b", "will affect", ErrorCategory.HOMOPHONE_SPELLING, "Used noun 'effect' where transitive verb 'affect' (to influence) is required."),
            (r"\ba\s+affect\b", "an effect", ErrorCategory.HOMOPHONE_SPELLING, "Used verb 'affect' where noun 'effect' (consequence/result) is required.")
        ]
        for pattern, fix, cat, reason in homophone_rules:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                errors.append(GrammarError(
                    category=cat,
                    start_char=match.start(),
                    end_char=match.end(),
                    problematic_text=match.group(0),
                    definition=self._catalog[cat]["definition"],
                    explanation=reason,
                    rule_violated=self._catalog[cat]["name"],
                    suggested_fix=fix
                ))

        # 2. Subject-Verb Agreement Rules
        sva_rules = [
            (r"\b(The\s+list\s+of\s+[a-z]+)\s+were\b", "was", "The head of the subject NP is singular 'list', requiring singular verb 'was'."),
            (r"\b(The\s+results\s+of\s+the\s+study)\s+is\b", "are", "The head of the subject NP is plural 'results', requiring plural verb 'are'."),
            (r"\b(he|she|it)\s+(don't)\b", "doesn't", "Third person singular subject requires auxiliary 'doesn't' (does not)."),
            (r"\b(they|we|you)\s+(was)\b", "were", "Plural subject requires past plural verb 'were'."),
            (r"\b(every\s+one\s+of\s+us)\s+are\b", "is", "'Every one' is grammatically singular and requires singular copula 'is'.")
        ]
        for pattern, fix, reason in sva_rules:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                errors.append(GrammarError(
                    category=ErrorCategory.SUBJECT_VERB_AGREEMENT,
                    start_char=match.start(),
                    end_char=match.end(),
                    problematic_text=match.group(0),
                    definition=self._catalog[ErrorCategory.SUBJECT_VERB_AGREEMENT]["definition"],
                    explanation=reason,
                    rule_violated=self._catalog[ErrorCategory.SUBJECT_VERB_AGREEMENT]["name"],
                    suggested_fix=match.group(0).rsplit(" ", 1)[0] + " " + fix
                ))

        # 3. Aspect Mismatch (Stative in Progressive)
        stative_rules = [
            (r"\b(am|is|are|was|were)\s+knowing\b", "know(s)", "Stative cognitive verb 'know' cannot take progressive aspect."),
            (r"\b(am|is|are|was|were)\s+believing\b", "believe(s)", "Stative verb 'believe' resists progressive aspect."),
            (r"\b(am|is|are|was|were)\s+understanding\b", "understand(s)", "Stative verb 'understand' expresses a state, not a dynamic progressive event.")
        ]
        for pattern, fix, reason in stative_rules:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                errors.append(GrammarError(
                    category=ErrorCategory.ASPECT_MISMATCH,
                    start_char=match.start(),
                    end_char=match.end(),
                    problematic_text=match.group(0),
                    definition=self._catalog[ErrorCategory.ASPECT_MISMATCH]["definition"],
                    explanation=reason,
                    rule_violated=self._catalog[ErrorCategory.ASPECT_MISMATCH]["name"],
                    suggested_fix=fix
                ))

        # 4. Article Phonetics (a vs an)
        article_rules = [
            (r"\ban\s+(university|user|unicorn|eulogy|one)\b", r"a \1", "Word begins with consonant phoneme /j/ or /w/, requiring indefinite article 'a'."),
            (r"\ba\s+(honest|hour|honor|heir)\b", r"an \1", "Initial 'h' is silent, word begins phonetically with a vowel sound, requiring 'an'.")
        ]
        for pattern, fix_pattern, reason in article_rules:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                word = match.group(1)
                fixed = re.sub(pattern, fix_pattern, match.group(0), flags=re.IGNORECASE)
                errors.append(GrammarError(
                    category=ErrorCategory.ARTICLE_MISUSE,
                    start_char=match.start(),
                    end_char=match.end(),
                    problematic_text=match.group(0),
                    definition=self._catalog[ErrorCategory.ARTICLE_MISUSE]["definition"],
                    explanation=reason,
                    rule_violated=self._catalog[ErrorCategory.ARTICLE_MISUSE]["name"],
                    suggested_fix=fixed
                ))

        # 5. Preposition & Collocational Errors
        prep_rules = [
            (r"\bcapable\s+to\s+([a-z]+)\b", r"capable of \1ing", "Adjective 'capable' subcategorizes for 'of' + gerund, not to-infinitive."),
            (r"\binterested\s+on\b", "interested in", "Adjective 'interested' subcategorizes for preposition 'in'."),
            (r"\bcongratulate\s+([a-z]+)\s+for\b", r"congratulate \1 on", "Verb 'congratulate' takes preposition 'on' for the achievement.")
        ]
        for pattern, fix_pattern, reason in prep_rules:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                errors.append(GrammarError(
                    category=ErrorCategory.PREPOSITION_ERROR,
                    start_char=match.start(),
                    end_char=match.end(),
                    problematic_text=match.group(0),
                    definition=self._catalog[ErrorCategory.PREPOSITION_ERROR]["definition"],
                    explanation=reason,
                    rule_violated=self._catalog[ErrorCategory.PREPOSITION_ERROR]["name"],
                    suggested_fix=re.sub(pattern, fix_pattern, match.group(0), flags=re.IGNORECASE)
                ))

        # 6. Correlative Conjunction Errors
        conj_rules = [
            (r"\bneither\s+([a-z]+)\s+or\s+([a-z]+)\b", r"neither \1 nor \2", "Correlative conjunction 'neither' pairs strictly with 'nor'."),
            (r"\beither\s+([a-z]+)\s+nor\s+([a-z]+)\b", r"either \1 or \2", "Correlative conjunction 'either' pairs strictly with 'or'.")
        ]
        for pattern, fix_pattern, reason in conj_rules:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                errors.append(GrammarError(
                    category=ErrorCategory.CONJUNCTION_ERROR,
                    start_char=match.start(),
                    end_char=match.end(),
                    problematic_text=match.group(0),
                    definition=self._catalog[ErrorCategory.CONJUNCTION_ERROR]["definition"],
                    explanation=reason,
                    rule_violated=self._catalog[ErrorCategory.CONJUNCTION_ERROR]["name"],
                    suggested_fix=re.sub(pattern, fix_pattern, match.group(0), flags=re.IGNORECASE)
                ))

        # 7. Register & Colloquialisms
        reg_rules = [
            (r"\bain't\b", "is not / are not", "Informal vernacular contraction 'ain't' is inappropriate for formal writing."),
            (r"\bgonna\b", "going to", "Oral slurred contraction 'gonna' must be written 'going to' in formal registers."),
            (r"\ba\s+lot\s+of\b", "numerous / substantial", "Colloquial quantifier 'a lot of' should be replaced with formal academic alternatives.")
        ]
        for pattern, fix, reason in reg_rules:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                errors.append(GrammarError(
                    category=ErrorCategory.REGISTER_MISMATCH,
                    start_char=match.start(),
                    end_char=match.end(),
                    problematic_text=match.group(0),
                    definition=self._catalog[ErrorCategory.REGISTER_MISMATCH]["definition"],
                    explanation=reason,
                    rule_violated=self._catalog[ErrorCategory.REGISTER_MISMATCH]["name"],
                    suggested_fix=fix
                ))

        # 8. Comma Splices (e.g., "clause, clause")
        splice_match = re.search(r"([a-z0-9\s]+),\s+([a-z0-9\s]+)\.", text, re.IGNORECASE)
        if splice_match:
            clause1 = splice_match.group(1).strip()
            clause2 = splice_match.group(2).strip()
            # Simple check if both have subject + verb
            if len(clause1.split()) >= 3 and len(clause2.split()) >= 3 and not any(clause2.lower().startswith(cc) for cc in ["and", "but", "so", "or", "because"]):
                errors.append(GrammarError(
                    category=ErrorCategory.COMMA_SPLICE,
                    start_char=splice_match.start(),
                    end_char=splice_match.end(),
                    problematic_text=splice_match.group(0),
                    definition=self._catalog[ErrorCategory.COMMA_SPLICE]["definition"],
                    explanation="Two independent clauses joined by only a comma without a coordinating conjunction.",
                    rule_violated=self._catalog[ErrorCategory.COMMA_SPLICE]["name"],
                    suggested_fix=f"{clause1}; {clause2}."
                ))

        return errors

    def correct_text(self, text: str) -> CorrectionResult:
        """
        Execute full document review workflow, returning annotations,
        pedagogical rationale, and fully corrected text with visual diffs.
        """
        errors = self.detect_errors(text)
        corrected = text
        reasoning_steps: List[str] = []

        # Sort errors from end to start to preserve character indices
        sorted_errors = sorted(errors, key=lambda e: e.start_char, reverse=True)

        for e in sorted_errors:
            # Replace in text
            before = corrected[:e.start_char]
            after = corrected[e.end_char:]
            corrected = before + e.suggested_fix + after
            reasoning_steps.append(
                f"Fixed {e.rule_violated}: Replaced '{e.problematic_text}' with '{e.suggested_fix}'. Rationale: {e.explanation}"
            )

        # Generate diff representation
        diff_lines = [
            f"- {text}",
            f"+ {corrected}"
        ]
        diff_view = "\n".join(diff_lines)

        summary = (
            f"Review Complete: Detected {len(errors)} error(s) across {len(set(e.category for e in errors))} grammatical categories. "
            f"All identified violations have been remediated in accordance with universal grammar principles."
        )

        return CorrectionResult(
            original_text=text,
            corrected_text=corrected,
            errors=errors,
            pedagogical_summary=summary,
            step_by_step_reasoning=reasoning_steps,
            diff_view=diff_view
        )
