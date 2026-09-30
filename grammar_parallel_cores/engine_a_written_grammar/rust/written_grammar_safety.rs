//! written_grammar_safety.rs - Engine A Sub-Core A1 (Rust)
//! Written Grammar & Discourse Engine: Lexical token safety, AST memory invariants, zero-allocation syntax bounds.

#![no_std]
#![allow(dead_code)]

/// Fixed-point Q16 score representation (0.0 to 1.0 -> 0 to 65535).
pub type Q16 = u16;

#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct WrittenGrammarSafetyReport {
    pub is_memory_safe: bool,
    pub token_count: u32,
    pub clause_count: u32,
    pub nesting_depth_limit: u16,
    pub syntactic_integrity_q16: Q16,
    pub punctuation_balance_q16: Q16,
}

impl WrittenGrammarSafetyReport {
    pub const fn empty() -> Self {
        Self {
            is_memory_safe: true,
            token_count: 0,
            clause_count: 0,
            nesting_depth_limit: 32,
            syntactic_integrity_q16: 65535,
            punctuation_balance_q16: 65535,
        }
    }
}

/// Validates written grammar input against zero-allocation buffer invariants.
pub fn validate_written_grammar_buffer(buffer: &[u8]) -> WrittenGrammarSafetyReport {
    if buffer.is_empty() {
        return WrittenGrammarSafetyReport {
            is_memory_safe: false,
            token_count: 0,
            clause_count: 0,
            nesting_depth_limit: 32,
            syntactic_integrity_q16: 0,
            punctuation_balance_q16: 0,
        };
    }

    let mut token_count: u32 = 0;
    let mut in_token = false;
    let mut clause_delimiters: u32 = 0;
    let mut open_parens: i32 = 0;
    let mut open_brackets: i32 = 0;
    let mut open_quotes: bool = false;
    let mut has_null = false;

    for &byte in buffer {
        if byte == 0 {
            has_null = true;
        }

        if byte == b' ' || byte == b'\t' || byte == b'\n' || byte == b'\r' {
            if in_token {
                token_count += 1;
                in_token = false;
            }
        } else {
            in_token = true;
        }

        match byte {
            b'.' | b';' | b'!' | b'?' => {
                clause_delimiters += 1;
            }
            b'(' => open_parens += 1,
            b')' => {
                if open_parens > 0 {
                    open_parens -= 1;
                }
            }
            b'[' => open_brackets += 1,
            b']' => {
                if open_brackets > 0 {
                    open_brackets -= 1;
                }
            }
            b'"' => open_quotes = !open_quotes,
            _ => {}
        }
    }

    if in_token {
        token_count += 1;
    }

    let punct_unbalanced = (open_parens != 0) || (open_brackets != 0) || open_quotes;
    let punct_score_q16: Q16 = if punct_unbalanced { 32768 } else { 65535 };
    let integrity_score_q16: Q16 = if has_null { 16384 } else { 65535 };

    WrittenGrammarSafetyReport {
        is_memory_safe: !has_null && token_count > 0,
        token_count,
        clause_count: clause_delimiters.max(1),
        nesting_depth_limit: 32,
        syntactic_integrity_q16: integrity_score_q16,
        punctuation_balance_q16: punct_score_q16,
    }
}
