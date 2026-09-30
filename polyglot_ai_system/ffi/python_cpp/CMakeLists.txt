cmake_minimum_required(VERSION 3.22)
project(PythonCppBridge VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# pybind11 extension module — compiled to engine_core_py.so
pybind11_add_module(engine_core_py
    engine_pybind.cpp
)

target_include_directories(engine_core_py
    PRIVATE ${Python3_INCLUDE_DIRS}
    PRIVATE ../../engine/cpp/include
)

target_link_libraries(engine_core_py
    PRIVATE engine_core
)

target_compile_options(engine_core_py PRIVATE
    $<$<CONFIG:Release>:-O3 -fvisibility=hidden>
)

# Install the extension module alongside the Python package
install(TARGETS engine_core_py
    LIBRARY DESTINATION engine/python/src/polyglot_engine
)
