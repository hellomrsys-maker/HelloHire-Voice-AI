"""
voice_agent/assemblyai_stream.py - Live AssemblyAI Universal-3 Pro Realtime WebSocket Pipeline.

Streams real-time microphone PCM or test audio to AssemblyAI Universal-3 Pro STT
and routes final transcripts directly into the Solo Rock VoiceAgentOrchestrator
with 0-ns 64-byte AMSV hardware state vector synchronization and biophysical voice rendering.
"""

from __future__ import annotations
import os
import sys
import json
import time
import asyncio
import argparse
from typing import Optional, AsyncGenerator

import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import websockets
from voice_agent.audio_io import MicrophoneStream, AudioConfig, AudioPlayer
from voice_agent.agent_orchestrator import VoiceAgentOrchestrator
from English_engine.brain.Analysis.vocal_cord_frequency_engine import SpeakerRegisterCohort

# Load .env file if present
def load_env_api_key() -> str:
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if api_key:
        return api_key
    env_path = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ASSEMBLYAI_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    # Require API key from environment or .env
    raise ValueError(
        "ASSEMBLYAI_API_KEY not found. Please set your API key in the .env file or export ASSEMBLYAI_API_KEY."
    )


URL = "wss://streaming.assemblyai.com/v3/ws?sample_rate=16000"


class AssemblyAIStreamingBridge:
    def __init__(
        self,
        api_key: Optional[str] = None,
        sample_rate: int = 16000,
        speaker_cohort: SpeakerRegisterCohort = SpeakerRegisterCohort.MEDIUM_REGISTER,
        play_response_audio: bool = True
    ):
        self.api_key = api_key or load_env_api_key()
        self.sample_rate = sample_rate
        self.play_response_audio = play_response_audio
        self.agent = VoiceAgentOrchestrator(
            language="English",
            speaker_cohort=speaker_cohort,
            sample_rate=sample_rate
        )
        self.mic = MicrophoneStream(AudioConfig(sample_rate=sample_rate, frame_duration_ms=50))
        self.running = False

    async def stream_from_mic(self) -> AsyncGenerator[bytes, None]:
        """Asynchronously yields raw 16kHz PCM chunks from microphone queue."""
        self.mic.start()
        try:
            while self.running:
                chunk = self.mic.read(timeout=0.1)
                if chunk is not None and len(chunk) > 0:
                    yield chunk
                await asyncio.sleep(0.01)
        finally:
            self.mic.stop()

    async def stream_from_wav_file(self, wav_path: str) -> AsyncGenerator[bytes, None]:
        """Streams an existing WAV file in chunks matching real-time pace."""
        import wave
        with wave.open(wav_path, "rb") as wf:
            framerate = wf.getframerate()
            chunk_size = int(framerate * 0.05)  # 50ms chunk
            while True:
                data = wf.readframes(chunk_size)
                if not data:
                    break
                yield data
                await asyncio.sleep(0.05)

    async def run_session(self, audio_generator: AsyncGenerator[bytes, None]):
        """Runs the live bi-directional WebSocket session."""
        self.running = True
        headers = {"Authorization": self.api_key}

        print("\n" + "=" * 80)
        print("  HELLOHIRE VOICE AI: ASSEMBLYAI UNIVERSAL-3 PRO LIVE STREAMING")
        print(f"  Endpoint: {URL}")
        print("=" * 80)

        async with websockets.connect(URL, additional_headers=headers) as ws:
            print("[CONNECTED] Authenticated with AssemblyAI Real-Time Engine.")

            async def send_audio():
                try:
                    async for chunk in audio_generator:
                        if not self.running:
                            break
                        await ws.send(chunk)
                    # Allow transcription pipeline to drain final turns
                    await asyncio.sleep(2.5)
                except asyncio.CancelledError:
                    pass
                finally:
                    # Clean session termination
                    try:
                        await ws.send(json.dumps({"type": "Terminate"}))
                    except Exception:
                        pass

            async def receive_transcripts():
                async for raw_msg in ws:
                    try:
                        msg = json.loads(raw_msg)
                        mtype = msg.get("type")

                        if mtype == "Begin":
                            print(f"[SESSION INITIALIZED] ID: {msg.get('id')} | Model: {msg.get('configuration', {}).get('model')}")

                        elif mtype == "Turn":
                            transcript = msg.get("transcript", "").strip()
                            is_final = msg.get("end_of_turn", False)

                            if transcript:
                                if not is_final:
                                    # Partial live transcript
                                    sys.stdout.write(f"\r  ... \"{transcript}\"")
                                    sys.stdout.flush()
                                else:
                                    # Final turn received!
                                    print(f"\r\n\n[USER UTTERANCE]: \"{transcript}\"")
                                    
                                    # Route directly to Solo Rock Voice Agent Orchestrator
                                    t0 = time.time()
                                    out = self.agent.process_utterance(
                                        transcript,
                                        play_audio=self.play_response_audio
                                    )
                                    latency = round((time.time() - t0) * 1000, 1)

                                    print(f"[HELLOHIRE VOICE AI REPLY]: \"{out['response_text']}\"")
                                    print(f"  * Matched Intent : {out['matched_intent']}")
                                    print(f"  * Scenario State : {out['scenario']} (Mean F0: {out['mean_f0_hz']} Hz)")
                                    print(f"  * Turn Latency   : {out['calibrated_gap_ms']} ms calibrated gap")
                                    print(f"  * AMSV Hardware  : Byte 22 locked at {out['amsv_hardware_byte_22']} (0-ns sync)")
                                    print(f"  * Total Runtime  : {latency} ms")
                                    print("-" * 70)

                        elif mtype == "Termination":
                            print("\n[SESSION TERMINATED] AssemblyAI session closed cleanly.")
                            break
                        else:
                            print(f"  [RAW MSG: {mtype}] {raw_msg}")

                    except Exception as e:
                        print(f"\n[ERROR] Parsing message: {e}")

            sender_task = asyncio.create_task(send_audio())
            receiver_task = asyncio.create_task(receive_transcripts())

            try:
                await sender_task
                # Wait for receiver to finish processing server responses up to Termination
                await receiver_task
            except (KeyboardInterrupt, asyncio.CancelledError):
                self.running = False
                sender_task.cancel()
                receiver_task.cancel()


def main():
    parser = argparse.ArgumentParser(description="AssemblyAI Universal-3 Pro Voice Agent Streamer")
    parser.add_argument("--test-file", type=str, help="Stream a WAV file instead of live microphone")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio playback")
    args = parser.parse_args()

    bridge = AssemblyAIStreamingBridge(play_response_audio=not args.no_audio)

    try:
        if args.test_file:
            if not os.path.exists(args.test_file):
                print(f"Error: WAV file '{args.test_file}' not found.")
                return
            print(f"Streaming from WAV file: {args.test_file}")
            asyncio.run(bridge.run_session(bridge.stream_from_wav_file(args.test_file)))
        else:
            print("Listening live on microphone... Speak into your mic! (Press Ctrl+C to quit)")
            asyncio.run(bridge.run_session(bridge.stream_from_mic()))
    except KeyboardInterrupt:
        print("\nSession stopped by user.")


if __name__ == "__main__":
    main()
