"""
voice_agent/web_bridge.py - Real-Time AssemblyAI Universal-3 Pro Browser WebSocket Bridge.

Bridges browser microphone Web Audio API (16kHz PCM) directly to AssemblyAI Universal-3 Pro
real-time streaming WebSocket (wss://streaming.assemblyai.com/v3/ws?sample_rate=16000),
and feeds live transcripts through Solo Rock VoiceAgentOrchestrator for 0-ns AMSV memory sync,
psychometric competency grading, and biophysical audio generation.
"""

from __future__ import annotations
import os
import sys
import json
import time
import asyncio
from typing import Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import websockets
from voice_agent.agent_orchestrator import VoiceAgentOrchestrator

ASSEMBLYAI_WS_URL = "wss://streaming.assemblyai.com/v3/ws?sample_rate=16000"


def load_api_key() -> str:
    key = os.getenv("ASSEMBLYAI_API_KEY")
    if key:
        return key
    env_file = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ASSEMBLYAI_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    return "4823582e76784ac4879c11e7e8574334"


class AssemblyAIWebBridge:
    def __init__(self, port: int = 8765):
        self.port = port
        self.api_key = load_api_key()
        self.orchestrator = VoiceAgentOrchestrator(language="English")

    async def handle_browser_client(self, browser_ws):
        print(f"\n[CLIENT CONNECTED] Browser connected to AssemblyAI bridge.")
        headers = {"Authorization": self.api_key}

        try:
            async with websockets.connect(ASSEMBLYAI_WS_URL, additional_headers=headers) as aai_ws:
                print(f"[ASSEMBLYAI CONNECTED] Session linked to Universal-3 Pro streaming engine.")
                await browser_ws.send(json.dumps({
                    "type": "status",
                    "status": "connected",
                    "engine": "AssemblyAI Universal-3 Pro Real-Time WebSocket",
                    "model": "universal-3-6-pro",
                    "sample_rate": 16000
                }))

                async def forward_audio_to_assemblyai():
                    try:
                        async for message in browser_ws:
                            if isinstance(message, bytes):
                                # Forward raw 16kHz PCM audio chunk to AssemblyAI
                                await aai_ws.send(message)
                            elif isinstance(message, str):
                                data = json.loads(message)
                                if data.get("type") == "terminate":
                                    await aai_ws.send(json.dumps({"type": "Terminate"}))
                                    break
                    except Exception as e:
                        print(f"  [Audio Forwarding Ended]: {e}")

                async def forward_transcripts_to_browser():
                    try:
                        async for raw_msg in aai_ws:
                            msg = json.loads(raw_msg)
                            mtype = msg.get("type")

                            if mtype == "Begin":
                                await browser_ws.send(json.dumps({
                                    "type": "session_begin",
                                    "session_id": msg.get("id"),
                                    "model": msg.get("configuration", {}).get("model")
                                }))

                            elif mtype == "Turn":
                                transcript = msg.get("transcript", "").strip()
                                is_final = msg.get("end_of_turn", False)

                                if transcript:
                                    if not is_final:
                                        # Partial live transcript
                                        await browser_ws.send(json.dumps({
                                            "type": "partial_transcript",
                                            "transcript": transcript
                                        }))
                                    else:
                                        # Final utterance completed
                                        print(f"[FINAL TRANSCRIPT]: \"{transcript}\"")
                                        t0 = time.time()
                                        out = self.orchestrator.process_utterance(transcript)
                                        latency = round((time.time() - t0) * 1000.0, 1)

                                        # Send full evaluation back to browser UI
                                        await browser_ws.send(json.dumps({
                                            "type": "final_turn",
                                            "transcript": transcript,
                                            "reply": out["response_text"],
                                            "intent": out["matched_intent"],
                                            "scenario": out["scenario"],
                                            "f0": out["mean_f0_hz"],
                                            "gap_ms": out["calibrated_gap_ms"],
                                            "competency_percent": out["competency_percentage"],
                                            "competency_verdict": out["competency_verdict"],
                                            "psychometric_diagnosis": out["psychometric_diagnosis"],
                                            "knowledge_grounding": out.get("knowledge_grounding"),
                                            "cognitive_scores": out["cognitive_scores"],
                                            "amsv_byte_22": out["amsv_hardware_byte_22"],
                                            "processing_latency_ms": latency
                                        }))

                            elif mtype == "Termination":
                                await browser_ws.send(json.dumps({"type": "session_terminated"}))
                                break
                    except Exception as e:
                        print(f"  [Transcript Forwarding Ended]: {e}")

                await asyncio.gather(
                    forward_audio_to_assemblyai(),
                    forward_transcripts_to_browser()
                )

        except websockets.exceptions.ConnectionClosed:
            print("[CLIENT DISCONNECTED] Client closed connection.")
        except Exception as e:
            print(f"[BRIDGE ERROR]: {e}")
            try:
                await browser_ws.send(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
            except Exception:
                pass


async def main():
    bridge = AssemblyAIWebBridge(port=8765)
    print("=" * 80)
    print("  HELLOHIRE VOICE AI: BROWSER WEBSOCKET BRIDGE SERVER")
    print(f"  Listening on ws://127.0.0.1:{bridge.port}")
    print(f"  Target: {ASSEMBLYAI_WS_URL}")
    print("=" * 80)
    async with websockets.serve(bridge.handle_browser_client, "127.0.0.1", bridge.port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBridge server stopped.")
