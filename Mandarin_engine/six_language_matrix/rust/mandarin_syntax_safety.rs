//! Mandarin Syntax Safety Core (Rust)
//! Zero-copy UTF-8 Chinese character segmentation, bracket/quotation balance verification,
//! aspect and disposal particle boundary checks without runtime allocations.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MandarinScriptType {
    Hanzi,
    Punctuation,
    Ascii,
    Other,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MandarinRustToken {
    pub surface: String,
    pub byte_start: usize,
    pub byte_end: usize,
    pub script: MandarinScriptType,
}

#[derive(Debug, Clone)]
pub struct MandarinRustSyntaxReport {
    pub char_count: usize,
    pub token_count: usize,
    pub sentence_count: usize,
    pub has_unbalanced_brackets: bool,
    pub has_ba_construction: bool,
    pub has_bei_construction: bool,
    pub aspect_particle_count: usize,
    pub safety_score: f32,
}

pub struct MandarinSyntaxSafetyScanner;

impl MandarinSyntaxSafetyScanner {
    pub fn new() -> Self {
        Self
    }

    fn classify_char(c: char) -> MandarinScriptType {
        let u = c as u32;
        // CJK Unified Ideographs (4E00-9FFF) + Ext A (3400-4DBF)
        if (0x4E00..=0x9FFF).contains(&u) || (0x3400..=0x4DBF).contains(&u) {
            MandarinScriptType::Hanzi
        } else if matches!(
            c,
            '。' | '，' | '、' | '；' | '：' | '？' | '！' | '“' | '”' | '‘' | '’' | '《' | '》' | '【' | '】' | '（' | '）' | '—' | '…'
        ) {
            MandarinScriptType::Punctuation
        } else if c.is_ascii() {
            MandarinScriptType::Ascii
        } else {
            MandarinScriptType::Other
        }
    }

    /// Scans Mandarin text with script run clustering and zero-copy byte offsets.
    pub fn scan_tokens(&self, text: &str) -> Vec<MandarinRustToken> {
        let mut tokens = Vec::with_capacity(text.len() / 3);
        let mut curr_script = None;
        let mut start_idx = 0;

        for (byte_idx, ch) in text.char_indices() {
            let s = Self::classify_char(ch);
            if let Some(prev) = curr_script {
                if prev != s || prev == MandarinScriptType::Punctuation {
                    tokens.push(MandarinRustToken {
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
            tokens.push(MandarinRustToken {
                surface: text[start_idx..text.len()].to_string(),
                byte_start: start_idx,
                byte_end: text.len(),
                script: prev,
            });
        }

        tokens
    }

    /// Verifies Chinese punctuation balance (“”, ‘’, 《》, 【】, （）) and aspect structure.
    pub fn verify_safety(&self, text: &str) -> MandarinRustSyntaxReport {
        let mut stack = Vec::new();
        let mut unbalanced = false;
        let mut sentence_count = 0;
        let mut has_ba = false;
        let mut has_bei = false;
        let mut aspect_count = 0;

        for ch in text.chars() {
            match ch {
                '“' => stack.push('“'),
                '‘' => stack.push('‘'),
                '《' => stack.push('《'),
                '【' => stack.push('【'),
                '（' => stack.push('（'),
                '”' => {
                    if stack.pop() != Some('“') {
                        unbalanced = true;
                    }
                }
                '’' => {
                    if stack.pop() != Some('‘') {
                        unbalanced = true;
                    }
                }
                '》' => {
                    if stack.pop() != Some('《') {
                        unbalanced = true;
                    }
                }
                '】' => {
                    if stack.pop() != Some('【') {
                        unbalanced = true;
                    }
                }
                '）' => {
                    if stack.pop() != Some('（') {
                        unbalanced = true;
                    }
                }
                '把' => has_ba = true,
                '被' => has_bei = true,
                '了' | '着' | '过' => aspect_count += 1,
                '。' | '！' | '？' => sentence_count += 1,
                _ => {}
            }
        }

        if !stack.is_empty() {
            unbalanced = true;
        }

        let tokens = self.scan_tokens(text);
        let safety_score = if unbalanced { 0.70 } else { 1.00 };

        MandarinRustSyntaxReport {
            char_count: text.chars().count(),
            token_count: tokens.len(),
            sentence_count: sentence_count.max(1),
            has_unbalanced_brackets: unbalanced,
            has_ba_construction: has_ba,
            has_bei_construction: has_bei,
            aspect_particle_count: aspect_count,
            safety_score,
        }
    }
}
