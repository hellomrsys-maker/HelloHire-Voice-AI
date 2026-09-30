//! Creative Poetic Forms and Rhetorical Meter Verification in Safe Rust

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PoeticMeter {
    IambicPentameter = 1,
    Haiku575 = 2,
    FreeVerse = 3,
}

pub struct PoeticVerifier;

impl PoeticVerifier {
    /// Heuristic English syllable counter based on vowel phoneme nuclei
    pub fn count_syllables(word: &str) -> usize {
        let w = word.to_lowercase();
        let cleaned: String = w.chars().filter(|c| c.is_alphabetic()).collect();
        if cleaned.is_empty() {
            return 0;
        }

        let vowels = ['a', 'e', 'i', 'o', 'u', 'y'];
        let mut count = 0;
        let mut prev_vowel = false;

        for ch in cleaned.chars() {
            let is_v = vowels.contains(&ch);
            if is_v && !prev_vowel {
                count += 1;
            }
            prev_vowel = is_v;
        }

        // Silent 'e' at end of word deduction
        if cleaned.ends_with('e') && !cleaned.ends_with("le") && count > 1 {
            count -= 1;
        }
        count.max(1)
    }

    /// Verifies strict 5-7-5 Haiku syllable distribution across 3 lines
    pub fn verify_haiku(line1: &str, line2: &str, line3: &str) -> (bool, [usize; 3]) {
        let s1: usize = line1.split_whitespace().map(Self::count_syllables).sum();
        let s2: usize = line2.split_whitespace().map(Self::count_syllables).sum();
        let s3: usize = line3.split_whitespace().map(Self::count_syllables).sum();

        let is_valid = s1 == 5 && s2 == 7 && s3 == 5;
        (is_valid, [s1, s2, s3])
    }

    /// Detects Chiasmus (ABBA structural inversion between two parallel clauses)
    pub fn detect_chiasmus(clause_a: &[&str], clause_b: &[&str]) -> bool {
        if clause_a.len() < 2 || clause_b.len() < 2 {
            return false;
        }
        let a_first = clause_a[0].to_lowercase();
        let a_last = clause_a[clause_a.len() - 1].to_lowercase();
        let b_first = clause_b[0].to_lowercase();
        let b_last = clause_b[clause_b.len() - 1].to_lowercase();

        a_first == b_last && a_last == b_first
    }
}
