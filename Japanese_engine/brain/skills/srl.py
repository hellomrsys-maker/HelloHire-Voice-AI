"""
srl.py - Japanese Predicate-Argument Structure (PAS) and Semantic Role Labeling.
Extracts Ga-case (Agent), O-case (Patient/Theme), Ni-case (Recipient/Goal),
De-case (Instrument/Location), and Predicates from Japanese sentences.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .tokenization import JapaneseTokenizer


@dataclass
class JapanesePASFrame:
    predicate: str
    predicate_index: int
    ga_agent: Optional[str] = None      # ガ格 (Agent / Experiencer)
    o_patient: Optional[str] = None     # ヲ格 (Theme / Patient)
    ni_recipient: Optional[str] = None  # ニ格 (Goal / Recipient / Time)
    de_instrument: Optional[str] = None # デ格 (Instrument / Setting)
    to_comitative: Optional[str] = None # ト格 (Partner / Quote)

    def __getitem__(self, item):
        return getattr(self, item)


class JapaneseSemanticRoleLabeler:
    """
    Predicate-Argument Structure (PAS) labeler for Japanese case-marked propositions.
    """

    COMMON_VERBS = [
        "開発した", "作成した", "分析した", "食べた", "読んだ", "書いた", "教えた",
        "開発する", "作成する", "分析する", "食べる", "読む", "書く", "教える",
        "行った", "来た", "走った", "話した", "設計した", "実行した"
    ]

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()

    def label_roles(self, sentence_text: str) -> List[JapanesePASFrame]:
        frames: List[JapanesePASFrame] = []
        text = sentence_text.strip()

        # Extract arguments by particle attachments
        ga_match = re.search(r"([\u4e00-\u9faf\u3040-\u30ffA-Za-z0-9]+)が", text)
        wa_match = re.search(r"([\u4e00-\u9faf\u3040-\u30ffA-Za-z0-9]+)は", text)
        o_match = re.search(r"([\u4e00-\u9faf\u3040-\u30ffA-Za-z0-9]+)を", text)
        ni_match = re.search(r"([\u4e00-\u9faf\u3040-\u30ffA-Za-z0-9]+)に", text)
        de_match = re.search(r"([\u4e00-\u9faf\u3040-\u30ffA-Za-z0-9]+)で", text)
        to_match = re.search(r"([\u4e00-\u9faf\u3040-\u30ffA-Za-z0-9]+)と", text)

        # Agent can be marked by が or topicalized by は
        agent = ga_match.group(1) if ga_match else (wa_match.group(1) if wa_match else None)
        patient = o_match.group(1) if o_match else None
        recipient = ni_match.group(1) if ni_match else None
        instrument = de_match.group(1) if de_match else None
        partner = to_match.group(1) if to_match else None

        # Find predicate
        detected_pred = None
        for v in self.COMMON_VERBS:
            if v in text:
                detected_pred = v
                break

        if not detected_pred:
            # Fallback: extract last content word ending before punctuation
            cleaned = re.sub(r"[。！？\s]+$", "", text)
            m = re.search(r"([\u4e00-\u9faf\u3040-\u30ff]+)$", cleaned)
            detected_pred = m.group(1) if m else "述語"

        frames.append(
            JapanesePASFrame(
                predicate=detected_pred,
                predicate_index=text.find(detected_pred),
                ga_agent=agent,
                o_patient=patient,
                ni_recipient=recipient,
                de_instrument=instrument,
                to_comitative=partner,
            )
        )

        return frames
