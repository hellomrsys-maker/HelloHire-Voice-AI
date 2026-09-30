cmake_minimum_required(VERSION 3.22)
project(JuliaCppBridge VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Julia
find_program(JULIA_EXE julia)
if(JULIA_EXE)
    execute_process(
        COMMAND ${JULIA_EXE} -e "print(Sys.BINDIR)"
        OUTPUT_VARIABLE JULIA_BINDIR
    )
    set(JULIA_INCLUDE_DIR "${JULIA_BINDIR}/../include/julia")
    set(JULIA_LIB_DIR     "${JULIA_BINDIR}/../lib")
endif()

# Julia embedding bridge (C++ code that can be called FROM Julia via ccall,
# and also embeds the Julia runtime for calling Julia FROM C++)
add_library(julia_cpp_bridge SHARED
    JuliaBridge.cpp
)

target_include_directories(julia_cpp_bridge
    PRIVATE ../../engine/cpp/include
    PRIVATE ../../training/cpp/include
)
if(JULIA_INCLUDE_DIR)
    target_include_directories(julia_cpp_bridge
        PRIVATE ${JULIA_INCLUDE_DIR}
    )
endif()

if(JULIA_LIB_DIR)
    target_link_directories(julia_cpp_bridge PRIVATE ${JULIA_LIB_DIR})
    target_link_libraries(julia_cpp_bridge PRIVATE julia)
endif()

target_compile_options(julia_cpp_bridge PRIVATE
    $<$<CONFIG:Release>:-O3>
)

install(TARGETS julia_cpp_bridge LIBRARY DESTINATION lib)
