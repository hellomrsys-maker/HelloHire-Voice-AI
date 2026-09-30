# Build Instructions — Polyglot AI System

## Quick Start

```bash
cd polyglot_ai_system
./scripts/build_all.sh --jobs 8
```

This builds all 6 language components in dependency order and installs everything.

---

## Prerequisites

### Required

| Tool | Minimum version | Purpose |
|------|----------------|---------|
| CMake | 3.24 | C++ and CUDA build system |
| Rust / Cargo | 1.75 | Rust components |
| Python | 3.10 | Python packages and scripts |
| GCC or Clang | GCC 12 / Clang 16 | C++20 support |

### Optional (enables full functionality)

| Tool | Purpose |
|------|---------|
| CUDA Toolkit 12.x + nvcc | GPU kernels (attention, optimizer, ASR/TTS) |
| Julia 1.9+ | Mathematical kernels and benchmarks |
| JDK 17+ + Gradle 8 | Java infrastructure and services |
| Triton 2.1+ | Triton GPU kernels (auto-installed with PyTorch) |
| flash-attn 2.4+ | Flash Attention Python bindings |

---

## Step-by-Step Build

### 1. Clone and enter project

```bash
cd polyglot_ai_system
```

### 2. Build Rust components

```bash
# Engine tokenizer and pipeline
cd engine/rust
cargo build --release
cd ../..

# Training data pipeline
cd training/rust
cargo build --release
cd ../..

# FFI Rust-C++ bridge
cd ffi/rust_cpp
cargo build --release
cd ../..
```

### 3. Build C++ and CUDA with CMake

```bash
# With CUDA
cmake -S . -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DPOLYGLOT_ENABLE_CUDA=ON \
    -DPOLYGLOT_BUILD_ENGINE=ON \
    -DPOLYGLOT_BUILD_TRAINING=ON \
    -DPOLYGLOT_BUILD_FFI=ON

cmake --build build --parallel 8

# Without CUDA (CPU-only)
cmake -S . -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DPOLYGLOT_ENABLE_CUDA=OFF \
    -DPOLYGLOT_BUILD_ENGINE=ON \
    -DPOLYGLOT_BUILD_TRAINING=ON \
    -DPOLYGLOT_BUILD_FFI=ON

cmake --build build --parallel 8
```

**Output artifacts:**
- `build/engine/polyglot_engine` — engine binary
- `build/engine/libpolyglot_engine.so` — engine shared library
- `build/training/polyglot_training` — training binary
- `build/ffi/libengine_pybind.so` — Python bindings
- `build/ffi/libengine_jni.so` — Java JNI library
- `build/ffi/libjulia_bridge.so` — Julia ccall bridge

### 4. Install Julia packages

```bash
# Engine math packages
julia --project=engine/julia -e 'using Pkg; Pkg.instantiate()'

# Training math packages
julia --project=training/julia -e 'using Pkg; Pkg.instantiate()'
```

### 5. Install Python packages

```bash
# Engine Python package
pip install -e engine/python

# Training Python package
pip install -e training/python

# For GPU training with Triton (Linux only):
pip install flash-attn triton
```

### 6. Build Java services

```bash
# Using Gradle wrapper (preferred)
./gradlew build

# Or if Gradle is installed globally
gradle build
```

---

## Running the System

### SYSTEM 2 — Verbal Engine (start first)

```bash
# Run the C++ engine binary directly
./build/engine/polyglot_engine --help

# Run the Python FastAPI server
export ENGINE_LIB_PATH=./build/engine/libpolyglot_engine.so
export ENGINE_WEIGHTS_PATH=./weights/engine_weights.safetensors
python3 -m polyglot_engine.server

# Or with uvicorn directly
uvicorn polyglot_engine.server:app --host 0.0.0.0 --port 8080

# Run the Java engine service
java -Djava.library.path=./build/ffi \
     -jar engine/java/build/libs/polyglot-engine-1.0.0.jar \
     --lib-path ./build/engine/libpolyglot_engine.so

# Verify engine is operational
python3 -m polyglot_engine.verify
```

### SYSTEM 1 — AI Training (start after engine is verified)

```bash
# Run C++ training binary
./build/training/polyglot_training \
    --data data/training/english_records.jsonl \
    --output output/training \
    --epochs 20 \
    --batch-size 64 \
    --lr 1e-4

# Run Python orchestrator
python3 -m polyglot_training.cli \
    --config config/training_config.yaml

# Run Java training service
java -Djava.library.path=./build/ffi \
     -jar training/java/build/libs/polyglot-training-1.0.0.jar \
     --data data/training/english_records.jsonl \
     --output output/training \
     --epochs 20

# Run Rust data pipeline standalone
./training/rust/target/release/polyglot-data-pipeline \
    --data data/training/english_records.jsonl \
    --epochs 1 --verbose
```

---

## Running Tests

### All integration tests

```bash
python3 scripts/run_integration_tests.py
```

### Per-language tests

```bash
# Rust
cargo test --manifest-path engine/rust/Cargo.toml
cargo test --manifest-path training/rust/Cargo.toml

# C++ (via CMake CTest)
cd build && ctest --output-on-failure

# Julia
julia --project=engine/julia   engine/julia/src/test_engine.jl
julia --project=training/julia training/julia/src/test_training.jl

# Python
pytest engine/python/
pytest training/python/

# Java
./gradlew test
```

### With full build and tests in one command

```bash
./scripts/build_all.sh --test --jobs 8
```

---

## Environment Variables

### Engine configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ENGINE_HOST` | `127.0.0.1` | C++ engine gRPC host |
| `ENGINE_PORT` | `50051` | C++ engine gRPC port |
| `ENGINE_LIB_PATH` | `` | Path to libpolyglot_engine.so |
| `ENGINE_WEIGHTS_PATH` | `` | Path to model weights (.safetensors) |
| `VOCAB_SIZE` | `32000` | Tokenizer vocabulary size |
| `HIDDEN_DIM` | `1024` | Model hidden dimension |
| `NUM_HEADS` | `16` | Attention heads |
| `NUM_LAYERS` | `24` | Transformer layers |
| `DEVICE` | `cuda` | Compute device (cuda / cpu) |
| `SERVER_HOST` | `0.0.0.0` | FastAPI server bind address |
| `SERVER_PORT` | `8080` | FastAPI server port |

### Training configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `TRAINING_DATA_PATH` | `` | JSONL training data path |
| `TRAINING_VOCAB_PATH` | `` | BPE vocabulary path |
| `TRAINING_OUTPUT_DIR` | `output/training` | Checkpoint output directory |
| `TRAINING_EPOCHS` | `10` | Number of training epochs |
| `TRAINING_BATCH` | `32` | Batch size |
| `TRAINING_LR` | `1e-4` | Learning rate |
| `TRAINING_WD` | `0.01` | Weight decay |
| `TRAINING_WORKERS` | `4` | Data pipeline workers |
| `TRAINING_IPC_SOCKET` | `/tmp/polyglot_training.sock` | IPC socket path |
| `TRAINING_NATIVE_LIB` | `` | Path to JNI native library |
| `TRAINING_USE_CUDA` | `true` | Enable CUDA |

---

## Troubleshooting

### `libpolyglot_engine.so: cannot open shared object file`
Add the build directory to `LD_LIBRARY_PATH`:
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/build/engine
```

### `UnsatisfiedLinkError` in Java
Set `-Djava.library.path` to include the directory containing `libengine_jni.so`:
```bash
java -Djava.library.path=./build/ffi -jar ...
```

### Julia package not found
Ensure you run Julia with `--project=engine/julia` or `--project=training/julia` so it finds `Project.toml`.

### CUDA kernels not loading
Verify CUDA toolkit version matches compiled kernels:
```bash
nvcc --version
python3 -c "import torch; print(torch.version.cuda)"
```
Both should report the same major.minor version.

### Rust `cxx` bridge compile error
Ensure the C++ include path is correct in `ffi/rust_cpp/build.rs`. The engine headers must be built before the bridge:
```bash
cmake --build build --target polyglot_engine_lib  # build C++ lib first
cd ffi/rust_cpp && cargo build --release
```

---

## Directory Structure (Summary)

```
polyglot_ai_system/
├── README.md
├── Makefile                         # Unified build orchestration
├── CMakeLists.txt                   # Top-level CMake
├── Cargo.toml                       # Rust workspace manifest
├── build.gradle                     # Java multi-project Gradle
├── language_engines/
│   └── English_engine.training.yaml # Canonical English engine (spec-compliant)
├── engine/                          # SYSTEM 2 — Verbal Communication Engine
│   ├── cpp/                         # C++ engine core
│   ├── rust/                        # Rust tokenizer + pipeline
│   ├── julia/                       # Julia math layer
│   ├── cuda/                        # CUDA + Triton kernels
│   ├── python/                      # Python engine package
│   └── java/                        # Java engine service
├── training/                        # SYSTEM 1 — AI Training System
│   ├── cpp/                         # C++ training core (8 faculties)
│   ├── rust/                        # Rust data pipeline
│   ├── julia/                       # Julia optimizer + benchmarks
│   ├── cuda/                        # Training CUDA + Triton kernels
│   ├── python/                      # Python training orchestrator
│   └── java/                        # Java training scheduler
├── ffi/                             # Cross-language bridges
│   ├── python_cpp/                  # pybind11
│   ├── java_cpp/                    # JNI
│   ├── julia_cpp/                   # ccall
│   └── rust_cpp/                    # cxx
├── scripts/
│   ├── build_all.sh                 # Full build script
│   └── run_integration_tests.py     # End-to-end tests
└── docs/
    ├── ARCHITECTURE.md              # This document's companion
    └── BUILD.md                     # This document
```
