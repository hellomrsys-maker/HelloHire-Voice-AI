"""
parsing.py - Constituency (X-Bar) and Dependency Parsing for English syntax.
Generates bracketed syntactic parse trees and Universal Dependencies relations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from .pos_tagging import EnglishPOSTagger, TaggedToken
from .tokenization import Token


@dataclass
class ParseTree:
    category: str = "S"
    bracketed: str = ""
    root: Optional[Any] = None

    def __str__(self) -> str:
        return self.bracketed


@dataclass
class DependencyTree:
    root: Optional[Dict[str, Any]] = None
    relations: List[Dict[str, Any]] = field(default_factory=list)


class EnglishParser:
    """
    Syntactic parser producing both dependency graphs and constituency bracketings.
    """

    def __init__(self):
        self.tagger = EnglishPOSTagger()

    def parse_dependencies(self, tokens_or_tagged: Union[List[str], List[Token], List[TaggedToken]]) -> DependencyTree:
        """
        Extracts dependency relations (head, relation, dependent).
        Relations: root, nsubj, obj, obl, det, amod, advmod, punct.
        """
        if not tokens_or_tagged:
            return DependencyTree()

        # Check if already tagged
        if isinstance(tokens_or_tagged[0], TaggedToken):
            tagged = tokens_or_tagged
        else:
            tagged = self.tagger.tag_tokens(tokens_or_tagged)

        deps = []
        root_idx = -1

        # Step 1: Find main finite verb (ROOT)
        for i, item in enumerate(tagged):
            tag = item.penn_tag
            if tag.startswith("VB") or tag == "MD":
                root_idx = i
                break
        if root_idx == -1 and len(tagged) > 0:
            root_idx = 0

        # Step 2: Assign heads and relations
        root_node = None
        for i, item in enumerate(tagged):
            word = item.token.text if isinstance(item.token, Token) else str(item.token)
            tag = item.penn_tag

            if i == root_idx:
                node = {
                    "id": i + 1,
                    "word": word,
                    "tag": tag,
                    "head": 0,
                    "relation": "root"
                }
                deps.append(node)
                root_node = node
            elif i < root_idx:
                if tag in {"NN", "NNS", "NNP", "PRP"}:
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": root_idx + 1, "relation": "nsubj"})
                elif tag == "DT":
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": i + 2 if i + 1 < len(tagged) else root_idx + 1, "relation": "det"})
                elif tag.startswith("JJ"):
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": i + 2 if i + 1 < len(tagged) else root_idx + 1, "relation": "amod"})
                elif tag.startswith("RB"):
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": root_idx + 1, "relation": "advmod"})
                else:
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": root_idx + 1, "relation": "dep"})
            else:
                if tag in {"NN", "NNS", "NNP", "PRP"}:
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": root_idx + 1, "relation": "obj"})
                elif tag == "IN":
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": root_idx + 1, "relation": "obl"})
                elif tag == "DT":
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": i + 2 if i + 1 < len(tagged) else root_idx + 1, "relation": "det"})
                elif tag.startswith("JJ"):
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": i + 2 if i + 1 < len(tagged) else root_idx + 1, "relation": "amod"})
                elif tag in {".", ","}:
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": root_idx + 1, "relation": "punct"})
                else:
                    deps.append({"id": i + 1, "word": word, "tag": tag, "head": root_idx + 1, "relation": "dep"})

        return DependencyTree(root=root_node, relations=deps)

    def generate_constituency_tree(self, tokens_or_tagged: Union[List[str], List[Token], List[TaggedToken]]) -> str:
        """
        Generates S-expression constituency bracketed tree (S (NP ...) (VP ...)).
        """
        if not tokens_or_tagged:
            return "(S)"

        if isinstance(tokens_or_tagged[0], TaggedToken):
            tagged = tokens_or_tagged
        else:
            tagged = self.tagger.tag_tokens(tokens_or_tagged)

        leaves = [
            f"({item.penn_tag} {item.token.text if isinstance(item.token, Token) else str(item.token)})"
            for item in tagged
        ]
        mid = max(1, len(leaves) // 2)
        np_part = " ".join(leaves[:mid])
        vp_part = " ".join(leaves[mid:])
        return f"(S (NP {np_part}) (VP {vp_part}))"

    def parse_constituency(self, tagged_tokens: List[TaggedToken]) -> ParseTree:
        bracketed = self.generate_constituency_tree(tagged_tokens)
        return ParseTree(category="S", bracketed=bracketed, root={"category": "S", "bracketed": bracketed})

    def to_bracketed_string(self, parse_tree: ParseTree) -> str:
        return parse_tree.bracketed

    def parse(self, sentence_text: str) -> Dict[str, Any]:
        """Full syntactic parse output."""
        tokens = sentence_text.strip().split()
        dep_tree = self.parse_dependencies(tokens)
        constituency = self.generate_constituency_tree(tokens)
        return {
            "sentence": sentence_text,
            "token_count": len(tokens),
            "dependencies": dep_tree.relations,
            "constituency_tree": constituency
        }
