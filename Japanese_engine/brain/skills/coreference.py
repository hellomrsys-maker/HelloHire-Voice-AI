"""
coreference.py - Japanese Zero-Anaphora (Zero-Pronoun) and Demonstrative Coreference Resolution.
Recovers elided subjects and objects from preceding discourse topics (wa/ga)
and resolves overt Japanese anaphors (kare, kanojo, kore, sore, are).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Union

from .tokenization import JapaneseTokenizer


@dataclass
class JapaneseCoreferenceChain:
    antecedent: str
    anaphor_type: str  # "ZERO_PRONOUN" (omitted subject), "OVERT_PRONOUN" (彼/彼女), "DEMONSTRATIVE" (これ/それ)
    sentence_distance: int
    resolved_role: str  # "SUBJ", "OBJ", "TOPIC"


class JapaneseCoreferenceResolver:
    """
    Resolves zero-anaphora and overt pronouns in Japanese discourse.
    """

    DEMONSTRATIVES = {"これ", "それ", "あれ", "この", "その", "あの"}
    OVERT_PRONOUNS = {"彼": "M", "彼女": "F", "彼ら": "PL", "彼等": "PL"}

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()

    def resolve(self, text_or_sentences: Union[str, List[str]]) -> List[Dict[str, Any]]:
        if isinstance(text_or_sentences, str):
            sentences = self.tokenizer.split_sentences(text_or_sentences)
        else:
            sentences = text_or_sentences

        chains: List[Dict[str, Any]] = []
        salient_entities: List[Dict[str, Any]] = []

        for sent_idx, sent in enumerate(sentences):
            # Extract topic marked by 'は' (primary antecedent candidate)
            wa_match = re.search(r"([\u4e00-\u9faf\u3040-\u30ffA-Za-z0-9]+)は", sent)
            ga_match = re.search(r"([\u4e00-\u9faf\u3040-\u30ffA-Za-z0-9]+)が", sent)

            if wa_match:
                topic_noun = wa_match.group(1)
                salient_entities.append({"text": topic_noun, "sent_idx": sent_idx, "salience": 100})
            elif ga_match:
                subj_noun = ga_match.group(1)
                salient_entities.append({"text": subj_noun, "sent_idx": sent_idx, "salience": 80})

            # Check for overt pronouns
            for p in self.OVERT_PRONOUNS:
                if p in sent:
                    if salient_entities:
                        antecedent = salient_entities[-1]["text"]
                        chains.append({
                            "antecedent": antecedent,
                            "anaphor": p,
                            "anaphor_type": "OVERT_PRONOUN",
                            "sent_dist": sent_idx - salient_entities[-1]["sent_idx"]
                        })

            # Check for zero-anaphora: if a sentence has a verb ending but no overt subject (no は or が)
            has_verb = any(v in sent for v in ["ます", "した", "る", "ない", "だ", "です"])
            has_subject = bool(wa_match or ga_match)

            if has_verb and not has_subject and salient_entities:
                # Omitted subject recovered from preceding topic
                recovered_antecedent = salient_entities[-1]["text"]
                chains.append({
                    "antecedent": recovered_antecedent,
                    "anaphor": "[Ø_SUBJ]",
                    "anaphor_type": "ZERO_PRONOUN",
                    "sent_dist": sent_idx - salient_entities[-1]["sent_idx"]
                })

        return chains
