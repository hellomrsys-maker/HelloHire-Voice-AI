// training/rust/src/normalizer.rs
//! Unicode normalization and text cleaning for training records.

use unicode_normalization::UnicodeNormalization;

pub struct Normalizer {
    pub nfc: bool,
    pub lowercase: bool,
    pub strip_control: bool,
    pub collapse_whitespace: bool,
}

impl Default for Normalizer {
    fn default() -> Self {
        Self {
            nfc: true,
            lowercase: false,
            strip_control: true,
            collapse_whitespace: true,
        }
    }
}

impl Normalizer {
    pub fn new() -> Self {
        Self::default()
    }

    /// Normalize a string according to configured rules.
    pub fn normalize(&self, input: &str) -> String {
        let mut s: String = if self.nfc {
            input.nfc().collect()
        } else {
            input.to_string()
        };

        if self.strip_control {
            s = s.chars().filter(|c| !c.is_control() || *c == '\n' || *c == '\t').collect();
        }

        if self.lowercase {
            s = s.to_lowercase();
        }

        if self.collapse_whitespace {
            // Replace any run of whitespace (except newlines) with a single space
            let mut result = String::with_capacity(s.len());
            let mut prev_space = false;
            for c in s.chars() {
                if c == ' ' || c == '\t' {
                    if !prev_space {
                        result.push(' ');
                        prev_space = true;
                    }
                } else {
                    prev_space = false;
                    result.push(c);
                }
            }
            s = result.trim().to_string();
        }

        s
    }

    /// Normalize all slot values in a record's slot map.
    pub fn normalize_slots(
        &self,
        slots: &std::collections::HashMap<String, String>,
    ) -> std::collections::HashMap<String, String> {
        slots
            .iter()
            .map(|(k, v)| (k.clone(), self.normalize(v)))
            .collect()
    }
}
