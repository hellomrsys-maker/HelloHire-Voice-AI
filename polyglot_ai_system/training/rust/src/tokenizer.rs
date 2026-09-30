// training/rust/src/tokenizer.rs
//! BPE tokenizer for the training data pipeline.
//! Implements byte-pair encoding with a configurable vocabulary,
//! special token handling, and parallel tokenization via Rayon.

use ahash::AHashMap;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;
use thiserror::Error;

/// Vocabulary: token string → token ID
pub type Vocab = AHashMap<String, u32>;

/// Reverse vocabulary: token ID → token string
pub type ReverseVocab = AHashMap<u32, String>;

#[derive(Debug, Error)]
pub enum TokenizerError {
    #[error("Vocabulary file not found: {0}")]
    VocabNotFound(String),
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("Unknown token: {0}")]
    UnknownToken(String),
}

/// Tokenizer kind selector.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TokenizerKind {
    Bpe,
    WordPiece,
    Unigram,
    Character,
}

/// Special token IDs used throughout the pipeline.
pub const PAD_ID: u32 = 0;
pub const UNK_ID: u32 = 1;
pub const BOS_ID: u32 = 2;
pub const EOS_ID: u32 = 3;
pub const SEP_ID: u32 = 4;
pub const MASK_ID: u32 = 5;

/// Core tokenizer trait.
pub trait Tokenizer: Send + Sync {
    fn encode(&self, text: &str) -> Vec<u32>;
    fn encode_batch(&self, texts: &[String]) -> Vec<Vec<u32>>;
    fn decode(&self, ids: &[u32]) -> String;
    fn vocab_size(&self) -> usize;
}

// ─────────────────────────────────────────────────────────────────────────────
// BPE Merge rule
// ─────────────────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MergeRule {
    pub left: String,
    pub right: String,
    pub merged: String,
    pub priority: u32,
}

// ─────────────────────────────────────────────────────────────────────────────
// BpeTokenizer
// ─────────────────────────────────────────────────────────────────────────────

pub struct BpeTokenizer {
    vocab: Vocab,
    reverse_vocab: ReverseVocab,
    merge_rules: Vec<MergeRule>,
    /// merge pair → (merged_token, priority)
    merge_map: AHashMap<(String, String), (String, u32)>,
    pub max_token_len: usize,
    pub add_bos: bool,
    pub add_eos: bool,
}

impl BpeTokenizer {
    /// Construct a BPE tokenizer from pre-built vocabulary and merge rules.
    pub fn new(vocab: Vocab, merge_rules: Vec<MergeRule>) -> Self {
        let mut reverse_vocab = AHashMap::with_capacity(vocab.len());
        for (tok, id) in &vocab {
            reverse_vocab.insert(*id, tok.clone());
        }

        let mut merge_map = AHashMap::with_capacity(merge_rules.len());
        for rule in &merge_rules {
            merge_map.insert(
                (rule.left.clone(), rule.right.clone()),
                (rule.merged.clone(), rule.priority),
            );
        }

        Self {
            vocab,
            reverse_vocab,
            merge_rules,
            merge_map,
            max_token_len: 16,
            add_bos: true,
            add_eos: true,
        }
    }

    /// Load vocabulary from a JSON file (HuggingFace tokenizer.json compatible).
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Self, TokenizerError> {
        let path = path.as_ref();
        if !path.exists() {
            return Err(TokenizerError::VocabNotFound(
                path.to_string_lossy().to_string(),
            ));
        }
        let content = std::fs::read_to_string(path)?;
        let data: serde_json::Value = serde_json::from_str(&content)?;

        let mut vocab: Vocab = AHashMap::new();
        if let Some(v) = data.get("vocab").and_then(|v| v.as_object()) {
            for (token, id) in v {
                if let Some(id_u64) = id.as_u64() {
                    vocab.insert(token.clone(), id_u64 as u32);
                }
            }
        }

        // Seed special tokens if missing
        for (tok, id) in [("<pad>", PAD_ID), ("<unk>", UNK_ID),
                           ("<s>", BOS_ID), ("</s>", EOS_ID),
                           ("<sep>", SEP_ID), ("<mask>", MASK_ID)] {
            vocab.entry(tok.to_string()).or_insert(id);
        }

        let merges_raw: Vec<serde_json::Value> = data
            .get("merges")
            .and_then(|m| m.as_array())
            .cloned()
            .unwrap_or_default();

        let mut merge_rules = Vec::with_capacity(merges_raw.len());
        for (priority, item) in merges_raw.iter().enumerate() {
            if let Some(s) = item.as_str() {
                let parts: Vec<&str> = s.splitn(2, ' ').collect();
                if parts.len() == 2 {
                    let left = parts[0].to_string();
                    let right = parts[1].to_string();
                    let merged = format!("{}{}", left, right);
                    merge_rules.push(MergeRule {
                        left,
                        right,
                        merged,
                        priority: priority as u32,
                    });
                }
            }
        }

        Ok(Self::new(vocab, merge_rules))
    }

    /// Build a minimal in-memory BPE tokenizer from character-level vocabulary.
    /// Used when no pre-built vocab is available.
    pub fn bootstrap_character_level(max_vocab: usize) -> Self {
        let mut vocab: Vocab = AHashMap::new();
        // Special tokens
        vocab.insert("<pad>".to_string(), PAD_ID);
        vocab.insert("<unk>".to_string(), UNK_ID);
        vocab.insert("<s>".to_string(), BOS_ID);
        vocab.insert("</s>".to_string(), EOS_ID);
        vocab.insert("<sep>".to_string(), SEP_ID);
        vocab.insert("<mask>".to_string(), MASK_ID);

        // ASCII printable characters
        let mut id: u32 = 6;
        for c in ' '..='~' {
            vocab.insert(c.to_string(), id);
            id += 1;
            if id as usize >= max_vocab {
                break;
            }
        }

        Self::new(vocab, vec![])
    }

    // ── Internal BPE algorithm ────────────────────────────────────────────

    /// Tokenize a single word into sub-word pieces using BPE merges.
    fn tokenize_word(&self, word: &str) -> Vec<String> {
        if word.is_empty() {
            return vec![];
        }

        // Start as character sequence
        let mut pieces: Vec<String> = word.chars().map(|c| c.to_string()).collect();

        // Apply merge rules greedily by priority order
        loop {
            let mut best: Option<(usize, u32)> = None; // (position, priority)

            for i in 0..pieces.len().saturating_sub(1) {
                let key = (pieces[i].clone(), pieces[i + 1].clone());
                if let Some((_, priority)) = self.merge_map.get(&key) {
                    if best.is_none() || *priority < best.unwrap().1 {
                        best = Some((i, *priority));
                    }
                }
            }

            match best {
                None => break,
                Some((pos, _)) => {
                    let key = (pieces[pos].clone(), pieces[pos + 1].clone());
                    let merged = self.merge_map[&key].0.clone();
                    pieces.remove(pos + 1);
                    pieces[pos] = merged;
                }
            }
        }

        pieces
    }

    /// Pre-tokenize text into words (whitespace split with leading Ġ marker).
    fn pretokenize(text: &str) -> Vec<String> {
        let mut words = Vec::new();
        let mut current = String::new();
        let mut first_in_word = true;

        for c in text.chars() {
            if c.is_whitespace() {
                if !current.is_empty() {
                    words.push(current.clone());
                    current.clear();
                }
                first_in_word = true;
            } else {
                if first_in_word && !words.is_empty() {
                    current.push('Ġ');
                }
                current.push(c);
                first_in_word = false;
            }
        }
        if !current.is_empty() {
            words.push(current);
        }
        words
    }
}

impl Tokenizer for BpeTokenizer {
    fn encode(&self, text: &str) -> Vec<u32> {
        let mut ids = Vec::new();

        if self.add_bos {
            ids.push(BOS_ID);
        }

        let words = Self::pretokenize(text);
        for word in &words {
            let pieces = self.tokenize_word(word);
            for piece in pieces {
                let id = self.vocab.get(&piece).copied().unwrap_or(UNK_ID);
                ids.push(id);
            }
        }

        if self.add_eos {
            ids.push(EOS_ID);
        }

        ids
    }

    fn encode_batch(&self, texts: &[String]) -> Vec<Vec<u32>> {
        texts
            .par_iter()
            .map(|t| self.encode(t.as_str()))
            .collect()
    }

    fn decode(&self, ids: &[u32]) -> String {
        let mut result = String::new();
        for &id in ids {
            if id == BOS_ID || id == EOS_ID || id == PAD_ID {
                continue;
            }
            if let Some(tok) = self.reverse_vocab.get(&id) {
                let tok = tok.trim_start_matches('Ġ');
                if !result.is_empty() && !tok.is_empty() {
                    result.push(' ');
                }
                result.push_str(tok);
            }
        }
        result
    }

    fn vocab_size(&self) -> usize {
        self.vocab.len()
    }
}
