"""
French Sentence Generation Skill.
Generates grammatically conforming French declarative, negative, and interrogative clauses
respecting non-pro-drop subject requirements and elision rules.
"""

from typing import Dict, Any, Optional
from .verb_conjugator import FrenchVerbConjugator


class FrenchGenerator:
    """
    Surface realizer and sentence synthesizer for French clauses.
    """

    PRONOUN_MAP = {
        "je": 0, "tu": 1, "il": 2, "elle": 2, "on": 2,
        "nous": 3, "vous": 4, "ils": 5, "elles": 5
    }

    VOWELS = {"a", "e", "i", "o", "u", "y", "é", "è", "ê", "à"}

    def __init__(self):
        self.conjugator = FrenchVerbConjugator()

    def generate_statement(
        self,
        subject: str,
        verb_lemma: str,
        obj: Optional[str] = None,
        negative: bool = False,
        tense: str = "present"
    ) -> str:
        """
        Synthesizes a declarative French clause with mandatory overt subject and optional negation.
        """
        subj_low = subject.lower().strip()
        person_idx = self.PRONOUN_MAP.get(subj_low, 2)  # default 3rd sing for nouns

        conjugated_verb = self.conjugator.get_conjugation_for_person(verb_lemma, person_idx, tense)

        # Handle subject elision for "je"
        verb_starts_vowel = len(conjugated_verb) > 0 and conjugated_verb[0].lower() in self.VOWELS

        if negative:
            # Bipartite negation: ne / n' + verb + pas
            ne_prefix = "n'" if verb_starts_vowel else "ne "
            verb_clause = f"{ne_prefix}{conjugated_verb} pas"
            subj_clean = "Je" if subj_low == "je" else subject.capitalize()
            statement = f"{subj_clean} {verb_clause}"
        else:
            if subj_low == "je" and verb_starts_vowel:
                statement = f"J'{conjugated_verb}"
            else:
                statement = f"{subject.capitalize()} {conjugated_verb}"

        if obj:
            statement += f" {obj}"

        statement += "."
        return statement

    def generate_question(
        self,
        subject: str,
        verb_lemma: str,
        obj: Optional[str] = None,
        method: str = "est_ce_que"  # "est_ce_que" or "inversion"
    ) -> str:
        """
        Synthesizes an interrogative French sentence via 'Est-ce que' or subject-verb inversion.
        """
        subj_low = subject.lower().strip()
        person_idx = self.PRONOUN_MAP.get(subj_low, 2)
        conjugated_verb = self.conjugator.get_conjugation_for_person(verb_lemma, person_idx, "present")

        obj_str = f" {obj}" if obj else ""

        if method == "inversion" and subj_low in self.PRONOUN_MAP:
            # Euphonic -t- insertion if 3rd person singular verb ends in vowel and pronoun begins with vowel
            if subj_low in {"il", "elle", "on"} and conjugated_verb[-1] in self.VOWELS:
                question = f"{conjugated_verb.capitalize()}-t-{subj_low}{obj_str} ?"
            else:
                question = f"{conjugated_verb.capitalize()}-{subj_low}{obj_str} ?"
        else:
            # Default "Est-ce que"
            # Elision for est-ce que before il/ils/elle/elles
            if subj_low in {"il", "ils", "elle", "elles"} or (len(subj_low) > 0 and subj_low[0] in self.VOWELS):
                est_ce = "Est-ce qu'"
            else:
                est_ce = "Est-ce que "
            question = f"{est_ce}{subj_low} {conjugated_verb}{obj_str} ?"

        return question
