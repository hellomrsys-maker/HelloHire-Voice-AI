"""
parsing.py - Japanese Bunsetsu Chunking and Head-Final Dependency Parsing (Kakariuke).
Models Japanese head-final projective syntax where each bunsetsu depends on a subsequent head.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

from .tokenization import JapaneseTokenizer, JapaneseToken
from .pos_tagging import JapanesePOSTagger, JapaneseTaggedToken


@dataclass
class Bunsetsu:
    index: int
    text: str
    content_word: str
    functional_word: Optional[str]
    head_index: int  # -1 if ROOT (usually sentence-final)
    relation: str    # "root", "ga_case", "o_case", "ni_case", "wa_topic", "modifier", "adv"
    tokens: List[JapaneseTaggedToken] = field(default_factory=list)

    @property
    def id(self) -> int:
        return self.index

    @property
    def head_id(self) -> int:
        return self.head_index

    @property
    def content(self) -> str:
        return self.text


@dataclass
class JapaneseParseTree:
    raw_sentence: str
    bunsetsu_list: List[Bunsetsu]
    root_index: int

    def __str__(self) -> str:
        lines = []
        for b in self.bunsetsu_list:
            head_str = f"-> {b.head_index}" if b.head_index != -1 else "ROOT"
            lines.append(f"[{b.index}] {b.text} ({b.relation}) {head_str}")
        return "\n".join(lines)


class JapaneseParser:
    """
    Syntactic dependency parser for Japanese Bunsetsu structures.
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()
        self.tagger = JapanesePOSTagger()

    def chunk_bunsetsu(self, tagged_tokens: List[JapaneseTaggedToken]) -> List[Bunsetsu]:
        """
        Groups tagged tokens into Bunsetsu units (Content word + following functional particles/auxiliaries).
        """
        bunsetsu_units: List[Bunsetsu] = []
        cur_tokens: List[JapaneseTaggedToken] = []
        b_idx = 0

        for tok in tagged_tokens:
            is_content = tok.pos_tag in {"名詞", "動詞", "形容詞", "形状詞", "代名詞", "固有名詞", "副詞", "連体詞", "接続詞"}

            # If current token is a new content word and we already have accumulated tokens, flush previous unit
            if is_content and cur_tokens and any(t.pos_tag in {"名詞", "動詞", "形容詞", "代名詞"} for t in cur_tokens):
                b_text = "".join(t.token.text for t in cur_tokens)
                c_word = cur_tokens[0].token.text
                f_words = [t.token.text for t in cur_tokens[1:] if t.pos_tag in {"助詞", "助動詞"}]
                f_word = "".join(f_words) if f_words else None

                bunsetsu_units.append(
                    Bunsetsu(
                        index=b_idx,
                        text=b_text,
                        content_word=c_word,
                        functional_word=f_word,
                        head_index=-1,
                        relation="dep",
                        tokens=cur_tokens[:],
                    )
                )
                b_idx += 1
                cur_tokens = [tok]
            else:
                cur_tokens.append(tok)

        if cur_tokens:
            b_text = "".join(t.token.text for t in cur_tokens)
            c_word = cur_tokens[0].token.text
            f_words = [t.token.text for t in cur_tokens[1:] if t.pos_tag in {"助詞", "助動詞"}]
            f_word = "".join(f_words) if f_words else None
            bunsetsu_units.append(
                Bunsetsu(
                    index=b_idx,
                    text=b_text,
                    content_word=c_word,
                    functional_word=f_word,
                    head_index=-1,
                    relation="dep",
                    tokens=cur_tokens[:],
                )
            )

        return bunsetsu_units

    def parse(self, text: str) -> JapaneseParseTree:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag_tokens(tokens)
        bunsetsus = self.chunk_bunsetsu(tagged)

        if not bunsetsus:
            return JapaneseParseTree(raw_sentence=text, bunsetsu_list=[], root_index=-1)

        # In Japanese, the final bunsetsu is almost invariably the sentence ROOT predicate
        root_idx = len(bunsetsus) - 1
        bunsetsus[root_idx].head_index = -1
        bunsetsus[root_idx].relation = "root"

        # Assign head and case relations for non-final bunsetsu
        for i in range(len(bunsetsus) - 1):
            b = bunsetsus[i]
            fw = b.functional_word or ""

            # Default head is the final main predicate
            b.head_index = root_idx

            if "は" in fw:
                b.relation = "wa_topic"
            elif "が" in fw:
                b.relation = "ga_case (subject)"
            elif "を" in fw:
                b.relation = "o_case (object)"
            elif "に" in fw:
                b.relation = "ni_case (indirect/locative)"
            elif "で" in fw:
                b.relation = "de_case (instrument/location)"
            elif "の" in fw:
                # Modifies the immediately following bunsetsu (Noun-no-Noun)
                b.head_index = i + 1
                b.relation = "no_genitive (modifies noun)"
            elif "と" in fw:
                b.relation = "to_case (comitative/quotative)"
            else:
                b.relation = "modifier"

        return JapaneseParseTree(
            raw_sentence=text,
            bunsetsu_list=bunsetsus,
            root_index=root_idx,
        )

    def parse_bunsetsu_dependencies(self, text: str) -> JapaneseParseTree:
        return self.parse(text)
