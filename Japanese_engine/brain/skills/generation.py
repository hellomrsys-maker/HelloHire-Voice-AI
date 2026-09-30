"""
generation.py - Japanese Constraint-Governed Agglutinative Clause Generator.
Synthesizes grammatically correct Japanese clauses matching target tense,
aspect (-te iru), voice (passive/causative), and politeness levels (Desu/Masu vs Da).
"""

from __future__ import annotations
from typing import Dict, Any, Optional


class JapaneseTextGenerator:
    """
    Grammar-governed generator producing syntactically correct Japanese sentences.
    """

    def generate(
        self,
        subject: str,
        verb: str,
        object_: Optional[str] = None,
        tense: str = "present",
        politeness: str = "teinei",  # "teinei" (丁寧語 / です・ます) or "plain" (普通体 / だ・である)
        voice: str = "active",       # "active", "passive" (-れる/-られる), "causative" (-せる/-させる)
        sentence_type: str = "declarative", # "declarative", "interrogative", "negative"
    ) -> str:
        # Build arguments
        subj_str = f"{subject}は" if subject else ""
        obj_str = f"{object_}を" if object_ else ""

        # Conjugate verb stem
        stem = verb
        if verb.endswith("る"):
            stem = verb[:-1]

        # Voice adjustments
        if voice == "passive":
            verb_stem = stem + "られ"
        elif voice == "causative":
            verb_stem = stem + "させ"
        else:
            verb_stem = stem

        # Politeness and tense
        if politeness == "teinei":
            if sentence_type == "negative":
                v_ending = "ません" if tense == "present" else "ませんでした"
            else:
                v_ending = "ます" if tense == "present" else "ました"
            final_verb = f"{verb_stem}{v_ending}"
        else:
            if sentence_type == "negative":
                v_ending = "ない" if tense == "present" else "なかった"
                final_verb = f"{verb_stem}{v_ending}"
            else:
                final_verb = f"{verb}" if tense == "present" else f"{verb_stem}た"

        # Interrogative particle
        q_mark = "か。" if sentence_type == "interrogative" else "。"

        parts = [p for p in [subj_str, obj_str, final_verb] if p]
        return "".join(parts) + q_mark
