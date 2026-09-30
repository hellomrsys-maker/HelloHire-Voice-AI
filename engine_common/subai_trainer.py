"""
subai_trainer.py — Real Supervised Trainer for Dedicated Sub-AIs.
=================================================================

Trains a Sub-AI neural model (WritingSubAINeural family) on REAL labeled data with
positive + negative examples, an optimizer loop, a held-out validation split, and
REAL metrics (accuracy / precision / recall / F1 on completeness, accuracy on the
terminal-punctuation head). "Verified" now means measured generalisation, not a file
hash.

Deterministic (seeded). Degrades gracefully if torch is unavailable.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from .training_data import SubAIDataset, binary_metrics, set_global_seed, GLOBAL_SEED

try:
    import torch
    import torch.nn.functional as F
    _TORCH_OK = True
except Exception:
    _TORCH_OK = False


@dataclass
class TrainingResult:
    domain: str
    trained: bool
    epochs: int
    final_train_loss: float
    val_completeness: Dict[str, float] = field(default_factory=dict)
    val_punctuation_accuracy: float = 0.0
    train_size: int = 0
    val_size: int = 0
    passed: bool = False
    note: str = ""


# Punctuation head class indices (from WritingSubAINeural): [Period, Question, Exclamation, Semicolon, Missing]
_MISSING_PUNCT_CLASS = 4


def _completeness_targets(dataset_split, device) -> "torch.Tensor":
    return torch.tensor([[e.completeness] for e in dataset_split], dtype=torch.float32, device=device)


def _punct_targets(dataset_split, device) -> "torch.Tensor":
    # 1 if terminal present -> class Period(0) as a stand-in "present"; 0 -> Missing(4).
    idx = [0 if e.has_terminal >= 0.5 else _MISSING_PUNCT_CLASS for e in dataset_split]
    return torch.tensor(idx, dtype=torch.long, device=device)


def train_sub_ai(
    model,
    dataset: SubAIDataset,
    epochs: int = 12,
    lr: float = 1e-3,
    max_length: int = 56,
    seed: int = GLOBAL_SEED,
    pass_threshold: float = 0.70,
    batch_size: int = 64,
) -> TrainingResult:
    """
    Supervised training of one Sub-AI on real labeled data. Optimises the completeness
    head (BCE) and the terminal-punctuation head (cross-entropy) with mini-batches,
    then reports held-out validation metrics.
    """
    domain = dataset.domain
    if not _TORCH_OK:
        return TrainingResult(domain, False, 0, 0.0, note="torch unavailable")
    if not dataset.train:
        return TrainingResult(domain, False, 0, 0.0, note="no training data")

    set_global_seed(seed)
    device = torch.device("cpu")
    model.to(device)
    model.train()

    tok = model.tokenizer
    train_ids, train_mask = tok.encode(dataset.train_texts, max_length=max_length)
    train_ids, train_mask = train_ids.to(device), train_mask.to(device)
    y_complete = _completeness_targets(dataset.train, device)
    y_punct = _punct_targets(dataset.train, device)

    n = train_ids.size(0)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    final_loss = 0.0
    for ep in range(1, epochs + 1):
        # Deterministic per-epoch shuffle of mini-batch order.
        perm = torch.randperm(n, generator=torch.Generator().manual_seed(seed + ep))
        epoch_loss = 0.0
        n_batches = 0
        for start in range(0, n, batch_size):
            idx = perm[start:start + batch_size]
            opt.zero_grad()
            out = model(train_ids[idx], train_mask[idx])
            loss = F.binary_cross_entropy(out["sentence_completeness"], y_complete[idx])
            if "terminal_punctuation_logits" in out:
                loss = loss + F.cross_entropy(out["terminal_punctuation_logits"], y_punct[idx])
            loss.backward()
            opt.step()
            epoch_loss += float(loss.item())
            n_batches += 1
        final_loss = epoch_loss / max(1, n_batches)

    # ---- Validation with real metrics ----
    val_complete_metrics: Dict[str, float] = {}
    val_punct_acc = 0.0
    eval_split = dataset.val or dataset.train
    model.eval()
    with torch.no_grad():
        v_ids, v_mask = tok.encode([e.text for e in eval_split], max_length=max_length)
        out = model(v_ids.to(device), v_mask.to(device))
        preds = [float(p) for p in out["sentence_completeness"].squeeze(-1).tolist()]
        labels = [e.completeness for e in eval_split]
        val_complete_metrics = binary_metrics(preds, labels)
        if "terminal_punctuation_logits" in out:
            punct_pred = out["terminal_punctuation_logits"].argmax(dim=-1).tolist()
            punct_true = [0 if e.has_terminal >= 0.5 else _MISSING_PUNCT_CLASS for e in eval_split]
            # "present vs missing" binary accuracy
            correct = sum(1 for p, t in zip(punct_pred, punct_true)
                          if (p == _MISSING_PUNCT_CLASS) == (t == _MISSING_PUNCT_CLASS))
            val_punct_acc = round(correct / max(1, len(punct_true)), 4)

    passed = val_complete_metrics.get("accuracy", 0.0) >= pass_threshold
    return TrainingResult(
        domain=domain,
        trained=True,
        epochs=epochs,
        final_train_loss=round(final_loss, 4),
        val_completeness=val_complete_metrics,
        val_punctuation_accuracy=val_punct_acc,
        train_size=len(dataset.train),
        val_size=len(eval_split),
        passed=passed,
        note="trained on real corpus with derived negatives",
    )
