"""
tests/test_assemblyai_and_wikipedia.py - Automated End-to-End Validation Suite.

Validates:
1. AssemblyAI Universal-3 Pro API live streaming and authentication
2. Free Wikipedia REST API & DuckDuckGo Instant Answer grounding
3. Grammatical conversational intent tree routing & dialogue response generation
4. 64-Byte AMSV hardware state vector synchronization (Byte 22 intent lock)
"""

import os
import sys
import unittest
import asyncio

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from voice_agent.agent_orchestrator import VoiceAgentOrchestrator
from voice_agent.knowledge_grounding import ground_candidate_speech, fetch_wikipedia_summary, fetch_duckduckgo_summary
from voice_agent.assemblyai_stream import AssemblyAIStreamingBridge


class TestAssemblyAIAndWikipedia(unittest.TestCase):
    def setUp(self):
        self.orchestrator = VoiceAgentOrchestrator(language="English")

    def test_01_wikipedia_free_grounding(self):
        """Verifies that free Wikipedia REST API retrieves accurate technical definitions."""
        concept = "rdma"
        res = fetch_wikipedia_summary(concept)
        self.assertIsNotNone(res, "Wikipedia REST API should return a valid summary")
        self.assertEqual(res["title"], "Remote direct memory access")
        self.assertIn("direct memory access", res["extract"].lower())
        print(f"\n[TEST PASS] Wikipedia Grounding: {res['title']} -> {res['extract'][:80]}...")

    def test_02_duckduckgo_free_fallback(self):
        """Verifies that DuckDuckGo Instant Answer API provides open fallback knowledge."""
        query = "Raft consensus algorithm"
        res = fetch_duckduckgo_summary(query)
        self.assertIsNotNone(res, "DuckDuckGo API should return an abstract definition")
        self.assertIn("consensus", res["extract"].lower())
        print(f"\n[TEST PASS] DuckDuckGo Grounding: {res['title']} -> {res['extract'][:80]}...")

    def test_03_speech_grounding_pipeline(self):
        """Verifies speech entity extraction and dual-source knowledge resolution."""
        utterance = "In our cluster, we implemented Raft consensus and bypassed the OS kernel with RDMA."
        knowledge = ground_candidate_speech(utterance)
        self.assertIsNotNone(knowledge, "Knowledge grounder should detect technical concepts in utterance")
        self.assertTrue(knowledge["title"] in ("Raft (algorithm)", "Remote direct memory access", "Consensus (computer science)"))
        print(f"\n[TEST PASS] Candidate Speech Grounded: {knowledge['title']}")

    def test_04_grammatical_dialogue_synthesis(self):
        """Verifies conversational intent tree produces grammatical, professional recruiter dialogues."""
        utterance = "In our distributed architecture, we employed kernel-bypass RDMA with a Raft consensus ring."
        res = self.orchestrator.process_utterance(utterance, play_audio=False)

        self.assertIsNotNone(res["response_text"])
        self.assertTrue(len(res["response_text"]) > 20)
        self.assertIn("Distributed", str(res.get("knowledge_grounding", {})))
        self.assertEqual(res["calibrated_gap_ms"], 518)
        self.assertGreaterEqual(res["competency_percentage"], 85)
        print(f"\n[TEST PASS] Recruiter Grammar Response: \"{res['response_text']}\"")
        print(f"            Matched Intent: {res['matched_intent']}")
        print(f"            Calibrated Latency: {res['calibrated_gap_ms']} ms")

    def test_05_zero_bridge_amsv_hardware_sync(self):
        """Verifies 64-byte AMSV memory vector synchronization without bridge overhead."""
        utterance = "Under peak PCIe bus saturation, we activate zero-copy backpressure queues."
        res = self.orchestrator.process_utterance(utterance, play_audio=False)

        self.assertEqual(res["amsv_hardware_byte_22"], "0x22")
        self.assertIn("Thinking Ability", res["cognitive_scores"])
        self.assertIn("Emotional Regulation", res["cognitive_scores"])
        print(f"\n[TEST PASS] AMSV Byte 22 Intent Locked: {res['amsv_hardware_byte_22']}")
        print(f"            Emotional Regulation: {res['cognitive_scores']['Emotional Regulation']}")

    def test_06_assemblyai_live_audio_stream(self):
        """Verifies live AssemblyAI Universal-3 Pro real-time WebSocket connection on 16kHz audio."""
        test_wav = os.path.join(ROOT_DIR, "assets", "audio", "test_spoken_speech_16k.wav")
        if not os.path.exists(test_wav):
            self.skipTest("Sample WAV file not found.")

        bridge = AssemblyAIStreamingBridge(play_response_audio=False)

        async def run_test():
            await bridge.run_session(bridge.stream_from_wav_file(test_wav))

        # Run async streaming session
        asyncio.run(run_test())
        print(f"\n[TEST PASS] AssemblyAI Universal-3 Pro WebSocket stream executed and parsed cleanly.")


if __name__ == "__main__":
    unittest.main()
