//! persuasion_stream.rs — Real-time rhetorical analysis in Rust

pub struct PersuasionAnalysis {
    pub logos: f32,
    pub ethos: f32,
    pub pathos: f32,
    pub kairos: f32,
    pub cta: f32,
    pub composite: f32,
}

pub fn analyze_persuasion(text: &str) -> PersuasionAnalysis {
    let lower = text.to_lowercase();

    let logic_cues = ["because", "therefore", "consequently", "hence", "specifically", "data shows", "evidence", "result"];
    let cred_cues = ["in my experience", "having led", "architected", "delivered", "built", "managed", "track record"];
    let emo_cues = ["pain point", "frustration", "empower", "delight", "transform", "impact", "vision", "passion"];
    let time_cues = ["now is the time", "critical", "urgent", "immediate", "inflection point", "today"];
    let cta_cues = ["recommend", "propose", "suggest", "let's", "next step", "we should", "plan is to", "execute"];

    let mut l_count = 0;
    for c in &logic_cues { if lower.contains(c) { l_count += 1; } }
    let logos = ((0.30 + (l_count as f32) * 0.15)).clamp(0.0, 1.0);

    let mut e_count = 0;
    for c in &cred_cues { if lower.contains(c) { e_count += 1; } }
    let ethos = ((e_count as f32) * 0.28).clamp(0.0, 1.0);

    let mut p_count = 0;
    for c in &emo_cues { if lower.contains(c) { p_count += 1; } }
    let pathos = ((0.20 + (p_count as f32) * 0.20)).clamp(0.0, 1.0);

    let mut k_count = 0;
    for c in &time_cues { if lower.contains(c) { k_count += 1; } }
    let kairos = ((0.35 + (k_count as f32) * 0.30)).clamp(0.0, 1.0);

    let mut c_count = 0;
    for c in &cta_cues { if lower.contains(c) { c_count += 1; } }
    let cta = ((0.20 + (c_count as f32) * 0.30)).clamp(0.0, 1.0);

    let composite = (0.30 * logos + 0.25 * ethos + 0.20 * pathos + 0.10 * kairos + 0.15 * cta).clamp(0.0, 1.0);

    PersuasionAnalysis {
        logos,
        ethos,
        pathos,
        kairos,
        cta,
        composite,
    }
}
