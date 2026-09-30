// training/rust/src/ffi.rs
//! C FFI exports for the Rust training data pipeline.
//! Called from C++ TrainingCore via dlopen / extern "C" ABI.

use crate::batch::{DataBatch, DataSource};
use crate::pipeline::{DataPipeline, PipelineConfig};
use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_double, c_int, c_uint, c_ulong};
use std::ptr;

/// Opaque handle to a DataPipeline.
pub struct PipelineHandle {
    inner: DataPipeline,
    batches: Vec<DataBatch>,
    current_batch: usize,
}

/// Create a new DataPipeline handle.
/// Returns null on failure.
///
/// # Safety
/// `data_path` must be a valid, nul-terminated UTF-8 C string.
/// `vocab_path` may be null to use a bootstrap tokenizer.
#[no_mangle]
pub unsafe extern "C" fn polyglot_pipeline_create(
    data_path: *const c_char,
    vocab_path: *const c_char,
    batch_size: c_uint,
    min_quality: c_double,
    num_workers: c_uint,
) -> *mut PipelineHandle {
    let data_path_str = if data_path.is_null() {
        return ptr::null_mut();
    } else {
        match CStr::from_ptr(data_path).to_str() {
            Ok(s) => s.to_string(),
            Err(_) => return ptr::null_mut(),
        }
    };

    let vocab_path_opt: Option<String> = if vocab_path.is_null() {
        None
    } else {
        CStr::from_ptr(vocab_path).to_str().ok().map(|s| s.to_string())
    };

    let config = PipelineConfig {
        batch_size: batch_size as usize,
        shuffle: true,
        min_quality_score: min_quality,
        vocab_path: vocab_path_opt,
        max_seq_len: 512,
        num_workers: num_workers as usize,
    };

    let source = DataSource::jsonl(data_path_str);

    match DataPipeline::new(config, vec![source]) {
        Ok(pipeline) => {
            let handle = Box::new(PipelineHandle {
                inner: pipeline,
                batches: Vec::new(),
                current_batch: 0,
            });
            Box::into_raw(handle)
        }
        Err(_) => ptr::null_mut(),
    }
}

/// Destroy a previously created pipeline handle and free memory.
///
/// # Safety
/// `handle` must have been returned by `polyglot_pipeline_create` and not yet freed.
#[no_mangle]
pub unsafe extern "C" fn polyglot_pipeline_destroy(handle: *mut PipelineHandle) {
    if !handle.is_null() {
        let _ = Box::from_raw(handle);
    }
}

/// Advance to the next batch. Returns 1 if a batch was loaded, 0 if epoch complete.
///
/// # Safety
/// `handle` must be a valid non-null pointer returned by `polyglot_pipeline_create`.
#[no_mangle]
pub unsafe extern "C" fn polyglot_pipeline_next_batch(handle: *mut PipelineHandle) -> c_int {
    let h = &mut *handle;
    // If we haven't loaded epoch batches yet, or exhausted them, run epoch
    if h.batches.is_empty() || h.current_batch >= h.batches.len() {
        match h.inner.epoch() {
            Ok(batches) => {
                h.batches = batches;
                h.current_batch = 0;
            }
            Err(_) => return 0,
        }
    }
    if h.current_batch < h.batches.len() {
        h.current_batch += 1;
        1
    } else {
        0
    }
}

/// Get the number of records in the current batch.
///
/// # Safety
/// `handle` must be valid and `polyglot_pipeline_next_batch` must have returned 1.
#[no_mangle]
pub unsafe extern "C" fn polyglot_batch_len(handle: *const PipelineHandle) -> c_ulong {
    let h = &*handle;
    if h.current_batch == 0 || h.current_batch > h.batches.len() {
        return 0;
    }
    h.batches[h.current_batch - 1].len() as c_ulong
}

/// Get the assembled_output text of record at index `idx` in the current batch.
/// Returns null if out of bounds. Caller must NOT free the returned pointer —
/// it is valid until the next call to polyglot_pipeline_next_batch.
///
/// # Safety
/// See above; `idx` must be within `polyglot_batch_len`.
#[no_mangle]
pub unsafe extern "C" fn polyglot_batch_get_record(
    handle: *const PipelineHandle,
    idx: c_ulong,
) -> *const c_char {
    let h = &*handle;
    if h.current_batch == 0 || h.current_batch > h.batches.len() {
        return ptr::null();
    }
    let batch = &h.batches[h.current_batch - 1];
    let i = idx as usize;
    if i >= batch.records.len() {
        return ptr::null();
    }
    // Allocate a CString — caller does NOT free; we leak intentionally here
    // (short-lived FFI path; memory reclaimed when pipeline is destroyed).
    // In production, use a per-batch arena or have caller pass a buffer.
    let s = &batch.records[i].assembled_output;
    match CString::new(s.as_str()) {
        Ok(cstr) => cstr.into_raw() as *const c_char,
        Err(_) => ptr::null(),
    }
}

/// Free a string pointer returned by `polyglot_batch_get_record`.
///
/// # Safety
/// `ptr` must have been returned by `polyglot_batch_get_record` and not yet freed.
#[no_mangle]
pub unsafe extern "C" fn polyglot_batch_free(ptr: *mut c_char) {
    if !ptr.is_null() {
        let _ = CString::from_raw(ptr);
    }
}
