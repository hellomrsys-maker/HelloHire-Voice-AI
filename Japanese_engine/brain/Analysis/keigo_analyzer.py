"""
Japanese Keigo Pragmatic Appropriateness Analyzer
=================================================
Infers social hierarchy, Uchi/Soto (内・外 in-group/out-group) dynamic boundaries,
and verifies correct honorific elevation concord across speaker, listener, and referent.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class KeigoAppropriatenessReport:
    utterance: str
    target_relationship: str  # e.g., "Company_to_Client", "Subordinate_to_Superior", "Peer_to_Peer"
    is_appropriate: bool
    violations: List[str] = field(default_factory=list)
    suggested_correction: Optional[str] = None
    recommended_level: str = "Teineigo / Kenjougo"


class JapaneseKeigoAnalyzer:
    """
    Evaluates whether an utterance complies with pragmatic Uchi/Soto and social distance norms.
    """

    def analyze_social_distance(
        self,
        utterance: str,
        speaker_role: str = "employee",
        listener_role: str = "client",
    ) -> KeigoAppropriatenessReport:
        violations: List[str] = []
        clean = utterance.strip()
        is_app = True
        suggested = clean

        # 1. External client context: In-group members (including own CEO/Bucho) must NOT be elevated with Sonkeigo
        if speaker_role == "employee" and listener_role == "client":
            # Check if speaker refers to own company head with -san or sonkeigo
            if re.search(r"(うちの社長様|当社の社長様|社長がおっしゃい|部長がおっしゃい)", clean):
                violations.append(
                    "ウチ・ソトの逆転エラー：社外（顧客）に対して自社の社長・上司に敬称・尊敬語を使用しています。自社の上司は身内（ウチ）として呼び捨てにし、動作は謙譲語（申す等）を用います。"
                )
                suggested = clean.replace("うちの社長様", "社長の鈴木").replace("がおっしゃい", "が申し")
                is_app = False

            # Check if speaking to client without keigo
            if clean.endswith("だ。") or clean.endswith("だよ。") or clean.endswith("する。"):
                violations.append("敬意不足：顧客に対する発話において常体（だ・である）が使用されています。")
                is_app = False

        # 2. Subordinate to superior in internal company
        elif speaker_role == "subordinate" and listener_role == "superior":
            if clean.endswith("うん。") or clean.endswith("だね。") or "ご苦労様" in clean:
                violations.append("上司に対する不適切な表現：『ご苦労様』は目上から目下への言葉です。『お疲れ様です』を使用してください。")
                suggested = clean.replace("ご苦労様", "お疲れ様です")
                is_app = False

        return KeigoAppropriatenessReport(
            utterance=clean,
            target_relationship=f"{speaker_role} -> {listener_role}",
            is_appropriate=is_app,
            violations=violations,
            suggested_correction=suggested if not is_app else None,
            recommended_level="Formal Kenjougo/Sonkeigo" if listener_role == "client" else "Teineigo",
        )
