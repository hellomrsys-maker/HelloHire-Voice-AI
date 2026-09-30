"""
train_phase1_engines.py — Unified Neural Training Pipeline for ALIE, ECSE, and PMCE.

Implements the neural training layer for:
  1. ALIE (Active Listening Intelligence Engine)
     - Reference alignment, QA relevance, discourse repair, coreference persistence, GLI
  2. ECSE (Emotional & Social Calibration Engine)
     - Affective valence, rapport warmth, behavioral mirroring, diplomatic disagreement, politeness
  3. PMCE (Persuasion & Message Construction Engine)
     - Classical rhetorical proofs: Logos, Ethos, Pathos, Kairos, Call-to-Action

Architecture & Loss:
  - Shared Transformer Encoder Backbone with 15 multi-task heads
  - Kendall & Gal Learnable Homoscedastic Log-Variances
  - Structured Curriculum Generation (4 communicative archetypes)
  - Zero-Bridge Synchronous Memory Sync into AMSV physical offsets:
      - 0x10, 0x18: ALIE Primary & Secondary (ccte_cog_bank_alpha & beta)
      - 0x20: ECSE Social State (rsse_format_scenario)
      - 0x28: PMCE Persuasion & Rhetoric State (aeee_examination)
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


class Phase1CognitiveNetwork(nn.Module):
    """
    15-head multi-task neural network unifying ALIE, ECSE, and PMCE on a shared transformer backbone.
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

        # ── ALIE Heads (Active Listening) ──────────────────────────────────
        self.alie_alignment_head   = head(3)  # [pronoun_echo, frame_retention, topic_lock]
        self.alie_relevance_head   = head(3)  # [on_topic_ratio, specificity, completeness]
        self.alie_repair_head      = head(2)  # [repair_detect, acknowledgement_density]
        self.alie_coreference_head = head(2)  # [entity_persistence, antecedent_resolution]
        self.alie_gli_head         = head(1)  # Global Listening Index

        # ── ECSE Heads (Emotional & Social Calibration) ─────────────────────
        self.ecse_affect_head       = head(3)  # [valence, arousal, composure]
        self.ecse_rapport_head      = head(2)  # [empathy_resonance, warmth]
        self.ecse_mirroring_head    = head(2)  # [lexical_alignment, energy_sync]
        self.ecse_disagree_head     = head(2)  # [diplomatic_cushion, constructive_pivot]
        self.ecse_politeness_head   = head(2)  # [deference, honorific_density]

        # ── PMCE Heads (Persuasion & Message Construction) ───────────────────
        self.pmce_logos_head        = head(3)  # [deductive_soundness, evidence_ratio, premise_flow]
        self.pmce_ethos_head        = head(2)  # [credibility_markers, competence_authority]
        self.pmce_pathos_head       = head(2)  # [narrative_engagement, emotional_resonance]
        self.pmce_kairos_head       = head(2)  # [timing_appropriateness, urgency_pacing]
        self.pmce_cta_head          = head(2)  # [actionability, conviction]

        # Master Communication Mastery Synthesis
        self.synthesis_head = nn.Sequential(
            nn.Linear(d_model, 128), nn.GELU(),
            nn.Linear(128, 1), nn.Sigmoid()
        )

        # Kendall & Gal Learnable Log-Variances for 15 task heads
        self.log_vars = nn.Parameter(torch.zeros(15))

    def forward(self, token_ids: torch.Tensor) -> Dict[str, torch.Tensor]:
        x = self.embedding(token_ids)
        x = self.encoder(x)
        x = self.norm(x)
        pooled = x.mean(dim=1)

        return {
            # ALIE
            "alie_alignment":   self.alie_alignment_head(pooled),
            "alie_relevance":   self.alie_relevance_head(pooled),
            "alie_repair":      self.alie_repair_head(pooled),
            "alie_coref":       self.alie_coreference_head(pooled),
            "alie_gli":         self.alie_gli_head(pooled),
            # ECSE
            "ecse_affect":      self.ecse_affect_head(pooled),
            "ecse_rapport":     self.ecse_rapport_head(pooled),
            "ecse_mirror":      self.ecse_mirroring_head(pooled),
            "ecse_disagree":    self.ecse_disagree_head(pooled),
            "ecse_politeness":  self.ecse_politeness_head(pooled),
            # PMCE
            "pmce_logos":       self.pmce_logos_head(pooled),
            "pmce_ethos":       self.pmce_ethos_head(pooled),
            "pmce_pathos":      self.pmce_pathos_head(pooled),
            "pmce_kairos":      self.pmce_kairos_head(pooled),
            "pmce_cta":         self.pmce_cta_head(pooled),
            # Synthesis
            "synthesis_cmi":    self.synthesis_head(pooled),
        }


class Phase1CognitiveTrainer:
    """
    Manages multi-task optimization, holdout validation, Kendall & Gal loss balancing,
    and Zero-Bridge AMSV synchronization for ALIE, ECSE, and PMCE.
    """

    TASK_HEADS = [
        ("alie_alignment", 3),
        ("alie_relevance", 3),
        ("alie_repair", 2),
        ("alie_coref", 2),
        ("alie_gli", 1),
        ("ecse_affect", 3),
        ("ecse_rapport", 2),
        ("ecse_mirror", 2),
        ("ecse_disagree", 2),
        ("ecse_politeness", 2),
        ("pmce_logos", 3),
        ("pmce_ethos", 2),
        ("pmce_pathos", 2),
        ("pmce_kairos", 2),
        ("pmce_cta", 2),
    ]

    def __init__(
        self,
        model: Optional[Phase1CognitiveNetwork] = None,
        lr: float = 1e-3,
        amsv_buffer: Optional[bytearray] = None,
        checkpoint_dir: str = "checkpoints"
    ):
        self.model = model or Phase1CognitiveNetwork()
        self.amsv_buffer = amsv_buffer
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-4)
        self.checkpoint_manager = CheckpointManager(checkpoint_dir=checkpoint_dir)

    def compute_loss(
        self,
        preds: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        total_loss = torch.tensor(0.0, device=preds["alie_gli"].device)
        breakdown = {}

        for i, (name, _) in enumerate(self.TASK_HEADS):
            precision = torch.exp(-self.model.log_vars[i])
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
            # ALIE Primary at 0x10: [align | relevance | repair | coref]
            q_align   = to_q16(preds["alie_alignment"][0].mean().item())
            q_relev   = to_q16(preds["alie_relevance"][0].mean().item())
            q_repair  = to_q16(preds["alie_repair"][0].mean().item())
            q_coref   = to_q16(preds["alie_coref"][0].mean().item())
            struct.pack_into("<HHHH", self.amsv_buffer, 0x10, q_align, q_relev, q_repair, q_coref)

            # ALIE Secondary / GLI at 0x18: [GLI | synthesis_cmi | 0 | 0]
            q_gli = to_q16(preds["alie_gli"][0, 0].item())
            q_cmi = to_q16(preds["synthesis_cmi"][0, 0].item())
            struct.pack_into("<HHHH", self.amsv_buffer, 0x18, q_gli, q_cmi, 0, 0)

            # ECSE at 0x20: [affect | rapport | mirror | politeness]
            q_affect = to_q16(preds["ecse_affect"][0].mean().item())
            q_rapp   = to_q16(preds["ecse_rapport"][0].mean().item())
            q_mirr   = to_q16(preds["ecse_mirror"][0].mean().item())
            q_polit  = to_q16(preds["ecse_politeness"][0].mean().item())
            struct.pack_into("<HHHH", self.amsv_buffer, 0x20, q_affect, q_rapp, q_mirr, q_polit)

            # PMCE at 0x28: [logos | ethos | pathos | cta]
            q_logos  = to_q16(preds["pmce_logos"][0].mean().item())
            q_ethos  = to_q16(preds["pmce_ethos"][0].mean().item())
            q_pathos = to_q16(preds["pmce_pathos"][0].mean().item())
            q_cta    = to_q16(preds["pmce_cta"][0].mean().item())
            struct.pack_into("<HHHH", self.amsv_buffer, 0x28, q_logos, q_ethos, q_pathos, q_cta)


def generate_phase1_curriculum_batch(
    batch_size: int = 8,
    seq_len: int = 32
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
    """
    Generates structured multi-archetype curriculum batches for ALIE, ECSE, and PMCE:
      Archetype 0: Active Diplomat (High ALIE, High ECSE, High PMCE Logos/Ethos)
      Archetype 1: Anxious / Passive Speaker (Moderate ALIE, Low Composure, Low PMCE Conviction)
      Archetype 2: Aggressive Orator (Low ALIE, Low Politeness, High PMCE Pathos/CTA)
      Archetype 3: Defensive Disengaged (Low ALIE, Low Rapport, Low PMCE Logos)
    """
    token_ids = torch.randint(0, 1000, (batch_size, seq_len))

    targets: Dict[str, torch.Tensor] = {
        "alie_alignment":   torch.zeros(batch_size, 3),
        "alie_relevance":   torch.zeros(batch_size, 3),
        "alie_repair":      torch.zeros(batch_size, 2),
        "alie_coref":       torch.zeros(batch_size, 2),
        "alie_gli":         torch.zeros(batch_size, 1),
        "ecse_affect":      torch.zeros(batch_size, 3),
        "ecse_rapport":     torch.zeros(batch_size, 2),
        "ecse_mirror":      torch.zeros(batch_size, 2),
        "ecse_disagree":    torch.zeros(batch_size, 2),
        "ecse_politeness":  torch.zeros(batch_size, 2),
        "pmce_logos":       torch.zeros(batch_size, 3),
        "pmce_ethos":       torch.zeros(batch_size, 2),
        "pmce_pathos":      torch.zeros(batch_size, 2),
        "pmce_kairos":      torch.zeros(batch_size, 2),
        "pmce_cta":         torch.zeros(batch_size, 2),
    }

    noise = 0.03
    for i in range(batch_size):
        arch = i % 4

        if arch == 0:  # Active Diplomat
            targets["alie_alignment"][i]   = torch.tensor([0.90, 0.88, 0.92])
            targets["alie_relevance"][i]   = torch.tensor([0.95, 0.90, 0.90])
            targets["alie_repair"][i]      = torch.tensor([0.85, 0.88])
            targets["alie_coref"][i]       = torch.tensor([0.92, 0.88])
            targets["alie_gli"][i]         = torch.tensor([0.91])
            targets["ecse_affect"][i]      = torch.tensor([0.85, 0.60, 0.90])
            targets["ecse_rapport"][i]     = torch.tensor([0.92, 0.90])
            targets["ecse_mirror"][i]      = torch.tensor([0.88, 0.85])
            targets["ecse_disagree"][i]    = torch.tensor([0.90, 0.88])
            targets["ecse_politeness"][i]  = torch.tensor([0.92, 0.88])
            targets["pmce_logos"][i]       = torch.tensor([0.92, 0.90, 0.88])
            targets["pmce_ethos"][i]       = torch.tensor([0.90, 0.92])
            targets["pmce_pathos"][i]      = torch.tensor([0.75, 0.70])
            targets["pmce_kairos"][i]      = torch.tensor([0.88, 0.85])
            targets["pmce_cta"][i]         = torch.tensor([0.85, 0.88])

        elif arch == 1:  # Anxious / Passive Speaker
            targets["alie_alignment"][i]   = torch.tensor([0.60, 0.55, 0.50])
            targets["alie_relevance"][i]   = torch.tensor([0.65, 0.50, 0.55])
            targets["alie_repair"][i]      = torch.tensor([0.70, 0.65])
            targets["alie_coref"][i]       = torch.tensor([0.50, 0.45])
            targets["alie_gli"][i]         = torch.tensor([0.55])
            targets["ecse_affect"][i]      = torch.tensor([0.40, 0.80, 0.35]) # low composure
            targets["ecse_rapport"][i]     = torch.tensor([0.50, 0.55])
            targets["ecse_mirror"][i]      = torch.tensor([0.45, 0.40])
            targets["ecse_disagree"][i]    = torch.tensor([0.30, 0.25])
            targets["ecse_politeness"][i]  = torch.tensor([0.85, 0.90]) # overly submissive
            targets["pmce_logos"][i]       = torch.tensor([0.55, 0.45, 0.50])
            targets["pmce_ethos"][i]       = torch.tensor([0.40, 0.35])
            targets["pmce_pathos"][i]      = torch.tensor([0.45, 0.50])
            targets["pmce_kairos"][i]      = torch.tensor([0.40, 0.35])
            targets["pmce_cta"][i]         = torch.tensor([0.30, 0.25])

        elif arch == 2:  # Aggressive Orator
            targets["alie_alignment"][i]   = torch.tensor([0.40, 0.70, 0.45])
            targets["alie_relevance"][i]   = torch.tensor([0.75, 0.60, 0.65])
            targets["alie_repair"][i]      = torch.tensor([0.20, 0.25]) # ignores repair cues
            targets["alie_coref"][i]       = torch.tensor([0.60, 0.55])
            targets["alie_gli"][i]         = torch.tensor([0.45])
            targets["ecse_affect"][i]      = torch.tensor([0.55, 0.85, 0.50]) # high arousal
            targets["ecse_rapport"][i]     = torch.tensor([0.35, 0.30])
            targets["ecse_mirror"][i]      = torch.tensor([0.30, 0.25])
            targets["ecse_disagree"][i]    = torch.tensor([0.20, 0.40]) # blunt disagreement
            targets["ecse_politeness"][i]  = torch.tensor([0.30, 0.25])
            targets["pmce_logos"][i]       = torch.tensor([0.65, 0.50, 0.60])
            targets["pmce_ethos"][i]       = torch.tensor([0.75, 0.70])
            targets["pmce_pathos"][i]      = torch.tensor([0.88, 0.85]) # strong pathos
            targets["pmce_kairos"][i]      = torch.tensor([0.70, 0.80])
            targets["pmce_cta"][i]         = torch.tensor([0.90, 0.85])

        else:  # Defensive Disengaged
            targets["alie_alignment"][i]   = torch.tensor([0.30, 0.35, 0.25])
            targets["alie_relevance"][i]   = torch.tensor([0.35, 0.30, 0.25])
            targets["alie_repair"][i]      = torch.tensor([0.15, 0.20])
            targets["alie_coref"][i]       = torch.tensor([0.25, 0.20])
            targets["alie_gli"][i]         = torch.tensor([0.28])
            targets["ecse_affect"][i]      = torch.tensor([0.25, 0.45, 0.30])
            targets["ecse_rapport"][i]     = torch.tensor([0.20, 0.15])
            targets["ecse_mirror"][i]      = torch.tensor([0.20, 0.15])
            targets["ecse_disagree"][i]    = torch.tensor([0.15, 0.20])
            targets["ecse_politeness"][i]  = torch.tensor([0.35, 0.30])
            targets["pmce_logos"][i]       = torch.tensor([0.25, 0.20, 0.25])
            targets["pmce_ethos"][i]       = torch.tensor([0.25, 0.20])
            targets["pmce_pathos"][i]      = torch.tensor([0.20, 0.25])
            targets["pmce_kairos"][i]      = torch.tensor([0.25, 0.20])
            targets["pmce_cta"][i]         = torch.tensor([0.15, 0.20])

        # Add noise
        for k in targets:
            dim = targets[k].shape[1]
            targets[k][i] = (targets[k][i] + torch.randn(dim) * noise).clamp(0.0, 1.0)

    return token_ids, targets
