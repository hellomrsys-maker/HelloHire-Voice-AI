// =============================================================================
// engine/rust/src/normalizer.rs
// Text normalization: Unicode NFC, NFKC, lowercasing, accent stripping,
// control character removal, whitespace normalization.
// =============================================================================

use unicode_normalization::UnicodeNormalization;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum NormalizationLevel {
    /// Only strip control characters and normalize whitespace
    Minimal,
    /// NFC + whitespace normalization + control char removal
    Standard,
    /// NFKC + lowercase + accent stripping + whitespace normalization
    Aggressive,
    /// No normalization
    None,
}

pub struct TextNormalizer {
    level: NormalizationLevel,
}

impl TextNormalizer {
    pub fn new(level: NormalizationLevel) -> Self {
        Self { level }
    }

    /// Applies the configured normalization level to the input text.
    pub fn normalize(&self, text: &str) -> String {
        match &self.level {
            NormalizationLevel::None      => text.to_string(),
            NormalizationLevel::Minimal   => self.normalize_minimal(text),
            NormalizationLevel::Standard  => self.normalize_standard(text),
            NormalizationLevel::Aggressive => self.normalize_aggressive(text),
        }
    }

    // -------------------------------------------------------------------------
    // Minimal: strip control characters, normalize whitespace
    // -------------------------------------------------------------------------

    fn normalize_minimal(&self, text: &str) -> String {
        let no_control = self.strip_control_chars(text);
        self.normalize_whitespace(&no_control)
    }

    // -------------------------------------------------------------------------
    // Standard: NFC + whitespace + control chars
    // -------------------------------------------------------------------------

    fn normalize_standard(&self, text: &str) -> String {
        let nfc: String = text.nfc().collect();
        let no_control  = self.strip_control_chars(&nfc);
        self.normalize_whitespace(&no_control)
    }

    // -------------------------------------------------------------------------
    // Aggressive: NFKC + lowercase + strip accents + whitespace
    // -------------------------------------------------------------------------

    fn normalize_aggressive(&self, text: &str) -> String {
        // NFKC decomposition
        let nfkc: String = text.nfkc().collect();

        // Lowercase
        let lower = nfkc.to_lowercase();

        // Strip combining marks (accents) after NFD decomposition
        let nfd_stripped: String = lower
            .nfd()
            .filter(|c| !unicode_normalization::char::is_combining_mark(*c))
            .collect();

        // Strip control characters
        let no_control = self.strip_control_chars(&nfd_stripped);

        // Normalize whitespace
        self.normalize_whitespace(&no_control)
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    fn strip_control_chars(&self, text: &str) -> String {
        text.chars()
            .filter(|&c| !c.is_control() || c == '\n' || c == '\t' || c == '\r')
            .collect()
    }

    fn normalize_whitespace(&self, text: &str) -> String {
        // Collapse multiple whitespace chars into a single space
        let mut result = String::with_capacity(text.len());
        let mut prev_was_space = false;

        for ch in text.chars() {
            if ch.is_whitespace() {
                if !prev_was_space && !result.is_empty() {
                    result.push(' ');
                }
                prev_was_space = true;
            } else {
                result.push(ch);
                prev_was_space = false;
            }
        }

        // Trim leading/trailing
        result.trim().to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_minimal_strips_control() {
        let n = TextNormalizer::new(NormalizationLevel::Minimal);
        let input = "Hello\x00 \x01World";
        let result = n.normalize(input);
        assert!(!result.contains('\x00'));
        assert!(!result.contains('\x01'));
        assert_eq!(result, "Hello World");
    }

    #[test]
    fn test_standard_nfc() {
        let n = TextNormalizer::new(NormalizationLevel::Standard);
        // Combining character sequence for 'é' (e + combining acute)
        let input = "cafe\u{0301}"; // café via combining accent
        let result = n.normalize(input);
        // Should be NFC: single precomposed character
        assert!(!result.contains('\u{0301}'));
    }

    #[test]
    fn test_aggressive_lowercase() {
        let n = TextNormalizer::new(NormalizationLevel::Aggressive);
        let result = n.normalize("Hello WORLD");
        assert_eq!(result, "hello world");
    }

    #[test]
    fn test_whitespace_collapse() {
        let n = TextNormalizer::new(NormalizationLevel::Standard);
        let result = n.normalize("hello   world   test");
        assert_eq!(result, "hello world test");
    }

    #[test]
    fn test_none_passthrough() {
        let n = TextNormalizer::new(NormalizationLevel::None);
        let input = "Hello  World\x00";
        assert_eq!(n.normalize(input), input);
    }
}
