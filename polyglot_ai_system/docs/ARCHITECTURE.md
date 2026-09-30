# Architecture — Polyglot AI System

## Overview

The Polyglot AI System is a production-grade, state-of-the-art AI training and inference platform implemented across exactly **6 programming languages**, each assigned to the layer where it delivers maximum benefit. The system comprises two fully integrated subsystems:

- **SYSTEM 2 — Verbal Communication Engine** (built and verified first)
- **SYSTEM 1 — AI Training System** (built after engine verification passes)

Both systems share the same polyglot infrastructure and communicate through well-defined FFI bridges.

---

## The Two Systems

### SYSTEM 2 — Verbal Communication Engine

The verbal engine is a **recruitment-driven architecture**: every component is instantiated in dependency order, registered by name, and wired through the `EngineCore` coordinator before any training begins.

```
Audio In ──► VocalInputProcessor (CUDA ASR kernel)
               │
               ▼
          LanguageUnderstanding (C++ + attention heads)
               │ tokenize (Rust BPE)
               ▼
          AttentionMechanism (Flash Attention 2, CUDA)
               │ KV-cache, RoPE
               ▼
          MemoryManager (episodic + semantic recall)
               │
               ▼
          ResponseGenerator (C++ + Julia math)
               │
               ▼
          VocalInputProcessor (CUDA TTS kernel)
               │
               ▼
         Audio Out / Text Out
```

The engine exposes:
- C++ binary: `polyglot_engine` (direct invocation)
- Python FastAPI server: `polyglot_engine.server` (REST API)
- Java service: `EngineService` (JVM orchestration)
- Julia math layer: `EngineFFI` (numerical computation)

**Build order enforcement:** The `Makefile` and `build_all.sh` both enforce that the engine is built, linked, and health-verified before the training system's loop is entered.

---

### SYSTEM 1 — AI Training System

Trains the following **cognitive faculties** in full:

| Faculty | What is trained | Loss function |
|---------|----------------|---------------|
| **Thinking / Deep Reasoning** | Multi-step chain-of-thought, logical deduction | Cross-entropy + chain coherence |
| **Concentration / Attention** | Sparse attention heads, focus persistence | Attention entropy regularizer |
| **Episodic Memory Recall** | In-context memory retrieval, recent event storage | Contrastive (triplet) loss |
| **Semantic Memory Recall** | Concept embeddings, semantic clustering | Memory consolidation loss |
| **Creativity / Divergent Thinking** | High-entropy generation, lexical novelty | Diversity loss + negative entropy |
| **Imagination / Synthesis** | Conditional generation, latent interpolation | KL divergence + reconstruction |
| **Metacognition** | Confidence calibration, uncertainty detection | Calibration cross-entropy |
| **Associative Reasoning** | Analogy completion, concept graph traversal | Hit@K ranking loss |
| **Curiosity-driven Exploration** | Novel token usage, topic diversity | Mutual information maximization |

---

## Language Assignments

### Rust — Data Processing and Memory-Safe Pipelines

**Location:** `engine/rust/`, `training/rust/`, `ffi/rust_cpp/`

- **BPE Tokenizer** (`tokenizer.rs`): Full byte-pair encoding with Rayon-parallel batch encoding, merge-rule priority queue, Ġ pre-tokenization
- **Data Pipeline** (`pipeline.rs`, `batch.rs`): Concurrent JSONL loading, spec-compliant record validation (no raw dialogue, approved-only), Unicode normalization
- **Component Family Registry** (`component_family.rs`): Stores slot-order templates, never raw sentences
- **C++ Bridge** (`ffi/rust_cpp/`): cxx-safe FFI; exposes tokenization and batch delivery to C++ TrainingCore via callback architecture
- **Engine FFI** (`engine/rust/src/ffi.rs`): `extern "C"` exports for C++ EngineCore to call Rust tokenizer at inference time

Key design properties: zero unsafe in hot paths, Rayon work-stealing for parallelism, memory-mapped I/O for large datasets, atomic counters for lock-free metrics.

### Julia — Mathematics, Simulations, Numerical Computing

**Location:** `engine/julia/`, `training/julia/`

- **AttentionMath.jl**: Scaled dot-product attention, RoPE, Flash Attention forward/backward reference implementation, causal masking
- **EmbeddingOps.jl**: Sinusoidal positional encoding, layer normalization, token embedding lookup, RMS norm
- **NumericalOptimizer.jl** (engine): Numerical optimization for attention weight calibration
- **TrainingOptimizer.jl**: Full AdamW, Lion, Sophia (second-order), Muon (Newton-Schulz orthogonalization), cosine/warmup/1-cycle LR schedules, gradient clipping
- **LossFunctions.jl**: Cross-entropy, KL divergence, contrastive/triplet, memory consolidation, creativity diversity, label smoothing
- **CognitiveBenchmarks.jl**: Evaluation suite for all 8 cognitive faculties (scores in [0,1])
- **TrainingFFI.jl**: `@cfunction` callbacks for C++ callers; loss computation, optimizer steps, benchmark scoring

### Python — High-Level Training API and Orchestration

**Location:** `engine/python/`, `training/python/`

- **LanguageEngine**: High-level model wrapper (PyTorch), forward pass, streaming generation
- **TrainingOrchestrator**: Full training loop coordinator; calls into C++, Rust, Julia layers
- **CognitiveTrainer**: Per-faculty trainers (ThinkingTrainer, AttentionTrainer, MemoryTrainer, CreativityTrainer, ImaginationTrainer)
- **ExperimentTracker**: MLflow + W&B dual-backend metrics logging
- **FastAPI Server** (`server.py`): REST endpoints for text/audio processing; SSE streaming
- **EngineTrainingAPI** (`training_api.py`): Bridge between running engine and training system; component family access, record validation, weight distillation

### C++ — Engine Core and Runtime

**Location:** `engine/cpp/`, `training/cpp/`

- **EngineCore**: Recruitment-driven component registry; orchestrates all engine subsystems
- **MemoryManager**: Episodic memory (temporal decay, capacity-limited ring buffer), semantic memory (embedding cosine search with FAISS-style indexing), associative graph
- **AttentionMechanism**: Multi-head attention with KV-cache, Flash Attention 2 dispatch, RoPE integration, incremental decoding
- **LanguageUnderstanding**: Input processing pipeline; calls Rust tokenizer via FFI, runs understanding layers
- **ResponseGenerator**: Sampling strategies (greedy, top-k, top-p, temperature), beam search, response assembly
- **VocalInputProcessor**: ASR (mel filterbank → CUDA kernel) and TTS pipeline
- **TrainingCore**: 8-faculty training loop with Julia math FFI, Rust data pipeline FFI, checkpoint save/load

### CUDA/Triton — GPU Kernels and Low-Level Parallelism

**Location:** `engine/cuda/`, `training/cuda/`

**Engine CUDA kernels:**
- `attention_kernel.cu`: Flash Attention 2 (tiled, online softmax, causal mask)
- `softmax_kernel.cu`: Numerically stable online softmax with shared memory
- `layernorm_kernel.cu`: Fused LayerNorm (Welford algorithm)
- `fused_rope_kernel.cu`: Rotary Position Embedding fused with attention QK projection
- `embedding_kernel.cu`: Vocabulary embedding lookup + gradient scatter
- `asr_kernel.cu`: Mel filterbank extraction, ASR feature preprocessing
- `tts_kernel.cu`: Neural vocoder synthesis kernels

**Training CUDA kernels:**
- `cross_entropy_kernel.cu`: Numerically stable softmax + cross-entropy (fused)
- `optimizer_kernel.cu`: AdamW optimizer step (vectorized float4, bias correction)
- `gelu_kernel.cu`: Exact and approximate GELU + backward pass
- `dropout_kernel.cu`: Bernoulli dropout (inverted), alpha dropout, DropConnect, fused dropout+GELU/SiLU

**Triton kernels:**
- `engine/cuda/triton/attention_triton.py`: Flash Attention forward + backward + RoPE (Flash Attention 2 algorithm)
- `training/cuda/triton/training_kernels_triton.py`: Dropout, AdamW, LayerNorm backward, fused cross-entropy with label smoothing, gradient accumulation (FP16→FP32), MoE top-K routing

### Java — Infrastructure, Scheduling, and Service Layer

**Location:** `engine/java/`, `training/java/`

**Engine Java:**
- `EngineService`: Component lifecycle management, JNI bridge coordination
- `EngineLibraryBridge`: JNI → C++ EngineCore; process, transcribe, synthesize, tokenize
- `EngineConfig`: Environment-driven configuration
- `TaskScheduler`: Priority queue scheduler (HIGH/NORMAL/LOW) with retry and exponential backoff
- `IPCChannel`: Unix domain socket IPC (4-byte length-prefixed JSON protocol)
- `EngineServiceMain`: CLI entry point

**Training Java:**
- `TrainingService`: Full training lifecycle; submits jobs, coordinates epochs, reports metrics
- `TrainingLibraryBridge`: JNI → C++ TrainingCore; training steps, evaluation, checkpoints
- `TrainingTaskScheduler`: Priority-based training task scheduling with retry semantics
- `TrainingIPCChannel`: IPC to Rust data pipeline (batch request/response) and Python orchestrator (metric reporting)
- `TrainingServiceMain`: CLI entry point

---

## Cross-Language FFI Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         POLYGLOT AI SYSTEM                          │
│                                                                     │
│  Python ◄──────────────── pybind11 ────────────────► C++           │
│  (orchestration)       ffi/python_cpp/              (engine core)  │
│                                                                     │
│  Java  ◄───────────────── JNI ──────────────────────► C++          │
│  (infrastructure)       ffi/java_cpp/               (engine core)  │
│                                                                     │
│  Julia ◄───────────────── ccall ────────────────────► C++          │
│  (math kernels)         ffi/julia_cpp/              (training)     │
│                                                                     │
│  Rust  ◄───────────────── cxx ──────────────────────► C++          │
│  (data pipeline)        ffi/rust_cpp/               (training)     │
│                                                                     │
│  CUDA/Triton ◄───── nvcc / cuLaunch ────────────────► C++          │
│  (GPU kernels)                                      (kernel calls) │
└─────────────────────────────────────────────────────────────────────┘
```

Each bridge has a dedicated directory under `ffi/` with:
- A build file (CMakeLists.txt or Cargo.toml)
- The bridge implementation (`.cpp`, `.rs`)
- Header declarations (`.h`)

**Bridge contracts:**
- Python ↔ C++: pybind11; Python GIL released on long calls; NumPy ↔ `float*` zero-copy
- Java ↔ C++: JNI; `nativeHandle` is an opaque `long` (C++ pointer stored as integer)
- Julia ↔ C++: `ccall` + `@cfunction`; Julia GC-pinned arrays passed as `Ptr{Float32}`
- Rust ↔ C++: `cxx` crate; zero-copy `&[i32]` ↔ `const int32_t*`; callback registration for async data delivery

---

## Canonical Training File

`language_engines/English_engine.training.yaml`

This is the **single canonical file** for the English verbal engine, per the spec. It stores:
- `engine_registry`: language identifier, version, recruitment configuration
- `ai_core`: cognitive faculty definitions and capability registry
- `brain`: neural architecture configuration
- `skills`: capability modules and slot definitions
- `language_engine`: grammar rules, parsing config, morphology
- `sentence_system`: component families + slot-order templates (NOT memorized sentences)
- `training_data`: approved, normalized training records (NOT raw dialogue)
- `evaluation`: validation rules (slot coverage, length, no-placeholder checks)
- `connections`: inter-language bridge labels
- `governance`: spec compliance rules and audit log

**Spec rules enforced:**
1. No raw dialogue stored — only slot+family structured items
2. Runtime artifacts never become permanent training files
3. Cross-language bridges are labeled connections only
4. One canonical file per language per engine

---

## Data Flow

### Inference (Engine Path)

```
User Input (text or audio)
    │
    ▼ [Rust: BPE tokenize]
Token IDs
    │
    ▼ [C++: LanguageUnderstanding]
    │   • Embedding lookup (CUDA kernel)
    │   • Positional encoding (Julia: EmbeddingOps)
    │   • Multi-head attention (CUDA: Flash Attention 2)
    │   • KV-cache update (C++: AttentionMechanism)
    │   • Memory lookup (C++: MemoryManager)
Understanding Context
    │
    ▼ [C++: ResponseGenerator + Julia: NumericalOptimizer]
    │   • Top-p / top-k sampling
    │   • Temperature scaling
    │   • Beam search
    │   • Detokenize (Rust)
Response Text
    │
    ▼ [CUDA: TTS kernel] (if audio output requested)
Audio Output
```

### Training (Training System Path)

```
Training Data (JSONL files)
    │
    ▼ [Rust: DataPipeline]
    │   • Validate (no raw dialogue, approved only)
    │   • Normalize (Unicode NFC, whitespace)
    │   • BPE tokenize
    │   • Batch + shuffle
DataBatch (token IDs, seq lengths)
    │
    ▼ [C++: TrainingCore → 8 faculty trainers]
    │   │
    │   ├─ [CUDA: cross_entropy + dropout + optimizer kernels]
    │   ├─ [Julia: LossFunctions + TrainingOptimizer]
    │   ├─ [Python: CognitiveTrainer orchestration]
    │   └─ [Java: TaskScheduler + IPC]
    │
Gradients + Weight Updates
    │
    ▼ [C++: TrainingCore.saveCheckpoint]
Checkpoint .bin
    │
    ▼ [Python: ExperimentTracker → MLflow / W&B]
Metrics + Artifacts
```

---

## Component Recruitment Order

The engine is built in this exact sequence (enforced by `Makefile` + `build_all.sh`):

1. **Rust**: Tokenizer + pipeline (no external deps)
2. **CUDA**: GPU kernels (compiled before C++ links against them)
3. **C++ Engine Core**: Links against Rust `.so` + CUDA `.a`
4. **Julia Engine**: Instantiates math packages
5. **FFI bridges**: Python/Java/Julia/Rust ↔ C++ bridges compiled
6. **Python engine package**: Installed editable; links against pybind11 bridge
7. **Java engine service**: JVM loads JNI library
8. **Engine verification**: `verify.py` runs all binding checks
9. **Training system build**: Only after engine verification passes
10. **Training loop**: Only after training system fully initialized

---

## Memory Architecture

### Episodic Memory (short-term)
- Fixed-capacity ring buffer (configurable, default 1024 episodes)
- Each episode: hidden state vector + timestamp + access count
- Temporal decay: importance = `exp(-λ·Δt) + base_importance`
- Retrieval: top-K cosine similarity + recency weighting

### Semantic Memory (long-term)
- Concept graph: `Map<string, Concept>` with embedding + activation + connections
- Spreading activation: BFS from query concept, dampen by distance
- Consolidation: periodically merges episodic → semantic (training loss guides this)

### Working Memory (KV-Cache)
- Standard Transformer KV-cache in C++ `AttentionMechanism`
- Sliding window for long sequences, flash decoding for incremental generation

---

## Build System

| Component | Build tool | Command |
|-----------|-----------|---------|
| C++ + CUDA | CMake 3.24+ | `cmake -S . -B build && cmake --build build` |
| Rust | Cargo | `cargo build --release` (per crate) |
| Python | pip/setuptools | `pip install -e engine/python training/python` |
| Julia | Pkg.jl | `julia --project=X -e 'using Pkg; Pkg.instantiate()'` |
| Java | Gradle 8+ | `gradle build` |
| All | make / bash | `make all` or `./scripts/build_all.sh` |

See [`docs/BUILD.md`](BUILD.md) for step-by-step build instructions.
