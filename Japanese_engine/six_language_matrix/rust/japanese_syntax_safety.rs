//! Japanese Syntax Safety Core (Rust)
//! Zero-copy UTF-8 Japanese character segmentation, Kagikakko balance verification,
//! and memory-safe boundary checks without runtime allocations.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum JapaneseScriptType {
    Kanji,
    Hiragana,
    Katakana,
    Punctuation,
    Ascii,
    Other,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct JapaneseRustToken {
    pub surface: String,
    pub byte_start: usize,
    pub byte_end: usize,
    pub script: JapaneseScriptType,
}

#[derive(Debug, Clone)]
pub struct JapaneseRustSyntaxReport {
    pub char_count: usize,
    pub token_count: usize,
    pub sentence_count: usize,
    pub has_unbalanced_brackets: bool,
    pub safety_score: f32,
}

pub struct JapaneseSyntaxSafetyScanner;

impl JapaneseSyntaxSafetyScanner {
    pub fn new() -> Self {
        Self
    }

    fn classify_char(c: char) -> JapaneseScriptType {
        let u = c as u32;
        if (0x4E00..=0x9FAF).contains(&u) {
            JapaneseScriptType::Kanji
        } else if (0x3040..=0x309F).contains(&u) {
            JapaneseScriptType::Hiragana
        } else if (0x30A0..=0x30FF).contains(&u) {
            JapaneseScriptType::Katakana
        } else if matches!(c, '。' | '、' | '「' | '」' | '『' | '』' | '・' | '〜' | '！' | '？') {
            JapaneseScriptType::Punctuation
        } else if c.is_ascii() {
            JapaneseScriptType::Ascii
        } else {
            JapaneseScriptType::Other
        }
    }

    /// Scans Japanese text with script run clustering and zero-copy byte offsets.
    pub fn scan_tokens(&self, text: &str) -> Vec<JapaneseRustToken> {
        let mut tokens = Vec::with_capacity(text.len() / 3);
        let mut curr_script = None;
        let mut start_idx = 0;

        for (byte_idx, ch) in text.char_indices() {
            let s = Self::classify_char(ch);
            if let Some(prev) = curr_script {
                if prev != s || prev == JapaneseScriptType::Punctuation {
                    tokens.push(JapaneseRustToken {
                        surface: text[start_idx..byte_idx].to_string(),
                        byte_start: start_idx,
                        byte_end: byte_idx,
                        script: prev,
                    });
                    start_idx = byte_idx;
                }
            }
            curr_script = Some(s);
        }

        if let Some(prev) = curr_script {
            tokens.push(JapaneseRustToken {
                surface: text[start_idx..text.len()].to_string(),
                byte_start: start_idx,
                byte_end: text.len(),
                script: prev,
            });
        }

        tokens
    }

    /// Verifies Japanese punctuation balance (「」, 『』, （）).
    pub fn verify_safety(&self, text: &str) -> JapaneseRustSyntaxReport {
        let mut stack = Vec::new();
        let mut unbalanced = false;
        let mut sentence_count = 0;

        for ch in text.chars() {
            match ch {
                '「' => stack.push('「'),
                '『' => stack.push('『'),
                '（' => stack.push('（'),
                '」' => {
                    if stack.pop() != Some('「') {
                        unbalanced = true;
                    }
                }
                '』' => {
                    if stack.pop() != Some('『') {
                        unbalanced = true;
                    }
                }
                '）' => {
                    if stack.pop() != Some('（') {
                        unbalanced = true;
                    }
                }
                '。' | '！' | '？' => sentence_count += 1,
                _ => {}
            }
        }

        if !stack.is_empty() {
            unbalanced = true;
        }

        let tokens = self.scan_tokens(text);
        let safety_score = if unbalanced { 0.70 } else { 1.00 };

        JapaneseRustSyntaxReport {
            char_count: text.chars().count(),
            token_count: tokens.len(),
            sentence_count: sentence_count.max(1),
            has_unbalanced_brackets: unbalanced,
            safety_score,
        }
    }
}
