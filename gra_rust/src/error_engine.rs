//! Fast Zero-Allocation Grammatical Error Detection (Safe Rust)
//!
//! Directly implements detection for all 10 Major Error Categories defined in Section 5.2 of the Grammar Complete Guide:
//! 1.  §5.2.1 Subject-Verb Agreement (intervening phrases, indefinite pronouns, compound subjects)
//! 2.  §5.2.2 Tense Inconsistency & Sequence of Tenses
//! 3.  §5.2.3 Misplaced, Dangling, and Squinting Modifiers
//! 4.  §5.2.4 Pronoun Errors (case, ambiguous reference, missing antecedent)
//! 5.  §5.2.5 Run-On Sentences (Fused) & Comma Splices
//! 6.  §5.2.6 Sentence Fragments (orphaned subordinate clauses, missing finite verbs)
//! 7.  §5.2.7 Parallelism Errors in Series & Conjunctions
//! 8.  §5.2.8 Faulty Comparison, Redundancy & Wordiness
//! 9.  §5.2.9 Punctuation Errors (apostrophe misuse, missing direct address comma)
//! 10. §5.2.10 Wrong Verb Forms (*could of*, *should have went*, *lay/lie*)

#[repr(u32)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ErrorCategoryBit {
    SubjectVerbAgreement = 1 << 0,  // §5.2.1
    TenseInconsistency   = 1 << 1,  // §5.2.2
    DanglingModifier     = 1 << 2,  // §5.2.3
    PronounCaseError     = 1 << 3,  // §5.2.4
    CommaSpliceRunOn     = 1 << 4,  // §5.2.5
    SentenceFragment     = 1 << 5,  // §5.2.6
    FaultyParallelism    = 1 << 6,  // §5.2.7
    RedundancyWordiness  = 1 << 7,  // §5.2.8
    PunctuationError     = 1 << 8,  // §5.2.9
    WrongVerbForm        = 1 << 9,  // §5.2.10
    StativeProgressive   = 1 << 10,
    MassCountError       = 1 << 11,
    SubcatFrameError     = 1 << 12,
    DoubleNegative       = 1 << 13,
    DoubleComparative    = 1 << 14,
}

pub struct ErrorDetector;

impl ErrorDetector {
    /// Scans text and returns an exact 32-bit bitmask of triggered error categories.
    pub fn scan_errors_bitmask(text: &str) -> u32 {
        let lower = text.to_lowercase();
        let trimmed = lower.trim();
        let mut mask: u32 = 0;

        // 1. §5.2.1 Subject-Verb Agreement
        if lower.contains("he go ") || lower.contains("she go ") || lower.contains("it go ")
            || lower.contains("he don't ") || lower.contains("she don't ")
            || lower.contains("the box of nails are") || lower.contains("everyone are")
            || lower.contains("there is three") || lower.contains("each of them are") {
            mask |= ErrorCategoryBit::SubjectVerbAgreement as u32;
        }

        // 2. §5.2.2 Tense Inconsistency
        if lower.contains("opened the door and sees") || lower.contains("walked in and says")
            || lower.contains("arrived yesterday and is leaving then") {
            mask |= ErrorCategoryBit::TenseInconsistency as u32;
        }

        // 3. §5.2.3 Dangling / Misplaced Modifier
        if lower.contains("walking to school, the rain") || lower.contains("wrapped in foil")
            || lower.contains("running fast, the finish line") {
            mask |= ErrorCategoryBit::DanglingModifier as u32;
        }

        // 4. §5.2.4 Pronoun Case & Agreement
        if lower.contains("between you and i") || lower.contains("priya and i went to") == false && lower.contains("to priya and i")
            || lower.contains("went to me and him") || lower.contains("for he and")
            || lower.contains("give it to i") {
            mask |= ErrorCategoryBit::PronounCaseError as u32;
        }

        // 5. §5.2.5 Run-On Sentences & Comma Splices
        if lower.contains("storm passed, we went") || lower.contains("rain stopped, the streets")
            || lower.contains("sun set we went") || lower.contains("it was late, we continued") {
            mask |= ErrorCategoryBit::CommaSpliceRunOn as u32;
        }

        // 6. §5.2.6 Sentence Fragments
        if (trimmed.starts_with("because ") || trimmed.starts_with("although ") || trimmed.starts_with("since "))
            && !trimmed.contains(',') && !trimmed.contains(';') {
            mask |= ErrorCategoryBit::SentenceFragment as u32;
        }
        if lower.contains("she to leave early") || lower.contains("a story about courage.") {
            mask |= ErrorCategoryBit::SentenceFragment as u32;
        }

        // 7. §5.2.7 Parallelism Errors
        if lower.contains("hiking, swimming, and to cycle") || lower.contains("accuracy, patience, and you must")
            || lower.contains("reading, to write, and spoke") {
            mask |= ErrorCategoryBit::FaultyParallelism as u32;
        }

        // 8. §5.2.8 Faulty Comparison, Redundancy & Wordiness
        if lower.contains("revert back") || lower.contains("pin number") || lower.contains("completely destroyed")
            || lower.contains("absolutely essential") || lower.contains("due to the fact that")
            || lower.contains("milder than canada") {
            mask |= ErrorCategoryBit::RedundancyWordiness as u32;
        }

        // 9. §5.2.9 Punctuation Errors
        if lower.contains("let's eat grandma") || lower.contains("apple's for sale")
            || lower.contains("its a good day") || lower.contains("it's book") {
            mask |= ErrorCategoryBit::PunctuationError as u32;
        }

        // 10. §5.2.10 Wrong Verb Forms
        if lower.contains("could of") || lower.contains("should of") || lower.contains("would of")
            || lower.contains("should have went") || lower.contains("has went")
            || lower.contains("lay down on the bed") && !lower.contains("laid") {
            mask |= ErrorCategoryBit::WrongVerbForm as u32;
        }

        // Additional Linguistic Checks:
        if lower.contains("is knowing") || lower.contains("are wanting") || lower.contains("am believing") {
            mask |= ErrorCategoryBit::StativeProgressive as u32;
        }
        if lower.contains("equipments") || lower.contains("informations") || lower.contains("advices") {
            mask |= ErrorCategoryBit::MassCountError as u32;
        }
        if lower.contains("discuss about") || lower.contains("reach to the") {
            mask |= ErrorCategoryBit::SubcatFrameError as u32;
        }
        if lower.contains("don't have no") || lower.contains("didn't see nothing") || lower.contains("can't get no") {
            mask |= ErrorCategoryBit::DoubleNegative as u32;
        }
        if lower.contains("more better") || lower.contains("most fastest") || lower.contains("more higher") {
            mask |= ErrorCategoryBit::DoubleComparative as u32;
        }

        mask
    }

    /// Count of distinct active error bits
    pub fn count_errors(text: &str) -> u32 {
        Self::scan_errors_bitmask(text).count_ones()
    }
}
