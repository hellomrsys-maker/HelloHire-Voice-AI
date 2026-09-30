"""Russian Dependency Parsing Skill.

Analyzes syntactic relations in Russian sentences:
Subject (nsubj), Root Verb (root), Direct Object (obj),
Prepositional Oblique (obl), and Adjectival Modifier (amod).
"""

from typing import List, Dict, Any
from .tokenization import RussianTokenizer
from .pos_tagging import RussianPOSTagger


class RussianDependencyParser:
    def __init__(self, tokenizer: RussianTokenizer = None, pos_tagger: RussianPOSTagger = None):
        self.tokenizer = tokenizer or RussianTokenizer()
        self.pos_tagger = pos_tagger or RussianPOSTagger()

    def parse(self, sentence: str) -> Dict[str, Any]:
        """Parses a Russian sentence into dependency relations."""
        tokens = self.tokenizer.tokenize(sentence)
        tagged = self.pos_tagger.tag(tokens)

        nodes = []
        root_idx = -1
        subject_idx = -1
        object_idx = -1

        for i, item in enumerate(tagged):
            nodes.append({
                "id": i,
                "token": item["token"],
                "pos": item["pos"],
                "head": -1,
                "deprel": "dep"
            })

        # Step 1: Find root (first finite verb)
        for i, node in enumerate(nodes):
            if node["pos"] == "VERB":
                root_idx = i
                node["deprel"] = "root"
                node["head"] = -1
                break

        # Fallback if no verb found
        if root_idx == -1 and len(nodes) > 0:
            root_idx = 0
            nodes[0]["deprel"] = "root"
            nodes[0]["head"] = -1

        # Step 2: Assign relations relative to root
        for i, node in enumerate(nodes):
            if i == root_idx:
                continue

            # Check for prepositional oblique phrase (ADP + NOUN)
            if node["pos"] == "ADP" and i + 1 < len(nodes):
                node["head"] = root_idx
                node["deprel"] = "case"
                nodes[i + 1]["head"] = root_idx
                nodes[i + 1]["deprel"] = "obl"
                continue

            if node["deprel"] != "dep":
                continue

            if node["pos"] in ("NOUN", "PRON"):
                if subject_idx == -1 and i < root_idx:
                    subject_idx = i
                    node["head"] = root_idx
                    node["deprel"] = "nsubj"
                elif object_idx == -1 and i > root_idx:
                    object_idx = i
                    node["head"] = root_idx
                    node["deprel"] = "obj"
                else:
                    node["head"] = root_idx
                    node["deprel"] = "obl"

            elif node["pos"] == "ADJ":
                # Lookahead for following noun
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
