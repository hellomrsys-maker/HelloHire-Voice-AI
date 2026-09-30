# =============================================================================
# Polyglot AI System — Unified Build Orchestration
# Covers SYSTEM 2 (Engine) and SYSTEM 1 (Training) across 6 languages
# =============================================================================

.PHONY: all engine training ffi verify-engine test-all clean \
        cpp cuda rust julia java python \
        engine-cpp engine-cuda engine-rust engine-julia engine-java engine-python \
        training-cpp training-cuda training-rust training-julia training-java training-python

BUILD_DIR     := build
CPP_BUILD     := $(BUILD_DIR)/cpp
CUDA_BUILD    := $(BUILD_DIR)/cuda
RUST_TARGET   := engine/rust/target/release
JULIA_PROJECT := engine/julia
JAVA_GRADLE   := ./gradlew
PYTHON_PIP    := pip

# =============================================================================
# Top-level targets
# =============================================================================

all: engine training
	@echo "=== Full system build complete ==="

engine: engine-cpp engine-cuda engine-rust engine-julia engine-java engine-python
	@echo "=== Engine system build complete ==="

training: engine verify-engine training-cpp training-cuda training-rust training-julia training-java training-python
	@echo "=== Training system build complete ==="

ffi: ffi-java-cpp ffi-python-cpp ffi-rust-cpp ffi-julia-cpp
	@echo "=== FFI bindings build complete ==="

# =============================================================================
# Engine — C++ Core Runtime
# =============================================================================

engine-cpp:
	@echo "--- Building C++ engine core ---"
	cmake -S engine/cpp -B $(CPP_BUILD)/engine \
	    -DCMAKE_BUILD_TYPE=Release \
	    -DBUILD_ENGINE=ON \
	    -DCMAKE_CXX_STANDARD=20 \
	    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
	cmake --build $(CPP_BUILD)/engine --parallel $$(nproc)
	@echo "--- C++ engine core built ---"

# =============================================================================
# Engine — CUDA / Triton GPU Kernels
# =============================================================================

engine-cuda:
	@echo "--- Building CUDA/Triton engine kernels ---"
	cmake -S engine/cuda -B $(CUDA_BUILD)/engine \
	    -DCMAKE_BUILD_TYPE=Release \
	    -DCUDA_ARCHITECTURES=80;86;89;90
	cmake --build $(CUDA_BUILD)/engine --parallel $$(nproc)
	@echo "--- CUDA engine kernels built ---"

# =============================================================================
# Engine — Rust Data Pipelines
# =============================================================================

engine-rust:
	@echo "--- Building Rust engine pipelines ---"
	cd engine/rust && cargo build --release 2>&1
	@echo "--- Rust engine pipelines built ---"

# =============================================================================
# Engine — Julia Mathematical Kernels
# =============================================================================

engine-julia:
	@echo "--- Building Julia engine modules ---"
	julia --project=$(JULIA_PROJECT) -e "\
	    using Pkg; \
	    Pkg.instantiate(); \
	    Pkg.precompile(); \
	    include(\"engine/julia/src/EngineCore.jl\")" 2>&1
	@echo "--- Julia engine modules built ---"

# =============================================================================
# Engine — Java Infrastructure Layer
# =============================================================================

engine-java:
	@echo "--- Building Java engine infrastructure ---"
	$(JAVA_GRADLE) :engine:java:build --no-daemon 2>&1
	@echo "--- Java engine infrastructure built ---"

# =============================================================================
# Engine — Python Orchestration API
# =============================================================================

engine-python:
	@echo "--- Building Python engine orchestration ---"
	$(PYTHON_PIP) install -e engine/python[dev] --quiet 2>&1
	@echo "--- Python engine orchestration built ---"

# =============================================================================
# FFI Binding Layers
# =============================================================================

ffi-java-cpp:
	@echo "--- Building Java<->C++ JNI bridge ---"
	cmake -S ffi/java_cpp -B $(BUILD_DIR)/ffi/java_cpp -DCMAKE_BUILD_TYPE=Release
	cmake --build $(BUILD_DIR)/ffi/java_cpp --parallel $$(nproc)

ffi-python-cpp:
	@echo "--- Building Python<->C++ pybind11 bridge ---"
	cmake -S ffi/python_cpp -B $(BUILD_DIR)/ffi/python_cpp -DCMAKE_BUILD_TYPE=Release
	cmake --build $(BUILD_DIR)/ffi/python_cpp --parallel $$(nproc)

ffi-rust-cpp:
	@echo "--- Building Rust<->C++ cxx bridge ---"
	cd ffi/rust_cpp && cargo build --release

ffi-julia-cpp:
	@echo "--- Building Julia<->C++ ccall bridge ---"
	cmake -S ffi/julia_cpp -B $(BUILD_DIR)/ffi/julia_cpp -DCMAKE_BUILD_TYPE=Release
	cmake --build $(BUILD_DIR)/ffi/julia_cpp --parallel $$(nproc)

# =============================================================================
# Engine Verification
# =============================================================================

verify-engine:
	@echo "--- Verifying engine operational status ---"
	python engine/python/src/verify_engine.py --all
	@echo "--- Engine verification passed ---"

# =============================================================================
# Training System Build Targets
# =============================================================================

training-cpp:
	@echo "--- Building C++ training runtime ---"
	cmake -S training/cpp -B $(CPP_BUILD)/training \
	    -DCMAKE_BUILD_TYPE=Release \
	    -DBUILD_TRAINING=ON \
	    -DCMAKE_CXX_STANDARD=20
	cmake --build $(CPP_BUILD)/training --parallel $$(nproc)

training-cuda:
	@echo "--- Building CUDA training kernels ---"
	cmake -S training/cuda -B $(CUDA_BUILD)/training \
	    -DCMAKE_BUILD_TYPE=Release \
	    -DCUDA_ARCHITECTURES=80;86;89;90
	cmake --build $(CUDA_BUILD)/training --parallel $$(nproc)

training-rust:
	@echo "--- Building Rust training pipelines ---"
	cd training/rust && cargo build --release

training-julia:
	@echo "--- Building Julia training modules ---"
	julia --project=training/julia -e "\
	    using Pkg; \
	    Pkg.instantiate(); \
	    Pkg.precompile(); \
	    include(\"training/julia/src/TrainingCore.jl\")"

training-java:
	@echo "--- Building Java training infrastructure ---"
	$(JAVA_GRADLE) :training:java:build --no-daemon

training-python:
	@echo "--- Building Python training API ---"
	$(PYTHON_PIP) install -e training/python[dev] --quiet

# =============================================================================
# Test Targets
# =============================================================================

test-all: test-engine test-training test-ffi test-integration
	@echo "=== All tests passed ==="

test-engine:
	@echo "--- Running engine tests ---"
	$(JAVA_GRADLE) :engine:java:test --no-daemon
	pytest engine/python/tests -v --tb=short
	cd engine/rust && cargo test --release
	julia --project=$(JULIA_PROJECT) -e "include(\"engine/julia/src/test_engine.jl\")"
	ctest --test-dir $(CPP_BUILD)/engine --output-on-failure

test-training:
	@echo "--- Running training tests ---"
	$(JAVA_GRADLE) :training:java:test --no-daemon
	pytest training/python/tests -v --tb=short
	cd training/rust && cargo test --release
	julia --project=training/julia -e "include(\"training/julia/src/test_training.jl\")"
	ctest --test-dir $(CPP_BUILD)/training --output-on-failure

test-ffi:
	@echo "--- Running FFI integration tests ---"
	pytest ffi/ -v --tb=short

test-integration:
	@echo "--- Running end-to-end integration tests ---"
	python scripts/run_integration_tests.py

# =============================================================================
# Clean
# =============================================================================

clean:
	rm -rf $(BUILD_DIR)
	cd engine/rust && cargo clean
	cd training/rust && cargo clean
	$(JAVA_GRADLE) clean --no-daemon
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	@echo "=== Clean complete ==="
