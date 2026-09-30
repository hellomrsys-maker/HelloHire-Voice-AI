"""
ner.py - Named Entity Recognition (NER) for English text.
Classifies spans into PERSON, ORG, GPE/LOC, DATE, and TECH entities.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Any

TITLE_PREFIXES = {"mr.", "mrs.", "ms.", "dr.", "prof.", "president", "director", "senator"}
ORG_SUFFIXES = {"inc.", "inc", "corp.", "corp", "llc", "ltd", "ltd.", "university", "institute", "group", "labs", "company"}
LOCATIONS = {"london", "paris", "tokyo", "new york", "berlin", "delhi", "san francisco", "california", "india", "japan", "germany", "usa", "uk"}
TECH_TERMS = {"python", "rust", "c++", "cuda", "triton", "java", "julia", "transformer", "pytorch", "linux", "git"}


@dataclass
class NamedEntity:
    text: str
    entity_type: str
    start_char: int = 0
    end_char: int = 0

    def __getitem__(self, item):
        if item in {"text", "entity"}:
            return self.text
        if item in {"entity_type", "label"}:
            return self.entity_type
        if item == "start_char":
            return self.start_char
        if item == "end_char":
            return self.end_char
        raise KeyError(item)


class EnglishNamedEntityRecognizer:
    """
    Rule-based and gazetteer-backed Named Entity Recognition engine.
    """

    def recognize(self, text: str) -> List[NamedEntity]:
        entities: List[NamedEntity] = []
        words = text.split()
        n = len(words)

        i = 0
        while i < n:
            raw_word = words[i]
            clean_word = re.sub(r"[^\w.-]", "", raw_word)
            lower = clean_word.lower()

            # 1. PERSON: Title prefix match or Capitalized full name
            if lower in TITLE_PREFIXES and i + 1 < n:
                name_parts = [clean_word]
                j = i + 1
                while j < n and words[j][0].isupper():
                    name_parts.append(re.sub(r"[^\w]", "", words[j]))
                    j += 1
                full_name = " ".join(name_parts)
                start_idx = text.find(full_name)
                entities.append(NamedEntity(text=full_name, entity_type="PERSON", start_char=start_idx, end_char=start_idx + len(full_name)))
                i = j
                continue

            # Person name detection by capitalization pair (e.g., "Alan Turing", "Marie Curie")
            if clean_word and clean_word[0].isupper() and lower not in {"the", "a", "in", "on", "at", "to", "for"}:
                if i + 1 < n and words[i + 1] and words[i + 1][0].isupper():
                    next_clean = re.sub(r"[^\w]", "", words[i + 1])
                    full_name = f"{clean_word} {next_clean}"
                    start_idx = text.find(full_name)
                    entities.append(NamedEntity(text=full_name, entity_type="PERSON", start_char=start_idx, end_char=start_idx + len(full_name)))
                    i += 2
                    continue

            # 2. ORG: Suffix match
            if lower in ORG_SUFFIXES and i > 0:
                org_parts = [re.sub(r"[^\w]", "", words[i - 1]), clean_word]
                full_org = " ".join(org_parts)
                start_idx = text.find(full_org)
                entities.append(NamedEntity(text=full_org, entity_type="ORG", start_char=start_idx, end_char=start_idx + len(full_org)))
                i += 1
                continue

            # 3. GPE/LOC: Gazetteer lookup
            if lower in LOCATIONS:
                start_idx = text.find(clean_word)
                entities.append(NamedEntity(text=clean_word, entity_type="GPE", start_char=start_idx, end_char=start_idx + len(clean_word)))
                i += 1
                continue

            # 4. TECH: Technical terms
            if lower in TECH_TERMS:
                start_idx = text.find(clean_word)
                entities.append(NamedEntity(text=clean_word, entity_type="TECH", start_char=start_idx, end_char=start_idx + len(clean_word)))
                i += 1
                continue

            # 5. DATE: Numeric year
            if re.match(r"^(19|20)\d{2}$", clean_word):
                start_idx = text.find(clean_word)
                entities.append(NamedEntity(text=clean_word, entity_type="DATE", start_char=start_idx, end_char=start_idx + len(clean_word)))
                i += 1
                continue

            i += 1

        return entities

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        named = self.recognize(text)
        return [
            {
                "entity": e.text,
                "label": e.entity_type,
                "start_char": e.start_char,
                "end_char": e.end_char,
            }
            for e in named
        ]
