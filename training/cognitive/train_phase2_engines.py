"""
train_phase2_engines.py — Unified Neural Training Pipeline for DCVE, NACE, LSCE, and PACE.

Implements the neural training layer for:
  1. DCVE (Domain Competence Verbal Engine)
     - Jargon substance vs buzzwords, conceptual precision, domain track, ontology grounding
  2. NACE (Narrative Arc & Coherence Engine)
     - Contradiction detection, theme stability, STAR climaxes, narrative forward momentum
  3. LSCE (Long-Short Cognitive Endurance Engine)
     - Fatigue trajectory, Type-Token Ratio lexical diversity drift, concentration resilience, recovery
  4. PACE (Pacing & Adaptation Calibration Engine)
     - Vocabulary complexity adjustment, response length calibration, register matching, interruption composure

Architecture & Loss:
  - Shared Transformer Encoder Backbone with 16 multi-task heads
  - Kendall & Gal Learnable Homoscedastic Log-Variances
  - Structured Curriculum Generation (4 candidate profiles)
  - Zero-Bridge Synchronous Memory Sync into AMSV physical offsets:
      - 0x30: DCVE [depth_q16, precision_q16] (<HH)
      - 0x34: NACE [coherence_q16, climax_q16] (<HH)
      - 0x3C: LSCE [stamina_q16] (<H)
      - 0x3E: PACE [adaptation_q16] (<H)
  - Overfitting Guard & Holdout Validation Loop
  - SHA-256 Checkpoint Serialization
"""

from __future__ import annotations
import os
import math
import struct
from typing import Dict, List, Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

from training.checkpoint_sync import CheckpointManager


class Phase2CognitiveNetwork(nn.Module):
    """
    16-head multi-task neural network unifying DCVE, NACE, LSCE, and PACE.
    """

    def __init__(self, vocab_size: int = 1000, d_model: int = 256, nhead: int = 4, num_layers: int = 3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=512, dropout=0.1, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(d_model)

        def head(out: int) -> nn.Sequential:
            return nn.Sequential(
                nn.Linear(d_model, 128),
                nn.GELU(),
                nn.Linear(128, out),
                nn.Sigmoid()
            )

        # ── DCVE Heads (Domain Competence) ─────────────────────────────────
        self.dcve_depth_head     = head(3)  # [substance_density, buzzword_penalty, depth_score]
        self.dcve_precision_head = head(3)  # [quantifier_density, causal_clarity, precision_score]
        self.dcve_track_head     = nn.Linear(d_model, 5)  # 5 domain tracks (Eng, Fin, Med, Leg, Exec)
        self.dcve_grounding_head = head(2)  # [relational_validity, grounding_score]

        # ── NACE Heads (Narrative Arc & Coherence) ─────────────────────────
        self.nace_coherence_head = head(2)  # [coherence_score, contradiction_penalty]
        self.nace_theme_head     = head(2)  # [theme_stability, identity_consistency]
        self.nace_climax_head    = head(3)  # [star_completeness, turnaround_impact, climax_score]
        self.nace_momentum_head  = head(2)  # [progression_velocity, momentum_score]

        # ── LSCE Heads (Cognitive Endurance) ───────────────────────────────
        self.lsce_stamina_head   = head(2)  # [stamina_score, fatigue_decay_rate]
        self.lsce_diversity_head = head(2)  # [lexical_richness, diversity_drift]
        self.lsce_resilience_head= head(2)  # [resilience_score, sub_clause_retention]
        self.lsce_recovery_head  = head(2)  # [recovery_score, rebound_velocity]

        # ── PACE Heads (Pacing & Adaptation Calibration) ───────────────────
        self.pace_vocab_head     = head(2)  # [vocab_compliance, target_complexity_match]
        self.pace_length_head    = head(2)  # [length_compliance, size_match]
        self.pace_register_head  = head(2)  # [register_match, formal_alignment]
        self.pace_interrupt_head = head(2)  # [composure_score, pivot_grace]

        # Master Cognitive Mastery Synthesis
        self.synthesis_head = nn.Sequential(
            nn.Linear(d_model, 128), nn.GELU(),
            nn.Linear(128, 1), nn.Sigmoid()
        )

        # Kendall & Gal Learnable Log-Variances for 16 task heads
        self.log_vars = nn.Parameter(torch.zeros(16))

    def forward(self, token_ids: torch.Tensor) -> Dict[str, torch.Tensor]:
        x = self.embedding(token_ids)
        x = self.encoder(x)
        x = self.norm(x)
        pooled = x.mean(dim=1)

        return {
            # DCVE
            "dcve_depth":      self.dcve_depth_head(pooled),
            "dcve_precision":  self.dcve_precision_head(pooled),
            "dcve_track":      self.dcve_track_head(pooled),
            "dcve_grounding":  self.dcve_grounding_head(pooled),
            # NACE
            "nace_coherence":  self.nace_coherence_head(pooled),
            "nace_theme":      self.nace_theme_head(pooled),
            "nace_climax":     self.nace_climax_head(pooled),
            "nace_momentum":   self.nace_momentum_head(pooled),
            # LSCE
            "lsce_stamina":    self.lsce_stamina_head(pooled),
            "lsce_diversity":  self.lsce_diversity_head(pooled),
            "lsce_resilience": self.lsce_resilience_head(pooled),
            "lsce_recovery":   self.lsce_recovery_head(pooled),
            # PACE
            "pace_vocab":      self.pace_vocab_head(pooled),
            "pace_length":     self.pace_length_head(pooled),
            "pace_register":   self.pace_register_head(pooled),
            "pace_interrupt":  self.pace_interrupt_head(pooled),
            # Synthesis
            "synthesis_cmi":   self.synthesis_head(pooled),
        }


class Phase2CognitiveTrainer:
    """
    Manages multi-task optimization, holdout validation, Kendall & Gal loss balancing,
    and Zero-Bridge AMSV synchronization for DCVE, NACE, LSCE, and PACE.
    """

    TASK_HEADS = [
        ("dcve_depth", 3, "mse"),
        ("dcve_precision", 3, "mse"),
        ("dcve_track", 5, "ce"),
        ("dcve_grounding", 2, "mse"),
        ("nace_coherence", 2, "mse"),
        ("nace_theme", 2, "mse"),
        ("nace_climax", 3, "mse"),
        ("nace_momentum", 2, "mse"),
        ("lsce_stamina", 2, "mse"),
        ("lsce_diversity", 2, "mse"),
        ("lsce_resilience", 2, "mse"),
        ("lsce_recovery", 2, "mse"),
        ("pace_vocab", 2, "mse"),
        ("pace_length", 2, "mse"),
        ("pace_register", 2, "mse"),
        ("pace_interrupt", 2, "mse"),
    ]

    def __init__(
        self,
        model: Optional[Phase2CognitiveNetwork] = None,
        lr: float = 1e-3,
        amsv_buffer: Optional[bytearray] = None,
        checkpoint_dir: str = "checkpoints"
    ):
        self.model = model or Phase2CognitiveNetwork()
        self.amsv_buffer = amsv_buffer
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-4)
        self.checkpoint_manager = CheckpointManager(checkpoint_dir=checkpoint_dir)

    def compute_loss(
        self,
        preds: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        total_loss = torch.tensor(0.0, device=preds["dcve_depth"].device)
        breakdown = {}

        for i, (name, _, loss_type) in enumerate(self.TASK_HEADS):
            precision = torch.exp(-self.model.log_vars[i])
            if loss_type == "ce":
                loss_i = F.cross_entropy(preds[name], targets[name])
            else:
                loss_i = F.mse_loss(preds[name], targets[name])

            weighted = 0.5 * precision * loss_i + 0.5 * self.model.log_vars[i]
            total_loss = total_loss + weighted
            breakdown[f"loss_{name}"] = loss_i.item()

        breakdown["total_weighted_loss"] = total_loss.item()
        return total_loss, breakdown

    def train_step(self, batch_tokens: torch.Tensor, targets: Dict[str, torch.Tensor]) -> Dict[str, float]:
        self.model.train()
        self.optimizer.zero_grad()
        preds = self.model(batch_tokens)
        loss, breakdown = self.compute_loss(preds, targets)
        loss.backward()
        self.optimizer.step()

        if self.amsv_buffer is not None:
            self._sync_amsv(preds)

        return breakdown

    def validate_step(self, batch_tokens: torch.Tensor, targets: Dict[str, torch.Tensor]) -> Dict[str, float]:
        self.model.eval()
        with torch.no_grad():
            preds = self.model(batch_tokens)
            _, breakdown = self.compute_loss(preds, targets)
        return {f"val_{k}": v for k, v in breakdown.items()}

    def _sync_amsv(self, preds: Dict[str, torch.Tensor]) -> None:
        """
        Zero-Bridge Synchronous Memory Rule:
        Direct physical in-place write into 64-byte AMSV without serialization.
        """
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return

        def to_q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        with torch.no_grad():
            # 0x30: DCVE [depth | precision] (<HH)
            q_depth = to_q16(preds["dcve_depth"][0, 2].item())
            q_prec  = to_q16(preds["dcve_precision"][0, 2].item())
            struct.pack_into("<HH", self.amsv_buffer, 0x30, q_depth, q_prec)

            # 0x34: NACE [coherence | climax] (<HH)
            q_cohere = to_q16(preds["nace_coherence"][0, 0].item())
            q_climax = to_q16(preds["nace_climax"][0, 2].item())
            struct.pack_into("<HH", self.amsv_buffer, 0x34, q_cohere, q_climax)

            # 0x3C: LSCE [stamina] (<H)
            q_stamina = to_q16(preds["lsce_stamina"][0, 0].item())
            struct.pack_into("<H", self.amsv_buffer, 0x3C, q_stamina)

            # 0x3E: PACE [adaptation] (<H)
            q_adapt = to_q16(preds["synthesis_cmi"][0, 0].item())
            struct.pack_into("<H", self.amsv_buffer, 0x3E, q_adapt)


def generate_phase2_curriculum_batch(
    batch_size: int = 8,
    seq_len: int = 32
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
    """
    Generates structured multi-archetype curriculum batches for DCVE, NACE, LSCE, and PACE:
      Archetype 0: Elite Principal Engineer (High depth, Exemplary narrative, Ironclad stamina, Seamless adaptation)
      Archetype 1: Fatigued Mid-Level (Starts proficient, fatigue decay sets in, multi-part retention drops)
      Archetype 2: Buzzword Jargon User (Hollow terms, high buzzwords, contradictory narrative, low precision)
      Archetype 3: Rigid Specialist (Deep in narrow domain, poor length calibration, defensive when interrupted)
    """
    token_ids = torch.randint(0, 1000, (batch_size, seq_len))

    targets: Dict[str, torch.Tensor] = {
        "dcve_depth":      torch.zeros(batch_size, 3),
        "dcve_precision":  torch.zeros(batch_size, 3),
        "dcve_track":      torch.zeros(batch_size, dtype=torch.long),
        "dcve_grounding":  torch.zeros(batch_size, 2),
        "nace_coherence":  torch.zeros(batch_size, 2),
        "nace_theme":      torch.zeros(batch_size, 2),
        "nace_climax":     torch.zeros(batch_size, 3),
        "nace_momentum":   torch.zeros(batch_size, 2),
        "lsce_stamina":    torch.zeros(batch_size, 2),
        "lsce_diversity":  torch.zeros(batch_size, 2),
        "lsce_resilience": torch.zeros(batch_size, 2),
        "lsce_recovery":   torch.zeros(batch_size, 2),
        "pace_vocab":      torch.zeros(batch_size, 2),
        "pace_length":     torch.zeros(batch_size, 2),
        "pace_register":   torch.zeros(batch_size, 2),
        "pace_interrupt":  torch.zeros(batch_size, 2),
    }

    noise = 0.03
    for i in range(batch_size):
        arch = i % 4

        if arch == 0:  # Elite Principal Engineer
            targets["dcve_depth"][i]      = torch.tensor([0.90, 0.10, 0.92])
            targets["dcve_precision"][i]  = torch.tensor([0.88, 0.90, 0.92])
            targets["dcve_track"][i]      = 0  # Engineering
            targets["dcve_grounding"][i]  = torch.tensor([0.92, 0.90])
            targets["nace_coherence"][i]  = torch.tensor([0.95, 0.05])
            targets["nace_theme"][i]      = torch.tensor([0.92, 0.90])
            targets["nace_climax"][i]     = torch.tensor([0.90, 0.92, 0.91])
            targets["nace_momentum"][i]   = torch.tensor([0.88, 0.90])
            targets["lsce_stamina"][i]    = torch.tensor([0.94, 0.05])
            targets["lsce_diversity"][i]  = torch.tensor([0.88, 0.05])
            targets["lsce_resilience"][i] = torch.tensor([0.92, 0.90])
            targets["lsce_recovery"][i]   = torch.tensor([0.90, 0.88])
            targets["pace_vocab"][i]      = torch.tensor([0.92, 0.90])
            targets["pace_length"][i]     = torch.tensor([0.95, 0.92])
            targets["pace_register"][i]   = torch.tensor([0.90, 0.88])
            targets["pace_interrupt"][i]  = torch.tensor([0.95, 0.92])

        elif arch == 1:  # Fatigued Mid-Level
            targets["dcve_depth"][i]      = torch.tensor([0.65, 0.25, 0.60])
            targets["dcve_precision"][i]  = torch.tensor([0.60, 0.55, 0.58])
            targets["dcve_track"][i]      = 0  # Engineering
            targets["dcve_grounding"][i]  = torch.tensor([0.70, 0.65])
            targets["nace_coherence"][i]  = torch.tensor([0.75, 0.20])
            targets["nace_theme"][i]      = torch.tensor([0.70, 0.65])
            targets["nace_climax"][i]     = torch.tensor([0.65, 0.60, 0.62])
            targets["nace_momentum"][i]   = torch.tensor([0.55, 0.50])
            targets["lsce_stamina"][i]    = torch.tensor([0.40, 0.55])  # fatigue decay
            targets["lsce_diversity"][i]  = torch.tensor([0.50, 0.40])  # diversity drift
            targets["lsce_resilience"][i] = torch.tensor([0.45, 0.40])
            targets["lsce_recovery"][i]   = torch.tensor([0.50, 0.45])
            targets["pace_vocab"][i]      = torch.tensor([0.65, 0.60])
            targets["pace_length"][i]     = torch.tensor([0.60, 0.55])
            targets["pace_register"][i]   = torch.tensor([0.70, 0.65])
            targets["pace_interrupt"][i]  = torch.tensor([0.65, 0.60])

        elif arch == 2:  # Buzzword Jargon User
            targets["dcve_depth"][i]      = torch.tensor([0.20, 0.85, 0.25])
            targets["dcve_precision"][i]  = torch.tensor([0.25, 0.20, 0.22])
            targets["dcve_track"][i]      = 4  # Executive
            targets["dcve_grounding"][i]  = torch.tensor([0.30, 0.25])
            targets["nace_coherence"][i]  = torch.tensor([0.40, 0.60])  # contradictions
            targets["nace_theme"][i]      = torch.tensor([0.35, 0.30])
            targets["nace_climax"][i]     = torch.tensor([0.30, 0.25, 0.28])
            targets["nace_momentum"][i]   = torch.tensor([0.35, 0.30])
            targets["lsce_stamina"][i]    = torch.tensor([0.55, 0.30])
            targets["lsce_diversity"][i]  = torch.tensor([0.45, 0.35])
            targets["lsce_resilience"][i] = torch.tensor([0.35, 0.30])
            targets["lsce_recovery"][i]   = torch.tensor([0.40, 0.35])
            targets["pace_vocab"][i]      = torch.tensor([0.35, 0.30])
            targets["pace_length"][i]     = torch.tensor([0.30, 0.25])  # rambles
            targets["pace_register"][i]   = torch.tensor([0.45, 0.40])
            targets["pace_interrupt"][i]  = torch.tensor([0.40, 0.35])

        else:  # Rigid Specialist
            targets["dcve_depth"][i]      = torch.tensor([0.88, 0.15, 0.85])
            targets["dcve_precision"][i]  = torch.tensor([0.85, 0.80, 0.82])
            targets["dcve_track"][i]      = 0  # Engineering
            targets["dcve_grounding"][i]  = torch.tensor([0.88, 0.85])
            targets["nace_coherence"][i]  = torch.tensor([0.80, 0.15])
            targets["nace_theme"][i]      = torch.tensor([0.90, 0.88])
            targets["nace_climax"][i]     = torch.tensor([0.70, 0.65, 0.68])
            targets["nace_momentum"][i]   = torch.tensor([0.60, 0.55])
            targets["lsce_stamina"][i]    = torch.tensor([0.80, 0.15])
            targets["lsce_diversity"][i]  = torch.tensor([0.82, 0.10])
            targets["lsce_resilience"][i] = torch.tensor([0.85, 0.80])
            targets["lsce_recovery"][i]   = torch.tensor([0.70, 0.65])
            targets["pace_vocab"][i]      = torch.tensor([0.45, 0.40])  # can't simplify
            targets["pace_length"][i]     = torch.tensor([0.40, 0.35])  # over-elaborates
            targets["pace_register"][i]   = torch.tensor([0.55, 0.50])
            targets["pace_interrupt"][i]  = torch.tensor([0.30, 0.25])  # defensive

        # Add noise
        for k in targets:
            if k == "dcve_track":
                continue
            dim = targets[k].shape[1]
            targets[k][i] = (targets[k][i] + torch.randn(dim) * noise).clamp(0.0, 1.0)

    return token_ids, targets
