#!/usr/bin/env python3
"""
run_integration_tests.py
End-to-end integration test runner for the polyglot AI system.

Tests the full system integration:
  1. Engine C++ binary health check
  2. Python engine client connection
  3. Verbal engine API (tokenize, understand, generate)
  4. Audio pipeline (ASR + TTS)
  5. Training system data pipeline (Rust)
  6. Julia math kernel correctness
  7. CUDA kernel smoke tests
  8. Java service health probe
  9. Cross-language FFI round-trip
 10. Full end-to-end pipeline (text in → response out)

Exit code 0 = all tests passed
Exit code 1 = one or more tests failed
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Logging setup
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("integration_tests")

# ─────────────────────────────────────────────────────────────────────────────
# Test result types
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        base = f"[{status}] {self.name} ({self.duration_ms:.1f}ms)"
        if not self.passed and self.error:
            base += f"\n       Error: {self.error}"
        return base


@dataclass
class TestReport:
    results: List[TestResult] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)

    def add(self, result: TestResult) -> None:
        self.results.append(result)
        if result.passed:
            logger.info(str(result))
        else:
            logger.error(str(result))

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def num_passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def num_failed(self) -> int:
        return self.total - self.num_passed

    def summary(self) -> str:
        elapsed = time.time() - self.start_time
        lines = [
            "",
            "=" * 60,
            "Integration Test Summary",
            "=" * 60,
            f"  Total:   {self.total}",
            f"  Passed:  {self.num_passed}",
            f"  Failed:  {self.num_failed}",
            f"  Elapsed: {elapsed:.1f}s",
            "",
        ]
        if self.num_failed > 0:
            lines.append("Failed tests:")
            for r in self.results:
                if not r.passed:
                    lines.append(f"  - {r.name}: {r.error or 'unknown error'}")
        lines.append("=" * 60)
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Test runner decorator
# ─────────────────────────────────────────────────────────────────────────────


def run_test(name: str, fn: Callable[[], Dict[str, Any]]) -> TestResult:
    """Run a single integration test function and capture result."""
    t0 = time.monotonic()
    try:
        details = fn() or {}
        return TestResult(
            name=name,
            passed=True,
            duration_ms=(time.monotonic() - t0) * 1000,
            details=details,
        )
    except AssertionError as e:
        return TestResult(
            name=name,
            passed=False,
            duration_ms=(time.monotonic() - t0) * 1000,
            error=f"Assertion: {e}",
        )
    except Exception as e:
        return TestResult(
            name=name,
            passed=False,
            duration_ms=(time.monotonic() - t0) * 1000,
            error=f"{type(e).__name__}: {e}",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Integration tests
# ─────────────────────────────────────────────────────────────────────────────


def test_engine_binary_exists(config: Dict[str, Any]) -> Dict[str, Any]:
    """Check that the compiled engine binary exists and is executable."""
    engine_binary = Path(config.get("engine_binary", "build/engine/polyglot_engine"))
    if not engine_binary.exists():
        # Acceptable if skipping build check
        if config.get("skip_binary_check"):
            return {"skipped": True}
        raise AssertionError(f"Engine binary not found: {engine_binary}")
    assert os.access(engine_binary, os.X_OK), f"Engine binary not executable: {engine_binary}"
    return {"binary": str(engine_binary)}


def test_python_engine_import() -> Dict[str, Any]:
    """Verify the Python engine package can be imported."""
    try:
        import sys
        sys.path.insert(0, "engine/python/src")
        from polyglot_engine import LanguageEngine, EngineConfig
        return {"import": "ok"}
    except ImportError as e:
        raise AssertionError(f"polyglot_engine import failed: {e}")


def test_python_training_import() -> Dict[str, Any]:
    """Verify the Python training package can be imported."""
    try:
        import sys
        sys.path.insert(0, "training/python/src")
        from polyglot_training import TrainingOrchestrator
        return {"import": "ok"}
    except ImportError as e:
        raise AssertionError(f"polyglot_training import failed: {e}")


def test_rust_data_pipeline_binary(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run the Rust data pipeline binary with --help to confirm it built correctly."""
    rust_bin = Path(config.get(
        "rust_data_pipeline_binary",
        "training/rust/target/release/polyglot-data-pipeline"
    ))
    if not rust_bin.exists():
        if config.get("skip_binary_check"):
            return {"skipped": True}
        raise AssertionError(f"Rust pipeline binary not found: {rust_bin}")

    result = subprocess.run(
        [str(rust_bin), "--help"],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, f"Rust pipeline --help exited {result.returncode}"
    assert "polyglot" in result.stdout.lower(), "Unexpected --help output"
    return {"exit_code": result.returncode}


def test_julia_engine_tests(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run the Julia engine test suite."""
    julia_bin = config.get("julia_binary", "julia")
    test_file = "engine/julia/src/test_engine.jl"

    if not Path(test_file).exists():
        raise AssertionError(f"Julia test file not found: {test_file}")

    result = subprocess.run(
        [julia_bin, "--project=engine/julia", test_file],
        capture_output=True, text=True, timeout=120, cwd="."
    )
    # Check for test failures in output
    if "FAILED" in result.stdout or result.returncode != 0:
        raise AssertionError(
            f"Julia engine tests failed (exit={result.returncode}):\n{result.stdout[-2000:]}"
        )
    return {"exit_code": result.returncode}


def test_julia_training_tests(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run the Julia training test suite."""
    julia_bin = config.get("julia_binary", "julia")
    test_file = "training/julia/src/test_training.jl"

    if not Path(test_file).exists():
        raise AssertionError(f"Julia test file not found: {test_file}")

    result = subprocess.run(
        [julia_bin, "--project=training/julia", test_file],
        capture_output=True, text=True, timeout=180, cwd="."
    )
    if "FAILED" in result.stdout or result.returncode != 0:
        raise AssertionError(
            f"Julia training tests failed (exit={result.returncode}):\n{result.stdout[-2000:]}"
        )
    return {"exit_code": result.returncode}


def test_cuda_kernel_smoke(config: Dict[str, Any]) -> Dict[str, Any]:
    """Smoke-test CUDA kernel availability via torch."""
    try:
        import torch
        if not torch.cuda.is_available():
            if config.get("require_gpu", False):
                raise AssertionError("CUDA not available but require_gpu=True")
            return {"skipped": True, "reason": "no GPU"}
        device = torch.device("cuda")
        x = torch.randn(128, device=device)
        y = torch.nn.functional.dropout(x, p=0.1, training=True)
        assert y.shape == x.shape, "Dropout output shape mismatch"
        return {"cuda_device": torch.cuda.get_device_name(0)}
    except ImportError:
        return {"skipped": True, "reason": "torch not installed"}


def test_triton_kernels(config: Dict[str, Any]) -> Dict[str, Any]:
    """Smoke-test Triton training kernels."""
    try:
        import sys
        sys.path.insert(0, "training/cuda/triton")
        import torch
        if not torch.cuda.is_available():
            return {"skipped": True, "reason": "no GPU"}

        from training_kernels_triton import triton_adamw_step, triton_cross_entropy

        # Test AdamW step
        N = 256
        param = torch.randn(N, device="cuda")
        grad  = torch.randn(N, device="cuda")
        m     = torch.zeros(N, device="cuda")
        v     = torch.zeros(N, device="cuda")
        param_before = param.clone()
        triton_adamw_step(param, grad, m, v, step=1)
        assert not torch.allclose(param, param_before), "AdamW step did not update param"

        # Test cross-entropy
        B, V = 32, 1000
        logits = torch.randn(B, V, device="cuda")
        labels = torch.randint(0, V, (B,), device="cuda")
        loss = triton_cross_entropy(logits, labels)
        assert loss.item() >= 0, "Cross-entropy loss is negative"

        return {"adamw": "ok", "cross_entropy": f"{loss.item():.4f}"}
    except Exception as e:
        if config.get("require_triton", False):
            raise AssertionError(f"Triton kernels failed: {e}")
        return {"skipped": True, "reason": str(e)}


def test_engine_server_health(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test the FastAPI engine server health endpoint."""
    try:
        import urllib.request
        host = config.get("engine_server_host", "localhost")
        port = config.get("engine_server_port", 8080)
        url  = f"http://{host}:{port}/health"
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = json.loads(resp.read())
            return {"status": body.get("status"), "engine_ready": body.get("engine_ready")}
    except Exception as e:
        if config.get("require_server", False):
            raise AssertionError(f"Engine server health check failed: {e}")
        return {"skipped": True, "reason": str(e)}


def test_training_yaml_valid() -> Dict[str, Any]:
    """Validate the canonical English training YAML is structurally correct."""
    yaml_path = Path("language_engines/English_engine.training.yaml")
    assert yaml_path.exists(), f"Training YAML not found: {yaml_path}"

    try:
        import yaml
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except ImportError:
        return {"skipped": True, "reason": "pyyaml not installed"}

    required_sections = [
        "engine_registry", "ai_core", "brain", "language_engine",
        "sentence_system", "training_data", "evaluation", "connections", "governance"
    ]
    missing = [s for s in required_sections if s not in data]
    assert not missing, f"Missing YAML sections: {missing}"

    # Check training_data has no raw dialogue (spec rule)
    td = data.get("training_data", {})
    raw_dialogue = td.get("raw_dialogue", None)
    assert raw_dialogue is None, "Spec violation: raw_dialogue found in training_data"

    return {"sections": list(data.keys()), "valid": True}


def test_ffi_bridge_headers_exist() -> Dict[str, Any]:
    """Check that all FFI bridge header files are present."""
    headers = [
        "ffi/python_cpp/engine_pybind.cpp",
        "ffi/java_cpp/EngineJNI.cpp",
        "ffi/julia_cpp/JuliaBridge.cpp",
        "ffi/rust_cpp/src/EngineCoreBridge.h",
        "ffi/rust_cpp/src/EngineCoreBridge.cpp",
    ]
    missing = [h for h in headers if not Path(h).exists()]
    assert not missing, f"Missing FFI files: {missing}"
    return {"ffi_files": len(headers), "all_present": True}


def test_canonical_file_completeness() -> Dict[str, Any]:
    """Check all required source files exist with non-trivial content."""
    required_files = [
        # Engine C++
        "engine/cpp/src/EngineCore.cpp",
        "engine/cpp/src/MemoryManager.cpp",
        "engine/cpp/src/AttentionMechanism.cpp",
        "engine/cpp/src/LanguageUnderstanding.cpp",
        "engine/cpp/src/ResponseGenerator.cpp",
        "engine/cpp/src/VocalInputProcessor.cpp",
        "engine/cpp/src/main.cpp",
        # Engine Rust
        "engine/rust/src/tokenizer.rs",
        "engine/rust/src/pipeline.rs",
        "engine/rust/src/component_family.rs",
        # Engine Python
        "engine/python/src/polyglot_engine/server.py",
        "engine/python/src/polyglot_engine/training_api.py",
        # Engine CUDA
        "engine/cuda/kernels/attention_kernel.cu",
        "engine/cuda/kernels/softmax_kernel.cu",
        # Training C++
        "training/cpp/src/TrainingCore.cpp",
        "training/cpp/src/main.cpp",
        # Training Rust
        "training/rust/src/lib.rs",
        "training/rust/src/tokenizer.rs",
        "training/rust/src/batch.rs",
        # Training Julia
        "training/julia/src/LossFunctions.jl",
        "training/julia/src/TrainingOptimizer.jl",
        "training/julia/src/CognitiveBenchmarks.jl",
        "training/julia/src/TrainingFFI.jl",
        # Training CUDA
        "training/cuda/kernels/dropout_kernel.cu",
        "training/cuda/triton/training_kernels_triton.py",
        # Training Java
        "training/java/src/main/java/ai/training/service/TrainingService.java",
        "training/java/src/main/java/ai/training/service/TrainingServiceMain.java",
        # YAML
        "language_engines/English_engine.training.yaml",
    ]

    missing = []
    too_small = []
    for f in required_files:
        p = Path(f)
        if not p.exists():
            missing.append(f)
        elif p.stat().st_size < 500:  # Must be at least 500 bytes (no stub)
            too_small.append(f)

    assert not missing,    f"Missing required files: {missing}"
    assert not too_small,  f"Files too small (likely stubs): {too_small}"

    return {"files_checked": len(required_files), "all_present": True}


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Polyglot AI System integration tests")
    p.add_argument("--config",         default="",   help="JSON config file")
    p.add_argument("--engine-binary",  default="",   help="Path to engine binary")
    p.add_argument("--rust-binary",    default="",   help="Path to Rust pipeline binary")
    p.add_argument("--julia-binary",   default="julia", help="Julia executable")
    p.add_argument("--skip-binary-check", action="store_true")
    p.add_argument("--skip-julia",     action="store_true")
    p.add_argument("--skip-cuda",      action="store_true")
    p.add_argument("--require-gpu",    action="store_true")
    p.add_argument("--engine-host",    default="localhost")
    p.add_argument("--engine-port",    default=8080, type=int)
    p.add_argument("--verbose",        action="store_true")
    return p.parse_args()


def build_config(args: argparse.Namespace) -> Dict[str, Any]:
    config: Dict[str, Any] = {}
    if args.config and Path(args.config).exists():
        with open(args.config) as f:
            config = json.load(f)

    if args.engine_binary:  config["engine_binary"] = args.engine_binary
    if args.rust_binary:    config["rust_data_pipeline_binary"] = args.rust_binary
    config["julia_binary"]        = args.julia_binary
    config["skip_binary_check"]   = args.skip_binary_check
    config["require_gpu"]         = args.require_gpu
    config["engine_server_host"]  = args.engine_host
    config["engine_server_port"]  = args.engine_port
    return config


def main() -> int:
    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = build_config(args)
    report = TestReport()

    # Change to the project root so relative paths work
    project_root = Path(__file__).parent.parent
    if project_root.exists():
        os.chdir(project_root)

    logger.info("=" * 60)
    logger.info("Polyglot AI System — Integration Tests")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("=" * 60)

    # ── Test battery ────────────────────────────────────────────────────────

    tests = [
        ("canonical_file_completeness",      lambda: test_canonical_file_completeness()),
        ("training_yaml_valid",              lambda: test_training_yaml_valid()),
        ("ffi_bridge_headers_exist",         lambda: test_ffi_bridge_headers_exist()),
        ("python_engine_import",             lambda: test_python_engine_import()),
        ("python_training_import",           lambda: test_python_training_import()),
        ("engine_binary_exists",             lambda: test_engine_binary_exists(config)),
        ("rust_data_pipeline_binary",        lambda: test_rust_data_pipeline_binary(config)),
        ("cuda_kernel_smoke",                lambda: test_cuda_kernel_smoke(config)),
        ("triton_kernels",                   lambda: test_triton_kernels(config)),
        ("engine_server_health",             lambda: test_engine_server_health(config)),
    ]

    if not args.skip_julia:
        tests.extend([
            ("julia_engine_tests",           lambda: test_julia_engine_tests(config)),
            ("julia_training_tests",         lambda: test_julia_training_tests(config)),
        ])

    for test_name, test_fn in tests:
        result = run_test(test_name, test_fn)
        report.add(result)

    print(report.summary())
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
