"""
multi_task_trainer.py - Joint Multi-Task Neural Training Pipeline.

Integrates the entire unified ecosystem into a single neural architecture:
1. VCE (Acoustic Phonetics & Prosody)
2. CCTE (8-Dimensional Cognitive Capabilities)
3. RSSE (Recruitment Scenarios, Interview Formats & Compliance)
4. AEEE (Item Response Theory Adaptive Parameters)
5. MAIO (Master AI Orchestration & Cognitive Trajectory Surveillance)
6. Universal Grammar (Syntactic Invariants, Constituency Tree Depth & Concord)
7. Creativity Engine (Metaphorical Tension & Rhetorical Figure Synthesis)
8. Error Diagnostic Engine (16-Class Morphosyntactic Error Detection & Span Localization)
9. Writing Skill Engine (Structural Cohesion, Flesch-Kincaid Readability & Style Register)
10. Pragmatics & Discourse Engine (Speech Act Classification & Gricean Compliance)

Optimized via:
- Kendall & Gal Learnable Homoscedastic Uncertainty Loss Weighting (10 heads).
- PCGrad (Projected Conflicting Gradients) multi-task conflict resolution.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F

from training.gradient_routing import PCGradOptimizer

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1)]

class SharedMultimodalEncoder(nn.Module):
    """
    Shared acoustic-linguistic representation encoder.
    """
    def __init__(self, in_features: int = 80, d_model: int = 256, nhead: int = 4, num_layers: int = 4):
        super().__init__()
        self.input_proj = nn.Linear(in_features, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=512,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [Batch, Time, in_features]
        h = self.input_proj(x)
        h = self.pos_encoder(h)
        h = self.transformer(h)
        return self.norm(h)

class MultiTaskModel(nn.Module):
    """
    Unified Multi-Task Architecture encompassing all 10 capabilities across the system.
    """
    def __init__(self, d_model: int = 256):
        super().__init__()
        self.encoder = SharedMultimodalEncoder(in_features=80, d_model=d_model)

        # 1. VCE Decoder Heads
        self.vce_phoneme_head = nn.Linear(d_model, 128)  # 128 phoneme vocabulary
        self.vce_prosody_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 3)  # F0, WPM, Energy
        )

        # 2. CCTE 8 Cognitive Capability Decoder
        self.ccte_head = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Linear(128, 8),
            nn.Sigmoid()  # 8 normalized capability scores in [0, 1]
        )

        # 3. RSSE Register & Scenario Decoder
        self.rsse_format_head = nn.Linear(d_model, 8)  # 8 interview formats
        self.rsse_compliance_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

        # 4. AEEE IRT Parameter Estimation Head
        self.aeee_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 2)  # [discrimination a, difficulty b]
        )

        # 5. MAIO Master Orchestration & Trajectory Head
        self.maio_trajectory_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 4)  # Cognitive trajectory derivatives (velocity, curvature)
        )
        self.maio_alert_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()  # Anomaly / Surveillance alert probability
        )

        # 6. Universal Grammar & Syntactic Well-Formedness Head
        self.grammar_validity_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()  # P(Grammatically Valid under UG)
        )
        self.grammar_depth_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Linear(32, 1)  # Syntactic tree depth regression
        )

        # 7. Creativity & Rhetorical Figure Head
        self.creativity_tension_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()  # Metaphorical tension score in [0, 1]
        )
        self.creativity_rhetoric_head = nn.Linear(d_model, 5)  # 5 rhetorical figures (Chiasmus, Anaphora, etc.)

        # 8. Error Diagnostic & Localization Head
        self.error_multilabel_head = nn.Linear(d_model, 16)  # 16 error classes
        self.error_span_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 2),
            nn.Sigmoid()  # [Start_ratio, End_ratio] of faulty span
        )

        # 9. Writing Cohesion, Readability & Register Head
        self.writing_cohesion_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()  # Structural cohesion score in [0, 1]
        )
        self.writing_readability_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Linear(32, 1)  # Flesch-Kincaid Grade Level regression
        )
        self.writing_register_head = nn.Linear(d_model, 5)  # 5 stylistic registers

        # 10. Pragmatics & Discourse Speech Act Head
        self.pragmatics_speech_act_head = nn.Linear(d_model, 6)  # Assertive, Directive, Commissive, Expressive, Declarative, Clarification
        self.pragmatics_gricean_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Linear(32, 4),
            nn.Sigmoid()  # 4 Gricean Maxims adherence [Quantity, Quality, Relation, Manner]
        )

        # 11. 7-Point Universal Correctness Framework Head (Part 10 of Guide: Checklist A-G)
        self.checklist_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 7),
            nn.Sigmoid()  # Dimensions [A, B, C, D, E, F, G]
        )

        # 12. Universal Typology & Cross-Linguistic Invariants Head
        self.typology_family_head = nn.Linear(d_model, 11)        # 11 language families
        self.typology_morph_head = nn.Linear(d_model, 4)          # 4 morphological types
        self.typology_align_head = nn.Linear(d_model, 4)          # 4 alignments
        self.typology_dir_head = nn.Linear(d_model, 2)            # 2 directions (Head-Initial, Head-Final)
        self.typology_pillars_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 8),
            nn.Sigmoid()                                          # 8 continuous pillar scores in [0, 1]
        )

        # 13. BandhuPrime Dedicated Skills, Eras & 5-Stage Editing Head
        self.bandhu_skill_head = nn.Linear(d_model, 6)            # 6 skills
        self.bandhu_era_head = nn.Linear(d_model, 4)              # 4 historical eras
        self.bandhu_stage_head = nn.Linear(d_model, 5)            # 5 editing stages
        self.bandhu_scores_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 3),
            nn.Sigmoid()                                          # [structural, register, consistency] in [0, 1]
        )

        # 14. ALIE — Active Listening Intelligence (5 dims: align, relevance, repair, coreference, GLI)
        self.alie_head = nn.Sequential(
            nn.Linear(d_model, 64), nn.GELU(), nn.Linear(64, 5), nn.Sigmoid()
        )

        # 15. ECSE — Emotional/Social Calibration (5 dims: affect, rapport, mirror, disagree, politeness)
        self.ecse_head = nn.Sequential(
            nn.Linear(d_model, 64), nn.GELU(), nn.Linear(64, 5), nn.Sigmoid()
        )

        # 16. PMCE — Persuasion & Message Construction (5 dims: logos, ethos, pathos, kairos, cta)
        self.pmce_head = nn.Sequential(
            nn.Linear(d_model, 64), nn.GELU(), nn.Linear(64, 5), nn.Sigmoid()
        )

        # 17. HCTE — Human Cognitive Thinking (3 dims: optimism, pessimism, cognitive_tension)
        self.hcte_head = nn.Sequential(
            nn.Linear(d_model, 64), nn.GELU(), nn.Linear(64, 3), nn.Sigmoid()
        )

        # Kendall & Gal Learnable Homoscedastic Log-Variances for all 17 unified tasks
        # s_i = log(sigma_i^2)
        self.log_vars = nn.Parameter(torch.zeros(17))

    def load_state_dict(self, state_dict: Dict[str, Any], strict: bool = True, assign: bool = False):
        """
        Backward-compatible checkpoint loader: allows legacy 13-task checkpoints
        to seamlessly load into the expanded 17-task MultiTaskModel.
        """
        if "log_vars" in state_dict and state_dict["log_vars"].shape == torch.Size([13]):
            padded_log_vars = torch.zeros(17, dtype=state_dict["log_vars"].dtype, device=state_dict["log_vars"].device)
            padded_log_vars[:13] = state_dict["log_vars"]
            state_dict = dict(state_dict)
            state_dict["log_vars"] = padded_log_vars
            return super().load_state_dict(state_dict, strict=False, assign=assign)
        return super().load_state_dict(state_dict, strict=strict, assign=assign)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        h = self.encoder(x)          # [Batch, Time, d_model]
        h_pool = h.mean(dim=1)       # [Batch, d_model] pooled sentence representation

        return {
            # 1. VCE
            "phoneme_logits": self.vce_phoneme_head(h),
            "prosody_preds": self.vce_prosody_head(h),
            # 2. CCTE
            "cognitive_scores": self.ccte_head(h_pool),
            # 3. RSSE
            "format_logits": self.rsse_format_head(h_pool),
            "compliance_pred": self.rsse_compliance_head(h_pool),
            # 4. AEEE
            "irt_params": self.aeee_head(h_pool),
            # 5. MAIO
            "maio_trajectory": self.maio_trajectory_head(h_pool),
            "maio_alert": self.maio_alert_head(h_pool),
            # 6. Universal Grammar
            "grammar_validity": self.grammar_validity_head(h_pool),
            "grammar_depth": self.grammar_depth_head(h_pool),
            # 7. Creativity
            "creativity_tension": self.creativity_tension_head(h_pool),
            "creativity_rhetoric": self.creativity_rhetoric_head(h_pool),
            # 8. Error Diagnostics
            "error_logits": self.error_multilabel_head(h_pool),
            "error_span": self.error_span_head(h_pool),
            # 9. Writing Skills
            "writing_cohesion": self.writing_cohesion_head(h_pool),
            "writing_readability": self.writing_readability_head(h_pool),
            "writing_register": self.writing_register_head(h_pool),
            # 10. Pragmatics
            "speech_act_logits": self.pragmatics_speech_act_head(h_pool),
            "gricean_maxims": self.pragmatics_gricean_head(h_pool),
            # 11. 7-Point Universal Correctness Framework
            "checklist_scores": self.checklist_head(h_pool),
            # 12. Universal Typology & Cross-Linguistic Invariants
            "typology_family_logits": self.typology_family_head(h_pool),
            "typology_morph_logits": self.typology_morph_head(h_pool),
            "typology_align_logits": self.typology_align_head(h_pool),
            "typology_dir_logits": self.typology_dir_head(h_pool),
            "typology_pillar_scores": self.typology_pillars_head(h_pool),
            # 13. BandhuPrime Dedicated Skills, Eras & 5-Stage Editing
            "bandhu_skill_logits": self.bandhu_skill_head(h_pool),
            "bandhu_era_logits":   self.bandhu_era_head(h_pool),
            "bandhu_stage_logits": self.bandhu_stage_head(h_pool),
            "bandhu_scores":       self.bandhu_scores_head(h_pool),
            # 14. ALIE — Active Listening Intelligence
            "alie_scores":  self.alie_head(h_pool),
            # 15. ECSE — Emotional/Social Calibration
            "ecse_scores":  self.ecse_head(h_pool),
            # 16. PMCE — Persuasion & Message Construction
            "pmce_scores":  self.pmce_head(h_pool),
            # 17. HCTE — Human Cognitive Thinking Engine
            "hcte_scores":  self.hcte_head(h_pool),
        }

class MultiTaskTrainer:
    """
    Unified Multi-Task Trainer managing all 13 domain losses with Kendall & Gal weighting and PCGrad.
    """
    def __init__(self, model: MultiTaskModel, lr: float = 1e-4, use_pcgrad: bool = True):
        self.model = model
        self.use_pcgrad = use_pcgrad
        base_optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-4)
        
        if self.use_pcgrad:
            self.optimizer = PCGradOptimizer(base_optimizer)
        else:
            self.optimizer = base_optimizer

    def compute_losses(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> Tuple[List[torch.Tensor], torch.Tensor]:
        """
        Computes the 13 distinct task domain losses and their Kendall & Gal uncertainty-weighted sum.
        """
        # Task 1: VCE Phonetics & Prosody
        b, t, c = predictions["phoneme_logits"].shape
        loss_vce_phoneme = F.cross_entropy(
            predictions["phoneme_logits"].reshape(-1, c),
            targets["phonemes"].reshape(-1)
        )
        loss_vce_prosody = F.mse_loss(predictions["prosody_preds"], targets["prosody"])
        loss_vce = loss_vce_phoneme + loss_vce_prosody

        # Task 2: CCTE Cognitive Capabilities (8 dims)
        loss_ccte = F.mse_loss(predictions["cognitive_scores"], targets["cognitive"])

        # Task 3: RSSE Recruitment Scenario Format & Compliance
        loss_rsse_format = F.cross_entropy(predictions["format_logits"], targets["format"])
        loss_rsse_comp = F.mse_loss(predictions["compliance_pred"], targets["compliance"])
        loss_rsse = loss_rsse_format + loss_rsse_comp

        # Task 4: AEEE Adaptive IRT Parameter Estimation
        loss_aeee = F.mse_loss(predictions["irt_params"], targets["irt"])

        # Task 5: MAIO Master Cognitive Trajectory & Alert Surveillance
        loss_maio_traj = F.mse_loss(predictions["maio_trajectory"], targets["maio_trajectory"])
        loss_maio_alert = F.binary_cross_entropy(predictions["maio_alert"], targets["maio_alert"])
        loss_maio = loss_maio_traj + loss_maio_alert

        # Task 6: Universal Grammar & Syntactic Well-Formedness
        loss_ug_valid = F.binary_cross_entropy(predictions["grammar_validity"], targets["grammar_validity"])
        loss_ug_depth = F.mse_loss(predictions["grammar_depth"], targets["grammar_depth"])
        loss_grammar = loss_ug_valid + loss_ug_depth

        # Task 7: Creativity, Metaphorical Tension & Rhetoric
        loss_creativity_tension = F.mse_loss(predictions["creativity_tension"], targets["creativity_tension"])
        loss_creativity_rhetoric = F.cross_entropy(predictions["creativity_rhetoric"], targets["creativity_rhetoric"])
        loss_creativity = loss_creativity_tension + loss_creativity_rhetoric

        # Task 8: Linguistic Error Detection & Span Localization
        loss_error_cls = F.binary_cross_entropy_with_logits(predictions["error_logits"], targets["error_labels"])
        loss_error_span = F.mse_loss(predictions["error_span"], targets["error_span"])
        loss_error = loss_error_cls + loss_error_span

        # Task 9: Writing Cohesion, Readability & Register
        loss_writing_cohesion = F.mse_loss(predictions["writing_cohesion"], targets["writing_cohesion"])
        loss_writing_readability = F.mse_loss(predictions["writing_readability"], targets["writing_readability"])
        loss_writing_register = F.cross_entropy(predictions["writing_register"], targets["writing_register"])
        loss_writing = loss_writing_cohesion + loss_writing_readability + loss_writing_register

        # Task 10: Pragmatics & Gricean Discourse
        loss_speech_act = F.cross_entropy(predictions["speech_act_logits"], targets["speech_act"])
        loss_gricean = F.mse_loss(predictions["gricean_maxims"], targets["gricean_maxims"])
        loss_pragmatics = loss_speech_act + loss_gricean

        # Task 11: 7-Point Universal Correctness Framework MSE
        loss_checklist = F.mse_loss(predictions["checklist_scores"], targets["checklist_scores"])

        # Task 12: Universal Typology & Cross-Linguistic Dimensions
        loss_typ_fam = F.cross_entropy(predictions["typology_family_logits"], targets["typology_family"])
        loss_typ_morph = F.cross_entropy(predictions["typology_morph_logits"], targets["typology_morph"])
        loss_typ_align = F.cross_entropy(predictions["typology_align_logits"], targets["typology_align"])
        loss_typ_dir = F.cross_entropy(predictions["typology_dir_logits"], targets["typology_dir"])
        loss_typ_pillars = F.mse_loss(predictions["typology_pillar_scores"], targets["typology_pillars"])
        loss_typology = loss_typ_fam + loss_typ_morph + loss_typ_align + loss_typ_dir + loss_typ_pillars

        # Task 13: BandhuPrime Dedicated Skills, Eras & 5-Stage Editing
        loss_bandhu_skill  = F.cross_entropy(predictions["bandhu_skill_logits"], targets["bandhu_skill"])
        loss_bandhu_era    = F.cross_entropy(predictions["bandhu_era_logits"],   targets["bandhu_era"])
        loss_bandhu_stage  = F.cross_entropy(predictions["bandhu_stage_logits"], targets["bandhu_stage"])
        loss_bandhu_scores = F.mse_loss(predictions["bandhu_scores"],             targets["bandhu_scores"])
        loss_bandhu = loss_bandhu_skill + loss_bandhu_era + loss_bandhu_stage + loss_bandhu_scores

        # Task 14: ALIE — Active Listening Intelligence [align, relevance, repair, coref, GLI]
        loss_alie = F.mse_loss(predictions["alie_scores"], targets["alie_scores"])

        # Task 15: ECSE — Emotional/Social Calibration [affect, rapport, mirror, disagree, politeness]
        loss_ecse = F.mse_loss(predictions["ecse_scores"], targets["ecse_scores"])

        # Task 16: PMCE — Persuasion & Message Construction [logos, ethos, pathos, kairos, cta]
        loss_pmce = F.mse_loss(predictions["pmce_scores"], targets["pmce_scores"])

        # Task 17: HCTE — Human Cognitive Thinking [optimism, pessimism, cognitive_tension]
        # Pre-mortem = pessimism dimension → 2x weight applied via extra loss term
        loss_hcte_base  = F.mse_loss(predictions["hcte_scores"], targets["hcte_scores"])
        loss_hcte_premortem = F.mse_loss(
            predictions["hcte_scores"][:, 1:2], targets["hcte_scores"][:, 1:2]
        ) * 2.0   # pessimism dim 2x weight
        loss_hcte = loss_hcte_base + loss_hcte_premortem

        task_losses = [
            loss_vce,
            loss_ccte,
            loss_rsse,
            loss_aeee,
            loss_maio,
            loss_grammar,
            loss_creativity,
            loss_error,
            loss_writing,
            loss_pragmatics,
            loss_checklist,
            loss_typology,
            loss_bandhu,
            loss_alie,
            loss_ecse,
            loss_pmce,
            loss_hcte,
        ]

        # Kendall & Gal Uncertainty Weighting:
        # L_total = sum_i [ 0.5 * exp(-s_i) * L_i + 0.5 * s_i ]
        weighted_loss = torch.tensor(0.0, device=predictions["phoneme_logits"].device)
        for i, loss in enumerate(task_losses):
            precision = torch.exp(-self.model.log_vars[i])
            weighted_loss = weighted_loss + 0.5 * precision * loss + 0.5 * self.model.log_vars[i]

        return task_losses, weighted_loss

    def train_step(self, x: torch.Tensor, targets: Dict[str, torch.Tensor]) -> Dict[str, float]:
        self.model.train()
        predictions = self.model(x)
        task_losses, total_weighted_loss = self.compute_losses(predictions, targets)

        if self.use_pcgrad and isinstance(self.optimizer, PCGradOptimizer):
            self.optimizer.pcgrad_backward(task_losses)
            self.optimizer.step()
        else:
            self.optimizer.zero_grad()
            total_weighted_loss.backward()
            self.optimizer.step()

        return {
            "loss_vce": task_losses[0].item(),
            "loss_ccte": task_losses[1].item(),
            "loss_rsse": task_losses[2].item(),
            "loss_aeee": task_losses[3].item(),
            "loss_maio": task_losses[4].item(),
            "loss_grammar": task_losses[5].item(),
            "loss_creativity": task_losses[6].item(),
            "loss_error": task_losses[7].item(),
            "loss_writing": task_losses[8].item(),
            "loss_pragmatics": task_losses[9].item(),
            "loss_checklist": task_losses[10].item(),
            "loss_typology": task_losses[11].item(),
            "loss_bandhu": task_losses[12].item(),
            "loss_alie": task_losses[13].item(),
            "loss_ecse": task_losses[14].item(),
            "loss_pmce": task_losses[15].item(),
            "loss_hcte": task_losses[16].item(),
            "total_weighted_loss": total_weighted_loss.item()
        }

    def validate_step(self, x: torch.Tensor, targets: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """
        Evaluation on a validation batch without gradient updates (Gap 4 Overfitting Guard).
        """
        self.model.eval()
        with torch.no_grad():
            predictions = self.model(x)
            task_losses, total_weighted_loss = self.compute_losses(predictions, targets)

        return {
            "val_loss_vce": task_losses[0].item(),
            "val_loss_ccte": task_losses[1].item(),
            "val_loss_rsse": task_losses[2].item(),
            "val_loss_aeee": task_losses[3].item(),
            "val_loss_maio": task_losses[4].item(),
            "val_loss_grammar": task_losses[5].item(),
            "val_loss_creativity": task_losses[6].item(),
            "val_loss_error": task_losses[7].item(),
            "val_loss_writing": task_losses[8].item(),
            "val_loss_pragmatics": task_losses[9].item(),
            "val_loss_checklist": task_losses[10].item(),
            "val_loss_typology": task_losses[11].item(),
            "val_loss_bandhu": task_losses[12].item(),
            "val_loss_alie": task_losses[13].item(),
            "val_loss_ecse": task_losses[14].item(),
            "val_loss_pmce": task_losses[15].item(),
            "val_loss_hcte": task_losses[16].item(),
            "val_total_weighted_loss": total_weighted_loss.item()
        }
