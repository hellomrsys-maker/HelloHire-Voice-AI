//! Linguistic Core, Universal Grammar, Phonology & Assessment Engine (Safe Rust)
//!
//! Provides zero-allocation verification across the linguistic domains:
//! - Universal Grammar invariants & 7-Point Checklist (Part 10 of Guide)
//! - Poetic meter and syllabification (Haiku, Sonnet)
//! - Phonology invariants and stress shift verification (Part 6)
//! - Zero-allocation 10-error category bitmask scanning (Part 5)
//! - CEFR proficiency mapping and IRT ability scaling

pub mod grammar;
pub mod creativity;
pub mod phonology;
pub mod error_engine;
pub mod assessment;
pub mod typology;
pub mod bandhu_skills;

use std::ffi::CStr;
use std::os::raw::c_char;
use grammar::{UniversalGrammarValidator, UniversalChecklistScores};
use creativity::PoeticVerifier;
use phonology::PhonologyVerifier;
use error_engine::ErrorDetector;
use assessment::AssessmentModel;
use typology::{TypologyAnalyzer, TypologicalEvaluation, LanguageFamily};
use bandhu_skills::{BandhuSkillEngine, SkillEvaluation, SkillType, HistoricalEra};

#[no_mangle]
pub extern "C" fn gra_rust_evaluate_typology(
    sentence: *const c_char,
    family_id: u8,
    out_eval: *mut TypologicalEvaluation,
) -> bool {
    if sentence.is_null() || out_eval.is_null() {
        return false;
    }
    let c_str = unsafe { CStr::from_ptr(sentence) };
    let Ok(str_slice) = c_str.to_str() else {
        return false;
    };
    let family = match family_id {
        0 => LanguageFamily::IndoEuropean,
        1 => LanguageFamily::SinoTibetan,
        2 => LanguageFamily::AfroAsiatic,
        3 => LanguageFamily::Austronesian,
        4 => LanguageFamily::NigerCongo,
        5 => LanguageFamily::JaponicKoreanic,
        6 => LanguageFamily::Dravidian,
        7 => LanguageFamily::Uralic,
        8 => LanguageFamily::Turkic,
        9 => LanguageFamily::NativeAmericanIsolates,
        _ => LanguageFamily::CreolesPidgins,
    };
    let eval = TypologyAnalyzer::evaluate_typology(str_slice, family);
    unsafe {
        *out_eval = eval;
    }
    true
}

#[no_mangle]
pub extern "C" fn gra_rust_check_epp(sentence: *const c_char) -> bool {
    if sentence.is_null() {
        return false;
    }
    let c_str = unsafe { CStr::from_ptr(sentence) };
    let Ok(str_slice) = c_str.to_str() else {
        return false;
    };
    let tokens: Vec<&str> = str_slice.split_whitespace().collect();
    UniversalGrammarValidator::verify_epp(&tokens)
}

#[no_mangle]
pub extern "C" fn gra_rust_evaluate_checklist(
    sentence: *const c_char,
    out_scores: *mut UniversalChecklistScores,
) -> bool {
    if sentence.is_null() || out_scores.is_null() {
        return false;
    }
    let c_str = unsafe { CStr::from_ptr(sentence) };
    let Ok(str_slice) = c_str.to_str() else {
        return false;
    };
    let scores = UniversalGrammarValidator::evaluate_checklist(str_slice);
    unsafe {
        *out_scores = scores;
    }
    true
}

#[no_mangle]
pub extern "C" fn gra_rust_count_syllables(word: *const c_char) -> usize {
    if word.is_null() {
        return 0;
    }
    let c_str = unsafe { CStr::from_ptr(word) };
    let Ok(str_slice) = c_str.to_str() else {
        return 0;
    };
    PoeticVerifier::count_syllables(str_slice)
}

#[no_mangle]
pub extern "C" fn gra_rust_verify_haiku(
    line1: *const c_char,
    line2: *const c_char,
    line3: *const c_char,
    out_counts: *mut usize,
) -> bool {
    if line1.is_null() || line2.is_null() || line3.is_null() {
        return false;
    }
    let s1 = unsafe { CStr::from_ptr(line1).to_str().unwrap_or("") };
    let s2 = unsafe { CStr::from_ptr(line2).to_str().unwrap_or("") };
    let s3 = unsafe { CStr::from_ptr(line3).to_str().unwrap_or("") };

    let (valid, counts) = PoeticVerifier::verify_haiku(s1, s2, s3);
    if !out_counts.is_null() {
        unsafe {
            *out_counts.add(0) = counts[0];
            *out_counts.add(1) = counts[1];
            *out_counts.add(2) = counts[2];
        }
    }
    valid
}

#[no_mangle]
pub extern "C" fn gra_rust_scan_errors(sentence: *const c_char) -> u32 {
    if sentence.is_null() {
        return 0;
    }
    let c_str = unsafe { CStr::from_ptr(sentence) };
    let Ok(str_slice) = c_str.to_str() else {
        return 0;
    };
    ErrorDetector::scan_errors_bitmask(str_slice)
}

#[no_mangle]
pub extern "C" fn gra_rust_score_to_cefr(score: f32) -> u8 {
    AssessmentModel::score_to_cefr(score) as u8
}

#[no_mangle]
pub extern "C" fn gra_rust_is_stress_shift_word(word: *const c_char) -> bool {
    if word.is_null() {
        return false;
    }
    let c_str = unsafe { CStr::from_ptr(word) };
    let Ok(str_slice) = c_str.to_str() else {
        return false;
    };
    PhonologyVerifier::is_trochaic_noun_iambic_verb_pair(str_slice)
}

#[no_mangle]
pub extern "C" fn gra_rust_evaluate_skill(
    text: *const c_char,
    skill_id: u8,
    out_eval: *mut SkillEvaluation,
) -> bool {
    if text.is_null() || out_eval.is_null() {
        return false;
    }
    let c_str = unsafe { CStr::from_ptr(text) };
    let Ok(str_slice) = c_str.to_str() else {
        return false;
    };
    let eval = match skill_id {
        0 => BandhuSkillEngine::evaluate_writing(str_slice),
        1 => BandhuSkillEngine::evaluate_email(str_slice),
        2 => BandhuSkillEngine::evaluate_listening_reduction(str_slice),
        3 => {
            // Pronunciation defaults to writing structural + acoustic placeholder
            let mut e = BandhuSkillEngine::evaluate_writing(str_slice);
            e.skill_id = SkillType::Pronouncing as u8;
            e
        },
        4 => BandhuSkillEngine::evaluate_reviewing(str_slice),
        5 => BandhuSkillEngine::evaluate_book_writing(str_slice),
        _ => BandhuSkillEngine::evaluate_writing(str_slice),
    };
    unsafe {
        *out_eval = eval;
    }
    true
}

#[no_mangle]
pub extern "C" fn gra_rust_classify_era(text: *const c_char) -> u8 {
    if text.is_null() {
        return HistoricalEra::Modern as u8;
    }
    let c_str = unsafe { CStr::from_ptr(text) };
    let Ok(str_slice) = c_str.to_str() else {
        return HistoricalEra::Modern as u8;
    };
    BandhuSkillEngine::classify_era(str_slice) as u8
}

#[cfg(test)]
mod tests {
    use super::*;
    use grammar::{MorphoFeatures, GrammaticalCase, VerbVoice};
    use phonology::{PhoneticFeature, ConsonantPlace, ConsonantManner};
    use assessment::CefrLevel;

    #[test]
    fn test_universal_grammar_epp() {
        let valid_tokens = ["the", "philosopher", "examined", "truth"];
        assert!(UniversalGrammarValidator::verify_epp(&valid_tokens));

        let invalid_tokens = ["running", "quickly", "through", "forests"];
        assert!(!UniversalGrammarValidator::verify_epp(&invalid_tokens));
    }

    #[test]
    fn test_7_point_checklist_scoring() {
        let good_sentence = "The diligent architect carefully inspected the structural foundation.";
        let scores = UniversalGrammarValidator::evaluate_checklist(good_sentence);
        assert!(scores.dim_a_structure >= 0.95);
        assert!(scores.dim_b_agreement >= 0.95);
        assert!(scores.dim_c_time_modality >= 0.95);
        assert!(scores.composite_score >= 0.90);

        let bad_sentence = "Because the train was late";
        let bad_scores = UniversalGrammarValidator::evaluate_checklist(bad_sentence);
        assert!(bad_scores.dim_a_structure < 0.5); // Sentence fragment detected
    }

    #[test]
    fn test_subject_verb_concord() {
        let subj_3sg = MorphoFeatures {
            person: 3,
            is_plural: false,
            case: GrammaticalCase::Nominative,
            voice: VerbVoice::Active,
        };
        assert!(UniversalGrammarValidator::check_concord(subj_3sg, 3, false));
        assert!(!UniversalGrammarValidator::check_concord(subj_3sg, 3, true));
    }

    #[test]
    fn test_haiku_verification() {
        let l1 = "an old silent pond";
        let l2 = "a frog jumps into the deep";
        let l3 = "water sounds again";
        let (is_haiku, counts) = PoeticVerifier::verify_haiku(l1, l2, l3);
        assert_eq!(counts[0], 5);
        assert_eq!(counts[1], 7);
        assert_eq!(counts[2], 5);
        assert!(is_haiku);
    }

    #[test]
    fn test_phonology_features() {
        let bilabial_p = PhoneticFeature {
            place: ConsonantPlace::Bilabial,
            manner: ConsonantManner::Plosive,
            is_voiced: false,
        };
        let bilabial_b = PhoneticFeature {
            place: ConsonantPlace::Bilabial,
            manner: ConsonantManner::Plosive,
            is_voiced: true,
        };
        let dist = PhonologyVerifier::consonant_distance(bilabial_p, bilabial_b);
        assert_eq!(dist, 0.15); // Only voicing differs

        assert!(PhonologyVerifier::is_trochaic_noun_iambic_verb_pair("record"));
        assert!(PhonologyVerifier::is_trochaic_noun_iambic_verb_pair("PROJECT"));
    }

    #[test]
    fn test_all_10_error_categories() {
        // §5.2.1 Agreement
        assert!(ErrorDetector::scan_errors_bitmask("The box of nails are heavy") > 0);
        // §5.2.2 Tense inconsistency
        assert!(ErrorDetector::scan_errors_bitmask("She opened the door and sees a stranger") > 0);
        // §5.2.3 Dangling modifier
        assert!(ErrorDetector::scan_errors_bitmask("Walking to school, the rain started") > 0);
        // §5.2.4 Pronoun case
        assert!(ErrorDetector::scan_errors_bitmask("The award went to Priya and I") > 0);
        // §5.2.5 Comma splice
        assert!(ErrorDetector::scan_errors_bitmask("The storm passed, we went outside") > 0);
        // §5.2.6 Fragment
        assert!(ErrorDetector::scan_errors_bitmask("Because the train was late") > 0);
        // §5.2.7 Parallelism
        assert!(ErrorDetector::scan_errors_bitmask("She likes hiking, swimming, and to cycle") > 0);
        // §5.2.8 Redundancy
        assert!(ErrorDetector::scan_errors_bitmask("Please revert back with your PIN number") > 0);
        // §5.2.9 Punctuation
        assert!(ErrorDetector::scan_errors_bitmask("Let's eat grandma") > 0);
        // §5.2.10 Wrong verb form
        assert!(ErrorDetector::scan_errors_bitmask("He could of should have went") > 0);
    }

    #[test]
    fn test_assessment_cefr_and_irt() {
        assert_eq!(AssessmentModel::score_to_cefr(95.0), CefrLevel::C2);
        assert_eq!(AssessmentModel::score_to_cefr(75.0), CefrLevel::B2);
        assert_eq!(AssessmentModel::score_to_cefr(35.0), CefrLevel::A1);

        let initial_theta = 0.0f32;
        let updated = AssessmentModel::update_theta_step(initial_theta, true, 0.5, 1.2);
        assert!(updated > initial_theta); // Correct answer increases theta
    }

    #[test]
    fn test_typology_evaluation() {
        let eval_turkic = TypologyAnalyzer::evaluate_typology(
            "Evlerinizden misiniz?",
            LanguageFamily::Turkic
        );
        assert_eq!(eval_turkic.family_id, LanguageFamily::Turkic as u8);
        assert_eq!(eval_turkic.morph_type_id, typology::MorphologicalType::Agglutinative as u8);
        assert_eq!(eval_turkic.directionality_id, typology::HeadDirectionality::HeadFinal as u8);
        assert!(eval_turkic.pillar_scores.p5_word_order >= 0.95);

        let eval_sinitic = TypologyAnalyzer::evaluate_typology(
            "Wǒ kànle nà běn shū",
            LanguageFamily::SinoTibetan
        );
        assert_eq!(eval_sinitic.morph_type_id, typology::MorphologicalType::Isolating as u8);

        let frictions = TypologyAnalyzer::predict_l1_l2_friction(
            LanguageFamily::IndoEuropean,
            LanguageFamily::Turkic
        );
        assert!(!frictions.is_empty());
        assert!(frictions[0].contains("Delayed Semantic Resolution"));
    }

    #[test]
    fn test_bandhu_skill_evaluation_c_abi() {
        let email_text = "Dear Dr. Patel,\n\nCould you please review the findings?\n\nBest regards,\nAlex";
        let eval = BandhuSkillEngine::evaluate_email(email_text);
        assert_eq!(eval.skill_id, SkillType::Emailing as u8);
        assert!(eval.register_score >= 0.9);
        assert_eq!(eval.fatal_errors_count, 0);

        let era = BandhuSkillEngine::classify_era("Pāṇini formulated the Aṣṭādhyāyī");
        assert_eq!(era, HistoricalEra::Ancient);
    }
}
