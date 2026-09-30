// =============================================================================
// engine/rust/src/ffi.rs
// C-linkage FFI exports from the Rust engine library.
// These functions are called by C++, Python, Java, and Julia via their
// respective FFI bridge layers.
// =============================================================================

use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int, c_uint};
use std::panic;

use crate::pipeline::{PreprocessingPipeline, PipelineConfig, PipelineOutput};
use crate::tokenizer::{EngineTokenizer, TokenizerConfig, TokenizationStrategy};
use crate::component_family::FamilyRegistry;

// =============================================================================
// Opaque handle types for C-linkage consumers
// =============================================================================

pub struct RustPipelineHandle {
    pipeline: PreprocessingPipeline,
}

pub struct RustTokenizerHandle {
    tokenizer: EngineTokenizer,
}

pub struct RustFamilyRegistryHandle {
    registry: FamilyRegistry,
}

// =============================================================================
// Pipeline FFI
// =============================================================================

/// Creates a preprocessing pipeline with default configuration.
/// Returns null on failure.
#[no_mangle]
pub extern "C" fn rust_pipeline_create() -> *mut RustPipelineHandle {
    let result = panic::catch_unwind(|| {
        let config = PipelineConfig::default();
        let pipeline = PreprocessingPipeline::new(config);
        Box::into_raw(Box::new(RustPipelineHandle { pipeline }))
    });
    result.unwrap_or(std::ptr::null_mut())
}

/// Creates a pipeline with a JSON configuration string.
/// Returns null on failure.
#[no_mangle]
pub extern "C" fn rust_pipeline_create_from_json(
    config_json: *const c_char,
) -> *mut RustPipelineHandle {
    let result = panic::catch_unwind(|| {
        if config_json.is_null() {
            return std::ptr::null_mut();
        }
        let json = unsafe { CStr::from_ptr(config_json) }.to_str().ok()?;
        let config: PipelineConfig = serde_json::from_str(json).ok()?;
        let pipeline = PreprocessingPipeline::new(config);
        Some(Box::into_raw(Box::new(RustPipelineHandle { pipeline })))
    });
    result.ok().flatten().unwrap_or(std::ptr::null_mut())
}

/// Processes a text document through the pipeline.
/// Returns a heap-allocated JSON string (caller must free with rust_free_string).
/// Returns null on failure.
#[no_mangle]
pub extern "C" fn rust_pipeline_process(
    handle:    *mut RustPipelineHandle,
    input:     *const c_char,
    input_len: c_uint,
) -> *mut c_char {
    let result = panic::catch_unwind(|| {
        if handle.is_null() || input.is_null() { return std::ptr::null_mut(); }
        let handle_ref = unsafe { &*handle };
        let text = unsafe {
            std::slice::from_raw_parts(input as *const u8, input_len as usize)
        };
        let text_str = std::str::from_utf8(text).ok()?;
        let output = handle_ref.pipeline.process(text_str);
        let json = serde_json::to_string(&output).ok()?;
        let c_str = CString::new(json).ok()?;
        Some(c_str.into_raw())
    });
    result.ok().flatten().unwrap_or(std::ptr::null_mut())
}

/// Destroys a pipeline handle.
#[no_mangle]
pub extern "C" fn rust_pipeline_destroy(handle: *mut RustPipelineHandle) {
    if !handle.is_null() {
        unsafe { let _ = Box::from_raw(handle); }
    }
}

// =============================================================================
// Tokenizer FFI
// =============================================================================

/// Creates a tokenizer handle with default configuration.
#[no_mangle]
pub extern "C" fn rust_tokenizer_create() -> *mut RustTokenizerHandle {
    let result = panic::catch_unwind(|| {
        let config = TokenizerConfig {
            strategy: TokenizationStrategy::Whitespace,
            add_special_tokens: true,
            ..Default::default()
        };
        let tokenizer = EngineTokenizer::new(config);
        Box::into_raw(Box::new(RustTokenizerHandle { tokenizer }))
    });
    result.unwrap_or(std::ptr::null_mut())
}

/// Tokenizes a text string. Returns JSON array of token records.
/// Returns null on failure.
#[no_mangle]
pub extern "C" fn rust_tokenizer_tokenize(
    handle: *mut RustTokenizerHandle,
    text:   *const c_char,
) -> *mut c_char {
    let result = panic::catch_unwind(|| {
        if handle.is_null() || text.is_null() { return std::ptr::null_mut(); }
        let handle_ref = unsafe { &*handle };
        let text_str = unsafe { CStr::from_ptr(text) }.to_str().ok()?;
        let tokens = handle_ref.tokenizer.tokenize(text_str).ok()?;
        let json = serde_json::to_string(&tokens).ok()?;
        let c_str = CString::new(json).ok()?;
        Some(c_str.into_raw())
    });
    result.ok().flatten().unwrap_or(std::ptr::null_mut())
}

/// Returns the vocabulary size.
#[no_mangle]
pub extern "C" fn rust_tokenizer_vocab_size(handle: *mut RustTokenizerHandle) -> c_uint {
    if handle.is_null() { return 0; }
    unsafe { (*handle).tokenizer.vocab_size() as c_uint }
}

/// Destroys a tokenizer handle.
#[no_mangle]
pub extern "C" fn rust_tokenizer_destroy(handle: *mut RustTokenizerHandle) {
    if !handle.is_null() {
        unsafe { let _ = Box::from_raw(handle); }
    }
}

// =============================================================================
// FamilyRegistry FFI
// =============================================================================

/// Creates a family registry pre-loaded with English defaults.
#[no_mangle]
pub extern "C" fn rust_registry_create() -> *mut RustFamilyRegistryHandle {
    let result = panic::catch_unwind(|| {
        let registry = FamilyRegistry::new();
        Box::into_raw(Box::new(RustFamilyRegistryHandle { registry }))
    });
    result.unwrap_or(std::ptr::null_mut())
}

/// Returns the number of families in the registry.
#[no_mangle]
pub extern "C" fn rust_registry_family_count(handle: *mut RustFamilyRegistryHandle) -> c_uint {
    if handle.is_null() { return 0; }
    unsafe { (*handle).registry.len() as c_uint }
}

/// Selects a random form from a named family.
/// Returns null if the family is not found.
#[no_mangle]
pub extern "C" fn rust_registry_select_form(
    handle:      *mut RustFamilyRegistryHandle,
    family_name: *const c_char,
    register_id: c_int,   // 0=Formal, 1=Neutral, 2=Informal, 3=Technical
    creativity:  f32,
) -> *mut c_char {
    let result = panic::catch_unwind(|| {
        if handle.is_null() || family_name.is_null() { return std::ptr::null_mut(); }
        let name = unsafe { CStr::from_ptr(family_name) }.to_str().ok()?;
        let register = match register_id {
            0 => crate::component_family::RegisterType::Formal,
            1 => crate::component_family::RegisterType::Neutral,
            2 => crate::component_family::RegisterType::Informal,
            3 => crate::component_family::RegisterType::Technical,
            _ => crate::component_family::RegisterType::Neutral,
        };
        let handle_ref = unsafe { &*handle };
        let family = handle_ref.registry.get(name)?;

        let mut rng = rand::thread_rng();
        let form = family.select_form(&register, creativity, &mut rng)?;
        let c_str = CString::new(form).ok()?;
        Some(c_str.into_raw())
    });
    result.ok().flatten().unwrap_or(std::ptr::null_mut())
}

/// Destroys a family registry handle.
#[no_mangle]
pub extern "C" fn rust_registry_destroy(handle: *mut RustFamilyRegistryHandle) {
    if !handle.is_null() {
        unsafe { let _ = Box::from_raw(handle); }
    }
}

// =============================================================================
// Utility: free a string allocated by this library
// =============================================================================

#[no_mangle]
pub extern "C" fn rust_free_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        unsafe { let _ = CString::from_raw(ptr); }
    }
}

// =============================================================================
// Health check
// =============================================================================

/// Returns 1 if the Rust engine module is functional.
#[no_mangle]
pub extern "C" fn rust_engine_health_check() -> c_int {
    1
}

/// Returns a version string (caller must free with rust_free_string).
#[no_mangle]
pub extern "C" fn rust_engine_version() -> *mut c_char {
    CString::new("engine-rust 1.0.0").map(|s| s.into_raw()).unwrap_or(std::ptr::null_mut())
}
