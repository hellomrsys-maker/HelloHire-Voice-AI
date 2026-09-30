"""
Spanish Sentence Generation Skill.
Synthesizes grammatically valid Spanish sentences respecting agreement, mood, and pro-drop.
"""

from typing import Dict, Any, Optional
from .verb_conjugator import SpanishVerbConjugator


class SpanishGenerator:
    """
    Template and rule-guided generator for Spanish clauses.
    """

    def __init__(self):
        self.conjugator = SpanishVerbConjugator()

    def generate(
        self,
        subject: str,
        verb_lemma: str,
        obj: str,
        tense: str = "presente_indicativo",
        pro_drop: bool = False,
        polite: bool = False,
        is_question: bool = False,
    ) -> str:
        """
        Synthesizes a Spanish clause with person agreement and inverted punctuation.
        """
        person_idx = 0
        s_low = subject.lower().strip()

        if polite or s_low == "usted":
            person_idx = 2 # 3rd person singular agreement
            subj_str = "Usted"
        elif s_low == "yo":
            person_idx = 0
            subj_str = "Yo"
        elif s_low in {"tú", "tu"}:
            person_idx = 1
            subj_str = "Tú"
        elif s_low in {"él", "ella"}:
            person_idx = 2
            subj_str = subject.capitalize()
        elif s_low in {"nosotros", "nosotras"}:
            person_idx = 3
            subj_str = subject.capitalize()
        elif s_low in {"ellos", "ellas", "ustedes"}:
            person_idx = 5
            subj_str = subject.capitalize()
        else:
            person_idx = 2
            subj_str = subject

        verb_form = self.conjugator.get_conjugation_for_person(verb_lemma, person_idx, tense)
        if not verb_form:
            verb_form = verb_lemma # Fallback

        if pro_drop:
            core = f"{verb_form.capitalize()} {obj}"
        else:
            core = f"{subj_str} {verb_form} {obj}"

        core = core.strip()

        if is_question:
            return f"¿{core}?"
        return f"{core}."
