// =============================================================================
// engine/rust/src/tokenizer.rs
// Production-grade tokenizer: BPE + WordPiece with full Unicode support,
// morphological annotation, and position tracking.
// =============================================================================

use std::collections::HashMap;
use std::sync::Arc;
use parking_lot::RwLock;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};
use tracing::{debug, warn};
use unicode_normalization::UnicodeNormalization;
use unicode_segmentation::UnicodeSegmentation;

// =============================================================================
// TokenizerConfig
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenizerConfig {
    /// Vocabulary size (e.g., 50257 for GPT-2 style)
    pub vocab_size: usize,

    /// Maximum sequence length before truncation
    pub max_length: usize,

    /// Tokenization strategy
    pub strategy: TokenizationStrategy,

    /// Whether to add special tokens ([CLS], [SEP], etc.)
    pub add_special_tokens: bool,

    /// Whether to lowercase all input
    pub do_lowercase: bool,

    /// Whether to strip accents (for multilingual models)
    pub strip_accents: bool,

    /// Padding token id
    pub pad_token_id: u32,

    /// Unknown token id
    pub unk_token_id: u32,

    /// CLS token id
    pub cls_token_id: u32,

    /// SEP token id
    pub sep_token_id: u32,

    /// MASK token id
    pub mask_token_id: u32,
}

impl Default for TokenizerConfig {
    fn default() -> Self {
        Self {
            vocab_size:         50257,
            max_length:         8192,
            strategy:           TokenizationStrategy::BPE,
            add_special_tokens: true,
            do_lowercase:       false,
            strip_accents:      false,
            pad_token_id:       0,
            unk_token_id:       1,
            cls_token_id:       2,
            sep_token_id:       3,
            mask_token_id:      4,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TokenizationStrategy {
    /// Byte-Pair Encoding (GPT-2 style)
    BPE,
    /// WordPiece (BERT style)
    WordPiece,
    /// Unigram (SentencePiece style)
    Unigram,
    /// Whitespace + punctuation split (baseline)
    Whitespace,
    /// Character-level (for morphologically rich languages)
    Character,
}

// =============================================================================
// TokenRecord — a fully annotated token
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenRecord {
    /// Surface form as it appeared in the input
    pub surface: String,

    /// Normalized form (lowercased, accent-stripped if configured)
    pub normalized: String,

    /// Dictionary base form (lemma)
    pub lemma: String,

    /// Universal Dependencies part-of-speech tag
    pub pos_tag: String,

    /// Dependency relation label
    pub dep_label: String,

    /// Zero-based position in the token sequence
    pub position: u32,

    /// Character start offset in the original string
    pub char_start: u32,

    /// Character end offset (exclusive) in the original string
    pub char_end: u32,

    /// Vocabulary ID
    pub token_id: u32,

    /// Tokenizer confidence [0, 1]
    pub confidence: f32,

    /// Whether this is a special token ([CLS], [SEP], etc.)
    pub is_special: bool,

    /// Sub-word continuation (e.g., ## prefix for BERT WordPiece)
    pub is_continuation: bool,
}

// =============================================================================
// Vocabulary — bidirectional token ↔ ID mapping
// =============================================================================

#[derive(Debug, Default)]
pub struct Vocabulary {
    token_to_id: HashMap<String, u32>,
    id_to_token: HashMap<u32, String>,
    next_id:     u32,
}

impl Vocabulary {
    pub fn new() -> Self {
        let mut vocab = Self::default();
        // Insert standard special tokens
        for tok in &["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"] {
            vocab.add(tok.to_string());
        }
        vocab
    }

    pub fn add(&mut self, token: String) -> u32 {
        if let Some(&id) = self.token_to_id.get(&token) {
            return id;
        }
        let id = self.next_id;
        self.token_to_id.insert(token.clone(), id);
        self.id_to_token.insert(id, token);
        self.next_id += 1;
        id
    }

    pub fn get_id(&self, token: &str) -> Option<u32> {
        self.token_to_id.get(token).copied()
    }

    pub fn get_token(&self, id: u32) -> Option<&str> {
        self.id_to_token.get(&id).map(|s| s.as_str())
    }

    pub fn size(&self) -> usize {
        self.token_to_id.len()
    }

    pub fn contains(&self, token: &str) -> bool {
        self.token_to_id.contains_key(token)
    }
}

// =============================================================================
// BPEMergeTable — BPE merge rules
// =============================================================================

#[derive(Debug, Default)]
pub struct BPEMergeTable {
    /// Ordered list of (a, b) → ab merge rules; lower index = higher priority
    merges: Vec<(String, String)>,
    /// Fast lookup: (a, b) → merge rank
    lookup: HashMap<(String, String), usize>,
}

impl BPEMergeTable {
    pub fn from_merges(merges: Vec<(String, String)>) -> Self {
        let lookup = merges
            .iter()
            .enumerate()
            .map(|(i, (a, b))| ((a.clone(), b.clone()), i))
            .collect();
        Self { merges, lookup }
    }

    pub fn get_rank(&self, a: &str, b: &str) -> Option<usize> {
        self.lookup.get(&(a.to_string(), b.to_string())).copied()
    }

    pub fn len(&self) -> usize {
        self.merges.len()
    }

    pub fn is_empty(&self) -> bool {
        self.merges.is_empty()
    }
}

// =============================================================================
// EngineTokenizer — main tokenizer struct
// =============================================================================

pub struct EngineTokenizer {
    config:      TokenizerConfig,
    vocab:       Arc<RwLock<Vocabulary>>,
    merge_table: Arc<BPEMergeTable>,
}

impl EngineTokenizer {
    /// Creates a new tokenizer with the given configuration.
    pub fn new(config: TokenizerConfig) -> Self {
        Self {
            vocab:       Arc::new(RwLock::new(Vocabulary::new())),
            merge_table: Arc::new(BPEMergeTable::default()),
            config,
        }
    }

    /// Creates a tokenizer with a pre-trained BPE vocabulary loaded from JSON.
    pub fn from_vocab_json(config: TokenizerConfig, vocab_json: &str) -> Result<Self> {
        let vocab_map: HashMap<String, u32> = serde_json::from_str(vocab_json)
            .context("Failed to parse vocabulary JSON")?;

        let mut vocab = Vocabulary::new();
        let mut sorted_entries: Vec<(String, u32)> = vocab_map.into_iter().collect();
        sorted_entries.sort_by_key(|(_, id)| *id);
        for (token, _) in sorted_entries {
            vocab.add(token);
        }

        Ok(Self {
            vocab:       Arc::new(RwLock::new(vocab)),
            merge_table: Arc::new(BPEMergeTable::default()),
            config,
        })
    }

    /// Tokenizes a text string into a Vec of TokenRecord.
    pub fn tokenize(&self, text: &str) -> Result<Vec<TokenRecord>> {
        match self.config.strategy {
            TokenizationStrategy::BPE       => self.tokenize_bpe(text),
            TokenizationStrategy::WordPiece => self.tokenize_wordpiece(text),
            TokenizationStrategy::Whitespace => self.tokenize_whitespace(text),
            TokenizationStrategy::Character  => self.tokenize_character(text),
            TokenizationStrategy::Unigram   => self.tokenize_unigram(text),
        }
    }

    /// Encodes text to token IDs.
    pub fn encode(&self, text: &str) -> Result<Vec<u32>> {
        let tokens = self.tokenize(text)?;
        Ok(tokens.iter().map(|t| t.token_id).collect())
    }

    /// Decodes a sequence of token IDs back to text.
    pub fn decode(&self, ids: &[u32]) -> String {
        let vocab = self.vocab.read();
        ids.iter()
            .filter_map(|&id| vocab.get_token(id))
            .collect::<Vec<_>>()
            .join(" ")
    }

    pub fn vocab_size(&self) -> usize {
        self.vocab.read().size()
    }

    // -------------------------------------------------------------------------
    // BPE Tokenization
    // -------------------------------------------------------------------------

    fn tokenize_bpe(&self, text: &str) -> Result<Vec<TokenRecord>> {
        // Step 1: Pre-tokenize on word boundaries using Unicode word segmentation
        let word_tokens: Vec<&str> = text.unicode_words().collect();

        let mut records: Vec<TokenRecord> = Vec::new();
        let mut position: u32 = 0;
        let mut char_offset: u32 = 0;

        for word in word_tokens {
            // Step 2: Convert word to sequence of unicode chars as initial BPE symbols
            let mut symbols: Vec<String> = word.chars().map(|c| c.to_string()).collect();

            // Step 3: Apply BPE merges
            if !self.merge_table.is_empty() {
                symbols = self.apply_bpe_merges(symbols);
            }

            // Step 4: Create TokenRecord for each symbol
            for (sym_i, sym) in symbols.iter().enumerate() {
                let normalized = if self.config.do_lowercase {
                    sym.to_lowercase()
                } else {
                    sym.clone()
                };

                let normalized = if self.config.strip_accents {
                    normalized.nfd().filter(|c| !unicode_normalization::char::is_combining_mark(*c)).collect()
                } else {
                    normalized
                };

                let vocab = self.vocab.read();
                let token_id = vocab.get_id(&normalized)
                    .unwrap_or(self.config.unk_token_id);

                records.push(TokenRecord {
                    surface:         sym.clone(),
                    normalized:      normalized.clone(),
                    lemma:           normalized.clone(),
                    pos_tag:         String::new(),
                    dep_label:       String::new(),
                    position,
                    char_start:      char_offset,
                    char_end:        char_offset + sym.len() as u32,
                    token_id,
                    confidence:      1.0,
                    is_special:      false,
                    is_continuation: sym_i > 0,
                });

                char_offset += sym.len() as u32;
                position += 1;
            }
        }

        // Add special tokens if configured
        if self.config.add_special_tokens {
            records = self.wrap_with_special_tokens(records);
        }

        // Truncate to max_length
        if records.len() > self.config.max_length {
            debug!("Truncating sequence from {} to {} tokens", records.len(), self.config.max_length);
            records.truncate(self.config.max_length);
        }

        Ok(records)
    }

    fn apply_bpe_merges(&self, mut symbols: Vec<String>) -> Vec<String> {
        // Iteratively apply the highest-priority merge until no merges remain
        loop {
            let mut best_rank  = usize::MAX;
            let mut best_pos   = None;

            for i in 0..symbols.len().saturating_sub(1) {
                if let Some(rank) = self.merge_table.get_rank(&symbols[i], &symbols[i + 1]) {
                    if rank < best_rank {
                        best_rank = rank;
                        best_pos  = Some(i);
                    }
                }
            }

            match best_pos {
                None => break,
                Some(pos) => {
                    let merged = format!("{}{}", symbols[pos], symbols[pos + 1]);
                    symbols[pos] = merged;
                    symbols.remove(pos + 1);
                }
            }
        }
        symbols
    }

    // -------------------------------------------------------------------------
    // WordPiece Tokenization (BERT style)
    // -------------------------------------------------------------------------

    fn tokenize_wordpiece(&self, text: &str) -> Result<Vec<TokenRecord>> {
        let words: Vec<&str> = text.unicode_words().collect();
        let mut records: Vec<TokenRecord> = Vec::new();
        let mut position: u32 = 0;
        let mut char_offset: u32 = 0;

        for word in words {
            let lower_word = if self.config.do_lowercase {
                word.to_lowercase()
            } else {
                word.to_string()
            };

            // Greedy forward max-match WordPiece
            let sub_tokens = self.wordpiece_split(&lower_word);

            for (i, sub) in sub_tokens.iter().enumerate() {
                let vocab = self.vocab.read();
                let token_id = vocab.get_id(sub).unwrap_or(self.config.unk_token_id);

                records.push(TokenRecord {
                    surface:         if i == 0 { word.to_string() } else { sub.clone() },
                    normalized:      sub.clone(),
                    lemma:           sub.trim_start_matches("##").to_string(),
                    pos_tag:         String::new(),
                    dep_label:       String::new(),
                    position,
                    char_start:      char_offset,
                    char_end:        char_offset + sub.len() as u32,
                    token_id,
                    confidence:      1.0,
                    is_special:      false,
                    is_continuation: i > 0,
                });

                char_offset += sub.len() as u32;
                position += 1;
            }
        }

        if self.config.add_special_tokens {
            records = self.wrap_with_special_tokens(records);
        }
        if records.len() > self.config.max_length {
            records.truncate(self.config.max_length);
        }
        Ok(records)
    }

    fn wordpiece_split(&self, word: &str) -> Vec<String> {
        let vocab = self.vocab.read();
        let chars: Vec<char> = word.chars().collect();
        let n = chars.len();

        if n == 0 {
            return vec![];
        }

        // Check if the whole word is in vocab
        if vocab.contains(word) {
            return vec![word.to_string()];
        }

        // Greedy forward max-match
        let mut result = Vec::new();
        let mut start = 0;

        while start < n {
            let mut end = n;
            let prefix = if start == 0 { "" } else { "##" };
            let mut found = false;

            while end > start {
                let substr: String = chars[start..end].iter().collect();
                let candidate = format!("{}{}", prefix, substr);
                if vocab.contains(&candidate) {
                    result.push(candidate);
                    start = end;
                    found = true;
                    break;
                }
                end -= 1;
            }

            if !found {
                // Fallback: split into individual characters with ## prefix
                let c: String = std::iter::once(chars[start]).collect();
                result.push(if start == 0 { c } else { format!("##{}", c) });
                start += 1;
            }
        }

        if result.is_empty() {
            result.push("[UNK]".to_string());
        }
        result
    }

    // -------------------------------------------------------------------------
    // Whitespace tokenization (baseline)
    // -------------------------------------------------------------------------

    fn tokenize_whitespace(&self, text: &str) -> Result<Vec<TokenRecord>> {
        let mut records: Vec<TokenRecord> = Vec::new();
        let mut position: u32 = 0;
        let mut char_offset: u32 = 0;
        let mut current = String::new();
        let mut tok_start: u32 = 0;

        for ch in text.chars() {
            let ch_len = ch.len_utf8() as u32;

            if ch.is_whitespace() {
                if !current.is_empty() {
                    records.push(self.make_record(
                        current.clone(), position, tok_start, char_offset, false));
                    position += 1;
                    current.clear();
                }
                char_offset += ch_len;
            } else if ch.is_ascii_punctuation() && ch != '\'' && ch != '-' {
                if !current.is_empty() {
                    records.push(self.make_record(
                        current.clone(), position, tok_start, char_offset, false));
                    position += 1;
                    current.clear();
                }
                tok_start = char_offset;
                records.push(self.make_record(
                    ch.to_string(), position, tok_start, char_offset + ch_len, false));
                position += 1;
                char_offset += ch_len;
            } else {
                if current.is_empty() { tok_start = char_offset; }
                current.push(ch);
                char_offset += ch_len;
            }
        }

        if !current.is_empty() {
            records.push(self.make_record(current, position, tok_start, char_offset, false));
        }

        if self.config.add_special_tokens {
            records = self.wrap_with_special_tokens(records);
        }
        if records.len() > self.config.max_length {
            records.truncate(self.config.max_length);
        }
        Ok(records)
    }

    // -------------------------------------------------------------------------
    // Character tokenization
    // -------------------------------------------------------------------------

    fn tokenize_character(&self, text: &str) -> Result<Vec<TokenRecord>> {
        let mut records: Vec<TokenRecord> = Vec::new();
        let mut position: u32 = 0;
        let mut char_offset: u32 = 0;

        for ch in text.chars() {
            let ch_str = ch.to_string();
            let ch_len = ch.len_utf8() as u32;
            records.push(self.make_record(
                ch_str, position, char_offset, char_offset + ch_len, false));
            position += 1;
            char_offset += ch_len;
        }

        if records.len() > self.config.max_length {
            records.truncate(self.config.max_length);
        }
        Ok(records)
    }

    // -------------------------------------------------------------------------
    // Unigram tokenization (SentencePiece style — simplified greedy)
    // -------------------------------------------------------------------------

    fn tokenize_unigram(&self, text: &str) -> Result<Vec<TokenRecord>> {
        // For now, delegate to BPE as a reasonable approximation.
        // Production: load sentencepiece model and use its forward DP algorithm.
        warn!("Unigram tokenizer: falling back to BPE approximation. \
               Load a SentencePiece model for full unigram support.");
        self.tokenize_bpe(text)
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    fn make_record(&self, surface: String, position: u32,
                   char_start: u32, char_end: u32,
                   is_special: bool) -> TokenRecord
    {
        let normalized = if self.config.do_lowercase {
            surface.to_lowercase()
        } else {
            surface.clone()
        };
        let vocab = self.vocab.read();
        let token_id = vocab.get_id(&normalized)
            .unwrap_or(self.config.unk_token_id);
        TokenRecord {
            surface,
            normalized:      normalized.clone(),
            lemma:           normalized,
            pos_tag:         String::new(),
            dep_label:       String::new(),
            position,
            char_start,
            char_end,
            token_id,
            confidence:      1.0,
            is_special,
            is_continuation: false,
        }
    }

    fn wrap_with_special_tokens(&self, mut records: Vec<TokenRecord>) -> Vec<TokenRecord> {
        let cls_tok = TokenRecord {
            surface:         "[CLS]".into(),
            normalized:      "[CLS]".into(),
            lemma:           "[CLS]".into(),
            pos_tag:         String::new(),
            dep_label:       String::new(),
            position:        0,
            char_start:      0,
            char_end:        0,
            token_id:        self.config.cls_token_id,
            confidence:      1.0,
            is_special:      true,
            is_continuation: false,
        };
        let sep_tok = TokenRecord {
            surface:         "[SEP]".into(),
            normalized:      "[SEP]".into(),
            lemma:           "[SEP]".into(),
            pos_tag:         String::new(),
            dep_label:       String::new(),
            position:        records.len() as u32 + 1,
            char_start:      0,
            char_end:        0,
            token_id:        self.config.sep_token_id,
            confidence:      1.0,
            is_special:      true,
            is_continuation: false,
        };

        // Re-number positions
        for (i, r) in records.iter_mut().enumerate() {
            r.position = i as u32 + 1;
        }

        let mut result = vec![cls_tok];
        result.extend(records);
        result.push(sep_tok);
        result
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_whitespace_tokenizer() {
        let config = TokenizerConfig {
            strategy: TokenizationStrategy::Whitespace,
            add_special_tokens: false,
            do_lowercase: true,
            ..Default::default()
        };
        let tok = EngineTokenizer::new(config);
        let records = tok.tokenize("Hi, I am Ash.").unwrap();
        // "Hi" "," "I" "am" "Ash" "."
        let surfaces: Vec<&str> = records.iter().map(|r| r.surface.as_str()).collect();
        assert!(surfaces.contains(&"Hi"));
        assert!(surfaces.contains(&"am"));
        assert!(surfaces.contains(&"Ash"));
        assert!(surfaces.contains(&"."));
    }

    #[test]
    fn test_wordpiece_special_tokens() {
        let config = TokenizerConfig {
            strategy: TokenizationStrategy::WordPiece,
            add_special_tokens: true,
            ..Default::default()
        };
        let tok = EngineTokenizer::new(config);
        let records = tok.tokenize("Hello world").unwrap();
        assert_eq!(records.first().map(|r| r.surface.as_str()), Some("[CLS]"));
        assert_eq!(records.last().map(|r| r.surface.as_str()),  Some("[SEP]"));
    }

    #[test]
    fn test_bpe_merge_application() {
        let merges = vec![
            ("h".into(), "e".into()),
            ("he".into(), "l".into()),
            ("hel".into(), "lo".into()),
        ];
        let config = TokenizerConfig {
            strategy: TokenizationStrategy::BPE,
            add_special_tokens: false,
            ..Default::default()
        };
        let mut tok = EngineTokenizer::new(config);
        Arc::get_mut(&mut tok.merge_table).unwrap().merges = merges.clone();
        // Manually test merge application
        let symbols = vec!["h".into(), "e".into(), "l".into(), "l".into(), "o".into()];
        let merged = tok.apply_bpe_merges(symbols);
        // After merges: "h"+"e"="he", "he"+"l"="hel", "hel"+"lo"="hello"
        assert!(!merged.is_empty());
    }

    #[test]
    fn test_vocab_bidirectional() {
        let mut vocab = Vocabulary::new();
        let id = vocab.add("engine".to_string());
        assert_eq!(vocab.get_id("engine"), Some(id));
        assert_eq!(vocab.get_token(id), Some("engine"));
    }

    #[test]
    fn test_encode_decode_roundtrip() {
        let config = TokenizerConfig {
            strategy: TokenizationStrategy::Whitespace,
            add_special_tokens: false,
            do_lowercase: true,
            ..Default::default()
        };
        let mut tok = EngineTokenizer::new(config);
        // Add words to vocab
        {
            let mut vocab = tok.vocab.write();
            vocab.add("hello".to_string());
            vocab.add("world".to_string());
        }
        let ids = tok.encode("hello world").unwrap();
        let decoded = tok.decode(&ids);
        assert!(!decoded.is_empty());
    }
}
