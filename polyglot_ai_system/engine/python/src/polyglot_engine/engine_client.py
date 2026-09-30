# =============================================================================
# engine/python/src/polyglot_engine/engine_client.py
# Python high-level client wrapping the C++ engine_core shared library
# via ctypes FFI.
# =============================================================================

from __future__ import annotations

import ctypes
import json
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import threading

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

@dataclass
class EngineClientConfig:
    """Configuration for the Python EngineClient."""

    # Path to the compiled engine_core shared library
    engine_lib_path: str = field(
        default_factory=lambda: os.environ.get(
            "ENGINE_LIB_PATH",
            str(Path(__file__).parent.parent.parent.parent.parent /
                "build" / "cpp" / "engine" / "libengine_core.so")
        )
    )

    # Path to the canonical engine training YAML file
    training_file_path: str = field(
        default_factory=lambda: os.environ.get(
            "ENGINE_TRAINING_FILE",
            str(Path(__file__).parent.parent.parent.parent.parent.parent /
                "language_engines" / "English_engine.training.yaml")
        )
    )

    # Engine configuration
    engine_id:       str = "verbal_comm_engine_v1"
    default_language: str = "en"
    enable_gpu:      bool = True
    thread_pool_size: int = 8
    attention_heads:  int = 16
    attention_dim:    int = 1024
    max_seq_length:   int = 8192
    reasoning_depth:  str = "moderate"  # "shallow" | "moderate" | "deep" | "extended"

    # Output modality: "text" | "speech_pcm" | "speech_opus"
    output_modality: str = "text"


# =============================================================================
# EngineClient
# =============================================================================

class EngineClient:
    """
    High-level Python client for the Verbal Communication Engine.

    Wraps the C++ engine_core shared library via ctypes.
    Provides a simple process_text() interface and manages the engine lifecycle.

    Thread-safe: Multiple threads may call process_text() concurrently.

    Example:
        >>> config = EngineClientConfig()
        >>> with EngineClient(config) as engine:
        ...     response = engine.process_text("Hi, I am Ash.")
        ...     print(response)
    """

    def __init__(self, config: EngineClientConfig):
        self._config   = config
        self._lib      = None
        self._handle   = None
        self._lock     = threading.Lock()
        self._operational = False

        self._load_library()
        self._setup_function_signatures()
        self._create_engine()

    # -------------------------------------------------------------------------
    # Context manager support
    # -------------------------------------------------------------------------

    def __enter__(self) -> EngineClient:
        return self

    def __exit__(self, *args) -> None:
        self.shutdown()

    # -------------------------------------------------------------------------
    # Library loading and FFI setup
    # -------------------------------------------------------------------------

    def _load_library(self) -> None:
        """Loads the C++ engine_core shared library."""
        lib_path = self._config.engine_lib_path

        if not os.path.exists(lib_path):
            logger.warning(
                "engine_core library not found at %s — running in stub mode",
                lib_path
            )
            self._lib = None
            return

        try:
            self._lib = ctypes.CDLL(lib_path)
            logger.info("Loaded engine_core library: %s", lib_path)
        except OSError as e:
            logger.error("Failed to load engine_core library: %s", e)
            self._lib = None

    def _setup_function_signatures(self) -> None:
        """Configures ctypes argument and return types for all FFI functions."""
        if self._lib is None:
            return

        # engine_create(config_json: char*) -> void*
        self._lib.engine_create.argtypes = [ctypes.c_char_p]
        self._lib.engine_create.restype  = ctypes.c_void_p

        # engine_recruit(handle: void*) -> int
        self._lib.engine_recruit.argtypes = [ctypes.c_void_p]
        self._lib.engine_recruit.restype  = ctypes.c_int

        # engine_process_text(handle, input, input_len, out_buf, out_buf_size) -> int
        self._lib.engine_process_text.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        self._lib.engine_process_text.restype = ctypes.c_int

        # engine_is_operational(handle) -> int
        self._lib.engine_is_operational.argtypes = [ctypes.c_void_p]
        self._lib.engine_is_operational.restype  = ctypes.c_int

        # engine_health_dump(handle) -> char*
        self._lib.engine_health_dump.argtypes = [ctypes.c_void_p]
        self._lib.engine_health_dump.restype  = ctypes.c_char_p

        # engine_free_string(char*) -> void
        self._lib.engine_free_string.argtypes = [ctypes.c_char_p]
        self._lib.engine_free_string.restype  = None

        # engine_destroy(handle) -> void
        self._lib.engine_destroy.argtypes = [ctypes.c_void_p]
        self._lib.engine_destroy.restype  = None

    def _create_engine(self) -> None:
        """Creates and recruits the engine instance."""
        if self._lib is None:
            logger.info("Running in stub mode — no C++ library loaded")
            self._operational = True
            return

        # Build config JSON
        config_json = json.dumps({
            "engine_id":       self._config.engine_id,
            "default_language": self._config.default_language,
            "enable_gpu":      self._config.enable_gpu,
            "thread_pool_size": self._config.thread_pool_size,
            "attention_heads":  self._config.attention_heads,
            "attention_dim":    self._config.attention_dim,
            "max_seq_length":   self._config.max_seq_length,
        }).encode("utf-8")

        # Create engine handle
        self._handle = self._lib.engine_create(config_json)
        if not self._handle:
            raise RuntimeError("engine_create() returned null — check config")

        # Recruit all subsystems
        result = self._lib.engine_recruit(ctypes.c_void_p(self._handle))
        if result != 1:
            raise RuntimeError("engine_recruit() failed — check C++ logs")

        # Verify operational status
        if not self._lib.engine_is_operational(ctypes.c_void_p(self._handle)):
            raise RuntimeError("Engine is not operational after recruitment")

        self._operational = True
        logger.info("Engine created and operational: %s", self._config.engine_id)

    # -------------------------------------------------------------------------
    # Core API
    # -------------------------------------------------------------------------

    def process_text(
        self,
        input_text: str,
        depth: Optional[str] = None,
        modality: Optional[str] = None,
    ) -> str:
        """
        Processes a text input through the verbal communication engine.

        Args:
            input_text: Raw input text to process.
            depth:      Reasoning depth override ("shallow","moderate","deep","extended").
                        Defaults to config.reasoning_depth.
            modality:   Output modality override. Defaults to config.output_modality.

        Returns:
            The engine's text response.

        Raises:
            RuntimeError: If the engine is not operational or processing fails.
        """
        if not self._operational:
            raise RuntimeError("Engine is not operational")

        if not input_text or not input_text.strip():
            return ""

        # Stub mode: return a meaningful test response
        if self._lib is None:
            return self._stub_response(input_text)

        input_bytes = input_text.encode("utf-8")
        out_buf_size = 65536
        out_buf = ctypes.create_string_buffer(out_buf_size)

        with self._lock:
            n = self._lib.engine_process_text(
                ctypes.c_void_p(self._handle),
                input_bytes,
                ctypes.c_size_t(len(input_bytes)),
                out_buf,
                ctypes.c_size_t(out_buf_size),
            )

        if n < 0:
            raise RuntimeError(f"engine_process_text() returned error code {n}")

        return out_buf.value[:n].decode("utf-8", errors="replace")

    def health_dump(self) -> dict:
        """Returns the engine's health status as a parsed dict."""
        if self._lib is None:
            return {"stub_mode": True, "operational": self._operational}

        with self._lock:
            raw = self._lib.engine_health_dump(ctypes.c_void_p(self._handle))

        if raw is None:
            return {}

        json_str = raw.decode("utf-8", errors="replace")
        return json.loads(json_str)

    def is_operational(self) -> bool:
        """Returns True if the engine is fully operational."""
        if self._lib is None:
            return self._operational
        with self._lock:
            return bool(self._lib.engine_is_operational(ctypes.c_void_p(self._handle)))

    def shutdown(self) -> None:
        """Shuts down the engine and releases all resources."""
        if self._lib is not None and self._handle is not None:
            with self._lock:
                self._lib.engine_destroy(ctypes.c_void_p(self._handle))
                self._handle = None
        self._operational = False
        logger.info("Engine shut down")

    # -------------------------------------------------------------------------
    # Stub mode responses (used when C++ library is not loaded)
    # -------------------------------------------------------------------------

    def _stub_response(self, input_text: str) -> str:
        """
        Returns a plausible stub response when running without the C++ library.
        Used for testing the Python layer in isolation.
        """
        lower = input_text.lower()
        if any(g in lower for g in ["hi", "hello", "hey"]):
            return "Nice to meet you."
        if "goodbye" in lower or "bye" in lower:
            return "Goodbye!"
        if "?" in input_text:
            return "That's an interesting question. Let me think about that."
        return "I understand."
