"""
training_data.py — Real Corpus Dataset Builder for Sub-AI Training.
===================================================================

Replaces synthetic training targets (torch.randn / torch.ones / constant 0.9) with
REAL labeled examples drawn from each engine's authentic corpora, plus programmatically
derived NEGATIVE examples so the models learn to DISCRIMINATE rather than to output a
constant.

Positive examples: sentences from ``<engine>/6_DATA_REQUIREMENTS/extracted_grammar_corpus.json``
(writing_corpus, email_corpus, listening_corpus, ...). These are well-formed and
labelled complete (1.0).

Negative examples (label 0.0) are derived deterministically from positives:
  * clause fragments (leading subordinate clause with no main clause),
  * truncated head fragments (first 2-3 words only),
  * terminal-punctuation removed (for the punctuation head),
  * subject-dropped / verb-dropped fragments.

Everything is seeded for reproducibility. Falls back to a compact authentic seed set
built from the language profile when a corpus is missing (non-English engines).
"""

from __future__ import annotations
import json
import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOBAL_SEED = 1729

# Corpus key -> sub-AI domain.
CORPUS_KEYS = {
    "writing": "writing_corpus",
    "email": "email_corpus",
    "listening": "listening_corpus",
    "pronunciation": "pronunciation_corpus",
    "reviewing": "reviewing_corpus",
    "book_writing": "book_writing_corpus",
}

_SUBORDINATORS = ["because", "although", "while", "since", "unless", "whereas", "if", "when"]


@dataclass
class LabeledExample:
    text: str
    completeness: float   # 1.0 complete, 0.0 fragment
    has_terminal: float   # 1.0 has terminal punctuation, 0.0 missing


@dataclass
class SubAIDataset:
    domain: str
    train: List[LabeledExample] = field(default_factory=list)
    val: List[LabeledExample] = field(default_factory=list)

    @property
    def train_texts(self) -> List[str]:
        return [e.text for e in self.train]

    @property
    def val_texts(self) -> List[str]:
        return [e.text for e in self.val]


def set_global_seed(seed: int = GLOBAL_SEED) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass
    try:
        import torch
        torch.manual_seed(seed)
    except Exception:
        pass


def _load_corpus(engine_dir: str, workspace_root: Optional[str] = None) -> Dict[str, list]:
    root = workspace_root or WORKSPACE_ROOT
    path = os.path.join(root, engine_dir, "6_DATA_REQUIREMENTS", "extracted_grammar_corpus.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _extract_text(row) -> Optional[str]:
    """Handle all corpus row shapes across engines:
    English:  [sentence, completeness, x, y]
    Others:   {"text": sentence, "is_valid": true, ...}
    Plain:    "sentence"
    """
    if isinstance(row, str):
        return row
    if isinstance(row, (list, tuple)) and row:
        return row[0] if isinstance(row[0], str) else None
    if isinstance(row, dict):
        for key in ("text", "sentence", "utterance", "content"):
            v = row.get(key)
            if isinstance(v, str):
                return v
    return None


def _positive_sentences(corpus: Dict[str, list], corpus_key: str, limit: int = 800) -> List[str]:
    rows = corpus.get(corpus_key, []) or []
    # Some engines may only populate writing_corpus; if the requested key is empty,
    # fall back to writing_corpus so every domain still gets real data.
    if not rows and corpus_key != "writing_corpus":
        rows = corpus.get("writing_corpus", []) or []
    out: List[str] = []
    for row in rows:
        text = _extract_text(row)
        if isinstance(text, str):
            t = text.strip()
            if len(t.split()) >= 3:
                out.append(t)
        if len(out) >= limit:
            break
    return out


def _make_negatives(positives: List[str], terminators: Tuple[str, ...], rng: random.Random,
                    ratio: float = 0.6) -> List[LabeledExample]:
    """Derive fragment / punctuation-broken negatives from complete positives."""
    negatives: List[LabeledExample] = []
    n_neg = int(len(positives) * ratio)
    pool = positives[:]
    rng.shuffle(pool)
    for i, sent in enumerate(pool[:n_neg]):
        words = sent.split()
        mode = i % 4
        if mode == 0 and len(words) >= 4:
            # Leading subordinate clause fragment (no main clause).
            frag = f"{rng.choice(_SUBORDINATORS)} {' '.join(words[:max(2, len(words)//2)])}"
            negatives.append(LabeledExample(frag, completeness=0.0, has_terminal=0.0))
        elif mode == 1 and len(words) >= 3:
            # Head fragment: first 2-3 words only, no verb/predicate closure.
            frag = " ".join(words[:rng.choice([2, 3])])
            negatives.append(LabeledExample(frag, completeness=0.0, has_terminal=0.0))
        elif mode == 2:
            # Punctuation removed but otherwise complete -> completeness 1.0, terminal 0.0.
            stripped = sent
            for t in terminators:
                stripped = stripped.rstrip(t).rstrip()
            negatives.append(LabeledExample(stripped, completeness=1.0, has_terminal=0.0))
        else:
            # Drop the subject (first word) -> dangling predicate fragment.
            frag = " ".join(words[1:]) if len(words) > 2 else words[-1]
            negatives.append(LabeledExample(frag, completeness=0.0, has_terminal=0.0))
    return negatives


def _has_terminal(text: str, terminators: Tuple[str, ...]) -> float:
    return 1.0 if any(text.strip().endswith(t) for t in terminators) else 0.0


def build_subai_dataset(
    engine_dir: str,
    domain: str,
    terminators: Tuple[str, ...] = (".", "!", "?"),
    val_fraction: float = 0.2,
    seed: int = GLOBAL_SEED,
    workspace_root: Optional[str] = None,
    fallback_positives: Optional[List[str]] = None,
    max_positives: int = 300,
) -> SubAIDataset:
    """Build a labeled train/val dataset for one sub-AI domain from real corpus data.

    ``max_positives`` caps the number of positive sentences so CPU training stays
    fast and reproducible; negatives are derived from that capped set.
    """
    rng = random.Random(seed)
    corpus = _load_corpus(engine_dir, workspace_root)
    corpus_key = CORPUS_KEYS.get(domain, "writing_corpus")
    positives_text = _positive_sentences(corpus, corpus_key, limit=max_positives)

    if not positives_text and fallback_positives:
        positives_text = [s for s in fallback_positives if len(s.split()) >= 2]

    positives_text = positives_text[:max_positives]

    pos_examples = [LabeledExample(t, completeness=1.0, has_terminal=_has_terminal(t, terminators))
                    for t in positives_text]
    neg_examples = _make_negatives(positives_text, terminators, rng)

    all_examples = pos_examples + neg_examples
    rng.shuffle(all_examples)

    if not all_examples:
        return SubAIDataset(domain=domain)

    n_val = max(1, int(len(all_examples) * val_fraction)) if len(all_examples) > 4 else 0
    val = all_examples[:n_val]
    train = all_examples[n_val:] or all_examples
    return SubAIDataset(domain=domain, train=train, val=val)


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #

def binary_metrics(preds: List[float], labels: List[float], threshold: float = 0.5) -> Dict[str, float]:
    """Accuracy / precision / recall / F1 for a binary head."""
    if not preds:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "n": 0}
    tp = fp = tn = fn = 0
    for p, y in zip(preds, labels):
        pred = 1 if p >= threshold else 0
        truth = 1 if y >= 0.5 else 0
        if pred == 1 and truth == 1: tp += 1
        elif pred == 1 and truth == 0: fp += 1
        elif pred == 0 and truth == 0: tn += 1
        else: fn += 1
    acc = (tp + tn) / max(1, len(preds))
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    f1 = 2 * prec * rec / max(1e-9, prec + rec)
    return {"accuracy": round(acc, 4), "precision": round(prec, 4),
            "recall": round(rec, 4), "f1": round(f1, 4), "n": len(preds)}
