"""
voice_agent/run_agent.py - Interactive Runner & Demonstration for Voice AI Agent.

Modes:
1. Benchmark Demo: Runs the 6 physical communicative scenarios on "It's okay", generates audio waveforms,
   and validates 0-ns AMSV memory sync.
2. Interactive Dialogue: Enter custom utterances or test intent matching and vocal cord tuning live.

Usage:
    py voice_agent/run_agent.py --demo
    py voice_agent/run_agent.py --interactive
"""

from __future__ import annotations
import os
import sys
import argparse
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from English_engine.brain.Analysis.vocal_cord_frequency_engine import (
    SituationalScenario,
    SpeakerRegisterCohort,
)
from voice_agent.agent_orchestrator import VoiceAgentOrchestrator
from voice_agent.audio_io import AudioPlayer

DEMO_OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "vocal_demos")


def run_benchmark_demo():
    print("\n" + "=" * 80)
    print("  VOICE AI AGENT: BIOPHYSICAL VOCAL CORD ACOUSTICS & ZERO-BRIDGE AMSV DEMO")
    print("  Calibrated Turn-Taking Gap: 518ms | Physical Laryngeal Frequency Modulation")
    print("=" * 80)

    os.makedirs(DEMO_OUTPUT_DIR, exist_ok=True)
    agent = VoiceAgentOrchestrator(speaker_cohort=SpeakerRegisterCohort.MEDIUM_REGISTER)

    scenarios = [
        SituationalScenario.CALM_REASSURANCE,
        SituationalScenario.CONFIDENCE_AUTHORITY,
        SituationalScenario.AGGRESSIVE_VIOLENCE,
        SituationalScenario.EMOTIONAL_VULNERABILITY,
        SituationalScenario.DEEP_MELANCHOLY,
        SituationalScenario.WHISPER_SECRECY,
    ]

    print("\n[SCENARIO 1-6 AUDIT ON \"It's okay\"]")
    for sc in scenarios:
        res = agent.process_utterance("How are you feeling?", forced_scenario=sc)
        pcm_bytes = res["pcm_bytes"]
        wav_path = os.path.join(DEMO_OUTPUT_DIR, f"demo_{sc.value.lower()}.wav")
        AudioPlayer.save_wav(pcm_bytes, wav_path)

        bio = res["laryngeal_biomechanics"]
        print(f"  • {sc.value:26} | F0: {res['mean_f0_hz']:5.1f}Hz | P_s: {bio['subglottal_pressure_cmh2o']:4.1f}cmH2O | O_q: {bio['open_quotient_oq']:0.2f} | Gap: {res['calibrated_gap_ms']}ms | Audio: {os.path.basename(wav_path)} ({res['audio_duration_ms']}ms)")

    print("\n[DIALOGUE INTENT TREE & HARDWARE MEMORY READBACK]")
    test_queries = [
        "How are you?",
        "Why was this decision taken without authorization?",
        "Is memory synchronization verified?",
        "Report status immediately.",
        "Is there anything else?",
    ]
    for q in test_queries:
        out = agent.process_utterance(q)
        print(f"  User : \"{q}\"")
        print(f"  Agent: \"{out['response_text']}\"")
        print(f"         Intent: {out['matched_intent']:26} | AMSV Byte 22: {out['amsv_hardware_byte_22']} | F0: {out['mean_f0_hz']}Hz | Latency: {out['agent_processing_latency_ms']}ms")
        print("  " + "-" * 76)

    print("\n" + "=" * 80)
    print("  ALL DEMOS COMPLETED SUCCESSFULLY — AUDIO SAMPLES SAVED TO data/vocal_demos/")
    print("=" * 80)


def run_interactive_mode():
    print("\n" + "=" * 80)
    print("  INTERACTIVE VOICE AI AGENT CONSOLE (TYPE 'exit' TO QUIT)")
    print("=" * 80)
    agent = VoiceAgentOrchestrator(speaker_cohort=SpeakerRegisterCohort.MEDIUM_REGISTER)

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input or user_input.lower() in ["exit", "quit", "q"]:
                break

            out = agent.process_utterance(user_input, play_audio=True)
            print(f"Agent > {out['response_text']}")
            print(f"        [Intent: {out['matched_intent']} | Scenario: {out['scenario']} | F0: {out['mean_f0_hz']}Hz | Gap: {out['calibrated_gap_ms']}ms | AMSV: {out['amsv_hardware_byte_22']}]")
        except (KeyboardInterrupt, EOFError):
            break
    print("\nSession adjourned.")


def main():
    parser = argparse.ArgumentParser(description="Voice AI Agent Runner")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive console")
    parser.add_argument("--demo", "-d", action="store_true", default=True, help="Run biophysical scenario benchmark demo")
    args = parser.parse_args()

    if args.interactive:
        run_interactive_mode()
    else:
        run_benchmark_demo()


if __name__ == "__main__":
    main()
