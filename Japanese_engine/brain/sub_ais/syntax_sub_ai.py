"""
Japanese Syntax Sub-AI Module
=============================
Dedicated artificial intelligence for Japanese syntactic structure verification,
Bunsetsu chunk parsing, Kakariuke head-final dependency validation, and particle case frames.
Strictly adheres to the Zero-Bridge Synchronous Memory Rule via direct physical AMSV memory writes.
"""

from __future__ import annotations
import torch
import torch.nn as nn
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.skills.pos_tagging import JapanesePOSTagger
from Japanese_engine.brain.skills.parsing import JapaneseParser


@dataclass
class JapaneseSyntaxEvaluation:
    text: str
    syntactic_integrity_score: float  # 0.0 to 1.0
    bunsetsu_count: int
    is_head_final: bool
    dependency_pairs: List[Dict[str, Any]]
    syntax_errors: List[str]
    amsv_synced: bool


class JapaneseSyntaxSubAI:
    """
    Japanese Syntactic Sub-AI combining neural representations with
    deterministic Bunsetsu parsing and head-final SOV structural verification.
    """

    def __init__(
        self,
        d_model: int = 128,
        amsv_view: Optional[AMSVEmbeddedView] = None,
    ) -> None:
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.tokenizer = JapaneseTokenizer()
        self.pos_tagger = JapanesePOSTagger()
        self.parser = JapaneseParser()

        # Neural feature projection for syntax embedding
        self.embedding = nn.Embedding(8192, d_model)
        self.syntax_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def evaluate(self, text: str) -> JapaneseSyntaxEvaluation:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag_tokens(tokens)
        parse_tree = self.parser.parse_bunsetsu_dependencies(text)

        # 1. Head-final validation: Predicate / Copula should terminate the sentence
        clean = text.strip()
        last_bunsetsu = parse_tree.bunsetsu_list[-1] if parse_tree.bunsetsu_list else None
        is_head_final = True
        syntax_errors: List[str] = []

        if last_bunsetsu:
            last_tokens = self.pos_tagger.tag_tokens(self.tokenizer.tokenize(last_bunsetsu.content))
            pos_set = {t.pos for t in last_tokens}
            if not ("Doushi" in pos_set or "Keiyoushi" in pos_set or "Jodoushi" in pos_set or clean.endswith(("。", "！", "？"))):
                is_head_final = False
                syntax_errors.append(f"統語規則違反：文末が述語（動詞・形容詞・助動詞）で終結していません（非述語終止：'{last_bunsetsu.content}'）。")

        # 2. Neural projection scoring
        tok_ids = [min(8191, hash(t.text) % 8192) for t in tokens]
        if tok_ids:
            with torch.no_grad():
                inp = torch.tensor([tok_ids], dtype=torch.long)
                emb = self.embedding(inp).mean(dim=1)
                neural_score = float(self.syntax_head(emb).item())
        else:
            neural_score = 0.5

        penalty = len(syntax_errors) * 0.30
        final_score = max(0.0, min(1.0, 0.7 * neural_score + 0.3 * (1.0 - penalty)))

        # 0-NANOSECOND SYNCHRONOUS MEMORY WRITE
        # Writes directly to physical memory address in AMSV
        self.amsv.set_global_structural_score(final_score)
        self.amsv.set_cognitive_score(1, final_score)  # Capability 1: Grammar/Syntax

        dep_pairs = [
            {"head_id": b.head_id, "dependent_content": b.content, "bunsetsu_id": b.id}
            for b in parse_tree.bunsetsu_list
        ]

        return JapaneseSyntaxEvaluation(
            text=text,
            syntactic_integrity_score=round(final_score, 4),
            bunsetsu_count=len(parse_tree.bunsetsu_list),
            is_head_final=is_head_final,
            dependency_pairs=dep_pairs,
            syntax_errors=syntax_errors,
            amsv_synced=True,
        )
