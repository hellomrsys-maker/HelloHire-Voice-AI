//! lib.rs — HCTE Rust crate root
use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct HcteSummary {
    pub gci: f32,
    pub cognitive_tension: f32,
    pub premortem_score: f32,
    pub cognitive_grade: u8,
}

#[no_mangle]
pub extern "C" fn hcte_rust_evaluate(
    scenario_ptr: *const c_char,
    out: *mut HcteSummary,
) -> i32 {
    if scenario_ptr.is_null() || out.is_null() {
        return -1;
    }
    let text = unsafe { CStr::from_ptr(scenario_ptr) }.to_str().unwrap_or("");
    let lower = text.to_lowercase();

    // 11 Persona Heuristics
    let has_numbers = lower.chars().any(|c| c.is_ascii_digit());
    let analyst = if has_numbers { 0.85 } else { 0.50 };
    let devils = if lower.contains("however") || lower.contains("risk") { 0.88 } else { 0.45 };
    let systems = if lower.contains("architecture") || lower.contains("scale") { 0.90 } else { 0.50 };
    let premortem = if lower.contains("fail") || lower.contains("mitigat") || lower.contains("bottleneck") { 0.92 } else { 0.40 };
    let lateral = if lower.contains("alternative") || lower.contains("innovat") { 0.80 } else { 0.50 };
    let first_principles = if lower.contains("fundamentally") || lower.contains("underlying") { 0.85 } else { 0.50 };
    let dialectical = if lower.contains("trade-off") || lower.contains("balance") { 0.88 } else { 0.50 };
    let counterfactual = if lower.contains("what if") || lower.contains("suppose") { 0.78 } else { 0.50 };
    let pragmatic = if lower.contains("deliver") || lower.contains("execute") { 0.85 } else { 0.50 };
    let second_order = if lower.contains("long-term") || lower.contains("consequence") { 0.82 } else { 0.50 };
    let epistemic = if lower.contains("uncertain") || lower.contains("confidence") { 0.80 } else { 0.50 };

    let scores = [
        analyst, devils, systems, lateral, premortem, first_principles,
        dialectical, counterfactual, pragmatic, second_order, epistemic
    ];

    // Pre-mortem (index 4) has 2x weight: total weight 12.0
    let mut sum: f32 = 0.0;
    for (i, &s) in scores.iter().enumerate() {
        let w = if i == 4 { 2.0 } else { 1.0 };
        sum += s * w;
    }
    let gci = sum / 12.0;

    let mut var_sum: f32 = 0.0;
    for (i, &s) in scores.iter().enumerate() {
        let w = if i == 4 { 2.0 } else { 1.0 };
        let diff = s - gci;
        var_sum += diff * diff * w;
    }
    let tension = (var_sum / 12.0).sqrt();

    let grade = if gci >= 0.75 { 1 }
        else if gci >= 0.55 { 2 }
        else if gci >= 0.35 { 3 }
        else { 4 };

    unsafe {
        (*out).gci = gci;
        (*out).cognitive_tension = tension;
        (*out).premortem_score = premortem;
        (*out).cognitive_grade = grade;
    }
    0
}
