// ffi/rust_cpp/build.rs
//! Build script for the Rust ↔ C++ cxx bridge.
//! Compiles EngineCoreBridge.cpp and links against the engine C++ library.

fn main() {
    cxx_build::bridge("src/lib.rs")
        .file("src/EngineCoreBridge.cpp")
        .flag_if_supported("-std=c++20")
        .flag_if_supported("-O3")
        .include("../../engine/cpp/include")
        .compile("polyglot_rust_cpp_bridge");

    println!("cargo:rerun-if-changed=src/lib.rs");
    println!("cargo:rerun-if-changed=src/EngineCoreBridge.cpp");
    println!("cargo:rerun-if-changed=../../engine/cpp/include/EngineCore.h");
}
