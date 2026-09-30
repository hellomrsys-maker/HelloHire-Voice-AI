// =============================================================================
// engine/rust/src/language_detector.rs
// Language identification using n-gram character model + trigram scoring.
// =============================================================================

use std::collections::HashMap;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DetectionResult {
    pub language:   String,  // BCP-47 language code (e.g., "en", "fr")
    pub confidence: f32,     // [0, 1]
}

pub struct LanguageDetector {
    /// language_code → (ngram → expected frequency)
    models: HashMap<String, HashMap<String, f32>>,
}

impl LanguageDetector {
    pub fn new() -> Self {
        let mut det = Self { models: HashMap::new() };
        det.load_default_models();
        det
    }

    /// Detects the language of the given text.
    pub fn detect(&self, text: &str) -> DetectionResult {
        if text.trim().is_empty() {
            return DetectionResult { language: "en".into(), confidence: 0.5 };
        }

        let text_ngrams = self.extract_char_trigrams(text);
        let mut scores: HashMap<&str, f32> = HashMap::new();

        for (lang, model) in &self.models {
            let mut score = 0.0f32;
            for (gram, &freq) in &text_ngrams {
                if let Some(&model_freq) = model.get(gram) {
                    score += freq * model_freq;
                }
            }
            scores.insert(lang, score);
        }

        let best = scores.iter().max_by(|a, b| a.1.partial_cmp(b.1).unwrap());
        match best {
            None => DetectionResult { language: "en".into(), confidence: 0.5 },
            Some((lang, &score)) => {
                let total: f32 = scores.values().sum();
                let confidence = if total > 0.0 { score / total } else { 0.5 };
                DetectionResult {
                    language:   lang.to_string(),
                    confidence: confidence.min(1.0).max(0.0),
                }
            }
        }
    }

    /// Extracts character trigrams with normalized frequencies from text.
    fn extract_char_trigrams(&self, text: &str) -> HashMap<String, f32> {
        let lower: String = text.to_lowercase();
        let chars: Vec<char> = lower.chars().collect();
        let mut counts: HashMap<String, u32> = HashMap::new();
        let total_trigrams = chars.len().saturating_sub(2);

        for i in 0..total_trigrams {
            let gram: String = chars[i..i+3].iter().collect();
            *counts.entry(gram).or_insert(0) += 1;
        }

        let total = total_trigrams.max(1) as f32;
        counts.into_iter()
            .map(|(k, v)| (k, v as f32 / total))
            .collect()
    }

    fn load_default_models(&mut self) {
        // English trigram model (top frequencies from large corpus)
        let en_model: HashMap<String, f32> = [
            ("the", 0.052), ("and", 0.028), ("ing", 0.020), ("ion", 0.015),
            ("tio", 0.013), ("ent", 0.012), ("ati", 0.011), ("for", 0.011),
            ("her", 0.010), ("ter", 0.009), ("hat", 0.009), ("tha", 0.012),
            ("ere", 0.010), ("ons", 0.008), ("nth", 0.007), ("int", 0.009),
        ].iter().map(|(k, v)| (k.to_string(), *v as f32)).collect();

        // French trigram model
        let fr_model: HashMap<String, f32> = [
            ("les", 0.040), ("est", 0.025), ("qui", 0.020), ("ent", 0.035),
            ("des", 0.030), ("que", 0.028), ("ion", 0.022), ("ais", 0.018),
            ("une", 0.020), ("sur", 0.015), ("ous", 0.018), ("par", 0.015),
        ].iter().map(|(k, v)| (k.to_string(), *v as f32)).collect();

        // German trigram model
        let de_model: HashMap<String, f32> = [
            ("der", 0.045), ("und", 0.030), ("die", 0.038), ("ein", 0.025),
            ("cht", 0.018), ("sch", 0.020), ("ich", 0.022), ("den", 0.020),
            ("ten", 0.018), ("ung", 0.022), ("ier", 0.015), ("gen", 0.018),
        ].iter().map(|(k, v)| (k.to_string(), *v as f32)).collect();

        // Spanish trigram model
        let es_model: HashMap<String, f32> = [
            ("que", 0.038), ("los", 0.028), ("con", 0.025), ("nte", 0.022),
            ("ado", 0.020), ("una", 0.018), ("cion", 0.017), ("del", 0.016),
            ("por", 0.015), ("ien", 0.014), ("tes", 0.015), ("cion", 0.017),
        ].iter().map(|(k, v)| (k.to_string(), *v as f32)).collect();

        // Italian trigram model
        let it_model: HashMap<String, f32> = [
            ("che", 0.040), ("del", 0.028), ("ell", 0.025), ("ion", 0.022),
            ("ent", 0.020), ("per", 0.018), ("ato", 0.020), ("non", 0.017),
        ].iter().map(|(k, v)| (k.to_string(), *v as f32)).collect();

        self.models.insert("en".into(), en_model);
        self.models.insert("fr".into(), fr_model);
        self.models.insert("de".into(), de_model);
        self.models.insert("es".into(), es_model);
        self.models.insert("it".into(), it_model);
    }
}

impl Default for LanguageDetector {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_english() {
        let det = LanguageDetector::new();
        let result = det.detect("The quick brown fox jumps over the lazy dog and the world");
        assert_eq!(result.language, "en");
        assert!(result.confidence > 0.3);
    }

    #[test]
    fn test_detect_french() {
        let det = LanguageDetector::new();
        let result = det.detect("Les enfants jouent dans les jardins et les parcs de la ville");
        assert_eq!(result.language, "fr");
    }

    #[test]
    fn test_detect_empty() {
        let det = LanguageDetector::new();
        let result = det.detect("");
        assert_eq!(result.language, "en");
        assert_eq!(result.confidence, 0.5);
    }
}
