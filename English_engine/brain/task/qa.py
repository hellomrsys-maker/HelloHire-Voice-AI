"""
Question Answering (QA) Engine over English Passages.
Combines exact span extraction, semantic role matching (SRL),
named entity filtering, and lexical overlap ranking to answer queries.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from English_engine.brain.skills.tokenization import EnglishTokenizer
from English_engine.brain.skills.ner import EnglishNamedEntityRecognizer
from English_engine.brain.skills.srl import EnglishSemanticRoleLabeler


@dataclass
class QAResult:
    query: str
    best_answer: str
    confidence: float
    answer_sentence: str
    char_start: int
    char_end: int
    matched_entities: List[str] = field(default_factory=list)


class QuestionAnsweringEngine:
    """
    Extractive QA engine answering factoid, entity, and causal questions from a context passage.
    """

    def __init__(self) -> None:
        self.tokenizer = EnglishTokenizer()
        self.ner = EnglishNamedEntityRecognizer()
        self.srl = EnglishSemanticRoleLabeler()

    def answer_question(self, passage: str, query: str) -> QAResult:
        sentences = self.tokenizer.split_sentences(passage)
        query_tokens = [t.text.lower() for t in self.tokenizer.tokenize(query) if t.is_word]
        query_set = set(query_tokens)

        # Question classification
        q_type = "general"
        if "who" in query_set:
            q_type = "person"
        elif "where" in query_set:
            q_type = "location"
        elif "when" in query_set:
            q_type = "time"
        elif "why" in query_set:
            q_type = "cause"

        best_sent = ""
        best_score = -1.0
        best_idx = 0

        for i, sent in enumerate(sentences):
            sent_tokens = [t.text.lower() for t in self.tokenizer.tokenize(sent) if t.is_word]
            overlap = len(set(sent_tokens) & query_set)
            score = overlap / max(1, len(query_set))

            # Bonus for question type matching entity types
            ner_res = self.ner.recognize(sent)
            if q_type == "person" and any(e.entity_type == "PERSON" for e in ner_res):
                score += 0.4
            elif q_type == "location" and any(e.entity_type == "GPE" for e in ner_res):
                score += 0.4
            elif q_type == "time" and any(e.entity_type == "DATE" for e in ner_res):
                score += 0.4

            if score > best_score:
                best_score = score
                best_sent = sent
                best_idx = i

        # Extract answer snippet
        start_char = passage.find(best_sent) if best_sent else 0
        end_char = start_char + len(best_sent)
        recognized_entities = self.ner.recognize(best_sent)
        ner_in_answer = [e.text for e in recognized_entities]

        # Specific extraction if factoid matching target question type
        answer_text = best_sent
        if q_type == "location":
            loc_matches = [e.text for e in recognized_entities if e.entity_type in {"GPE", "LOC"}]
            if loc_matches:
                answer_text = loc_matches[0]
        elif q_type == "person":
            person_matches = [e.text for e in recognized_entities if e.entity_type == "PERSON"]
            if person_matches:
                answer_text = person_matches[0]
        elif q_type == "time":
            time_matches = [e.text for e in recognized_entities if e.entity_type == "DATE"]
            if time_matches:
                answer_text = time_matches[0]
        elif ner_in_answer:
            answer_text = ner_in_answer[0]

        conf = min(0.98, max(0.20, best_score))

        return QAResult(
            query=query,
            best_answer=answer_text,
            confidence=round(conf, 2),
            answer_sentence=best_sent,
            char_start=start_char,
            char_end=end_char,
            matched_entities=ner_in_answer,
        )
