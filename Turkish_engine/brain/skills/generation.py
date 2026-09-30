"""Turkish Generation Skill.

Generates grammatical Turkish clauses conforming to head-final SOV order,
harmonic suffix agglutination, differential object marking, and postposition valency.
"""

from typing import Dict, Any, Optional
from .case_engine import TurkishCaseEngine
from .verb_conjugator import TurkishVerbConjugator
from .vowel_harmony_engine import TurkishVowelHarmonyEngine


class TurkishSentenceGenerator:
    def __init__(
        self,
        case_engine: TurkishCaseEngine = None,
        verb_conjugator: TurkishVerbConjugator = None,
        harmony_engine: TurkishVowelHarmonyEngine = None
    ):
        self.case_engine = case_engine or TurkishCaseEngine()
        self.verb_conjugator = verb_conjugator or TurkishVerbConjugator()
        self.harmony = harmony_engine or TurkishVowelHarmonyEngine()

    def generate_transitive_sov(
        self,
        subject: str,
        verb_lemma: str,
        object_noun: str,
        is_definite_object: bool = True,
        tense: str = "past",
        person: str = "3sg"
    ) -> str:
        """Generates a standard Turkish Subject-Object-Verb (SOV) sentence."""
        # 1. Subject (Nominative)
        subj_str = subject.strip().capitalize()

        # 2. Object with Differential Object Marking
        if is_definite_object:
            obj_str = self.case_engine.inflect_noun(object_noun, case="acc")
        else:
            obj_str = object_noun.strip()

        # 3. Finite Verb
        verb_str = self.verb_conjugator.conjugate(verb_lemma, tense=tense, person=person)

        return f"{subj_str} {obj_str} {verb_str}."

    def generate_postpositional_clause(
        self,
        subject: str,
        noun: str,
        postposition: str,
        verb_lemma: str,
        tense: str = "past"
    ) -> str:
        """Generates Subject + [Noun + Postposition] + Verb."""
        subj_str = subject.strip().capitalize()

        # Check required case for postposition
        postp_low = postposition.lower()
        if postp_low in ("kadar", "doğru", "göre", "rağmen"):
            inflected_noun = self.case_engine.inflect_noun(noun, case="dat")
        elif postp_low in ("sonra", "önce", "beri", "dolayı", "ötürü"):
            inflected_noun = self.case_engine.inflect_noun(noun, case="abl")
        else:
            inflected_noun = noun

        verb_str = self.verb_conjugator.conjugate(verb_lemma, tense=tense, person="3sg")
        return f"{subj_str} {inflected_noun} {postposition} {verb_str}."

    def generate_polite_request(self, verb_lemma: str) -> str:
        """Generates a formal polite request using the Aorist question form (e.g. 'Açar mısınız?')."""
        stem = self.verb_conjugator.get_stem(verb_lemma)
        two_v = self.harmony.get_two_way_harmonic_vowel(stem)
        aorist_verb = f"{stem}{two_v}r"

        harm_q = self.harmony.get_four_way_harmonic_vowel(aorist_verb)
        question_particle = f"m{harm_q}s{harm_q}n{harm_q}z"

        return f"{aorist_verb.capitalize()} {question_particle}?"
