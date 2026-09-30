"""
train_hcte_cognitive_ai.py — HCTE Neural Training Layer

Trains a dedicated 11-head network for the Human Cognitive Thinking Engine.
Each head corresponds to one cognitive persona.

Special design choices:
  - Pre-Mortem head gets 2× loss weight (negative thinking is most valuable)
  - Cognitive Tension regularization: penalise if all personas agree too easily
  - Homoscedastic uncertainty weighting (Kendall & Gal) across all 11 heads
"""
from __future__ import annotations
import struct
from typing import Dict, List, Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class HCTECognitiveNetwork(nn.Module):
    """
    11-head multi-task network for human-like cognitive persona simulation.

    Input:  token_ids [B, seq_len]
    Output: Dict of 11 persona scores + tension + synthesis
    """
    def __init__(self, vocab_size: int = 1000, d_model: int = 256,
                 nhead: int = 4, num_layers: int = 3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=512, dropout=0.1, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(d_model)

        # 11 Persona Heads
        def head(out: int) -> nn.Sequential:
            return nn.Sequential(
                nn.Linear(d_model, 128), nn.GELU(),
                nn.Linear(128, out), nn.Sigmoid()
            )

        self.optimist_head          = head(1)   # optimism score
        self.pessimist_head         = head(1)   # pessimism/risk score
        self.premortem_head         = head(3)   # [severity, probability, solution_coverage]
        self.devils_advocate_head   = head(1)   # challenge urgency
        self.analyst_head           = head(2)   # [evidence_score, logic_chain]
        self.intuitive_head         = head(1)   # heuristic confidence
        self.empath_head            = head(2)   # [human_salience, impact_awareness]
        self.systems_head           = head(2)   # [system_awareness, complexity_depth]
        self.visionary_head         = head(2)   # [horizon_score, paradigm_detected]
        self.absurdist_head         = head(1)   # divergence score
        self.metacog_head           = head(2)   # [cognitive_tension, metacog_alert_level]

        # Synthesis head: cross-persona attention
        self.synthesis_head = nn.Sequential(
            nn.Linear(d_model, 256), nn.GELU(),
            nn.Linear(256, 128), nn.GELU(),
            nn.Linear(128, 1), nn.Sigmoid()   # global_cognitive_index
        )

        # 11 learnable log-variances for Kendall & Gal uncertainty weighting
        self.log_vars = nn.Parameter(torch.zeros(11))

    def forward(self, token_ids: torch.Tensor) -> Dict[str, torch.Tensor]:
        x = self.embedding(token_ids)
        x = self.encoder(x)
        x = self.norm(x)
        pooled = x.mean(dim=1)

        return {
            "optimist":        self.optimist_head(pooled),
            "pessimist":       self.pessimist_head(pooled),
            "premortem":       self.premortem_head(pooled),
            "devils_advocate": self.devils_advocate_head(pooled),
            "analyst":         self.analyst_head(pooled),
            "intuitive":       self.intuitive_head(pooled),
            "empath":          self.empath_head(pooled),
            "systems":         self.systems_head(pooled),
            "visionary":       self.visionary_head(pooled),
            "absurdist":       self.absurdist_head(pooled),
            "metacog":         self.metacog_head(pooled),
            "synthesis":       self.synthesis_head(pooled),
        }


class HCTETrainer:
    def __init__(self, model: Optional[HCTECognitiveNetwork] = None,
                 amsv_buffer: Optional[bytearray] = None):
        self.model = model or HCTECognitiveNetwork()
        self.amsv_buffer = amsv_buffer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(), lr=1e-3, weight_decay=1e-4
        )

    def compute_loss(
        self,
        preds: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        heads = [
            ("optimist", 1),
            ("pessimist", 1),
            ("premortem", 3),   # ← gets 2× weight
            ("devils_advocate", 1),
            ("analyst", 2),
            ("intuitive", 1),
            ("empath", 2),
            ("systems", 2),
            ("visionary", 2),
            ("absurdist", 1),
            ("metacog", 2),
        ]

        total_loss = torch.tensor(0.0)
        breakdown = {}

        for i, (name, _) in enumerate(heads):
            precision = torch.exp(-self.model.log_vars[i])
            loss_i = F.mse_loss(preds[name], targets[name])

            # Pre-Mortem gets 2× weight — negative thinking matters most
            multiplier = 2.0 if name == "premortem" else 1.0

            weighted = multiplier * (0.5 * precision * loss_i + 0.5 * self.model.log_vars[i])
            total_loss = total_loss + weighted
            breakdown[f"loss_{name}"] = loss_i.item()

        # Cognitive Tension Regularization:
        # Penalize if the metacog predicts LOW tension (groupthink)
        # We want tension >= 0.30 — healthy disagreement between personas
        tension_pred = preds["metacog"][:, 0]  # first dim = cognitive_tension
        tension_penalty = F.relu(0.30 - tension_pred).mean() * 0.5
        total_loss = total_loss + tension_penalty
        breakdown["tension_penalty"] = tension_penalty.item()

        return total_loss, breakdown

    def train_step(
        self,
        batch_tokens: torch.Tensor,
        targets: Dict[str, torch.Tensor]
    ) -> Dict[str, float]:
        self.model.train()
        self.optimizer.zero_grad()
        preds = self.model(batch_tokens)
        loss, breakdown = self.compute_loss(preds, targets)
        loss.backward()
        self.optimizer.step()

        if self.amsv_buffer is not None:
            self._sync_amsv(preds)

        breakdown["total_loss"] = loss.item()
        return breakdown

    def _sync_amsv(self, preds: Dict[str, torch.Tensor]) -> None:
        """Zero-Bridge write to AMSV 0x38 (HCTE region)."""
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return
        with torch.no_grad():
            opt_val     = preds["optimist"][0, 0].item()
            pess_val    = preds["pessimist"][0, 0].item()
            tension_val = preds["metacog"][0, 0].item()
            sol_val     = preds["premortem"][0, 2].item()   # solution_coverage

        def to_q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        struct.pack_into("<HHHH", self.amsv_buffer, 0x38,
                         to_q16(opt_val), to_q16(pess_val),
                         to_q16(tension_val), to_q16(sol_val))


def generate_hcte_curriculum_batch(
    batch_size: int = 8,
    seq_len: int = 32
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
    """
    Structured curriculum batches for HCTE training.

    Archetype A: Crisis scenario — high pessimism, high pre-mortem RPN, high tension
    Archetype B: Opportunity scenario — high optimism, low risk, visionary horizon high
    Archetype C: Complex problem — high systems/analyst, balanced optimism/pessimism
    Archetype D: Creative challenge — high absurdist/visionary, moderate analyst
    """
    token_ids = torch.randint(0, 1000, (batch_size, seq_len))

    targets: Dict[str, torch.Tensor] = {
        "optimist":        torch.zeros(batch_size, 1),
        "pessimist":       torch.zeros(batch_size, 1),
        "premortem":       torch.zeros(batch_size, 3),   # [severity, prob, solution]
        "devils_advocate": torch.zeros(batch_size, 1),
        "analyst":         torch.zeros(batch_size, 2),
        "intuitive":       torch.zeros(batch_size, 1),
        "empath":          torch.zeros(batch_size, 2),
        "systems":         torch.zeros(batch_size, 2),
        "visionary":       torch.zeros(batch_size, 2),
        "absurdist":       torch.zeros(batch_size, 1),
        "metacog":         torch.zeros(batch_size, 2),   # [tension, alert]
    }

    noise = 0.04
    for i in range(batch_size):
        arch = i % 4

        if arch == 0:   # Crisis scenario
            targets["optimist"][i]        = torch.tensor([0.25])
            targets["pessimist"][i]       = torch.tensor([0.88])
            targets["premortem"][i]       = torch.tensor([0.90, 0.72, 0.60])  # high severity, prob; moderate solutions
            targets["devils_advocate"][i] = torch.tensor([0.80])
            targets["analyst"][i]         = torch.tensor([0.65, 0.70])
            targets["intuitive"][i]       = torch.tensor([0.50])
            targets["empath"][i]          = torch.tensor([0.70, 0.65])
            targets["systems"][i]         = torch.tensor([0.75, 0.80])
            targets["visionary"][i]       = torch.tensor([0.40, 0.35])
            targets["absurdist"][i]       = torch.tensor([0.30])
            targets["metacog"][i]         = torch.tensor([0.75, 0.60])  # HIGH tension, HIGH alert

        elif arch == 1: # Opportunity scenario
            targets["optimist"][i]        = torch.tensor([0.90])
            targets["pessimist"][i]       = torch.tensor([0.25])
            targets["premortem"][i]       = torch.tensor([0.30, 0.20, 0.92])  # low risk; high solutions
            targets["devils_advocate"][i] = torch.tensor([0.45])
            targets["analyst"][i]         = torch.tensor([0.70, 0.68])
            targets["intuitive"][i]       = torch.tensor([0.85])
            targets["empath"][i]          = torch.tensor([0.55, 0.50])
            targets["systems"][i]         = torch.tensor([0.50, 0.45])
            targets["visionary"][i]       = torch.tensor([0.88, 0.80])  # HIGH vision
            targets["absurdist"][i]       = torch.tensor([0.60])
            targets["metacog"][i]         = torch.tensor([0.45, 0.10])  # moderate tension, low alert

        elif arch == 2: # Complex problem
            targets["optimist"][i]        = torch.tensor([0.55])
            targets["pessimist"][i]       = torch.tensor([0.60])
            targets["premortem"][i]       = torch.tensor([0.70, 0.55, 0.75])
            targets["devils_advocate"][i] = torch.tensor([0.65])
            targets["analyst"][i]         = torch.tensor([0.88, 0.85])  # HIGH analytical
            targets["intuitive"][i]       = torch.tensor([0.55])
            targets["empath"][i]          = torch.tensor([0.65, 0.60])
            targets["systems"][i]         = torch.tensor([0.90, 0.85])  # HIGH systems
            targets["visionary"][i]       = torch.tensor([0.60, 0.55])
            targets["absurdist"][i]       = torch.tensor([0.40])
            targets["metacog"][i]         = torch.tensor([0.65, 0.30])  # healthy tension

        else:           # Creative challenge
            targets["optimist"][i]        = torch.tensor([0.72])
            targets["pessimist"][i]       = torch.tensor([0.35])
            targets["premortem"][i]       = torch.tensor([0.40, 0.30, 0.85])
            targets["devils_advocate"][i] = torch.tensor([0.55])
            targets["analyst"][i]         = torch.tensor([0.48, 0.45])
            targets["intuitive"][i]       = torch.tensor([0.75])
            targets["empath"][i]          = torch.tensor([0.60, 0.55])
            targets["systems"][i]         = torch.tensor([0.55, 0.50])
            targets["visionary"][i]       = torch.tensor([0.80, 0.75])
            targets["absurdist"][i]       = torch.tensor([0.90])   # HIGH creative
            targets["metacog"][i]         = torch.tensor([0.50, 0.15])

        # Add calibration noise
        for k in targets:
            dim = targets[k].shape[1]
            targets[k][i] = (targets[k][i] + torch.randn(dim) * noise).clamp(0.0, 1.0)

    return token_ids, targets
