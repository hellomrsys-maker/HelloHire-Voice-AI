"""
ccte_subagents.py — Python Sub-Agents for the Eight Cognitive Capabilities.

Implements all 8 domain intelligence sub-agents:
  1. ThinkingAbilitySubAgent
  2. ConcentrationFocusSubAgent
  3. RecallMemorySubAgent
  4. CreativeThinkingSubAgent
  5. ImaginationSimulationSubAgent
  6. AnalyticalThinkingSubAgent
  7. VerbalReasoningSubAgent
  8. EmotionalRegulationSubAgent

Synchronizes real-time scores directly into the 64-byte AMSV State Vector.
"""

from typing import Dict, List, Any, Optional
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from amsv.python.amsv_embedded import AMSVEmbeddedView


class BaseCognitiveSubAgent:
    def __init__(self, capability_index: int, name: str, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.capability_index = capability_index
        self.name = name
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.score_history: List[float] = []

    def sync_score_to_amsv(self, score: float) -> None:
        clamped = max(0.0, min(1.0, float(score)))
        self.amsv.set_cognitive_score(self.capability_index, clamped)
        self.score_history.append(clamped)


# 1. Thinking Ability Sub-Agent
class ThinkingAbilitySubAgent(BaseCognitiveSubAgent):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        super().__init__(0, "Thinking Ability", amsv_view)

    def evaluate(self, inference_steps: List[str]) -> Dict[str, Any]:
        chain_len = len(inference_steps)
        reasoning_depth = min(10, chain_len * 2)
        decomposition_score = 0.90 if chain_len >= 3 else 0.50
        composite = min(1.0, (reasoning_depth / 10.0) * 0.6 + decomposition_score * 0.4)
        self.sync_score_to_amsv(composite)
        return {
            "capability": self.name,
            "inference_chain_length": chain_len,
            "reasoning_depth": reasoning_depth,
            "score": round(composite, 3)
        }


# 2. Concentration and Focus Sub-Agent
class ConcentrationFocusSubAgent(BaseCognitiveSubAgent):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        super().__init__(1, "Concentration & Focus", amsv_view)

    def evaluate(self, speech_consistency: float, pause_variance: float) -> Dict[str, Any]:
        distraction_resistance = max(0.0, 1.0 - (pause_variance / 4.0))
        focus_score = (distraction_resistance * 0.6) + (speech_consistency * 0.4)
        self.sync_score_to_amsv(focus_score)
        return {
            "capability": self.name,
            "distraction_resistance": round(distraction_resistance, 3),
            "score": round(focus_score, 3)
        }


# 3. Recall and Memory Sub-Agent
class RecallMemorySubAgent(BaseCognitiveSubAgent):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        super().__init__(2, "Recall & Memory Function", amsv_view)

    def evaluate(self, recalled_items: int, target_items: int, latency_sec: float) -> Dict[str, Any]:
        activation = recalled_items / max(1, target_items)
        latency_penalty = min(0.3, latency_sec * 0.05)
        score = max(0.0, min(1.0, activation - latency_penalty))
        self.sync_score_to_amsv(score)
        return {
            "capability": self.name,
            "working_memory_span": recalled_items,
            "recall_latency_sec": latency_sec,
            "score": round(score, 3)
        }


# 4. Creative Thinking Sub-Agent
class CreativeThinkingSubAgent(BaseCognitiveSubAgent):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        super().__init__(3, "Creative Thinking", amsv_view)

    def evaluate(self, cluster_count: int, mean_semantic_distance: float) -> Dict[str, Any]:
        divergence = min(1.0, cluster_count / 5.0)
        novelty = (divergence * 0.5) + (min(1.0, mean_semantic_distance) * 0.5)
        self.sync_score_to_amsv(novelty)
        return {
            "capability": self.name,
            "semantic_clusters": cluster_count,
            "novelty_index": round(novelty, 3),
            "score": round(novelty, 3)
        }


# 5. Imagination and Mental Simulation Sub-Agent
class ImaginationSimulationSubAgent(BaseCognitiveSubAgent):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        super().__init__(4, "Imagination & Mental Simulation", amsv_view)

    def evaluate(self, counterfactual_count: int, sensory_detail_ratio: float) -> Dict[str, Any]:
        vividness = min(1.0, sensory_detail_ratio / 0.15)
        branching = min(1.0, counterfactual_count / 4.0)
        score = (vividness * 0.5) + (branching * 0.5)
        self.sync_score_to_amsv(score)
        return {
            "capability": self.name,
            "counterfactual_branches": counterfactual_count,
            "vividness": round(vividness, 3),
            "score": round(score, 3)
        }


# 6. Analytical and Critical Thinking Sub-Agent
class AnalyticalThinkingSubAgent(BaseCognitiveSubAgent):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        super().__init__(5, "Analytical & Critical Thinking", amsv_view)

    def evaluate(self, is_valid_logic: bool, fallacy_count: int, evidence_weight: float) -> Dict[str, Any]:
        valid_score = 1.0 if is_valid_logic else 0.3
        score = max(0.0, min(1.0, (valid_score * 0.5 + evidence_weight * 0.5) - fallacy_count * 0.2))
        self.sync_score_to_amsv(score)
        return {
            "capability": self.name,
            "logical_validity": is_valid_logic,
            "fallacies_detected": fallacy_count,
            "score": round(score, 3)
        }


# 7. Verbal Reasoning Sub-Agent
class VerbalReasoningSubAgent(BaseCognitiveSubAgent):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        super().__init__(6, "Verbal Reasoning", amsv_view)

    def evaluate(self, parse_depth: int, coherence_cosine: float, inferential_gaps: int) -> Dict[str, Any]:
        score = max(0.0, min(1.0, coherence_cosine - (inferential_gaps * 0.1)))
        self.sync_score_to_amsv(score)
        return {
            "capability": self.name,
            "syntactic_depth": parse_depth,
            "semantic_coherence": round(coherence_cosine, 3),
            "score": round(score, 3)
        }


# 8. Emotional Regulation Sub-Agent
class EmotionalRegulationSubAgent(BaseCognitiveSubAgent):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        super().__init__(7, "Emotional Regulation", amsv_view)

    def evaluate(self, pitch_tremor_hz: float, vocal_shimmer: float, vocal_jitter: float) -> Dict[str, Any]:
        stress = min(1.0, (pitch_tremor_hz / 5.0) * 0.5 + (vocal_jitter / 0.02) * 0.5)
        confidence = max(0.0, min(1.0, 1.0 - stress))
        self.sync_score_to_amsv(confidence)
        return {
            "capability": self.name,
            "stress_biomarker": round(stress, 3),
            "confidence_index": round(confidence, 3),
            "score": round(confidence, 3)
        }


# Master Coordinator across all 8 sub-agents
class CCTECoordinator:
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.agents = [
            ThinkingAbilitySubAgent(self.amsv),
            ConcentrationFocusSubAgent(self.amsv),
            RecallMemorySubAgent(self.amsv),
            CreativeThinkingSubAgent(self.amsv),
            ImaginationSimulationSubAgent(self.amsv),
            AnalyticalThinkingSubAgent(self.amsv),
            VerbalReasoningSubAgent(self.amsv),
            EmotionalRegulationSubAgent(self.amsv),
        ]

    def evaluate_all(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        # 1. Thinking
        results["thinking"] = self.agents[0].evaluate(parameters.get("inference_steps", ["premise", "deduction", "conclusion"]))
        # 2. Focus
        results["focus"] = self.agents[1].evaluate(parameters.get("speech_consistency", 0.85), parameters.get("pause_variance", 0.4))
        # 3. Memory
        results["memory"] = self.agents[2].evaluate(parameters.get("recalled_items", 6), parameters.get("target_items", 7), parameters.get("latency_sec", 1.1))
        # 4. Creativity
        results["creativity"] = self.agents[3].evaluate(parameters.get("cluster_count", 4), parameters.get("mean_distance", 0.78))
        # 5. Imagination
        results["imagination"] = self.agents[4].evaluate(parameters.get("counterfactuals", 3), parameters.get("sensory_ratio", 0.12))
        # 6. Analytical
        results["analytical"] = self.agents[5].evaluate(parameters.get("valid_logic", True), parameters.get("fallacies", 0), parameters.get("evidence_weight", 0.88))
        # 7. Verbal
        results["verbal"] = self.agents[6].evaluate(parameters.get("parse_depth", 4), parameters.get("coherence", 0.82), parameters.get("gaps", 0))
        # 8. Emotional
        results["emotional"] = self.agents[7].evaluate(parameters.get("tremor_hz", 1.2), parameters.get("shimmer", 0.02), parameters.get("jitter", 0.008))

        # Read back verified AMSV scores
        amsv_scores = self.amsv.get_all_cognitive_scores()
        return {
            "evaluations": results,
            "amsv_synchronized_scores": amsv_scores,
            "global_cognitive_index": round(sum(amsv_scores) / 8.0, 3)
        }

    def evaluate_candidate_turn(self, utterance: str, speech_wpm: float = 135.0) -> Dict[str, float]:
        """
        Convenience evaluator mapping transcript to the 8 cognitive capability scores.
        """
        words = utterance.split()
        word_count = len(words)

        # Heuristics for cognitive signals
        analytical_markers = ["because", "therefore", "trade-off", "matrix", "consensus", "latency", "architecture"]
        analytical_score = min(1.0, 0.4 + sum(1 for m in analytical_markers if m in utterance.lower()) * 0.1)

        emotional_score = 0.85 if "panic" not in utterance.lower() else 0.45
        focus_score = 0.90 if abs(speech_wpm - 135.0) < 25.0 else 0.65
        thinking_score = min(1.0, 0.5 + (word_count / 80.0) * 0.4)
        memory_score = 0.80
        creativity_score = 0.75
        imagination_score = 0.70
        verbal_score = min(1.0, 0.5 + (word_count / 60.0) * 0.4)

        scores = {
            "thinking_ability": thinking_score,
            "concentration_focus": focus_score,
            "memory_recall": memory_score,
            "creative_thinking": creativity_score,
            "imagination": imagination_score,
            "analytical_thinking": analytical_score,
            "verbal_reasoning": verbal_score,
            "emotional_regulation": emotional_score,
        }

        # Sync to AMSV
        ordered = [
            thinking_score, focus_score, memory_score, creativity_score,
            imagination_score, analytical_score, verbal_score, emotional_score
        ]
        self.amsv.set_all_cognitive_scores(ordered)
        return scores

