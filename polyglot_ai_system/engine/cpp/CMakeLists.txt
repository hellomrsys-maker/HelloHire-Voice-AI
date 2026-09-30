cmake_minimum_required(VERSION 3.22)
project(EngineCore VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Threads REQUIRED)
find_package(OpenMP REQUIRED)

# =============================================================================
# Engine Core Library
# =============================================================================

add_library(engine_core SHARED
    src/EngineCore.cpp
    src/VocalInputProcessor.cpp
    src/LanguageUnderstanding.cpp
    src/ResponseGenerator.cpp
    src/SpeechSynthesizer.cpp
    src/MemoryManager.cpp
    src/AttentionMechanism.cpp
    src/RecruitmentOrchestrator.cpp
    src/TokenizerBridge.cpp
    src/FFIBridge.cpp
)

target_include_directories(engine_core
    PUBLIC  include
    PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(engine_core
    PRIVATE Threads::Threads
    PRIVATE OpenMP::OpenMP_CXX
)

target_compile_options(engine_core PRIVATE
    -Wall -Wextra -Wpedantic
    -ffast-math
    $<$<CONFIG:Release>:-O3 -march=native>
    $<$<CONFIG:Debug>:-O0 -g3 -fsanitize=address,undefined>
)

target_compile_definitions(engine_core PRIVATE
    ENGINE_VERSION_MAJOR=1
    ENGINE_VERSION_MINOR=0
    ENGINE_VERSION_PATCH=0
)

# =============================================================================
# Engine CLI executable (for standalone engine validation)
# =============================================================================

add_executable(engine_cli src/main.cpp)
target_link_libraries(engine_cli PRIVATE engine_core)

# =============================================================================
# Tests
# =============================================================================

option(BUILD_ENGINE_TESTS "Build engine unit tests" ON)
if(BUILD_ENGINE_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# =============================================================================
# Install rules
# =============================================================================

install(TARGETS engine_core engine_cli
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)
install(DIRECTORY include/ DESTINATION include/engine_core)
