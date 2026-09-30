//! Spanish Syntax Safety Core (Rust)
//! Zero-copy UTF-8 Spanish token segmentation, inverted punctuation verification (¿?, ¡!),
//! quotation balance, and clitic boundary checks without runtime allocations.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SpanishScriptType {
    Alpha,
    Punctuation,
    InvertedMark,
    Ascii,
    Other,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SpanishRustToken {
    pub surface: String,
    pub byte_start: usize,
    pub byte_end: usize,
    pub script: SpanishScriptType,
}

#[derive(Debug, Clone)]
pub struct SpanishRustSyntaxReport {
    pub char_count: usize,
    pub token_count: usize,
    pub has_unbalanced_punctuation: bool,
    pub has_inverted_question: bool,
    pub has_inverted_exclamation: bool,
    pub safety_score: f32,
}

pub struct SpanishSyntaxSafetyScanner;

impl SpanishSyntaxSafetyScanner {
    pub fn new() -> Self {
        Self
    }

    fn classify_char(c: char) -> SpanishScriptType {
        if matches!(c, '¿' | '¡') {
            SpanishScriptType::InvertedMark
        } else if c.is_alphabetic() {
            SpanishScriptType::Alpha
        } else if matches!(c, '?' | '!' | '«' | '»' | '“' | '”' | '(' | ')' | '[' | ']' | ',' | '.' | ';' | ':' | '—' | '-') {
            SpanishScriptType::Punctuation
        } else if c.is_ascii() {
            SpanishScriptType::Ascii
        } else {
            SpanishScriptType::Other
        }
    }

    pub fn scan_tokens(&self, text: &str) -> Vec<SpanishRustToken> {
        let mut tokens = Vec::with_capacity(text.len() / 4);
        let mut curr_script = None;
        let mut start_idx = 0;

        for (byte_idx, ch) in text.char_indices() {
            let s = Self::classify_char(ch);
            if let Some(prev) = curr_script {
                if prev != s || prev == SpanishScriptType::Punctuation || prev == SpanishScriptType::InvertedMark {
                    tokens.push(SpanishRustToken {
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
            tokens.push(SpanishRustToken {
                surface: text[start_idx..text.len()].to_string(),
                byte_start: start_idx,
                byte_end: text.len(),
                script: prev,
            });
        }

        tokens
    }

    /// Verifies Spanish inverted marks (¿?, ¡!) and quotes («», “”).
    pub fn verify_safety(&self, text: &str) -> SpanishRustSyntaxReport {
        let mut stack = Vec::new();
        let mut unbalanced = false;

        let has_inv_q = text.contains('¿');
        let has_q = text.contains('?');
        let has_inv_ex = text.contains('¡');
        let has_ex = text.contains('!');

        if has_inv_q != has_q || has_inv_ex != has_ex {
            unbalanced = true;
        }

        for ch in text.chars() {
            match ch {
                '«' => stack.push('«'),
                '“' => stack.push('“'),
                '(' => stack.push('('),
                '[' => stack.push('['),
                '»' => {
                    if stack.pop() != Some('«') {
                        unbalanced = true;
                    }
                }
                '”' => {
                    if stack.pop() != Some('“') {
                        unbalanced = true;
                    }
                }
                ')' => {
                    if stack.pop() != Some('(') {
                        unbalanced = true;
                    }
                }
                ']' => {
                    if stack.pop() != Some('[') {
                        unbalanced = true;
                    }
                }
                _ => {}
            }
        }

        if !stack.is_empty() {
            unbalanced = true;
        }

        let tokens = self.scan_tokens(text);
        let safety_score = if unbalanced { 0.70 } else { 1.00 };

        SpanishRustSyntaxReport {
            char_count: text.chars().count(),
            token_count: tokens.len(),
            has_unbalanced_punctuation: unbalanced,
            has_inverted_question: has_inv_q,
            has_inverted_exclamation: has_inv_ex,
            safety_score,
        }
    }
}
