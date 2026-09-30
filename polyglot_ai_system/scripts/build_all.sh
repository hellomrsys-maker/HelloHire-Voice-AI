#!/usr/bin/env bash
# build_all.sh — Unified build script for the polyglot AI system.
# Builds all 6 language components in the correct dependency order:
#   1. Rust (engine + training data pipelines)
#   2. C++ + CUDA (engine core + training core)
#   3. FFI bridges (Python/pybind11, Java/JNI, Julia/ccall, Rust/cxx)
#   4. Julia (engine + training packages)
#   5. Python (engine + training packages)
#   6. Java (engine + training services)
#
# Usage:
#   ./scripts/build_all.sh [OPTIONS]
#   Options:
#     --debug       Build in debug mode (default: release)
#     --no-cuda     Disable CUDA compilation
#     --no-java     Skip Java build
#     --no-julia    Skip Julia package installation
#     --jobs N      Parallel build jobs (default: nproc)
#     --clean       Clean all build artifacts before building
#     --test        Run tests after each language component builds
#     --help        Print this help

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build"

CMAKE_BUILD_TYPE="Release"
CUDA_ENABLED=true
JAVA_ENABLED=true
JULIA_ENABLED=true
RUN_TESTS=false
CLEAN=false
JOBS="${JOBS:-$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*"; }
log_section() { echo -e "\n${BLUE}════════════════════════════════════════════════════════${NC}"; \
                echo -e "${BLUE}  $*${NC}"; \
                echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"; }

# ─────────────────────────────────────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --debug)     CMAKE_BUILD_TYPE="Debug"; shift ;;
        --no-cuda)   CUDA_ENABLED=false; shift ;;
        --no-java)   JAVA_ENABLED=false; shift ;;
        --no-julia)  JULIA_ENABLED=false; shift ;;
        --jobs)      JOBS="$2"; shift 2 ;;
        --clean)     CLEAN=true; shift ;;
        --test)      RUN_TESTS=true; shift ;;
        --help|-h)
            head -30 "${BASH_SOURCE[0]}" | grep "^#" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ─────────────────────────────────────────────────────────────────────────────
# Prerequisites check
# ─────────────────────────────────────────────────────────────────────────────

log_section "Checking prerequisites"

check_cmd() {
    if command -v "$1" &>/dev/null; then
        log_ok "$1 found: $(command -v "$1")"
        return 0
    else
        if [[ "${2:-required}" == "optional" ]]; then
            log_warn "$1 not found (optional — skipping related builds)"
        else
            log_error "$1 not found (required)"
            return 1
        fi
    fi
}

check_cmd cmake
check_cmd cargo
check_cmd python3
JULIA_AVAILABLE=true;  check_cmd julia  optional || JULIA_AVAILABLE=false
JAVA_AVAILABLE=true;   check_cmd javac  optional || JAVA_AVAILABLE=false
NVCC_AVAILABLE=true;   check_cmd nvcc   optional || NVCC_AVAILABLE=false
check_cmd pkg-config optional || true

if [[ "${CUDA_ENABLED}" == true && "${NVCC_AVAILABLE}" == false ]]; then
    log_warn "CUDA requested but nvcc not found — disabling CUDA"
    CUDA_ENABLED=false
fi
if [[ "${JAVA_ENABLED}" == true && "${JAVA_AVAILABLE}" == false ]]; then
    log_warn "Java requested but javac not found — disabling Java"
    JAVA_ENABLED=false
fi
if [[ "${JULIA_ENABLED}" == true && "${JULIA_AVAILABLE}" == false ]]; then
    log_warn "Julia requested but julia not found — disabling Julia"
    JULIA_ENABLED=false
fi

cd "${PROJECT_ROOT}"
log_info "Project root: ${PROJECT_ROOT}"
log_info "Build type:   ${CMAKE_BUILD_TYPE}"
log_info "Jobs:         ${JOBS}"
log_info "CUDA:         ${CUDA_ENABLED}"
log_info "Java:         ${JAVA_ENABLED}"
log_info "Julia:        ${JULIA_ENABLED}"

# ─────────────────────────────────────────────────────────────────────────────
# Clean
# ─────────────────────────────────────────────────────────────────────────────

if [[ "${CLEAN}" == true ]]; then
    log_section "Cleaning build artifacts"
    rm -rf "${BUILD_DIR}"
    find . -name "target" -maxdepth 3 -type d | grep -v ".git" | xargs rm -rf 2>/dev/null || true
    log_ok "Clean complete"
fi

mkdir -p "${BUILD_DIR}"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Rust components
# ─────────────────────────────────────────────────────────────────────────────

log_section "1. Building Rust components"

# Engine Rust
log_info "Building engine/rust..."
(cd engine/rust && cargo build --release -j "${JOBS}" 2>&1 | tail -5)
log_ok "engine/rust built"

# Training Rust
log_info "Building training/rust..."
(cd training/rust && cargo build --release -j "${JOBS}" 2>&1 | tail -5)
log_ok "training/rust built"

# FFI Rust-C++ bridge
log_info "Building ffi/rust_cpp..."
(cd ffi/rust_cpp && cargo build --release -j "${JOBS}" 2>&1 | tail -5)
log_ok "ffi/rust_cpp built"

if [[ "${RUN_TESTS}" == true ]]; then
    log_info "Running Rust tests..."
    (cd engine/rust  && cargo test --release 2>&1 | tail -10) || log_warn "engine/rust tests had failures"
    (cd training/rust && cargo test --release 2>&1 | tail -10) || log_warn "training/rust tests had failures"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 2. C++ + CUDA (CMake)
# ─────────────────────────────────────────────────────────────────────────────

log_section "2. Building C++ and CUDA components"

CMAKE_ARGS=(
    -DCMAKE_BUILD_TYPE="${CMAKE_BUILD_TYPE}"
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
    -DPOLYGLOT_BUILD_ENGINE=ON
    -DPOLYGLOT_BUILD_TRAINING=ON
    -DPOLYGLOT_BUILD_FFI=ON
)
if [[ "${CUDA_ENABLED}" == true ]]; then
    CMAKE_ARGS+=(-DPOLYGLOT_ENABLE_CUDA=ON)
else
    CMAKE_ARGS+=(-DPOLYGLOT_ENABLE_CUDA=OFF)
fi

cmake -S . -B "${BUILD_DIR}" "${CMAKE_ARGS[@]}"
cmake --build "${BUILD_DIR}" --parallel "${JOBS}"
log_ok "C++ and CUDA components built"

# ─────────────────────────────────────────────────────────────────────────────
# 3. Julia packages
# ─────────────────────────────────────────────────────────────────────────────

if [[ "${JULIA_ENABLED}" == true ]]; then
    log_section "3. Installing Julia packages"

    log_info "Instantiating engine/julia..."
    julia --project=engine/julia -e 'using Pkg; Pkg.instantiate()' 2>&1 | tail -5
    log_ok "engine/julia packages installed"

    log_info "Instantiating training/julia..."
    julia --project=training/julia -e 'using Pkg; Pkg.instantiate()' 2>&1 | tail -5
    log_ok "training/julia packages installed"

    if [[ "${RUN_TESTS}" == true ]]; then
        log_info "Running Julia engine tests..."
        julia --project=engine/julia engine/julia/src/test_engine.jl 2>&1 | tail -20 \
            || log_warn "Julia engine tests had failures"
        log_info "Running Julia training tests..."
        julia --project=training/julia training/julia/src/test_training.jl 2>&1 | tail -20 \
            || log_warn "Julia training tests had failures"
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 4. Python packages
# ─────────────────────────────────────────────────────────────────────────────

log_section "4. Installing Python packages"

log_info "Installing engine/python (editable)..."
pip install -e engine/python --quiet
log_ok "engine/python installed"

log_info "Installing training/python (editable)..."
pip install -e training/python --quiet
log_ok "training/python installed"

if [[ "${RUN_TESTS}" == true ]]; then
    log_info "Running Python tests..."
    python3 -m pytest engine/python -q 2>&1 | tail -10 || log_warn "Python engine tests had failures"
    python3 -m pytest training/python -q 2>&1 | tail -10 || log_warn "Python training tests had failures"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 5. Java
# ─────────────────────────────────────────────────────────────────────────────

if [[ "${JAVA_ENABLED}" == true ]]; then
    log_section "5. Building Java components"

    if command -v gradle &>/dev/null; then
        gradle build -p . --parallel 2>&1 | tail -20
        log_ok "Java build complete (Gradle)"
    elif [[ -f "./gradlew" ]]; then
        chmod +x ./gradlew
        ./gradlew build --parallel 2>&1 | tail -20
        log_ok "Java build complete (gradlew)"
    else
        log_warn "Neither gradle nor gradlew found — skipping Java build"
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 6. Integration tests (optional)
# ─────────────────────────────────────────────────────────────────────────────

if [[ "${RUN_TESTS}" == true ]]; then
    log_section "6. Running integration tests"
    python3 scripts/run_integration_tests.py \
        --skip-julia \
        --engine-binary "${BUILD_DIR}/engine/polyglot_engine" \
        --rust-binary "training/rust/target/release/polyglot-data-pipeline" \
        2>&1 | tail -40 || log_warn "Some integration tests failed"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

log_section "Build Summary"
log_ok "Rust engine:        engine/rust/target/release/libpolyglot_engine.{so,dylib,dll}"
log_ok "Rust training:      training/rust/target/release/polyglot-data-pipeline"
log_ok "C++ engine:         ${BUILD_DIR}/engine/polyglot_engine"
log_ok "C++ training:       ${BUILD_DIR}/training/polyglot_training"
[[ "${CUDA_ENABLED}" == true ]] && log_ok "CUDA kernels:       ${BUILD_DIR}/engine/cuda/ and ${BUILD_DIR}/training/cuda/"
[[ "${JULIA_ENABLED}" == true ]] && log_ok "Julia packages:     engine/julia and training/julia"
log_ok "Python packages:    polyglot-engine and polyglot-training (editable installs)"
[[ "${JAVA_ENABLED}" == true ]] && log_ok "Java:               engine/java and training/java"
echo ""
log_ok "All components built successfully!"
echo ""
log_info "To run the engine:  ${BUILD_DIR}/engine/polyglot_engine --help"
log_info "To run training:    ${BUILD_DIR}/training/polyglot_training --help"
log_info "To run API server:  python3 -m polyglot_engine.server"
log_info "To run tests:       python3 scripts/run_integration_tests.py"
