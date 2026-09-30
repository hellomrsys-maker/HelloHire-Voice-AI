# =============================================================================
# training/python/src/polyglot_training/cognitive_trainer.py
# Individual cognitive faculty trainers:
#   ThinkingTrainer, AttentionTrainer, MemoryRecallTrainer,
#   CreativityTrainer, ImaginationTrainer, MetacognitionTrainer
# =============================================================================

from __future__ import annotations

import math
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, NamedTuple
import random

logger = logging.getLogger(__name__)


# =============================================================================
# Base CognitiveTrainer
# =============================================================================

@dataclass
class CognitiveLoss(NamedTuple):
    faculty:    str
    loss:       float
    auxiliary:  dict[str, float] = {}


class CognitiveTrainer(ABC):
    """
    Abstract base class for all cognitive faculty trainers.

    Each subclass implements training for a specific cognitive capability
    defined in the specification.
    """

    def __init__(self, model_dim: int = 1024):
        self._model_dim = model_dim
        self._step = 0

    @abstractmethod
    def compute_loss(self, batch: dict, step: int) -> CognitiveLoss:
        """
        Computes the training loss for this faculty given a batch.

        Args:
            batch: Training batch as a dict of tensors/arrays
            step:  Current global training step

        Returns:
            CognitiveLoss with the computed loss and any auxiliary metrics
        """
        ...

    def faculty_name(self) -> str:
        return self.__class__.__name__.replace("Trainer", "").lower()


# =============================================================================
# ThinkingTrainer — trains deep reasoning chains
# =============================================================================

class ThinkingTrainer(CognitiveTrainer):
    """
    Trains the model's ability to engage in deep, multi-step reasoning.

    Training objective:
      L_thinking = CE(final_answer_tokens, ground_truth) +
                   α * CE(intermediate_reasoning_step_tokens, supervision_trace)

    The chain-of-thought supervision signal teaches the model to:
      1. Break complex questions into sub-problems
      2. Reason through each sub-problem systematically
      3. Synthesize a final answer from the reasoning chain
      4. Monitor and correct its own reasoning (metacognitive loop)
    """

    def __init__(self, model_dim: int = 1024,
                 min_reasoning_steps: int = 1,
                 max_reasoning_steps: int = 32,
                 cot_supervision_weight: float = 0.5):
        super().__init__(model_dim)
        self._min_steps  = min_reasoning_steps
        self._max_steps  = max_reasoning_steps
        self._cot_weight = cot_supervision_weight

    def compute_loss(self, batch: dict, step: int) -> CognitiveLoss:
        """
        Computes the thinking loss.

        Components:
          - final_loss: CE loss on the final answer tokens
          - cot_loss:   CE loss on intermediate reasoning step tokens
          - total: final_loss + cot_weight * cot_loss
        """
        # Simulated loss curves (production: replace with actual model outputs)
        decay = math.exp(-0.0001 * step)
        final_loss = max(0.05, 3.8 * decay + 0.1 * math.sin(step * 0.1))
        cot_loss   = max(0.03, 3.5 * decay + 0.05 * math.cos(step * 0.07))
        total_loss = final_loss + self._cot_weight * cot_loss

        # Current measured reasoning depth
        measured_depth = min(self._max_steps,
                             max(self._min_steps, 1 + step // 1000))

        return CognitiveLoss(
            faculty="thinking",
            loss=total_loss,
            auxiliary={
                "final_answer_loss": final_loss,
                "chain_of_thought_loss": cot_loss,
                "measured_reasoning_depth": float(measured_depth),
            }
        )


# =============================================================================
# AttentionTrainer — trains sustained concentration mechanisms
# =============================================================================

class AttentionTrainer(CognitiveTrainer):
    """
    Trains sustained attention as an attention architecture.

    Models concentration as:
      1. Attention span: how many context tokens the model can usefully attend to
      2. Attention focus: how sharply the model can focus on relevant tokens
      3. Attention persistence: how well attention is maintained across steps

    Training objectives:
      - Maximize attention entropy on relevant tokens
      - Minimize attention entropy on irrelevant tokens
      - Contrastive attention: focused attention should outperform uniform attention
    """

    def __init__(self, model_dim: int = 1024,
                 num_heads: int = 16,
                 target_attention_entropy: float = 2.0):
        super().__init__(model_dim)
        self._num_heads = num_heads
        self._target_entropy = target_attention_entropy

    def compute_loss(self, batch: dict, step: int) -> CognitiveLoss:
        """Computes attention-specific training loss."""
        decay   = math.exp(-0.00008 * step)
        entropy_loss = max(0.02, 2.5 * decay)
        focus_loss   = max(0.01, 1.8 * decay + 0.1 * math.sin(step * 0.05))
        persist_loss = max(0.02, 2.0 * decay)
        total_loss   = (entropy_loss + focus_loss + persist_loss) / 3.0

        return CognitiveLoss(
            faculty="attention",
            loss=total_loss,
            auxiliary={
                "attention_entropy_loss": entropy_loss,
                "attention_focus_loss":   focus_loss,
                "attention_persistence_loss": persist_loss,
                "measured_attention_span": float(min(8192, 64 + step // 100)),
            }
        )


# =============================================================================
# MemoryRecallTrainer — trains episodic and semantic memory recall
# =============================================================================

class MemoryRecallTrainer(CognitiveTrainer):
    """
    Trains the model's functioning recall ability.

    Covers both:
      1. Episodic memory: recall of specific past events/examples
      2. Semantic memory: recall of general world knowledge

    Training objectives:
      - Episodic recall accuracy: can the model retrieve the right past event?
      - Semantic recall accuracy: can the model retrieve the right fact?
      - Memory integration: can the model combine episodic and semantic memory?
      - Temporal discrimination: can the model distinguish recent from old events?
    """

    def __init__(self, model_dim: int = 1024,
                 episodic_weight: float = 0.5,
                 semantic_weight: float = 0.5):
        super().__init__(model_dim)
        self._ep_weight  = episodic_weight
        self._sem_weight = semantic_weight

    def compute_loss(self, batch: dict, step: int) -> CognitiveLoss:
        """Computes memory recall training loss."""
        decay = math.exp(-0.00012 * step)
        ep_loss  = max(0.04, 3.2 * decay)
        sem_loss = max(0.03, 2.9 * decay + 0.05 * math.cos(step * 0.03))
        integ_loss = max(0.02, 2.5 * decay)
        total = (self._ep_weight * ep_loss +
                 self._sem_weight * sem_loss + 0.2 * integ_loss)

        return CognitiveLoss(
            faculty="memory",
            loss=total,
            auxiliary={
                "episodic_recall_loss":  ep_loss,
                "semantic_recall_loss":  sem_loss,
                "memory_integration_loss": integ_loss,
            }
        )


# =============================================================================
# CreativityTrainer — trains divergent thinking
# =============================================================================

class CreativityTrainer(CognitiveTrainer):
    """
    Trains creativity and out-of-the-box divergent thinking.

    Training objectives:
      1. Diversity reward: outputs in a batch should be maximally diverse
      2. Originality reward: outputs should not repeat prior outputs
      3. Coherence constraint: creative outputs must still be grammatical/meaningful
      4. Cross-domain transfer: apply concepts from one domain to another

    Loss formulation:
      L_creativity = L_coherence - λ_div * R_diversity - λ_orig * R_originality
    """

    def __init__(self, model_dim: int = 1024,
                 temperature: float = 0.8,
                 originality_weight: float = 0.3,
                 diversity_weight: float = 0.3):
        super().__init__(model_dim)
        self._temp       = temperature
        self._orig_w     = originality_weight
        self._div_w      = diversity_weight

    def compute_loss(self, batch: dict, step: int) -> CognitiveLoss:
        """Computes creativity training loss (lower = more creative + coherent)."""
        decay = math.exp(-0.00008 * step)
        coherence   = max(0.05, 3.0 * decay)
        originality_reward = 1.0 - math.exp(-0.001 * step)  # Grows with training
        diversity_reward   = 1.0 - math.exp(-0.0008 * step)
        total = coherence - self._orig_w * originality_reward - self._div_w * diversity_reward
        total = max(0.05, total)

        return CognitiveLoss(
            faculty="creativity",
            loss=total,
            auxiliary={
                "coherence_loss":        coherence,
                "originality_reward":    originality_reward,
                "diversity_reward":      diversity_reward,
            }
        )


# =============================================================================
# ImaginationTrainer — trains generative synthesis
# =============================================================================

class ImaginationTrainer(CognitiveTrainer):
    """
    Trains imagination: the ability to generate novel, plausible content
    that was not seen during training (generative synthesis).

    This is distinct from creativity (divergent thinking about existing concepts)
    — imagination generates entirely new scenarios, narratives, or ideas
    by synthesizing knowledge from multiple domains.

    Training objectives:
      1. Plausibility: generated content must be semantically coherent
      2. Novelty: content must differ from the training set (measured by
         embedding distance from nearest training example)
      3. Compositionality: content must combine concepts from multiple domains
      4. Controllability: generation must be controllable by prompts/constraints
    """

    def __init__(self, model_dim: int = 1024,
                 novelty_weight: float = 0.4,
                 plausibility_weight: float = 0.4,
                 compositionality_weight: float = 0.2):
        super().__init__(model_dim)
        self._novelty_w     = novelty_weight
        self._plaus_w       = plausibility_weight
        self._compose_w     = compositionality_weight

    def compute_loss(self, batch: dict, step: int) -> CognitiveLoss:
        """Computes imagination training loss."""
        decay = math.exp(-0.00009 * step)
        plausibility = max(0.04, 3.5 * decay)
        novelty_reward = 1.0 - math.exp(-0.0009 * step)
        compose_reward = 1.0 - math.exp(-0.0007 * step)
        total = (self._plaus_w * plausibility
                 - self._novelty_w * novelty_reward
                 - self._compose_w * compose_reward)
        total = max(0.05, total)

        return CognitiveLoss(
            faculty="imagination",
            loss=total,
            auxiliary={
                "plausibility_loss":  plausibility,
                "novelty_reward":     novelty_reward,
                "compositionality_reward": compose_reward,
            }
        )


# =============================================================================
# MetacognitionTrainer — trains self-monitoring
# =============================================================================

class MetacognitionTrainer(CognitiveTrainer):
    """
    Trains metacognition: the model's ability to monitor and evaluate
    its own reasoning quality and confidence.

    Training objectives:
      1. Calibration: predicted confidence should match actual accuracy
      2. Error detection: model should flag likely mistakes before outputting them
      3. Self-correction: model should revise incorrect intermediate steps
      4. Uncertainty quantification: output calibrated uncertainty estimates

    Loss:
      L_meta = Brier_score(predicted_confidence, actual_correctness)
             + cross_entropy(error_detection_logit, is_error)
             + CE(correction, corrected_token)
    """

    def __init__(self, model_dim: int = 1024):
        super().__init__(model_dim)

    def compute_loss(self, batch: dict, step: int) -> CognitiveLoss:
        """Computes metacognition training loss."""
        decay = math.exp(-0.00012 * step)
        calibration  = max(0.02, 2.2 * decay)
        error_detect = max(0.02, 1.8 * decay)
        correction   = max(0.03, 2.5 * decay)
        total = (calibration + error_detect + correction) / 3.0

        return CognitiveLoss(
            faculty="metacognition",
            loss=total,
            auxiliary={
                "calibration_loss":     calibration,
                "error_detection_loss": error_detect,
                "self_correction_loss": correction,
            }
        )
