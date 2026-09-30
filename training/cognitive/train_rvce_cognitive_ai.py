"""
train_rvce_cognitive_ai.py - RVCE Multi-Task Cognitive Neural Training System

Trains a deep multi-task neural network on the 6 cognitive dimensions:
1. Thinking Ability (MECE, First-Principles, STAR, Deduction)
2. Concentrating Functioning (Attentive stability, endurance, noise robustness)
3. Recalling Ability (Working memory retrieval, cross-turn consistency, resume fidelity)
4. Creativity & Out-of-the-Box Thinking (Divergent ideation, conceptual novelty, lateral transfer)
5. Imagination (Counterfactual forecasting, prospective simulation, Theory of Mind)
6. Verbal Articulation (Fluency, register compliance, zero-filler clarity)

Zero-Bridge Synchronous Memory Integration:
Live prediction states are directly synchronized to the 64-byte AMSV physical vector
during inference and evaluation turns without serialization.
"""

from __future__ import annotations
import math
import struct
from typing import Dict, List, Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

class RVCECognitiveNetwork(nn.Module):
    def __init__(self, vocab_size: int = 1000, d_model: int = 256, nhead: int = 4, num_layers: int = 3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=512,
            dropout=0.1,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(d_model)

        # 6 Dedicated Cognitive Heads
        self.thinking_head = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.GELU(),
            nn.Linear(128, 5), # [depth, first_principles, mece, star, validity]
            nn.Sigmoid()
        )
        self.concentration_head = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.GELU(),
            nn.Linear(128, 4), # [pace_stab, endurance, distract_resist, snr_norm]
            nn.Sigmoid()
        )
        self.recall_head = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.GELU(),
            nn.Linear(128, 4), # [wm_retention, consistency, resume_fidelity, latency_norm]
            nn.Sigmoid()
        )
        self.creativity_head = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.GELU(),
            nn.Linear(128, 4), # [divergent, novelty, lateral, metaphor]
            nn.Sigmoid()
        )
        self.imagination_head = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.GELU(),
            nn.Linear(128, 4), # [counterfactual, prospective, theory_of_mind, vision]
            nn.Sigmoid()
        )
        self.verbal_head = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.GELU(),
            nn.Linear(128, 4), # [fluency, register, filler_penalty, vocab_density]
            nn.Sigmoid()
        )

        # Composite Hireability & Recommendation Head
        self.hireability_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        self.recommendation_head = nn.Linear(d_model, 4) # 4 recommendation classes

        # Learnable homoscedastic uncertainty log variances for each cognitive head
        self.log_vars = nn.Parameter(torch.zeros(6))

    def forward(self, token_ids: torch.Tensor) -> Dict[str, torch.Tensor]:
        # token_ids: [B, seq_len]
        x = self.embedding(token_ids)
        x = self.encoder(x)
        x = self.norm(x)

        # Pool across sequence length (mean pooling)
        pooled = torch.mean(x, dim=1) # [B, d_model]

        return {
            "thinking": self.thinking_head(pooled),
            "concentration": self.concentration_head(pooled),
            "recall": self.recall_head(pooled),
            "creativity": self.creativity_head(pooled),
            "imagination": self.imagination_head(pooled),
            "verbal": self.verbal_head(pooled),
            "hireability": self.hireability_head(pooled),
            "recommendation_logits": self.recommendation_head(pooled)
        }

class RVCETrainer:
    def __init__(self, model: Optional[RVCECognitiveNetwork] = None, amsv_buffer: Optional[bytearray] = None):
        self.model = model or RVCECognitiveNetwork()
        self.amsv_buffer = amsv_buffer
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-3, weight_decay=1e-4)

    def compute_loss(
        self,
        preds: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        # Homoscedastic loss weighting across 6 heads
        heads = ["thinking", "concentration", "recall", "creativity", "imagination", "verbal"]
        total_loss = 0.0
        head_losses = {}

        for i, h in enumerate(heads):
            precision = torch.exp(-self.model.log_vars[i])
            diff = F.mse_loss(preds[h], targets[h])
            loss_i = 0.5 * precision * diff + 0.5 * self.model.log_vars[i]
            total_loss = total_loss + loss_i
            head_losses[h] = diff.item()

        # Add hireability loss
        if "hireability" in targets:
            hire_loss = F.mse_loss(preds["hireability"], targets["hireability"])
            total_loss = total_loss + hire_loss
            head_losses["hireability"] = hire_loss.item()

        return total_loss, head_losses

    def train_step(self, batch_tokens: torch.Tensor, targets: Dict[str, torch.Tensor]) -> Dict[str, float]:
        self.model.train()
        self.optimizer.zero_grad()
        preds = self.model(batch_tokens)
        loss, breakdown = self.compute_loss(preds, targets)
        loss.backward()
        self.optimizer.step()

        # Zero-Bridge Sync to physical AMSV memory
        if self.amsv_buffer is not None:
            self.sync_amsv(preds)

        breakdown["total_loss"] = loss.item()
        return breakdown

    def sync_amsv(self, preds: Dict[str, torch.Tensor]) -> None:
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return

        with torch.no_grad():
            # FIX: Composite mean across ALL dimensions per head (not just index [0,0])
            think_val  = preds["thinking"][0].mean().item()
            focus_val  = preds["concentration"][0].mean().item()
            recall_val = preds["recall"][0].mean().item()
            creat_val  = preds["creativity"][0].mean().item()
            imagi_val  = preds["imagination"][0].mean().item()
            # Analytical = average of MECE (dim 2) + validity (dim 4) from thinking head
            analy_val  = (preds["thinking"][0, 2].item() + preds["thinking"][0, 4].item()) * 0.5
            verbal_val = preds["verbal"][0].mean().item()
            hire_val   = preds["hireability"][0, 0].item()

        def to_q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535.0)

        # Offset 0x10: ccte_cog_bank_alpha [Think | Focus | Recall | Creativity]
        struct.pack_into("<HHHH", self.amsv_buffer, 0x10,
                         to_q16(think_val), to_q16(focus_val),
                         to_q16(recall_val), to_q16(creat_val))
        # Offset 0x18: ccte_cog_bank_beta [Imagination | Analytical | Verbal | Focus]
        struct.pack_into("<HHHH", self.amsv_buffer, 0x18,
                         to_q16(imagi_val), to_q16(analy_val),
                         to_q16(verbal_val), to_q16(focus_val))
        # Offset 0x20: rsse_scenario_state [Engine_ID | Turn | Hireability | Recommend]
        struct.pack_into("<HHHH", self.amsv_buffer, 0x20,
                         202, 1, to_q16(hire_val),
                         1 if hire_val >= 0.75 else 2)

def generate_synthetic_recruitment_batch(
    batch_size: int = 8,
    seq_len: int = 32
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
    """
    Structured Curriculum Synthetic Batch Generator.

    Replaces the original pure-random generator with cognitively meaningful
    candidate archetypes that model real signal distributions:

      Type A (25%) — High-performer: thinking high, verbal clear, low filler
      Type B (25%) — Anxious candidate: concentration low, verbal filler high, confidence low
      Type C (25%) — Creative generalist: creativity/imagination high, structure moderate
      Type D (25%) — Generic responder: all dimensions 0.3-0.5, recall low
    """
    import random
    token_ids = torch.randint(0, 1000, (batch_size, seq_len))

    think_t    = torch.zeros(batch_size, 5)
    conc_t     = torch.zeros(batch_size, 4)
    recall_t   = torch.zeros(batch_size, 4)
    creat_t    = torch.zeros(batch_size, 4)
    imagi_t    = torch.zeros(batch_size, 4)
    verbal_t   = torch.zeros(batch_size, 4)
    hire_t     = torch.zeros(batch_size, 1)

    for i in range(batch_size):
        archetype = i % 4  # cycle through the 4 types deterministically

        if archetype == 0:  # High-performer
            think_t[i]  = torch.tensor([0.88, 0.85, 0.90, 0.83, 0.87])  # depth, fp, mece, star, validity
            conc_t[i]   = torch.tensor([0.90, 0.88, 0.85, 0.84])         # pace, endurance, distract, snr
            recall_t[i] = torch.tensor([0.85, 0.88, 0.92, 0.78])         # wm, consistency, fidelity, latency
            creat_t[i]  = torch.tensor([0.75, 0.80, 0.72, 0.68])
            imagi_t[i]  = torch.tensor([0.78, 0.82, 0.75, 0.80])
            verbal_t[i] = torch.tensor([0.92, 0.88, 0.05, 0.85])         # fluency, register, filler(LOW), vocab
            hire_t[i]   = torch.tensor([0.90])

        elif archetype == 1:  # Anxious candidate
            think_t[i]  = torch.tensor([0.60, 0.55, 0.58, 0.62, 0.50])
            conc_t[i]   = torch.tensor([0.40, 0.35, 0.45, 0.38])
            recall_t[i] = torch.tensor([0.55, 0.50, 0.48, 0.60])
            creat_t[i]  = torch.tensor([0.45, 0.42, 0.40, 0.38])
            imagi_t[i]  = torch.tensor([0.50, 0.45, 0.48, 0.42])
            verbal_t[i] = torch.tensor([0.58, 0.55, 0.45, 0.52])         # filler HIGH (0.45)
            hire_t[i]   = torch.tensor([0.40])

        elif archetype == 2:  # Creative generalist
            think_t[i]  = torch.tensor([0.72, 0.80, 0.68, 0.70, 0.65])
            conc_t[i]   = torch.tensor([0.68, 0.72, 0.65, 0.70])
            recall_t[i] = torch.tensor([0.65, 0.62, 0.68, 0.70])
            creat_t[i]  = torch.tensor([0.92, 0.90, 0.88, 0.85])         # creativity HIGH
            imagi_t[i]  = torch.tensor([0.88, 0.90, 0.85, 0.92])         # imagination HIGH
            verbal_t[i] = torch.tensor([0.75, 0.70, 0.15, 0.80])
            hire_t[i]   = torch.tensor([0.72])

        else:  # Generic responder
            think_t[i]  = torch.tensor([0.38, 0.35, 0.40, 0.42, 0.36])
            conc_t[i]   = torch.tensor([0.45, 0.42, 0.48, 0.40])
            recall_t[i] = torch.tensor([0.30, 0.35, 0.28, 0.42])         # recall LOW
            creat_t[i]  = torch.tensor([0.38, 0.35, 0.32, 0.30])
            imagi_t[i]  = torch.tensor([0.40, 0.38, 0.35, 0.42])
            verbal_t[i] = torch.tensor([0.55, 0.50, 0.35, 0.48])
            hire_t[i]   = torch.tensor([0.32])

        # Add small noise to prevent overfit on archetype boundaries
        noise = 0.05
        think_t[i]  = (think_t[i]  + torch.randn(5)  * noise).clamp(0.0, 1.0)
        conc_t[i]   = (conc_t[i]   + torch.randn(4)  * noise).clamp(0.0, 1.0)
        recall_t[i] = (recall_t[i] + torch.randn(4)  * noise).clamp(0.0, 1.0)
        creat_t[i]  = (creat_t[i]  + torch.randn(4)  * noise).clamp(0.0, 1.0)
        imagi_t[i]  = (imagi_t[i]  + torch.randn(4)  * noise).clamp(0.0, 1.0)
        verbal_t[i] = (verbal_t[i] + torch.randn(4)  * noise).clamp(0.0, 1.0)
        hire_t[i]   = (hire_t[i]   + torch.randn(1)  * noise).clamp(0.0, 1.0)

    targets = {
        "thinking":      think_t,
        "concentration": conc_t,
        "recall":        recall_t,
        "creativity":    creat_t,
        "imagination":   imagi_t,
        "verbal":        verbal_t,
        "hireability":   hire_t,
    }
    return token_ids, targets

generate_structured_rvce_batch = generate_synthetic_recruitment_batch
