//! listening_stream.rs — Zero-Copy Listening Signal Extractor (ALIE Rust Layer)
//!
//! Extracts pronoun alignment, repair signals, Jaccard topic overlap,
//! and co-referential entity chains from raw candidate/interviewer turn pairs.

pub struct ListeningStreamAnalysis {
    pub jaccard_topic_overlap: f32,
    pub pronoun_echo_detected: bool,
    pub repair_signal_count: u32,
    pub entity_carry_count: u32,
    pub latency_score: f32,
    pub composite_listening_score: f32,
}

const REPAIR_CUES: &[&str] = &[
    "could you clarify", "what do you mean", "did you mean",
    "can you elaborate", "just to confirm", "are you asking about",
    "let me make sure i understood"
];

fn tokenise(text: &str) -> Vec<String> {
    text.to_lowercase()
        .split(|c: char| !c.is_alphabetic())
        .filter(|w| w.len() >= 2)
        .map(|w| w.to_string())
        .collect()
}

fn jaccard_similarity(a: &[String], b: &[String]) -> f32 {
    use std::collections::HashSet;
    let sa: HashSet<&String> = a.iter().collect();
    let sb: HashSet<&String> = b.iter().collect();
    let intersect = sa.intersection(&sb).count();
    let union = sa.union(&sb).count();
    if union == 0 { 0.0 } else { intersect as f32 / union as f32 }
}

pub fn analyze_listening_pair(
    question: &str,
    answer: &str,
    history: &[&str],
    latency_ms: f32,
) -> ListeningStreamAnalysis {
    let q_lower = question.to_lowercase();
    let a_lower = answer.to_lowercase();
    let q_tokens = tokenise(question);
    let a_tokens = tokenise(answer);

    // 1. Topic Jaccard
    let jaccard = (jaccard_similarity(&q_tokens, &a_tokens) * 3.0).clamp(0.1, 1.0);

    // 2. Pronoun echo
    let q_has_you = q_lower.contains("you") || q_lower.contains("your");
    let a_has_i = a_lower.contains(" i ") || a_lower.contains("my ") || a_lower.contains("we ");
    let pronoun_echo = q_has_you && a_has_i;

    // 3. Repair signals
    let repair_count = REPAIR_CUES.iter()
        .filter(|&&c| a_lower.contains(c))
        .count() as u32;

    // 4. Entity carry-forward
    let mut entity_carry = 0u32;
    for prev in history {
        for w in tokenise(prev) {
            if w.len() >= 5 && a_tokens.iter().any(|t| t == &w) {
                entity_carry += 1;
            }
        }
    }

    // 5. Latency score
    let latency_score = if latency_ms >= 800.0 && latency_ms <= 2200.0 {
        1.0
    } else if latency_ms < 300.0 {
        0.40
    } else if latency_ms < 800.0 {
        (0.40 + (latency_ms / 800.0) * 0.60).clamp(0.4, 1.0)
    } else {
        let excess = latency_ms - 2200.0;
        (-0.00045 * excess as f64).exp() as f32
    };

    let repair_score = match repair_count {
        0 => 0.60,
        1 | 2 => 0.95,
        _ => (0.95 - (repair_count - 2) as f32 * 0.20).clamp(0.3, 0.95),
    };

    let coref_score = if history.is_empty() {
        0.87
    } else {
        (0.40 + (entity_carry as f32 / 5.0).clamp(0.0, 1.0) * 0.55).clamp(0.3, 1.0)
    };

    let echo_score = if pronoun_echo { 0.95 } else { 0.40 };

    let composite = jaccard * 0.25
        + echo_score * 0.20
        + latency_score * 0.15
        + repair_score * 0.15
        + coref_score * 0.25;

    ListeningStreamAnalysis {
        jaccard_topic_overlap: jaccard,
        pronoun_echo_detected: pronoun_echo,
        repair_signal_count: repair_count,
        entity_carry_count: entity_carry,
        latency_score,
        composite_listening_score: composite.clamp(0.0, 1.0),
    }
}
