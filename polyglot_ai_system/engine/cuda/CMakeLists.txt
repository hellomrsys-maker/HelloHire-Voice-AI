cmake_minimum_required(VERSION 3.22)
project(EngineCUDA VERSION 1.0.0 LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_ARCHITECTURES 80 86 89 90)

find_package(CUDAToolkit REQUIRED)

add_library(engine_cuda SHARED
    kernels/attention_kernel.cu
    kernels/softmax_kernel.cu
    kernels/embedding_kernel.cu
    kernels/asr_kernel.cu
    kernels/tts_kernel.cu
    kernels/layernorm_kernel.cu
    kernels/fused_rope_kernel.cu
)

target_include_directories(engine_cuda
    PUBLIC  ${CMAKE_CURRENT_SOURCE_DIR}/kernels
    PRIVATE ${CUDAToolkit_INCLUDE_DIRS}
)

target_link_libraries(engine_cuda
    PRIVATE CUDA::cudart
    PRIVATE CUDA::cublas
    PRIVATE CUDA::cufft
)

set_target_properties(engine_cuda PROPERTIES
    CUDA_SEPARABLE_COMPILATION ON
    POSITION_INDEPENDENT_CODE ON
)

target_compile_options(engine_cuda PRIVATE
    $<$<COMPILE_LANGUAGE:CUDA>:
        --use_fast_math
        -O3
        --ptxas-options=-v
        --maxrregcount=64
    >
)

install(TARGETS engine_cuda LIBRARY DESTINATION lib)
