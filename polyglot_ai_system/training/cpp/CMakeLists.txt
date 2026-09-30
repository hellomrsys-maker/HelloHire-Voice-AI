cmake_minimum_required(VERSION 3.22)
project(TrainingCPP VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Threads REQUIRED)
find_package(OpenMP REQUIRED)

add_library(training_cpp SHARED
    src/TrainingCore.cpp
    src/CognitiveModel.cpp
    src/ThinkingEngine.cpp
    src/MemoryTraining.cpp
    src/CreativityTraining.cpp
    src/ImaginationModule.cpp
    src/MetacognitionTrainer.cpp
    src/TrainingDataManager.cpp
    src/CheckpointManager.cpp
    src/LossComputer.cpp
)

target_include_directories(training_cpp PUBLIC include)
target_link_libraries(training_cpp
    PRIVATE Threads::Threads
    PRIVATE OpenMP::OpenMP_CXX
)

target_compile_options(training_cpp PRIVATE
    -Wall -Wextra
    $<$<CONFIG:Release>:-O3 -march=native>
)

add_executable(training_cli src/main.cpp)
target_link_libraries(training_cli PRIVATE training_cpp)

install(TARGETS training_cpp training_cli
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(DIRECTORY include/ DESTINATION include/training_cpp)
