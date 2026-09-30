"""
Japanese Presupposition Checker
===============================
Extracts pragmatic presuppositions, factive entailments, and change-of-state triggers
from Japanese utterances.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class JapanesePresupposition:
    trigger_type: str  # "Factive_Verb", "Change_Of_State", "Iterative", "Definite_Reference"
    trigger_expression: str
    presupposed_proposition: str
    strength: float


@dataclass
class JapanesePresuppositionReport:
    sentence: str
    total_presuppositions: int
    presuppositions: List[JapanesePresupposition] = field(default_factory=list)


class JapanesePresuppositionChecker:
    """
    Extracts underlying presuppositions that remain invariant under negation
    in Japanese discourse.
    """

    def check(self, text: str) -> JapanesePresuppositionReport:
        presuppositions: List[JapanesePresupposition] = []

        # 1. Factive verbs (知っている, 気づく, 後悔する)
        # e.g. "彼が嘘をついたことを知っている" -> Presupposes "彼が嘘をついた" is fact
        factive_matches = re.finditer(r"([^\s、。]+(こと|の))を(知って|気づい|後悔し|後悔して)", text)
        for m in factive_matches:
            presuppositions.append(
                JapanesePresupposition(
                    trigger_type="Factive_Verb",
                    trigger_expression=m.group(0),
                    presupposed_proposition=f"事実前提：『{m.group(1)}』という事実は客観的に真である。",
                    strength=0.98,
                )
            )

        # 2. Change of state verbs (やめる, 始める, 続ける)
        # e.g. "タバコをやめた" -> Presupposes "以前はタバコを吸っていた"
        cos_matches = re.finditer(r"([^\s、。]+)を(やめた|やめる|開始した|始めた|続けている)", text)
        for m in cos_matches:
            target, verb = m.group(1), m.group(2)
            if "やめ" in verb:
                prop = f"状態変化前提：以前は『{target}』を行っていた。"
            elif "始" in verb or "開始" in verb:
                prop = f"状態変化前提：それ以前は『{target}』を行っていなかった。"
            else:
                prop = f"継続前提：従前から『{target}』を継続して行っていた。"

            presuppositions.append(
                JapanesePresupposition(
                    trigger_type="Change_Of_State",
                    trigger_expression=m.group(0),
                    presupposed_proposition=prop,
                    strength=0.92,
                )
            )

        # 3. Iteratives (また, 再び, もう一度)
        # e.g. "また失敗した" -> Presupposes "以前にも失敗した"
        iter_matches = re.finditer(r"(また|再び|もう一度)\s*([^\s、。]+)", text)
        for m in iter_matches:
            presuppositions.append(
                JapanesePresupposition(
                    trigger_type="Iterative",
                    trigger_expression=m.group(0),
                    presupposed_proposition=f"反復前提：過去にも類似の事象（『{m.group(2)}』）が少なくとも一度発生した。",
                    strength=0.90,
                )
            )

        # 4. Definite demonstratives (その, あの)
        # e.g. "その本" -> Presupposes "話者と聞き手が特定できる本が存在する"
        def_matches = re.finditer(r"(その|あの)([^\s、。]+)", text)
        for m in def_matches:
            presuppositions.append(
                JapanesePresupposition(
                    trigger_type="Definite_Reference",
                    trigger_expression=m.group(0),
                    presupposed_proposition=f"存在前提：文脈または物理環境において『{m.group(2)}』が唯一特定可能として存在する。",
                    strength=0.88,
                )
            )

        return JapanesePresuppositionReport(
            sentence=text,
            total_presuppositions=len(presuppositions),
            presuppositions=presuppositions,
        )
