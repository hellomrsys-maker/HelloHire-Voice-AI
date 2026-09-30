"""
Japanese Intent and Speech Act Mapper
====================================
Maps utterances to Austin/Searle illocutionary forces with specialized detection
of Japanese high-context indirect speech acts (察し Sasshi, indirect requests & refusals).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class JapaneseSpeechAct:
    act_type: str  # "Assertive", "Directive", "Commissive", "Expressive", "Declarative"
    illocutionary_force: str
    is_indirect_sasshi: bool
    politeness_level: str
    confidence: float
    detected_marker: str


@dataclass
class JapaneseIntentReport:
    utterance: str
    primary_speech_act: JapaneseSpeechAct
    secondary_acts: List[JapaneseSpeechAct] = field(default_factory=list)


class JapaneseIntentMapper:
    """
    Classifies Japanese utterances into pragmatic intent frames, detecting subtle
    honorific requests, nuanced polite demurrals, and implicit directives.
    """

    def map_intent(self, text: str) -> JapaneseIntentReport:
        clean = text.strip()
        acts: List[JapaneseSpeechAct] = []

        # 1. Indirect polite requests (Directive)
        request_patterns = [
            (r"(していただけないでしょうか|していただけますか|願えますでしょうか|いただければ幸いです)", "Polite Honorific Request", True, "Sonkeigo / Kenjougo", 0.95),
            (r"(してください|してくださいませ|してちょうだい)", "Direct Request / Instruction", False, "Teineigo", 0.90),
            (r"(〜てくれ|〜ろ|〜しなさい)", "Imperative Order", False, "Plain / Authoritative", 0.92),
        ]
        for pat, desc, sasshi, polite, conf in request_patterns:
            m = re.search(pat, clean)
            if m:
                acts.append(
                    JapaneseSpeechAct(
                        act_type="Directive",
                        illocutionary_force=desc,
                        is_indirect_sasshi=sasshi,
                        politeness_level=polite,
                        confidence=conf,
                        detected_marker=m.group(0),
                    )
                )

        # 2. Indirect refusals / Hesitation (Assertive with indirect expressive refusal)
        refusal_patterns = [
            (r"(ちょっと(厳しい|難しい|都合が)|前向きに検討させていただきます|見送らせて)", "Indirect Polite Refusal (Demurral)", True, "Diplomatic / Formal", 0.92),
            (r"(できません|お断りいたします|無理です)", "Explicit Refusal", False, "Plain / Direct Polite", 0.95),
        ]
        for pat, desc, sasshi, polite, conf in refusal_patterns:
            m = re.search(pat, clean)
            if m:
                acts.append(
                    JapaneseSpeechAct(
                        act_type="Assertive / Refusal",
                        illocutionary_force=desc,
                        is_indirect_sasshi=sasshi,
                        politeness_level=polite,
                        confidence=conf,
                        detected_marker=m.group(0),
                    )
                )

        # 3. Commissives (Promises, Commitments, Proposals)
        commissive_patterns = [
            (r"(いたします|努めます|引き受けます|お約束します)", "Formal Commitment / Pledge", False, "Kenjougo", 0.88),
            (r"(しましょうか|しませんか|行こう)", "Joint Proposal / Invitation", False, "Teineigo / Plain Volitional", 0.85),
        ]
        for pat, desc, sasshi, polite, conf in commissive_patterns:
            m = re.search(pat, clean)
            if m:
                acts.append(
                    JapaneseSpeechAct(
                        act_type="Commissive",
                        illocutionary_force=desc,
                        is_indirect_sasshi=sasshi,
                        politeness_level=polite,
                        confidence=conf,
                        detected_marker=m.group(0),
                    )
                )

        # 4. Expressives (Gratitude, Apology, Greeting)
        expressive_patterns = [
            (r"(ありがとう|感謝|恐縮|お礼申し上げます)", "Gratitude Expressive", False, "High Polite", 0.95),
            (r"(申し訳|すみません|ごめんなさい|失礼)", "Apology / Regret Expressive", False, "Formal Apology", 0.95),
        ]
        for pat, desc, sasshi, polite, conf in expressive_patterns:
            m = re.search(pat, clean)
            if m:
                acts.append(
                    JapaneseSpeechAct(
                        act_type="Expressive",
                        illocutionary_force=desc,
                        is_indirect_sasshi=sasshi,
                        politeness_level=polite,
                        confidence=conf,
                        detected_marker=m.group(0),
                    )
                )

        # Default fallback: Assertive statement
        if not acts:
            acts.append(
                JapaneseSpeechAct(
                    act_type="Assertive",
                    illocutionary_force="Informative Statement / Proposition",
                    is_indirect_sasshi=False,
                    politeness_level="Neutral",
                    confidence=0.75,
                    detected_marker="Declarative sentence ending",
                )
            )

        return JapaneseIntentReport(
            utterance=text,
            primary_speech_act=acts[0],
            secondary_acts=acts[1:],
        )
