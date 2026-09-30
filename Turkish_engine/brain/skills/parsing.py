"""Turkish Dependency Parsing Skill.

Analyzes head-final SOV syntactic relations in Turkish clauses:
Subject (nsubj), Root Verb (root), Direct Object (obj),
Postpositional Oblique (obl), and Adjectival Modifier (amod).
"""

from typing import List, Dict, Any
from .tokenization import TurkishTokenizer
from .pos_tagging import TurkishPOSTagger


class TurkishDependencyParser:
    def __init__(
        self,
        tokenizer: TurkishTokenizer = None,
        pos_tagger: TurkishPOSTagger = None
    ):
        self.tokenizer = tokenizer or TurkishTokenizer()
        self.pos_tagger = pos_tagger or TurkishPOSTagger()

    def parse(self, sentence: str) -> Dict[str, Any]:
        """Parses a Turkish sentence into dependency relations."""
        tokens = self.tokenizer.tokenize(sentence)
        tagged = self.pos_tagger.tag(tokens)

        nodes = []
        for i, item in enumerate(tagged):
            nodes.append({
                "id": i,
                "token": item["token"],
                "pos": item["pos"],
                "head": -1,
                "deprel": "dep"
            })

        # Step 1: Find root (head-final: look for last finite VERB)
        root_idx = -1
        for i in reversed(range(len(nodes))):
            if nodes[i]["pos"] == "VERB":
                root_idx = i
                nodes[i]["deprel"] = "root"
                nodes[i]["head"] = -1
                break

        # Fallback if no verb identified
        if root_idx == -1 and len(nodes) > 0:
            root_idx = len(nodes) - 1
            nodes[root_idx]["deprel"] = "root"
            nodes[root_idx]["head"] = -1

        # Step 2: Assign relations relative to root
        subj_idx = -1
        obj_idx = -1

        for i, node in enumerate(nodes):
            if i == root_idx:
                continue

            # Postposition phrase: NOUN + ADP (head is ADP, modifying root)
            if node["pos"] == "ADP":
                node["head"] = root_idx
                node["deprel"] = "case"
                if i > 0 and nodes[i - 1]["pos"] in ("NOUN", "PRON"):
                    nodes[i - 1]["head"] = root_idx
                    nodes[i - 1]["deprel"] = "obl"
                continue

            if node["deprel"] != "dep":
                continue

            if node["pos"] in ("NOUN", "PRON"):
                if subj_idx == -1 and i < root_idx:
                    subj_idx = i
                    node["head"] = root_idx
                    node["deprel"] = "nsubj"
                elif i < root_idx:
                    # If immediately preceding verb, likely direct object
                    if i == root_idx - 1:
                        obj_idx = i
                        node["head"] = root_idx
                        node["deprel"] = "obj"
                    else:
                        node["head"] = root_idx
                        node["deprel"] = "obl"

            elif node["pos"] == "ADJ":
                if i + 1 < len(nodes) and nodes[i + 1]["pos"] == "NOUN":
                    node["head"] = i + 1
                    node["deprel"] = "amod"
                else:
                    node["head"] = root_idx
                    node["deprel"] = "amod"

            elif node["pos"] == "ADV":
                node["head"] = root_idx
                node["deprel"] = "advmod"

            elif node["pos"] == "PUNCT":
                node["head"] = root_idx
                node["deprel"] = "punct"

        return {
            "sentence": sentence,
            "root_index": root_idx,
            "nodes": nodes
        }
