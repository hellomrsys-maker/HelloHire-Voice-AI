# =============================================================================
# engine/python/src/polyglot_engine/verify.py
# Engine verification script — validates all subsystems are operational
# before any training begins. Called by `make verify-engine`.
# =============================================================================

from __future__ import annotations

import sys
import logging
import argparse
import time
from typing import NamedTuple

logger = logging.getLogger(__name__)


class VerificationResult(NamedTuple):
    component: str
    passed:    bool
    message:   str
    latency_ms: float


def verify_python_layer() -> VerificationResult:
    """Verifies the Python engine client can be imported and instantiated."""
    t0 = time.monotonic()
    try:
        from polyglot_engine.engine_client import EngineClient, EngineClientConfig
        from polyglot_engine.language_engine import LanguageEngineLoader

        config = EngineClientConfig(enable_gpu=False, thread_pool_size=2)
        with EngineClient(config) as client:
            assert client.is_operational(), "Engine not operational"

            # Test basic response
            response = client.process_text("Hi, I am Ash.")
            assert isinstance(response, str), "Response must be a string"
            assert len(response) > 0, "Response must not be empty"

        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="python_layer",
            passed=True,
            message=f"Python layer OK — response: '{response[:60]}'",
            latency_ms=elapsed,
        )
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="python_layer",
            passed=False,
            message=f"Python layer FAILED: {e}",
            latency_ms=elapsed,
        )


def verify_language_engine_loader() -> VerificationResult:
    """Verifies the language engine YAML loader."""
    t0 = time.monotonic()
    try:
        from pathlib import Path
        from polyglot_engine.language_engine import LanguageEngineLoader

        loader = LanguageEngineLoader()
        yaml_path = Path(__file__).parent.parent.parent.parent.parent.parent / \
            "language_engines" / "English_engine.training.yaml"

        engine = loader.load_or_create_default(str(yaml_path))
        assert engine.engine_registry.language_code == "en", "Language code must be 'en'"

        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="language_engine_loader",
            passed=True,
            message=(
                f"Loader OK — engine_id={engine.engine_registry.engine_id}, "
                f"hash={engine.file_hash[:12]}..."
            ),
            latency_ms=elapsed,
        )
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="language_engine_loader",
            passed=False,
            message=f"Language engine loader FAILED: {e}",
            latency_ms=elapsed,
        )


def verify_cpp_library() -> VerificationResult:
    """Verifies the C++ engine_core library is loadable."""
    t0 = time.monotonic()
    try:
        import ctypes
        import os
        from pathlib import Path

        lib_candidates = [
            os.environ.get("ENGINE_LIB_PATH", ""),
            str(Path(__file__).parent.parent.parent.parent.parent /
                "build" / "cpp" / "engine" / "libengine_core.so"),
            "/usr/local/lib/libengine_core.so",
        ]

        loaded = False
        for candidate in lib_candidates:
            if candidate and os.path.exists(candidate):
                lib = ctypes.CDLL(candidate)
                # Verify the health check export exists
                assert hasattr(lib, "engine_create"), "Missing engine_create symbol"
                loaded = True
                elapsed = (time.monotonic() - t0) * 1000
                return VerificationResult(
                    component="cpp_library",
                    passed=True,
                    message=f"C++ library loaded: {candidate}",
                    latency_ms=elapsed,
                )

        # Library not found — not a hard failure in development
        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="cpp_library",
            passed=False,
            message=(
                "C++ engine_core library not found. "
                "Run: cmake --build build/cpp/engine && make engine-cpp"
            ),
            latency_ms=elapsed,
        )
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="cpp_library",
            passed=False,
            message=f"C++ library check FAILED: {e}",
            latency_ms=elapsed,
        )


def verify_rust_library() -> VerificationResult:
    """Verifies the Rust engine library is loadable."""
    t0 = time.monotonic()
    try:
        import ctypes
        import os
        from pathlib import Path

        candidates = [
            str(Path(__file__).parent.parent.parent.parent.parent /
                "engine" / "rust" / "target" / "release" / "libengine_rust.so"),
            os.environ.get("RUST_LIB_PATH", ""),
        ]

        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                lib = ctypes.CDLL(candidate)
                result = lib.rust_engine_health_check()
                elapsed = (time.monotonic() - t0) * 1000
                return VerificationResult(
                    component="rust_library",
                    passed=(result == 1),
                    message=f"Rust library health check: {result}",
                    latency_ms=elapsed,
                )

        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="rust_library",
            passed=False,
            message=(
                "Rust engine library not found. "
                "Run: cd engine/rust && cargo build --release"
            ),
            latency_ms=elapsed,
        )
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="rust_library",
            passed=False,
            message=f"Rust library check FAILED: {e}",
            latency_ms=elapsed,
        )


def verify_cuda_available() -> VerificationResult:
    """Verifies CUDA is available for GPU kernels."""
    t0 = time.monotonic()
    try:
        import torch
        available = torch.cuda.is_available()
        elapsed = (time.monotonic() - t0) * 1000

        if available:
            device_name = torch.cuda.get_device_name(0)
            capability = torch.cuda.get_device_capability(0)
            return VerificationResult(
                component="cuda",
                passed=True,
                message=f"CUDA available: {device_name} (compute {capability[0]}.{capability[1]})",
                latency_ms=elapsed,
            )
        else:
            return VerificationResult(
                component="cuda",
                passed=False,
                message="CUDA not available — GPU kernels will be disabled",
                latency_ms=elapsed,
            )
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="cuda",
            passed=False,
            message=f"CUDA check failed: {e}",
            latency_ms=elapsed,
        )


def verify_triton_kernels() -> VerificationResult:
    """Verifies Triton FlashAttention kernel."""
    t0 = time.monotonic()
    try:
        import torch
        if not torch.cuda.is_available():
            elapsed = (time.monotonic() - t0) * 1000
            return VerificationResult(
                component="triton_kernels",
                passed=False,
                message="Skipped — CUDA not available",
                latency_ms=elapsed,
            )

        import sys, os
        triton_path = os.path.join(os.path.dirname(__file__),
                                   "..", "..", "..", "..", "..",
                                   "engine", "cuda", "triton")
        sys.path.insert(0, os.path.abspath(triton_path))
        from attention_triton import verify_triton_attention

        passed = verify_triton_attention(batch=1, heads=2, seq_len=32, head_dim=32)
        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="triton_kernels",
            passed=passed,
            message="Triton FlashAttention: PASSED" if passed else "Triton FlashAttention: FAILED",
            latency_ms=elapsed,
        )
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        return VerificationResult(
            component="triton_kernels",
            passed=False,
            message=f"Triton kernel check failed: {e}",
            latency_ms=elapsed,
        )


def run_verification(args: argparse.Namespace | None = None) -> bool:
    """
    Runs all engine verification checks.

    Returns:
        True if all critical checks pass, False otherwise.

    The 'critical' checks are:
        - python_layer
        - language_engine_loader

    Non-critical (logged as warnings):
        - cpp_library (may not be compiled yet)
        - rust_library (may not be compiled yet)
        - cuda (may not be on a GPU machine)
        - triton_kernels (may not be on a GPU machine)
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    check_all = (args is None) or getattr(args, "all", False)

    verifiers = [
        verify_python_layer,
        verify_language_engine_loader,
    ]

    if check_all:
        verifiers += [
            verify_cpp_library,
            verify_rust_library,
            verify_cuda_available,
            verify_triton_kernels,
        ]

    critical_components = {"python_layer", "language_engine_loader"}

    results = []
    for verifier in verifiers:
        result = verifier()
        results.append(result)
        status_icon = "✓" if result.passed else "✗"
        level = logging.INFO if result.passed else logging.WARNING
        logger.log(level,
                   "%s [%s] %.1fms — %s",
                   status_icon, result.component, result.latency_ms, result.message)

    # Determine overall pass/fail
    critical_passed = all(
        r.passed for r in results if r.component in critical_components
    )

    total     = len(results)
    passed    = sum(1 for r in results if r.passed)
    critical_count = sum(1 for r in results if r.component in critical_components)

    print(f"\n{'='*60}")
    print(f"Engine Verification: {passed}/{total} checks passed")
    print(f"Critical checks: {critical_count}/{len(critical_components)}")
    print("Status: OPERATIONAL" if critical_passed else "Status: NOT OPERATIONAL")
    print('='*60)

    return critical_passed


def main() -> None:
    """CLI entry point for engine verification."""
    parser = argparse.ArgumentParser(
        description="Polyglot AI Engine Verification Tool"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Run all checks including library presence and GPU checks"
    )
    args = parser.parse_args()

    success = run_verification(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
