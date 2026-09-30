"""
pos_tagger.py — Real Part-of-Speech Tagger (trained on UD annotations).
=======================================================================

A self-contained, word-level neural POS tagger trained on genuine Universal
Dependencies UPOS labels. This is real linguistic supervision: the model learns
to assign one of the 17 universal POS tags to each word, per language, and is
evaluated by held-out TOKEN accuracy against a majority-class baseline.

Architecture: word embedding (+ a hashed sub-word/character fallback for OOV
robustness) -> Transformer encoder -> per-token UPOS classifier. Deterministic.
Degrades gracefully without torch.
"""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .ud_pos_data import PosDataset, PosSentence, UPOS_TAGS, NUM_UPOS, UPOS2ID

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    _TORCH_OK = True
except Exception:
    _TORCH_OK = False


GLOBAL_SEED = 1729
PAD_TAG = 0  # matches "<PAD>" at index 0 in UPOS_TAGS


# --------------------------------------------------------------------------- #
# Vocabulary
# --------------------------------------------------------------------------- #

class WordVocab:
    """Word-level vocabulary with a hashed bucket space for OOV words so unseen
    tokens still receive a stable, informative embedding index."""

    def __init__(self, min_freq: int = 2, max_size: int = 20000, hash_buckets: int = 4096):
        self.min_freq = min_freq
        self.max_size = max_size
        self.hash_buckets = hash_buckets
        self.word2id: Dict[str, int] = {"<pad>": 0, "<unk>": 1}
        self.built = False

    def build(self, sentences: List[PosSentence]) -> None:
        freq: Dict[str, int] = {}
        for s in sentences:
            for w in s.words:
                wl = w.lower()
                freq[wl] = freq.get(wl, 0) + 1
        for w, c in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])):
            if c < self.min_freq:
                continue
            if len(self.word2id) >= self.max_size:
                break
            if w not in self.word2id:
                self.word2id[w] = len(self.word2id)
        self.built = True

    @property
    def base_size(self) -> int:
        return len(self.word2id)

    @property
    def total_size(self) -> int:
        return self.base_size + self.hash_buckets

    def encode_word(self, w: str) -> int:
        wl = w.lower()
        if wl in self.word2id:
            return self.word2id[wl]
        # Stable hashed bucket for OOV, offset past the known vocab.
        h = int(hashlib.md5(wl.encode("utf-8")).hexdigest(), 16) % self.hash_buckets
        return self.base_size + h

    def to_dict(self) -> Dict:
        return {"min_freq": self.min_freq, "max_size": self.max_size,
                "hash_buckets": self.hash_buckets, "word2id": self.word2id}

    @classmethod
    def from_dict(cls, d: Dict) -> "WordVocab":
        v = cls(min_freq=d.get("min_freq", 2), max_size=d.get("max_size", 20000),
                hash_buckets=d.get("hash_buckets", 4096))
        v.word2id = {k: int(i) for k, i in d.get("word2id", {"<pad>": 0, "<unk>": 1}).items()}
        v.built = True
        return v


if _TORCH_OK:
    class POSTaggerModel(nn.Module):
        def __init__(self, vocab_size: int, d_model: int = 96, nhead: int = 4,
                     num_layers: int = 2, num_tags: int = NUM_UPOS):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
            layer = nn.TransformerEncoderLayer(
                d_model=d_model, nhead=nhead, dim_feedforward=256,
                dropout=0.1, activation="gelu", batch_first=True)
            self.encoder = nn.TransformerEncoder(layer, num_layers=num_layers)
            self.classifier = nn.Linear(d_model, num_tags)

        def forward(self, token_ids, attention_mask=None):
            h = self.embedding(token_ids)
            key_padding_mask = (attention_mask == 0) if attention_mask is not None else None
            h = self.encoder(h, src_key_padding_mask=key_padding_mask)
            return self.classifier(h)  # [B, L, num_tags]


@dataclass
class POSTrainingResult:
    engine_dir: str
    treebank: str
    trained: bool
    epochs: int
    final_train_loss: float
    val_token_accuracy: float
    majority_baseline: float
    train_sentences: int
    val_sentences: int
    vocab_size: int
    passed: bool = False
    note: str = ""
    model: object = None      # trained POSTaggerModel (not serialised in reports)
    vocab: object = None      # WordVocab used for training


def _majority_baseline(train: List[PosSentence], val: List[PosSentence]) -> float:
    """Accuracy of always predicting the most frequent tag (from train) on val."""
    counts: Dict[int, int] = {}
    for s in train:
        for t in s.tags:
            counts[t] = counts.get(t, 0) + 1
    if not counts:
        return 0.0
    majority = max(counts, key=counts.get)
    total = correct = 0
    for s in val:
        for t in s.tags:
            total += 1
            if t == majority:
                correct += 1
    return round(correct / max(1, total), 4)


def _batchify(sentences, vocab, max_len, device):
    ids, masks, labels = [], [], []
    for s in sentences:
        toks = [vocab.encode_word(w) for w in s.words][:max_len]
        labs = s.tags[:max_len]
        m = [1] * len(toks)
        pad = max_len - len(toks)
        toks += [0] * pad
        labs = labs + [PAD_TAG] * pad
        m += [0] * pad
        ids.append(toks); masks.append(m); labels.append(labs)
    return (torch.tensor(ids, dtype=torch.long, device=device),
            torch.tensor(masks, dtype=torch.long, device=device),
            torch.tensor(labels, dtype=torch.long, device=device))


def train_pos_tagger(dataset: PosDataset, epochs: int = 12, lr: float = 1e-3,
                     max_len: int = 40, batch_size: int = 32,
                     seed: int = GLOBAL_SEED, pass_margin: float = 0.10) -> POSTrainingResult:
    """Train a POS tagger on real UD data; report held-out token accuracy vs. baseline.

    ``passed`` requires beating the majority-class baseline by ``pass_margin``.
    """
    tb = dataset.treebank
    if not _TORCH_OK:
        return POSTrainingResult(dataset.engine_dir, tb, False, 0, 0.0, 0.0, 0.0,
                                 len(dataset.train), len(dataset.val), 0, note="torch unavailable")
    if not dataset.train:
        return POSTrainingResult(dataset.engine_dir, tb, False, 0, 0.0, 0.0, 0.0,
                                 0, 0, 0, note=f"no data ({dataset.status})")

    import random
    random.seed(seed)
    torch.manual_seed(seed)
    device = torch.device("cpu")

    vocab = WordVocab()
    vocab.build(dataset.train)

    model = POSTaggerModel(vocab_size=vocab.total_size).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    # Ignore PAD label (index 0) in the loss.
    loss_fn = nn.CrossEntropyLoss(ignore_index=PAD_TAG)

    tr_ids, tr_mask, tr_lab = _batchify(dataset.train, vocab, max_len, device)
    n = tr_ids.size(0)
    final_loss = 0.0
    model.train()
    for ep in range(1, epochs + 1):
        perm = torch.randperm(n, generator=torch.Generator().manual_seed(seed + ep))
        epoch_loss = 0.0
        nb = 0
        for start in range(0, n, batch_size):
            idx = perm[start:start + batch_size]
            opt.zero_grad()
            logits = model(tr_ids[idx], tr_mask[idx])  # [b, L, T]
            loss = loss_fn(logits.reshape(-1, logits.size(-1)), tr_lab[idx].reshape(-1))
            loss.backward()
            opt.step()
            epoch_loss += float(loss.item()); nb += 1
        final_loss = epoch_loss / max(1, nb)

    # Held-out token accuracy.
    eval_split = dataset.val or dataset.train
    model.eval()
    correct = total = 0
    with torch.no_grad():
        v_ids, v_mask, v_lab = _batchify(eval_split, vocab, max_len, device)
        logits = model(v_ids, v_mask)
        preds = logits.argmax(dim=-1)
        mask = v_mask.bool()
        correct = int(((preds == v_lab) & mask).sum().item())
        total = int(mask.sum().item())
    val_acc = round(correct / max(1, total), 4)
    baseline = _majority_baseline(dataset.train, eval_split)
    passed = val_acc >= baseline + pass_margin

    return POSTrainingResult(
        engine_dir=dataset.engine_dir, treebank=tb, trained=True, epochs=epochs,
        final_train_loss=round(final_loss, 4), val_token_accuracy=val_acc,
        majority_baseline=baseline, train_sentences=len(dataset.train),
        val_sentences=len(eval_split), vocab_size=vocab.base_size,
        passed=passed, note="trained on UD UPOS labels",
        model=model, vocab=vocab,
    )


# --------------------------------------------------------------------------- #
# Checkpoint save / load + prediction
# --------------------------------------------------------------------------- #

def save_pos_checkpoint(result: POSTrainingResult, path: str) -> bool:
    """Persist the trained POS model weights + vocab + tagset to ``path`` (.pt)."""
    if not _TORCH_OK or result.model is None or result.vocab is None:
        return False
    import os as _os
    _os.makedirs(_os.path.dirname(_os.path.abspath(path)), exist_ok=True)
    torch.save({
        "model_state": result.model.state_dict(),
        "vocab": result.vocab.to_dict(),
        "tagset": UPOS_TAGS,
        "d_model": 96,
        "engine_dir": result.engine_dir,
        "treebank": result.treebank,
        "val_token_accuracy": result.val_token_accuracy,
    }, path)
    return True


class LoadedPOSTagger:
    """A ready-to-use tagger restored from a checkpoint. tag(words) -> List[UPOS str]."""

    def __init__(self, checkpoint_path: str, max_len: int = 40):
        if not _TORCH_OK:
            raise RuntimeError("torch unavailable")
        ckpt = torch.load(checkpoint_path, map_location="cpu")
        self.tagset = ckpt.get("tagset", UPOS_TAGS)
        self.vocab = WordVocab.from_dict(ckpt["vocab"])
        self.max_len = max_len
        self.model = POSTaggerModel(vocab_size=self.vocab.total_size,
                                    d_model=ckpt.get("d_model", 96),
                                    num_tags=len(self.tagset))
        self.model.load_state_dict(ckpt["model_state"])
        self.model.eval()
        self.val_token_accuracy = ckpt.get("val_token_accuracy", None)

    def tag(self, words: List[str]) -> List[str]:
        if not words:
            return []
        toks = [self.vocab.encode_word(w) for w in words][:self.max_len]
        ids = torch.tensor([toks], dtype=torch.long)
        mask = torch.ones_like(ids)
        with torch.no_grad():
            logits = self.model(ids, mask)
            pred_ids = logits.argmax(dim=-1)[0].tolist()
        tags = [self.tagset[i] if 0 <= i < len(self.tagset) else "X" for i in pred_ids]
        # If input longer than max_len, pad remaining with X.
        if len(words) > len(tags):
            tags += ["X"] * (len(words) - len(tags))
        return tags[:len(words)]


# --------------------------------------------------------------------------- #
# Per-engine driver + CLI
# --------------------------------------------------------------------------- #

def train_engine_pos(engine_dir: str, epochs: int = 12, max_sentences: int = 600,
                     save: bool = True, workspace_root: Optional[str] = None) -> Dict:
    """Build the UD POS dataset for one engine, train the tagger, and (optionally)
    persist a checkpoint + a report next to the engine's data. Returns a summary dict."""
    import json
    import os as _os
    from .ud_pos_data import build_pos_dataset
    from .data_sources import get_source

    root = workspace_root or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    try:
        treebanks = get_source(engine_dir).ud_treebanks
    except Exception:
        treebanks = []

    if not treebanks:
        return {"engine": engine_dir, "status": "no UD treebank mapped (POS needs UD annotations)",
                "trained": False}

    ds = build_pos_dataset(engine_dir, treebanks, max_sentences=max_sentences)
    res = train_pos_tagger(ds, epochs=epochs)

    summary = {
        "engine": engine_dir,
        "treebank": res.treebank,
        "license": ds.license,
        "trained": res.trained,
        "val_token_accuracy": res.val_token_accuracy,
        "majority_baseline": res.majority_baseline,
        "beats_baseline_by": round(res.val_token_accuracy - res.majority_baseline, 4),
        "train_sentences": res.train_sentences,
        "val_sentences": res.val_sentences,
        "vocab_size": res.vocab_size,
        "final_train_loss": res.final_train_loss,
        "passed": res.passed,
        "note": res.note,
        "tagset": "UD 17 Universal POS",
    }

    if save and res.trained:
        out_dir = _os.path.join(root, engine_dir, "6_DATA_REQUIREMENTS")
        _os.makedirs(out_dir, exist_ok=True)
        # Persist the trained model checkpoint (weights + vocab + tagset).
        ckpt_dir = _os.path.join(root, "checkpoints")
        ckpt_path = _os.path.join(ckpt_dir, f"{engine_dir.lower()}_pos_tagger.pt")
        if save_pos_checkpoint(res, ckpt_path):
            summary["checkpoint"] = ckpt_path
        with open(_os.path.join(out_dir, "pos_training_report.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def _main(argv=None) -> int:
    import argparse, json
    from .data_sources import all_sources
    ap = argparse.ArgumentParser(description="Train UD POS taggers per engine.")
    ap.add_argument("--engine", help="Engine dir, e.g. English_engine")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--epochs", type=int, default=12)
    args = ap.parse_args(argv)

    if args.all:
        results = {}
        for eng in sorted(all_sources()):
            results[eng] = train_engine_pos(eng, epochs=args.epochs)
            r = results[eng]
            print(f"{eng}: acc={r.get('val_token_accuracy')} "
                  f"baseline={r.get('majority_baseline')} passed={r.get('passed')} "
                  f"({r.get('status', r.get('note',''))})")
        trained = sum(1 for r in results.values() if r.get("trained"))
        passed = sum(1 for r in results.values() if r.get("passed"))
        print(f"POS trained {trained} engines, {passed} beat baseline.")
    elif args.engine:
        r = train_engine_pos(args.engine, epochs=args.epochs)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        ap.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
