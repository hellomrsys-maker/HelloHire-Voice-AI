"""
Japanese Question Answering Pipeline
====================================
Interrogative analysis and answer-span extraction for Japanese text.
Resolves interrogative pronouns (誰 dare, どこ doko, いつ itsu, 何 nani, なぜ naze)
against passage Named Entities, case frames, and causal connectives.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.skills.ner import JapaneseNamedEntityRecognizer
from Japanese_engine.brain.skills.srl import JapaneseSemanticRoleLabeler


@dataclass
class JapaneseQAResult:
    question: str
    context: str
    answer: str
    interrogative_type: str  # "WHO", "WHERE", "WHEN", "WHAT", "WHY", "HOW"
    confidence: float
    evidence_sentence: str


class JapaneseQuestionAnsweringPipeline:
    """
    Japanese extractive QA matching question interrogatives to contextual syntactic and semantic roles.
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()
        self.ner = JapaneseNamedEntityRecognizer()
        self.srl = JapaneseSemanticRoleLabeler()

    def answer_question(self, question: str, passage: str) -> JapaneseQAResult:
        # Detect interrogative type
        q_type = "WHAT"
        if "誰" in question or "どなた" in question:
            q_type = "WHO"
        elif "どこ" in question or "どちら" in question or "何処" in question:
            q_type = "WHERE"
        elif "いつ" in question or "何時" in question or "何年" in question or "何日" in question:
            q_type = "WHEN"
        elif "なぜ" in question or "どうして" in question or "何故" in question or "理由" in question:
            q_type = "WHY"
        elif "どう" in question or "いかに" in question or "どのように" in question:
            q_type = "HOW"
        elif "何" in question:
            q_type = "WHAT"

        sentences = [s.strip() for s in re.split(r"[。！？\n]+", passage) if s.strip()]
        if not sentences:
            return JapaneseQAResult(question, passage, "回答不可（文脈なし）", q_type, 0.0, "")

        # Find best sentence by keyword overlap (excluding question particles)
        q_tokens = [t.text for t in self.tokenizer.tokenize(question) if len(t.text) > 1 and t.text not in ["誰", "どこ", "いつ", "何", "なぜ", "ですか", "ますか"]]
        best_sentence = sentences[0]
        max_overlap = -1

        for s in sentences:
            overlap = sum(1 for tok in q_tokens if tok in s)
            if overlap > max_overlap:
                max_overlap = overlap
                best_sentence = s

        # Extract answer according to question type
        answer = best_sentence
        conf = 0.75

        if q_type == "WHO":
            entities = self.ner.extract_entities(best_sentence)
            persons = [e.text for e in entities if e.label == "PERSON"]
            if persons:
                answer = persons[0]
                conf = 0.92
            else:
                m = re.search(r"([^\s、。]+)[はが]", best_sentence)
                if m:
                    answer = m.group(1)
                    conf = 0.82

        elif q_type == "WHERE":
            entities = self.ner.extract_entities(best_sentence)
            gpe = [e.text for e in entities if e.label == "GPE"]
            if gpe:
                answer = gpe[0]
                conf = 0.92
            else:
                m = re.search(r"([^\s、。]+)[にでへ]", best_sentence)
                if m:
                    answer = m.group(1)
                    conf = 0.80

        elif q_type == "WHEN":
            entities = self.ner.extract_entities(best_sentence)
            dates = [e.text for e in entities if e.label == "DATE"]
            if dates:
                answer = dates[0]
                conf = 0.92
            else:
                m = re.search(r"(\d+年|\d+月|\d+日|\d+時|[^\s、。]+頃)", best_sentence)
                if m:
                    answer = m.group(0)
                    conf = 0.85

        elif q_type == "WHY":
            m = re.search(r"([^\s、。]+(から|ため|ので|ゆえに))", best_sentence)
            if m:
                answer = m.group(1)
                conf = 0.88

        elif q_type == "WHAT":
            m = re.search(r"([^\s、。]+)を", best_sentence)
            if m:
                answer = m.group(1)
                conf = 0.85

        return JapaneseQAResult(
            question=question,
            context=passage,
            answer=answer,
            interrogative_type=q_type,
            confidence=round(conf, 2),
            evidence_sentence=best_sentence,
        )
