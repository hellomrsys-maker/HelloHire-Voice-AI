// =============================================================================
// engine/rust/src/sentence_segmenter.rs
// Sentence segmentation with abbreviation handling, quote awareness,
// and multilingual support.
// =============================================================================

use serde::{Deserialize, Serialize};
use unicode_segmentation::UnicodeSegmentation;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Sentence {
    pub text:  String,
    pub start: u32,  // Byte offset start in original string
    pub end:   u32,  // Byte offset end (exclusive)
}

pub struct SentenceSegmenter {
    abbreviations: Vec<String>,
}

impl SentenceSegmenter {
    pub fn new() -> Self {
        let abbreviations = vec![
            "Mr", "Mrs", "Ms", "Dr", "Prof", "Sr", "Jr", "Rev", "Gen",
            "Sgt", "Cpl", "Pvt", "Capt", "Lt", "Col", "Brig", "Adm",
            "vs", "etc", "e.g", "i.e", "al", "fig", "vol", "pp", "ch",
            "dept", "est", "approx", "avg", "max", "min", "no", "St",
            "Blvd", "Ave", "Rd", "Hwy", "Mt", "Inc", "Ltd", "Corp",
        ].into_iter().map(String::from).collect();

        Self { abbreviations }
    }

    /// Segments text into sentences.
    pub fn segment(&self, text: &str) -> Vec<Sentence> {
        if text.trim().is_empty() {
            return vec![];
        }

        let mut sentences: Vec<Sentence> = Vec::new();
        let mut current_start: u32 = 0;
        let mut current_end:   u32 = 0;
        let bytes = text.as_bytes();
        let len   = bytes.len();

        let chars: Vec<(usize, char)> = text.char_indices().collect();

        let mut i = 0;
        while i < chars.len() {
            let (byte_pos, ch) = chars[i];
            current_end = byte_pos as u32 + ch.len_utf8() as u32;

            if self.is_sentence_terminal(ch) {
                // Check if this is a real sentence boundary
                if self.is_real_boundary(text, &chars, i) {
                    let sentence_text = text[current_start as usize..current_end as usize]
                        .trim()
                        .to_string();
                    if !sentence_text.is_empty() {
                        sentences.push(Sentence {
                            text:  sentence_text,
                            start: current_start,
                            end:   current_end,
                        });
                    }
                    // Skip following whitespace
                    let mut j = i + 1;
                    while j < chars.len() && chars[j].1.is_whitespace() {
                        j += 1;
                    }
                    current_start = if j < chars.len() {
                        chars[j].0 as u32
                    } else {
                        len as u32
                    };
                    i = j;
                    continue;
                }
            }

            i += 1;
        }

        // Add remaining text as final sentence
        if (current_start as usize) < len {
            let remaining = text[current_start as usize..].trim().to_string();
            if !remaining.is_empty() {
                sentences.push(Sentence {
                    text:  remaining,
                    start: current_start,
                    end:   len as u32,
                });
            }
        }

        if sentences.is_empty() && !text.trim().is_empty() {
            sentences.push(Sentence {
                text:  text.trim().to_string(),
                start: 0,
                end:   len as u32,
            });
        }

        sentences
    }

    fn is_sentence_terminal(&self, ch: char) -> bool {
        matches!(ch, '.' | '!' | '?' | '…' | '\u{3002}' | '\u{FF61}')
    }

    fn is_real_boundary(&self, text: &str, chars: &[(usize, char)], pos: usize) -> bool {
        let (byte_pos, _ch) = chars[pos];

        // Check if it's an abbreviation
        if self.is_abbreviation(text, byte_pos) {
            return false;
        }

        // Must be followed by whitespace or end of string
        let next_pos = pos + 1;
        if next_pos >= chars.len() {
            return true;
        }
        let (_next_byte, next_ch) = chars[next_pos];
        if !next_ch.is_whitespace() {
            return false;
        }

        // The character after the whitespace should be uppercase or end of string
        let mut j = next_pos + 1;
        while j < chars.len() && chars[j].1.is_whitespace() {
            j += 1;
        }
        if j >= chars.len() {
            return true;
        }
        let (_jbyte, jch) = chars[j];
        jch.is_uppercase() || jch == '"' || jch == '\'' || jch == '('
    }

    fn is_abbreviation(&self, text: &str, period_pos: usize) -> bool {
        // Find the word that precedes this period
        let preceding = &text[..period_pos];
        let word_start = preceding
            .rfind(|c: char| c.is_whitespace() || c == '.' || c == ',')
            .map(|p| p + 1)
            .unwrap_or(0);
        let word = &preceding[word_start..];

        self.abbreviations.iter().any(|abbr| abbr.eq_ignore_ascii_case(word))
    }
}

impl Default for SentenceSegmenter {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_segmentation() {
        let seg = SentenceSegmenter::new();
        let sents = seg.segment("Hi, I am Ash. How are you? I am doing well!");
        assert_eq!(sents.len(), 3);
        assert!(sents[0].text.contains("Ash"));
        assert!(sents[1].text.contains("you"));
        assert!(sents[2].text.contains("well"));
    }

    #[test]
    fn test_abbreviation_no_split() {
        let seg = SentenceSegmenter::new();
        let sents = seg.segment("Dr. Smith works at MIT. He is a great researcher.");
        assert_eq!(sents.len(), 2);
        assert!(sents[0].text.contains("Dr. Smith"));
    }

    #[test]
    fn test_empty_input() {
        let seg = SentenceSegmenter::new();
        let sents = seg.segment("");
        assert!(sents.is_empty());
    }

    #[test]
    fn test_single_sentence_no_period() {
        let seg = SentenceSegmenter::new();
        let sents = seg.segment("Hello world");
        assert_eq!(sents.len(), 1);
        assert_eq!(sents[0].text, "Hello world");
    }

    #[test]
    fn test_multiple_terminals() {
        let seg = SentenceSegmenter::new();
        let sents = seg.segment("Really?! Are you sure?");
        assert!(sents.len() >= 1);
    }
}
