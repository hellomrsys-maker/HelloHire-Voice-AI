"""
Spanish Morphosyntactic Parser Skill.
Extracts clause hierarchy, pro-drop null subjects, subjunctive triggers, and clitic chains.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional

SUBJUNCTIVE_TRIGGERS = {
    "quiero que", "quiere que", "deseo que", "espero que", "ojalá",
    "dudo que", "no creo que", "no pienso que", "es necesario que",
    "es importante que", "es posible que", "recomiendo que", "sugiero que",
    "para que", "a fin de que", "antes de que", "sin que"
}

SUBJECT_PRONOUNS = {"yo", "tú", "vos", "él", "ella", "nosotros", "nosotras", "vosotros", "vosotras", "ellos", "ellas", "usted", "ustedes"}


@dataclass
class SpanishSentenceStructure:
    has_overt_subject: bool
    overt_subject: Optional[str]
    is_pro_drop: bool
    has_subjunctive_trigger: bool
    subjunctive_triggers: List[str]
    has_clitic_chain: bool
    clitics: List[str]
    has_personal_a: bool


class SpanishParser:
    """
    Parser for Spanish sentence architecture, null subjects, and modal triggers.
    """

    def parse(self, tagged_tokens: List[Tuple[str, str]]) -> SpanishSentenceStructure:
        tokens = [t[0] for t in tagged_tokens]
        text_joined = " ".join(tokens).lower()

        # Subject discovery
        overt_subject = None
        has_verb = False
        first_verb_idx = -1

        for idx, (tok, tag) in enumerate(tagged_tokens):
            if tag in {"VERB", "AUX"} and first_verb_idx == -1:
                first_verb_idx = idx
                has_verb = True

        for idx, (tok, tag) in enumerate(tagged_tokens):
            low = tok.lower()
            if low in SUBJECT_PRONOUNS:
                overt_subject = tok
                break
            # Candidate noun subject must occur before the verb and not be preceded by a preposition
            if tag == "NOUN" and overt_subject is None:
                if first_verb_idx != -1 and idx < first_verb_idx:
                    prev_tag = tagged_tokens[idx - 1][1] if idx > 0 else None
                    if prev_tag != "ADP":
                        overt_subject = tok
                        break

        has_overt = overt_subject is not None
        is_pro_drop = has_verb and not has_overt

        # Subjunctive triggers
        triggers_found = []
        for trig in SUBJUNCTIVE_TRIGGERS:
            if trig in text_joined:
                triggers_found.append(trig)

        # Clitics
        clitics_found = []
        clitic_set = {"me", "te", "se", "nos", "os", "le", "les", "lo", "la", "los", "las"}
        for tok, tag in tagged_tokens:
            if tok.lower() in clitic_set:
                clitics_found.append(tok.lower())

        # Personal "a" (marks direct object human/animate referents, e.g. "a Juan", "a los estudiantes", "al profesor")
        has_personal_a = False
        for i in range(len(tagged_tokens) - 1):
            if tagged_tokens[i][0].lower() in {"a", "al"}:
                for j in range(i + 1, min(i + 4, len(tagged_tokens))):
                    tok_tag = tagged_tokens[j][1]
                    if tok_tag in {"NOUN", "PRON"}:
                        has_personal_a = True
                        break
                    elif tok_tag not in {"DET", "ADJ"}:
                        break
                if has_personal_a:
                    break

        return SpanishSentenceStructure(
            has_overt_subject=has_overt,
            overt_subject=overt_subject,
            is_pro_drop=is_pro_drop,
            has_subjunctive_trigger=len(triggers_found) > 0,
            subjunctive_triggers=triggers_found,
            has_clitic_chain=len(clitics_found) > 0,
            clitics=clitics_found,
            has_personal_a=has_personal_a,
        )
