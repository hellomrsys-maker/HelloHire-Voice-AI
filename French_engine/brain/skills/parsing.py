"""
French Sentence Parsing Skill.
Analyzes syntactic configuration, enforces non-pro-drop subject requirement,
identifies expletive/dummy subjects, detects bipartite negation, and extracts subjunctive triggers.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional


@dataclass
class FrenchSentenceStructure:
    has_overt_subject: bool
    subject_token: Optional[str]
    is_expletive_subject: bool
    is_imperative: bool
    has_bipartite_negation: bool
    negation_pair: Optional[Tuple[str, str]]
    has_subjunctive_trigger: bool
    subjunctive_triggers: List[str]
    clitics: List[str]
    verb_tokens: List[str]


class FrenchParser:
    """
    Parser for French clauses enforcing Gallo-Romance non-pro-drop constraints
    and identifying structural operators.
    """

    SUBJECT_PRONOUNS = {
        "je", "j'", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles", "ce", "c'"
    }

    EXPLETIVE_PATTERNS = {
        ("il", "faut"), ("il", "fallait"), ("il", "faudra"),
        ("il", "pleut"), ("il", "pleuvait"), ("il", "pleuvra"),
        ("il", "s'agit"), ("il", "y", "a"), ("c'", "est"), ("ce", "sont")
    }

    SUBJUNCTIVE_TRIGGERS = [
        "il faut que", "il est nécessaire que", "vouloir que", "veux que", "veut que", "veulent que",
        "bien que", "pour que", "afin que", "avant que", "sans que",
        "douter que", "doute que", "avoir peur que", "a peur que", "souhaiter que"
    ]

    NEGATION_FIRST = {"ne", "n'"}
    NEGATION_SECOND = {"pas", "plus", "jamais", "rien", "personne", "aucun", "aucune"}

    CLITIC_SET = {
        "me", "m'", "te", "t'", "se", "s'", "nous", "vous", "le", "la", "l'", "les", "lui", "leur", "y", "en"
    }

    def parse(self, tagged_tokens: List[Tuple[str, str]]) -> FrenchSentenceStructure:
        words = [t[0].lower() for t in tagged_tokens]
        full_text = " ".join(words)

        # 1. Subject Identification
        has_overt_subject = False
        subject_token = None
        is_expletive = False
        is_imperative = False

        # Check for expletive expressions
        if len(words) >= 2 and words[0] in {"il", "ce", "c'"} and words[1] in {"faut", "pleut", "est", "sont", "y", "s'agit"}:
            is_expletive = True
            has_overt_subject = True
            subject_token = words[0]
        else:
            for i, (tok, tag) in enumerate(tagged_tokens):
                low = tok.lower()
                if low in self.SUBJECT_PRONOUNS:
                    has_overt_subject = True
                    subject_token = tok
                    break
                elif tag in {"NOUN", "PROPN"} and i < 3:
                    # Pre-verbal nominal subject
                    has_overt_subject = True
                    subject_token = tok
                    break

        # Check if imperative
        if not has_overt_subject and len(tagged_tokens) > 0 and tagged_tokens[0][1] in {"VERB"}:
            is_imperative = True

        # 2. Bipartite Negation Detection (ne...pas)
        has_negation = False
        neg_pair = None
        neg1_idx = -1
        for i, w in enumerate(words):
            if w in self.NEGATION_FIRST:
                neg1_idx = i
                break
        if neg1_idx != -1:
            for j in range(neg1_idx + 1, min(neg1_idx + 5, len(words))):
                if words[j] in self.NEGATION_SECOND:
                    has_negation = True
                    neg_pair = (words[neg1_idx], words[j])
                    break

        # 3. Subjunctive Trigger Detection
        triggers_found: List[str] = []
        for trig in self.SUBJUNCTIVE_TRIGGERS:
            if trig in full_text:
                triggers_found.append(trig)

        # 4. Clitics & Verbs Extraction
        clitics_found: List[str] = []
        verbs_found: List[str] = []
        for tok, tag in tagged_tokens:
            low = tok.lower()
            if low in self.CLITIC_SET and low not in self.SUBJECT_PRONOUNS:
                clitics_found.append(low)
            elif tag in {"VERB", "AUX"}:
                verbs_found.append(tok)

        return FrenchSentenceStructure(
            has_overt_subject=has_overt_subject,
            subject_token=subject_token,
            is_expletive_subject=is_expletive,
            is_imperative=is_imperative,
            has_bipartite_negation=has_negation,
            negation_pair=neg_pair,
            has_subjunctive_trigger=len(triggers_found) > 0,
            subjunctive_triggers=triggers_found,
            clitics=clitics_found,
            verb_tokens=verbs_found,
        )
