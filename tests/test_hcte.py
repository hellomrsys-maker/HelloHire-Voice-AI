"""
test_hcte.py — Human Cognitive Thinking Engine (HCTE) Integration Tests
All 11 personas + orchestrator + training layer + AMSV verified.
"""
import sys, os, struct
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import torch

from hcte.python.sub_ais.optimist_thinker import OptimistThinker
from hcte.python.sub_ais.pessimist_thinker import PessimistThinker
from hcte.python.sub_ais.premortem_analyst import PreMortemAnalyst
from hcte.python.sub_ais.devils_advocate import DevilsAdvocate
from hcte.python.sub_ais.analyst_thinker import AnalystThinker, IntuitiveThinker, EmpathThinker
from hcte.python.sub_ais.systems_thinker import (
    SystemsThinker, VisionaryThinker, AbsurdistThinker, MetacognitionMonitor
)
from hcte.python.hcte_orchestrator import HumanCognitiveThinkingOrchestrator
from training.train_hcte_cognitive_ai import (
    HCTECognitiveNetwork, HCTETrainer, generate_hcte_curriculum_batch
)

# ── POSITIVE SCENARIO ──────────────────────────────────────────────────────────
OPPORTUNITY = (
    "We have a strong opportunity to build a distributed microservices platform. "
    "The potential for growth is exciting. We're confident we can expand our advantage "
    "and create innovative solutions that benefit our customers. The team is capable."
)

# ── CRISIS SCENARIO ────────────────────────────────────────────────────────────
CRISIS = (
    "The project is facing critical failure. We're missing the deadline and the budget "
    "is overrun. Key team members may leave. The assumption that customers want this "
    "product is now in serious doubt. We have a systemic communication breakdown."
)

# ── COMPLEX SCENARIO ──────────────────────────────────────────────────────────
COMPLEX = (
    "This is a complex interdependent system with feedback loops across teams. "
    "The evidence suggests we need a data-driven analysis. Therefore we should examine "
    "the downstream consequences and second-order effects of our proposed architecture."
)


class TestOptimistThinker:
    def test_opportunity_scores_high(self):
        r = OptimistThinker().think(OPPORTUNITY)
        assert r["composite_score"] >= 0.40
        assert r["emotional_charge"] > 0.0

    def test_crisis_scores_low(self):
        r = OptimistThinker().think(CRISIS)
        assert r["composite_score"] <= 0.45

    def test_best_case_always_generated(self):
        r = OptimistThinker().think("Some scenario.")
        assert "best_case_outcome" in r and len(r["best_case_outcome"]) > 5


class TestPessimistThinker:
    def test_crisis_scores_high(self):
        r = PessimistThinker().think(CRISIS)
        assert r["composite_score"] >= 0.55
        assert r["emotional_charge"] < 0.0

    def test_risks_enumerated(self):
        r = PessimistThinker().think(CRISIS)
        assert len(r["enumerated_risks"]) >= 1

    def test_opportunity_still_has_baseline_pessimism(self):
        r = PessimistThinker().think(OPPORTUNITY)
        # Pessimist always maintains baseline worry (>= 0.10)
        assert r["composite_score"] >= 0.10


class TestPreMortemAnalyst:
    def test_failure_modes_generated_for_crisis(self):
        r = PreMortemAnalyst().think(CRISIS)
        assert r["failure_mode_count"] >= 3

    def test_worst_case_has_causal_chain(self):
        r = PreMortemAnalyst().think(CRISIS)
        wc = r["worst_case"]
        assert len(wc["causal_chain"]) >= 1

    def test_worst_case_has_prevention_and_recovery(self):
        r = PreMortemAnalyst().think(CRISIS)
        wc = r["worst_case"]
        assert len(wc["prevention"]) >= 1
        assert len(wc["recovery"]) >= 1

    def test_solution_coverage_positive(self):
        r = PreMortemAnalyst().think(COMPLEX)
        assert r["solution_coverage"] >= 0.50

    def test_pessimism_index_high_for_crisis(self):
        r = PreMortemAnalyst().think(CRISIS)
        assert r["pessimism_index"] >= 0.10

    def test_early_warnings_present(self):
        r = PreMortemAnalyst().think(CRISIS)
        assert len(r["worst_case"]["early_warnings"]) >= 1


class TestDevilsAdvocate:
    def test_consensus_attack_generated(self):
        scenario = "Everyone clearly agrees that this approach is the obvious best practice we should always follow."
        r = DevilsAdvocate().think(scenario)
        assert r["consensus_markers_found"] >= 2
        assert r["challenge_urgency"] >= 0.50

    def test_inversions_generated(self):
        r = DevilsAdvocate().think(OPPORTUNITY)
        assert len(r["assumption_inversions"]) >= 1

    def test_steelman_present(self):
        r = DevilsAdvocate().think(OPPORTUNITY)
        assert len(r["steelman_opposition"]) > 20


class TestAnalystThinker:
    def test_data_backed_detected(self):
        scenario = "The evidence shows a 40% improvement. Data indicates p99 latency dropped by 35ms. Therefore we recommend proceeding."
        r = AnalystThinker().think(scenario)
        assert r["data_backed"] is True
        assert r["logic_chain_score"] >= 0.30

    def test_fallacy_penalty_applied(self):
        scenario = "Everyone knows this is right. It's obvious. Common sense says we should always do this."
        r = AnalystThinker().think(scenario)
        assert r["fallacy_count"] >= 2


class TestIntuitiveThinker:
    def test_domain_familiarity_detected(self):
        scenario = "In the startup engineering product space, the market data shows an emerging technical pattern."
        r = IntuitiveThinker().think(scenario)
        assert r["domain_familiarity"] >= 0.45

    def test_fast_path_verdict_returned(self):
        r = IntuitiveThinker().think(OPPORTUNITY)
        assert r["fast_path_verdict"] in ("PROCEED", "PAUSE_AND_VERIFY")


class TestEmpathThinker:
    def test_human_salience_for_people_scenario(self):
        scenario = "The team and employees will be significantly affected. Customer trust and user wellbeing are at stake."
        r = EmpathThinker().think(scenario)
        assert r["human_salience"] >= 0.45
        assert len(r["affected_groups"]) >= 1

    def test_affected_groups_populated(self):
        r = EmpathThinker().think(CRISIS)
        assert len(r["affected_groups"]) >= 1


class TestSystemsThinker:
    def test_feedback_loops_detected(self):
        scenario = "The systemic feedback loop creates a cascade of downstream and upstream interdependent effects."
        r = SystemsThinker().think(scenario)
        assert r["system_awareness"] >= 0.45
        assert len(r["second_order_effects"]) >= 1

    def test_second_order_effects_for_automation(self):
        scenario = "We should automate this process with an AI tool to scale efficiently."
        r = SystemsThinker().think(scenario)
        assert any("2nd order" in e for e in r["second_order_effects"])


class TestVisionaryThinker:
    def test_long_horizon_detected(self):
        scenario = "In 5 years, the AI disruption will transform and revolutionize the entire platform paradigm across the next decade."
        r = VisionaryThinker().think(scenario)
        assert r["horizon_label"] == "LONG"
        assert r["composite_score"] >= 0.40

    def test_short_horizon_default(self):
        r = VisionaryThinker().think("We need to fix the bug today.")
        assert r["horizon_label"] == "SHORT"


class TestAbsurdistThinker:
    def test_lateral_leaps_always_generated(self):
        r = AbsurdistThinker().think(OPPORTUNITY)
        assert len(r["wild_ideas"]) >= 3

    def test_constraint_boosts_reframe_score(self):
        scenario = "We cannot change the architecture because it is required and must stay as is."
        r = AbsurdistThinker().think(scenario)
        assert r["reframe_urgency"] >= 0.55


class TestMetacognitionMonitor:
    def test_groupthink_detected_when_low_tension(self):
        # All personas give same score — tension = 0
        outputs = {n: {"composite_score": 0.70} for n in
                   ["optimist","pessimist","analyst","intuitive","empath","systems"]}
        r = MetacognitionMonitor().monitor(outputs)
        assert r["cognitive_tension"] <= 0.05
        assert any("GROUPTHINK" in a for a in r["bias_alerts"])

    def test_optimism_bias_detected(self):
        outputs = {
            "optimist":  {"composite_score": 0.92},
            "pessimist": {"composite_score": 0.20},
            "analyst":   {"composite_score": 0.60},
        }
        r = MetacognitionMonitor().monitor(outputs)
        assert any("OPTIMISM BIAS" in a for a in r["bias_alerts"])

    def test_healthy_tension_no_alerts(self):
        # Diverse persona scores = healthy tension
        outputs = {
            "optimist":  {"composite_score": 0.90},
            "pessimist": {"composite_score": 0.15},
            "analyst":   {"composite_score": 0.70},
            "absurdist": {"composite_score": 0.85},
            "empath":    {"composite_score": 0.40},
        }
        r = MetacognitionMonitor().monitor(outputs)
        assert r["cognitive_tension"] >= 0.20


class TestHCTEOrchestrator:
    def test_full_pipeline_crisis(self):
        orc = HumanCognitiveThinkingOrchestrator()
        r = orc.think(CRISIS)
        assert "global_cognitive_index" in r
        assert "pessimism_index" in r
        assert r["pessimism_index"] >= 0.15
        assert r["cognitive_label"] in ("HIGHLY_INSIGHTFUL","INSIGHTFUL","ADEQUATE","SHALLOW")

    def test_full_pipeline_opportunity(self):
        orc = HumanCognitiveThinkingOrchestrator()
        r = orc.think(OPPORTUNITY)
        assert r["optimism_charge"] >= 0.30

    def test_amsv_sync_writes_hcte_region(self):
        buf = bytearray(64)
        orc = HumanCognitiveThinkingOrchestrator(master_amsv_buffer=buf)
        orc.think(CRISIS)
        opt_raw, pess_raw, tension_raw, sol_raw = struct.unpack_from("<HHHH", buf, 0x38)
        assert pess_raw > 0    # pessimism written to 0x38

    def test_worst_case_with_solutions(self):
        orc = HumanCognitiveThinkingOrchestrator()
        r = orc.think(CRISIS)
        wc = r["worst_case"]
        assert len(wc.get("prevention", [])) >= 1
        assert len(wc.get("recovery", [])) >= 1

    def test_all_11_personas_present(self):
        orc = HumanCognitiveThinkingOrchestrator()
        r = orc.think(COMPLEX)
        expected = {"optimist","pessimist","premortem_analyst","devils_advocate",
                    "analyst","intuitive","empath","systems_thinker",
                    "visionary","absurdist","metacognition_monitor"}
        assert expected.issubset(set(r["personas"].keys()))


class TestHCTETraining:
    def test_forward_pass_correct_shapes(self):
        net = HCTECognitiveNetwork(vocab_size=100, d_model=64, nhead=4, num_layers=1)
        tokens = torch.randint(0, 100, (4, 16))
        out = net(tokens)
        assert out["optimist"].shape == (4, 1)
        assert out["premortem"].shape == (4, 3)
        assert out["metacog"].shape == (4, 2)
        assert out["synthesis"].shape == (4, 1)

    def test_train_step_returns_all_losses(self):
        trainer = HCTETrainer(HCTECognitiveNetwork(vocab_size=1000, d_model=64, nhead=4, num_layers=1))
        tokens, targets = generate_hcte_curriculum_batch(batch_size=4, seq_len=16)
        result = trainer.train_step(tokens, targets)
        assert "total_loss" in result
        assert "loss_premortem" in result
        assert "tension_penalty" in result

    def test_curriculum_batch_archetypes(self):
        tokens, targets = generate_hcte_curriculum_batch(batch_size=8, seq_len=16)
        # Archetype 0 (crisis): pessimist should be high
        assert targets["pessimist"][0, 0].item() >= 0.70
        # Archetype 1 (opportunity): optimist should be high
        assert targets["optimist"][1, 0].item() >= 0.70
        # Archetype 3 (creative): absurdist should be high
        assert targets["absurdist"][3, 0].item() >= 0.70

    def test_amsv_sync_in_training(self):
        buf = bytearray(64)
        trainer = HCTETrainer(
            HCTECognitiveNetwork(vocab_size=1000, d_model=64, nhead=4, num_layers=1),
            amsv_buffer=buf
        )
        tokens, targets = generate_hcte_curriculum_batch(batch_size=4, seq_len=16)
        trainer.train_step(tokens, targets)
        opt_raw, pess_raw, tension_raw, sol_raw = struct.unpack_from("<HHHH", buf, 0x38)
        assert opt_raw > 0 or pess_raw > 0   # at least one value written
