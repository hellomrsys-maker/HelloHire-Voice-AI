//! social_stream.rs — Real-time stream processing for ECSE in Rust

pub struct SocialAnalysis {
    pub positive_affect: f32,
    pub negative_affect: f32,
    pub valence_score: f32,
    pub warmth_density: f32,
    pub collective_identity: f32,
    pub diplomatic_tact: f32,
    pub composite_score: f32,
}

pub fn analyze_social_metrics(text: &str) -> SocialAnalysis {
    let lower = text.to_lowercase();
    let pos_cues = ["excited", "thrilled", "passionate", "delighted", "love", "genuinely", "absolutely", "fantastic", "proud", "confident"];
    let neg_cues = ["unfortunately", "difficult", "struggle", "challenging", "frustrat", "anxious", "concerned", "worried", "hesitant"];
    let warmth_cues = ["i appreciate", "thank you", "insightful", "completely agree", "understand", "empathize", "resonates"];
    let collective_cues = ["we ", "our team", "together", "collectively", "collaborat"];

    let mut pos: f32 = 0.0;
    for c in &pos_cues {
        if lower.contains(c) {
            pos += 0.12;
        }
    }
    pos = pos.clamp(0.0, 1.0);

    let mut neg: f32 = 0.0;
    for c in &neg_cues {
        if lower.contains(c) {
            neg += 0.12;
        }
    }
    neg = neg.clamp(0.0, 1.0);

    let valence = (pos - neg).clamp(-1.0, 1.0);

    let mut w_count = 0;
    for c in &warmth_cues {
        if lower.contains(c) {
            w_count += 1;
        }
    }
    let warmth = ((w_count as f32) * 0.25).clamp(0.0, 1.0);

    let mut c_count = 0;
    for c in &collective_cues {
        if lower.contains(c) {
            c_count += 1;
        }
    }
    let collective = ((c_count as f32) * 0.22).clamp(0.0, 1.0);

    let diplomatic = if lower.contains("wrong") || lower.contains("incorrect") {
        0.3
    } else {
        0.85
    };

    let composite = (pos * 0.25 + (1.0 - neg) * 0.20 + warmth * 0.25 + collective * 0.15 + diplomatic * 0.15).clamp(0.0, 1.0);

    SocialAnalysis {
        positive_affect: pos,
        negative_affect: neg,
        valence_score: valence,
        warmth_density: warmth,
        collective_identity: collective,
        diplomatic_tact: diplomatic,
        composite_score: composite,
    }
}
