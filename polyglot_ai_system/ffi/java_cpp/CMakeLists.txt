cmake_minimum_required(VERSION 3.22)
project(JavaCppBridge VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(JNI REQUIRED)

# JNI shared library
add_library(engine_core_jni SHARED
    EngineJNI.cpp
)

target_include_directories(engine_core_jni
    PRIVATE ${JNI_INCLUDE_DIRS}
    PRIVATE ../../engine/cpp/include
)

target_link_libraries(engine_core_jni
    PRIVATE engine_core
    PRIVATE ${JNI_LIBRARIES}
)

target_compile_options(engine_core_jni PRIVATE
    $<$<CONFIG:Release>:-O3 -fvisibility=hidden>
)

install(TARGETS engine_core_jni
    LIBRARY DESTINATION lib
)
