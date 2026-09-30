cmake_minimum_required(VERSION 3.22)
project(PolyglotAISystem VERSION 1.0.0 LANGUAGES CXX CUDA)

# =============================================================================
# Top-level CMake — Polyglot AI System
# Orchestrates C++ and CUDA components for both Engine and Training systems
# =============================================================================

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)

# Build type default
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG -fvisibility=hidden")
set(CMAKE_CXX_FLAGS_DEBUG   "-O0 -g3 -fsanitize=address,undefined")

# CUDA architectures (Ampere + Ada + Hopper)
set(CMAKE_CUDA_ARCHITECTURES 80 86 89 90)

# =============================================================================
# Find dependencies
# =============================================================================

find_package(CUDA REQUIRED)
find_package(Threads REQUIRED)
find_package(OpenMP REQUIRED)

# Optional: find Python for pybind11
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Optional: find JNI for Java bridge
find_package(JNI)

# =============================================================================
# Sub-projects
# =============================================================================

option(BUILD_ENGINE   "Build the verbal communication engine"  ON)
option(BUILD_TRAINING "Build the AI training system"           ON)
option(BUILD_FFI      "Build FFI binding layers"               ON)
option(BUILD_TESTS    "Build test suites"                      ON)

if(BUILD_ENGINE)
  add_subdirectory(engine/cpp)
  add_subdirectory(engine/cuda)
endif()

if(BUILD_TRAINING)
  add_subdirectory(training/cpp)
  add_subdirectory(training/cuda)
endif()

if(BUILD_FFI)
  add_subdirectory(ffi/python_cpp)
  if(JNI_FOUND)
    add_subdirectory(ffi/java_cpp)
  endif()
  add_subdirectory(ffi/julia_cpp)
endif()

if(BUILD_TESTS)
  enable_testing()
endif()
