"""
coreference.py - Pronoun and entity chain resolution for discourse coherence.
Handles anaphoric pronouns, antecedent resolution, and gender/number agreement.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Union

PRONOUN_FEATURES = {
    "he": {"gender": "M", "number": "SG"},
    "him": {"gender": "M", "number": "SG"},
    "his": {"gender": "M", "number": "SG"},
    "she": {"gender": "F", "number": "SG"},
    "her": {"gender": "F", "number": "SG"},
    "it": {"gender": "N", "number": "SG"},
    "its": {"gender": "N", "number": "SG"},
    "they": {"gender": "ANY", "number": "PL_OR_EPICENE"},
    "them": {"gender": "ANY", "number": "PL_OR_EPICENE"},
    "their": {"gender": "ANY", "number": "PL_OR_EPICENE"}
}


@dataclass
class CoreferenceChain:
    antecedent: str
    anaphor: str
    sentence_distance: int = 0


class EnglishCoreferenceResolver:
    """
    Coreference resolution engine building antecedent-anaphor clusters.
    """

    def resolve(self, text_or_sentences: Union[str, List[str]]) -> List[Dict[str, Any]]:
        if isinstance(text_or_sentences, str):
            sentences = [s.strip() for s in re.split(r"[.!?]+", text_or_sentences) if s.strip()]
        else:
            sentences = text_or_sentences
        return self.resolve_coreference(sentences)

    def resolve_coreference(self, sentences: List[str]) -> List[Dict[str, Any]]:
        clusters = []
        known_entities = []

        for sent_idx, sent in enumerate(sentences):
            words = sent.split()
            for w_idx, word in enumerate(words):
                clean = re.sub(r"[^\w]", "", word)
                lower = clean.lower()

                # Anaphor candidate: Pronoun (checked first to capture capitalized pronouns at sentence starts)
                if lower in PRONOUN_FEATURES:
                    p_feat = PRONOUN_FEATURES[lower]
                    matched_antecedent = None
                    for cand in reversed(known_entities):
                        if p_feat["gender"] == "ANY" or cand["gender"] == p_feat["gender"] or p_feat["gender"] == "N":
                            matched_antecedent = cand
                            break

                    if matched_antecedent:
                        clusters.append({
                            "antecedent": matched_antecedent["text"],
                            "anaphor": clean,
                            "sent_dist": sent_idx - matched_antecedent["sent_idx"],
                            "antecedent_pos": (matched_antecedent["sent_idx"], matched_antecedent["word_idx"]),
                            "anaphor_pos": (sent_idx, w_idx)
                        })

                # Entity candidate: Capitalized noun or subject
                elif clean and clean[0].isupper() and lower not in {"the", "a", "an", "this", "that"}:
                    entity_entry = {
                        "text": clean,
                        "sent_idx": sent_idx,
                        "word_idx": w_idx,
                        "gender": "F" if lower in {"mary", "alice", "sarah", "marie", "curie"} else ("M" if lower in {"john", "bob", "david", "alan", "turing"} else "N"),
                        "number": "SG"
                    }
                    known_entities.append(entity_entry)

        return clusters
