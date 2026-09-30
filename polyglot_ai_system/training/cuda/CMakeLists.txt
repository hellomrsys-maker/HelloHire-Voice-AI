cmake_minimum_required(VERSION 3.22)
project(TrainingCUDA VERSION 1.0.0 LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_ARCHITECTURES 80 86 89 90)

find_package(CUDAToolkit REQUIRED)

add_library(training_cuda SHARED
    kernels/cross_entropy_kernel.cu
    kernels/optimizer_kernel.cu
    kernels/dropout_kernel.cu
    kernels/gelu_kernel.cu
)

target_include_directories(training_cuda
    PUBLIC  ${CMAKE_CURRENT_SOURCE_DIR}/kernels
    PRIVATE ${CUDAToolkit_INCLUDE_DIRS}
)

target_link_libraries(training_cuda
    PRIVATE CUDA::cudart
    PRIVATE CUDA::cublas
)

set_target_properties(training_cuda PROPERTIES
    CUDA_SEPARABLE_COMPILATION ON
    POSITION_INDEPENDENT_CODE ON
)

target_compile_options(training_cuda PRIVATE
    $<$<COMPILE_LANGUAGE:CUDA>:--use_fast_math -O3>
)

install(TARGETS training_cuda LIBRARY DESTINATION lib)
