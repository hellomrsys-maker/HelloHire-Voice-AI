"""
server.py — VerbalEngineServer
FastAPI REST server exposing the verbal communication engine as a production-grade
HTTP service. Provides endpoints for speech input processing, language understanding,
response generation, and speech synthesis. Used by all 6-language orchestration layers.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from .engine_client import EngineClient, EngineClientError
from .language_engine import LanguageEngine, EngineConfig as LangEngineConfig
from .verify import EngineVerifier, VerificationReport

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("polyglot_engine.server")


# ---------------------------------------------------------------------------
# Pydantic request / response schemas
# ---------------------------------------------------------------------------


class TextInputRequest(BaseModel):
    """Request payload for text-based verbal input."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str = Field(..., min_length=1, max_length=32_768, description="Raw verbal input text")
    language: str = Field(default="en", description="BCP-47 language tag")
    context_turns: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Prior conversation turns: [{role: 'user'|'assistant', content: str}]",
    )
    stream: bool = Field(default=False, description="Stream response tokens")
    max_tokens: int = Field(default=512, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class AudioInputRequest(BaseModel):
    """Request payload for audio-encoded verbal input (base64 PCM/WAV)."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audio_b64: str = Field(..., description="Base64-encoded audio bytes (PCM 16-bit 16kHz mono)")
    sample_rate: int = Field(default=16_000)
    channels: int = Field(default=1)
    language: str = Field(default="en")
    max_tokens: int = Field(default=512, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class EngineResponse(BaseModel):
    """Unified verbal engine response."""

    session_id: str
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    language: str
    tokens_generated: int
    latency_ms: float
    component_trace: List[str] = Field(
        default_factory=list, description="Component execution trace for debugging"
    )
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AudioOutputResponse(BaseModel):
    """TTS synthesis response — audio returned as base64."""

    session_id: str
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audio_b64: str
    sample_rate: int
    duration_seconds: float
    latency_ms: float


class HealthResponse(BaseModel):
    """Service health report."""

    status: str
    uptime_seconds: float
    engine_ready: bool
    verification: Optional[Dict[str, Any]] = None
    components: Dict[str, str] = Field(default_factory=dict)


class VerifyRequest(BaseModel):
    """Trigger a live engine verification run."""

    deep: bool = Field(default=False, description="Run deep verification including GPU kernels")


# ---------------------------------------------------------------------------
# Application state
# ---------------------------------------------------------------------------


class _AppState:
    """Singleton mutable application state attached to the FastAPI app."""

    def __init__(self) -> None:
        self.engine_client: Optional[EngineClient] = None
        self.language_engine: Optional[LanguageEngine] = None
        self.verifier: Optional[EngineVerifier] = None
        self.start_time: float = time.monotonic()
        self.ready: bool = False
        self._lock: asyncio.Lock = asyncio.Lock()

    async def initialize(self, config: Dict[str, Any]) -> None:
        """Async initialization: start C++ engine, verify, mark ready."""
        async with self._lock:
            logger.info("Initializing EngineClient …")
            self.engine_client = EngineClient(
                host=config.get("engine_host", "127.0.0.1"),
                port=int(config.get("engine_port", 50051)),
                lib_path=config.get("engine_lib_path", ""),
            )
            self.engine_client.connect()

            logger.info("Initializing LanguageEngine …")
            lang_cfg = LangEngineConfig(
                vocab_size=int(config.get("vocab_size", 32_000)),
                hidden_dim=int(config.get("hidden_dim", 1024)),
                num_heads=int(config.get("num_heads", 16)),
                num_layers=int(config.get("num_layers", 24)),
                max_seq_len=int(config.get("max_seq_len", 4096)),
                device=config.get("device", "cuda"),
            )
            self.language_engine = LanguageEngine(lang_cfg)
            self.language_engine.load_weights(config.get("weights_path", ""))

            logger.info("Running engine verification …")
            self.verifier = EngineVerifier(
                engine_client=self.engine_client,
                language_engine=self.language_engine,
            )
            report: VerificationReport = self.verifier.verify()
            if not report.passed:
                raise RuntimeError(
                    f"Engine verification FAILED: {report.failures}"
                )
            logger.info("Engine verification PASSED — server is ready.")
            self.ready = True

    async def shutdown(self) -> None:
        async with self._lock:
            if self.engine_client:
                self.engine_client.disconnect()
            self.ready = False


_state = _AppState()


# ---------------------------------------------------------------------------
# Lifespan context manager
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: initialize engine on startup, shutdown on teardown."""
    config: Dict[str, Any] = {
        "engine_host": os.getenv("ENGINE_HOST", "127.0.0.1"),
        "engine_port": os.getenv("ENGINE_PORT", "50051"),
        "engine_lib_path": os.getenv("ENGINE_LIB_PATH", ""),
        "weights_path": os.getenv("ENGINE_WEIGHTS_PATH", ""),
        "vocab_size": os.getenv("VOCAB_SIZE", "32000"),
        "hidden_dim": os.getenv("HIDDEN_DIM", "1024"),
        "num_heads": os.getenv("NUM_HEADS", "16"),
        "num_layers": os.getenv("NUM_LAYERS", "24"),
        "max_seq_len": os.getenv("MAX_SEQ_LEN", "4096"),
        "device": os.getenv("DEVICE", "cuda"),
    }
    try:
        await _state.initialize(config)
    except Exception as exc:
        logger.error("Engine initialization failed: %s", exc)
        # Server still starts but reports not-ready; allows health probes
    yield
    await _state.shutdown()


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------


app = FastAPI(
    title="Polyglot Verbal Engine API",
    description=(
        "Production REST API for the 6-language verbal communication engine. "
        "Handles speech input, language understanding, response generation, "
        "and speech synthesis. Part of the polyglot_ai_system."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Middleware — request tracing
# ---------------------------------------------------------------------------


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Attach a unique X-Request-ID header to every response."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------------------------
# Dependency — readiness guard
# ---------------------------------------------------------------------------


def _require_ready() -> None:
    """Raise 503 if the engine is not yet ready."""
    if not _state.ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Engine not ready — initialization in progress or failed.",
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse, tags=["Operations"])
async def health() -> HealthResponse:
    """
    Liveness + readiness health endpoint.
    Returns component status for each engine subsystem.
    """
    uptime = time.monotonic() - _state.start_time
    components: Dict[str, str] = {}

    if _state.engine_client:
        try:
            ping_ok = _state.engine_client.ping()
            components["cpp_engine"] = "ok" if ping_ok else "degraded"
        except Exception:
            components["cpp_engine"] = "error"
    else:
        components["cpp_engine"] = "not_initialized"

    if _state.language_engine:
        components["language_engine"] = "ok" if _state.language_engine.is_loaded() else "not_loaded"
    else:
        components["language_engine"] = "not_initialized"

    return HealthResponse(
        status="ok" if _state.ready else "initializing",
        uptime_seconds=uptime,
        engine_ready=_state.ready,
        components=components,
    )


@app.post("/verify", response_model=Dict[str, Any], tags=["Operations"])
async def verify(req: VerifyRequest) -> Dict[str, Any]:
    """
    Trigger a live engine verification run and return the full report.
    Pass deep=true to also exercise GPU kernels.
    """
    _require_ready()
    assert _state.verifier is not None
    report: VerificationReport = _state.verifier.verify(deep=req.deep)
    return {
        "passed": report.passed,
        "checks_run": report.checks_run,
        "failures": report.failures,
        "latency_ms": report.latency_ms,
        "timestamp": report.timestamp,
    }


@app.post("/engine/process", response_model=EngineResponse, tags=["Engine"])
async def process_text(req: TextInputRequest) -> EngineResponse:
    """
    Primary verbal engine endpoint.
    Accepts text, runs the full pipeline:
      1. Tokenisation (Rust)
      2. Language understanding (C++ / attention)
      3. Response generation (Python / Julia math)
      4. Returns structured response
    """
    _require_ready()
    t0 = time.monotonic()

    try:
        assert _state.language_engine is not None
        assert _state.engine_client is not None

        # 1. Tokenise via engine client (calls Rust tokenizer through C++ FFI)
        tokens = _state.engine_client.tokenize(req.text, language=req.language)

        # 2. Run full language understanding pipeline
        understanding = _state.language_engine.understand(
            tokens=tokens,
            context_turns=req.context_turns,
        )

        # 3. Generate response
        response_text, token_count = _state.language_engine.generate(
            understanding=understanding,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )

        latency_ms = (time.monotonic() - t0) * 1000.0

        return EngineResponse(
            session_id=req.session_id,
            text=response_text,
            language=req.language,
            tokens_generated=token_count,
            latency_ms=latency_ms,
            component_trace=understanding.get("trace", []),
            confidence=understanding.get("confidence", 1.0),
            metadata={"input_tokens": len(tokens)},
        )

    except EngineClientError as exc:
        logger.error("EngineClientError: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /engine/process")
        raise HTTPException(status_code=500, detail=f"Internal engine error: {exc}")


@app.post("/engine/process/stream", tags=["Engine"])
async def process_text_stream(req: TextInputRequest):
    """
    Streaming variant of /engine/process.
    Returns tokens as Server-Sent Events (text/event-stream).
    """
    _require_ready()
    assert _state.language_engine is not None
    assert _state.engine_client is not None

    async def token_generator():
        try:
            tokens = _state.engine_client.tokenize(req.text, language=req.language)
            understanding = _state.language_engine.understand(
                tokens=tokens,
                context_turns=req.context_turns,
            )
            async for token_text in _state.language_engine.generate_stream(
                understanding=understanding,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
            ):
                yield f"data: {token_text}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:
            yield f"data: [ERROR] {exc}\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")


@app.post("/engine/audio/transcribe", response_model=EngineResponse, tags=["Audio"])
async def transcribe_audio(req: AudioInputRequest) -> EngineResponse:
    """
    ASR endpoint: base64-encoded PCM audio → understood verbal response.
    Uses the CUDA ASR kernel via the engine client.
    """
    _require_ready()
    t0 = time.monotonic()

    try:
        import base64

        assert _state.engine_client is not None
        assert _state.language_engine is not None

        audio_bytes = base64.b64decode(req.audio_b64)

        # ASR: audio bytes → transcript text via C++ engine (CUDA kernel)
        transcript = _state.engine_client.transcribe(
            audio_bytes=audio_bytes,
            sample_rate=req.sample_rate,
            channels=req.channels,
            language=req.language,
        )

        # Full pipeline on transcript
        tokens = _state.engine_client.tokenize(transcript, language=req.language)
        understanding = _state.language_engine.understand(tokens=tokens, context_turns=[])
        response_text, token_count = _state.language_engine.generate(
            understanding=understanding,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )

        latency_ms = (time.monotonic() - t0) * 1000.0

        return EngineResponse(
            session_id=req.session_id,
            text=response_text,
            language=req.language,
            tokens_generated=token_count,
            latency_ms=latency_ms,
            component_trace=["asr_kernel", "tokenizer", "language_engine"],
            confidence=understanding.get("confidence", 1.0),
            metadata={"transcript": transcript},
        )

    except Exception as exc:
        logger.exception("Error in /engine/audio/transcribe")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/engine/audio/synthesize", response_model=AudioOutputResponse, tags=["Audio"])
async def synthesize_audio(
    session_id: str,
    text: str,
    language: str = "en",
    sample_rate: int = 22_050,
) -> AudioOutputResponse:
    """
    TTS endpoint: text → base64-encoded synthesised speech audio.
    Uses the CUDA TTS kernel via the engine client.
    """
    _require_ready()
    t0 = time.monotonic()

    try:
        import base64

        assert _state.engine_client is not None

        audio_bytes: bytes = _state.engine_client.synthesize(
            text=text,
            language=language,
            sample_rate=sample_rate,
        )

        duration_seconds = len(audio_bytes) / (sample_rate * 2)  # 16-bit mono
        latency_ms = (time.monotonic() - t0) * 1000.0

        return AudioOutputResponse(
            session_id=session_id,
            audio_b64=base64.b64encode(audio_bytes).decode("ascii"),
            sample_rate=sample_rate,
            duration_seconds=duration_seconds,
            latency_ms=latency_ms,
        )

    except Exception as exc:
        logger.exception("Error in /engine/audio/synthesize")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/engine/components", response_model=Dict[str, Any], tags=["Engine"])
async def list_components() -> Dict[str, Any]:
    """
    List all recruited engine components with their current status.
    Reflects the recruitment-driven architecture: every component is
    instantiated and tracked by name.
    """
    _require_ready()
    assert _state.engine_client is not None

    components = _state.engine_client.list_components()
    return {"components": components, "total": len(components)}


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception for request %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {type(exc).__name__}: {exc}"},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


class VerbalEngineServer:
    """
    High-level wrapper for the FastAPI verbal engine server.
    Manages configuration, startup, and graceful shutdown.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        workers: int = 1,
        log_level: str = "info",
        reload: bool = False,
    ) -> None:
        self.host = host
        self.port = port
        self.workers = workers
        self.log_level = log_level
        self.reload = reload

    def run(self) -> None:
        """Start the uvicorn ASGI server."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        logger.info(
            "Starting VerbalEngineServer on %s:%d (workers=%d)",
            self.host,
            self.port,
            self.workers,
        )
        uvicorn.run(
            "polyglot_engine.server:app",
            host=self.host,
            port=self.port,
            workers=self.workers,
            log_level=self.log_level,
            reload=self.reload,
            access_log=True,
        )


def create_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    workers: int = 1,
) -> VerbalEngineServer:
    """Factory function — construct a configured VerbalEngineServer."""
    return VerbalEngineServer(host=host, port=port, workers=workers)


if __name__ == "__main__":
    srv = create_server(
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", "8080")),
        workers=int(os.getenv("SERVER_WORKERS", "1")),
    )
    srv.run()
