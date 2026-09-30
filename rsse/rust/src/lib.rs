//! RSSE C-ABI & Safe Memory Integration Library
//!
//! Provides deterministic C-FFI entry points and zero-bridge AMSV memory synchronization
//! for the Recruitment Scenario Simulation Engine.

pub mod ontology;
pub mod verbal_evaluator;

pub use verbal_evaluator::{StarScores, VerbalTurnEvaluation, evaluate_verbal_turn, rsse_evaluate_verbal_turn};

use std::ffi::CStr;
use std::os::raw::c_char;
use std::sync::atomic::{AtomicU64, Ordering};
use ontology::{SCENARIO_CATALOG, get_scenario_by_id, evaluate_register_compliance};

/// Returns total number of available scenarios in ontology.
#[no_mangle]
pub extern "C" fn rsse_get_scenario_count() -> u32 {
    SCENARIO_CATALOG.len() as u32
}

/// Returns scenario ID by 0-based catalog index.
#[no_mangle]
pub extern "C" fn rsse_get_scenario_id_by_index(index: u32) -> u16 {
    if let Some(scenario) = SCENARIO_CATALOG.get(index as usize) {
        scenario.scenario_id
    } else {
        0
    }
}

/// Returns interview format code (1-8) for given scenario ID.
#[no_mangle]
pub extern "C" fn rsse_get_scenario_format(scenario_id: u16) -> u16 {
    if let Some(scenario) = get_scenario_by_id(scenario_id) {
        scenario.format as u16
    } else {
        0
    }
}

/// Copies core scenario prompt into destination buffer. Returns bytes written.
#[no_mangle]
pub extern "C" fn rsse_get_scenario_prompt(
    scenario_id: u16,
    out_buf: *mut u8,
    max_len: usize,
) -> usize {
    if out_buf.is_null() || max_len == 0 {
        return 0;
    }
    if let Some(scenario) = get_scenario_by_id(scenario_id) {
        let bytes = scenario.core_prompt.as_bytes();
        let copy_len = bytes.len().min(max_len - 1);
        unsafe {
            std::ptr::copy_nonoverlapping(bytes.as_ptr(), out_buf, copy_len);
            *out_buf.add(copy_len) = 0; // null terminate
        }
        copy_len
    } else {
        0
    }
}

/// Copies a probe question (depth or stress) into destination buffer.
#[no_mangle]
pub extern "C" fn rsse_get_probe(
    scenario_id: u16,
    is_stress: bool,
    probe_index: u32,
    out_buf: *mut u8,
    max_len: usize,
) -> usize {
    if out_buf.is_null() || max_len == 0 {
        return 0;
    }
    if let Some(scenario) = get_scenario_by_id(scenario_id) {
        let probes = if is_stress {
            scenario.probes_stress
        } else {
            scenario.probes_depth
        };
        if let Some(&probe_text) = probes.get(probe_index as usize) {
            let bytes = probe_text.as_bytes();
            let copy_len = bytes.len().min(max_len - 1);
            unsafe {
                std::ptr::copy_nonoverlapping(bytes.as_ptr(), out_buf, copy_len);
                *out_buf.add(copy_len) = 0;
            }
            return copy_len;
        }
    }
    0
}

/// Evaluates candidate transcript against register expectations.
/// Returns register compliance in range [0.0, 1.0].
#[no_mangle]
pub extern "C" fn rsse_evaluate_compliance(
    scenario_id: u16,
    transcript: *const c_char,
    wpm: f32,
) -> f32 {
    if transcript.is_null() {
        return 0.0;
    }
    let c_str = unsafe { CStr::from_ptr(transcript) };
    let Ok(trans_str) = c_str.to_str() else {
        return 0.0;
    };

    if let Some(scenario) = get_scenario_by_id(scenario_id) {
        evaluate_register_compliance(scenario, trans_str, wpm)
    } else {
        0.0
    }
}

/// Directly writes RSSE state into the 64-byte AMSV state vector at offset 0x20 (u64 slot 4).
/// Bit Layout:
/// - Bits 0-15:  scenario_id (u16)
/// - Bits 16-31: turn_counter (u16)
/// - Bits 32-47: register_compliance Q16 (u16)
/// - Bits 48-63: phase (u16)
#[no_mangle]
pub extern "C" fn rsse_sync_to_amsv(
    amsv_u64_slot4_ptr: *mut u64,
    scenario_id: u16,
    turn: u16,
    compliance: f32,
    phase: u16,
) {
    if amsv_u64_slot4_ptr.is_null() {
        return;
    }
    let comp_q16 = ((compliance.clamp(0.0, 1.0) * 65535.0) as u16) as u64;
    let word: u64 = (scenario_id as u64)
        | ((turn as u64) << 16)
        | (comp_q16 << 32)
        | ((phase as u64) << 48);

    let atomic_ref = unsafe { &*(amsv_u64_slot4_ptr as *const AtomicU64) };
    atomic_ref.store(word, Ordering::Release);
}
