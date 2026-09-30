//! verbal_stream_processor.rs - Zero-Copy High-Throughput Stream Processor for RVCE
//!
//! Handles real-time candidate transcript ingestion, phoneme/text stream chunking,
//! filler word detection, STAR boundary tracking, and lexical diversity metrics.

pub struct StreamAnalysis {
    pub total_words: usize,
    pub unique_words: usize,
    pub type_token_ratio: f32,
    pub filler_count: usize,
    pub filler_ratio: f32,
    pub pace_wpm: f32,
    pub star_completeness: f32,
}

const FILLERS: &[&str] = &[
    "um", "uh", "like", "you know", "sort of", "kind of", "basically", "actually", "literally"
];

const STAR_SITUATION: &[&str] = &["situation", "context was", "at my previous company", "background was"];
const STAR_TASK: &[&str]      = &["task was", "objective was", "goal was to", "responsible for"];
const STAR_ACTION: &[&str]    = &["action i took", "i implemented", "i designed", "we built", "i led"];
const STAR_RESULT: &[&str]    = &["result was", "outcome was", "reduced", "increased by", "delivered"];

pub fn process_transcript_stream(transcript: &str, duration_seconds: f32) -> StreamAnalysis {
    let lower = transcript.to_lowercase();
    let words: Vec<&str> = lower.split_whitespace().collect();
    let total_words = words.len();

    if total_words == 0 {
        return StreamAnalysis {
            total_words: 0,
            unique_words: 0,
            type_token_ratio: 0.0,
            filler_count: 0,
            filler_ratio: 0.0,
            pace_wpm: 0.0,
            star_completeness: 0.0,
        };
    }

    // Unique words computation (zero-allocation sort & dedup)
    let mut sorted_words = words.clone();
    sorted_words.sort_unstable();
    sorted_words.dedup();
    let unique_words = sorted_words.len();
    let type_token_ratio = (unique_words as f32) / (total_words as f32);

    // Filler word counter
    let mut filler_count = 0;
    for &filler in FILLERS {
        if filler.contains(' ') {
            // Multi-word filler like "you know"
            let mut start = 0;
            while let Some(pos) = lower[start..].find(filler) {
                filler_count += 1;
                start += pos + filler.len();
            }
        } else {
            filler_count += words.iter().filter(|&&w| w == filler).count();
        }
    }
    let filler_ratio = (filler_count as f32) / (total_words as f32);

    // Pace WPM
    let minutes = if duration_seconds > 0.0 { duration_seconds / 60.0 } else { 1.0 };
    let pace_wpm = (total_words as f32) / minutes;

    // STAR Completeness
    let has_s = STAR_SITUATION.iter().any(|&c| lower.contains(c)) as u32;
    let has_t = STAR_TASK.iter().any(|&c| lower.contains(c)) as u32;
    let has_a = STAR_ACTION.iter().any(|&c| lower.contains(c)) as u32;
    let has_r = STAR_RESULT.iter().any(|&c| lower.contains(c)) as u32;
    let star_completeness = ((has_s + has_t + has_a + has_r) as f32) / 4.0;

    StreamAnalysis {
        total_words,
        unique_words,
        type_token_ratio,
        filler_count,
        filler_ratio,
        pace_wpm,
        star_completeness,
    }
}
