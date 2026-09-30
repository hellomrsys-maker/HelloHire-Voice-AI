"""
Japanese Zero-Pronoun and Argument Recovery Engine
==================================================
Resolves unexpressed syntactic arguments (Zero-Anaphora / Pro-drop) in Japanese discourse
by tracking topic chains, interlocutor perspectives, honorific constraints, and giving/receiving verb valency.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer


@dataclass
class OmittedArgumentRecovery:
    predicate: str
    omitted_role: str  # "Subject (が格)", "Direct_Object (を格)", "Recipient (に格)"
    inferred_referent: str
    confidence: float
    grounding_heuristic: str


@dataclass
class ZeroPronounReport:
    discourse_topic: Optional[str]
    recovered_arguments: List[OmittedArgumentRecovery] = field(default_factory=list)


class JapaneseZeroPronounResolver:
    """
    Recovers omitted subjects and objects across conversational turns and multi-sentence paragraphs.
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()

    def resolve_discourse(self, discourse_history: List[str], current_utterance: str) -> ZeroPronounReport:
        # 1. Establish active topic from history or current sentence
        active_topic = None
        for s in reversed(discourse_history + [current_utterance]):
            m = re.search(r"([^\s、。]+)は", s)
            if m:
                active_topic = m.group(1)
                break

        recoveries: List[OmittedArgumentRecovery] = []

        # 2. Analyze current utterance predicates
        # Check if subject is explicitly present
        has_explicit_subject = bool(re.search(r"[はが]", current_utterance))

        # Check honorific cues (Sonkeigo indicates listener; Kenjougo indicates speaker)
        if "おっしゃ" in current_utterance or "ご覧に" in current_utterance or "召し上が" in current_utterance or "いらっしゃ" in current_utterance:
            recoveries.append(
                OmittedArgumentRecovery(
                    predicate=current_utterance,
                    omitted_role="Subject (が格)",
                    inferred_referent="聞き手（あなた / 先方様）",
                    confidence=0.95,
                    grounding_heuristic="尊敬語（Sonkeigo）の一致制約：動作主は目上または聞き手",
                )
            )
        elif "拝見" in current_utterance or "伺い" in current_utterance or "申し上げ" in current_utterance or "いたし" in current_utterance or "存じ" in current_utterance:
            recoveries.append(
                OmittedArgumentRecovery(
                    predicate=current_utterance,
                    omitted_role="Subject (が格)",
                    inferred_referent="話し手（私 / 当社）",
                    confidence=0.96,
                    grounding_heuristic="謙譲語（Kenjougo）の一致制約：動作主は自己またはウチ側",
                )
            )
        # Check giving/receiving verbs (授受動詞)
        elif "くれる" in current_utterance or "くださる" in current_utterance:
            recoveries.append(
                OmittedArgumentRecovery(
                    predicate=current_utterance,
                    omitted_role="Recipient (に格)",
                    inferred_referent="話し手（私）",
                    confidence=0.94,
                    grounding_heuristic="受益動詞（くれる・くださる）制約：恩恵の受取手は常に話し手側",
                )
            )
        elif not has_explicit_subject:
            # Fallback to topic continuity
            ref = active_topic if active_topic else "話し手（私）"
            recoveries.append(
                OmittedArgumentRecovery(
                    predicate=current_utterance,
                    omitted_role="Subject (が格)",
                    inferred_referent=ref,
                    confidence=0.80 if active_topic else 0.65,
                    grounding_heuristic="談話主題連鎖（Topic-chain continuity）による省略復元",
                )
            )

        return ZeroPronounReport(
            discourse_topic=active_topic,
            recovered_arguments=recoveries,
        )
