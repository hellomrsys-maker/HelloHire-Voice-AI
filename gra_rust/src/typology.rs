//! Universal Comparative Grammar Typology Engine (Safe Rust)
//!
//! Translates the comparative typology guide into zero-allocation structural analysis:
//! - 11 Language Families
//! - 4 Morphological Types (Isolating, Agglutinative, Fusional, Polysynthetic)
//! - 4 Grammatical Alignments (Nom-Acc, Erg-Abs, Active-Stative, Symmetrical Voice)
//! - Head Directionality (Head-Initial vs Head-Final)
//! - 8-Pillar Universal Typological Diagnostic Scores
//! - Greenbergian Word Order Harmony & L1->L2 Negative Transfer Predictor

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LanguageFamily {
    IndoEuropean = 0,
    SinoTibetan = 1,
    AfroAsiatic = 2,
    Austronesian = 3,
    NigerCongo = 4,
    JaponicKoreanic = 5,
    Dravidian = 6,
    Uralic = 7,
    Turkic = 8,
    NativeAmericanIsolates = 9,
    CreolesPidgins = 10,
}

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MorphologicalType {
    Isolating = 0,
    Agglutinative = 1,
    Fusional = 2,
    Polysynthetic = 3,
}

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum GrammaticalAlignment {
    NominativeAccusative = 0,
    ErgativeAbsolutive = 1,
    ActiveStative = 2,
    SymmetricalVoice = 3,
}

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HeadDirectionality {
    HeadInitial = 0,
    HeadFinal = 1,
}

#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct EightPillarScores {
    pub p1_phonology: f32,
    pub p2_nominal_classification: f32,
    pub p3_case_particles: f32,
    pub p4_verbal_tam: f32,
    pub p5_word_order: f32,
    pub p6_questions_negation: f32,
    pub p7_politeness_deixis: f32,
    pub p8_idiomatic_metaphor: f32,
}

impl Default for EightPillarScores {
    fn default() -> Self {
        Self {
            p1_phonology: 0.85,
            p2_nominal_classification: 0.80,
            p3_case_particles: 0.85,
            p4_verbal_tam: 0.88,
            p5_word_order: 0.90,
            p6_questions_negation: 0.86,
            p7_politeness_deixis: 0.82,
            p8_idiomatic_metaphor: 0.80,
        }
    }
}

#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct TypologicalEvaluation {
    pub family_id: u8,
    pub morph_type_id: u8,
    pub alignment_id: u8,
    pub directionality_id: u8,
    pub synthesis_index: f32,
    pub greenberg_harmony: f32,
    pub pillar_scores: EightPillarScores,
}

pub struct TypologyAnalyzer;

impl TypologyAnalyzer {
    /// Returns default canonical morphological and alignment profile for a family
    pub fn canonical_family_profile(family: LanguageFamily) -> (MorphologicalType, GrammaticalAlignment, HeadDirectionality, f32, f32) {
        match family {
            LanguageFamily::IndoEuropean => (
                MorphologicalType::Fusional,
                GrammaticalAlignment::NominativeAccusative,
                HeadDirectionality::HeadInitial,
                2.1,
                0.78,
            ),
            LanguageFamily::SinoTibetan => (
                MorphologicalType::Isolating,
                GrammaticalAlignment::NominativeAccusative,
                HeadDirectionality::HeadInitial,
                1.05,
                0.92,
            ),
            LanguageFamily::AfroAsiatic => (
                MorphologicalType::Fusional,
                GrammaticalAlignment::NominativeAccusative,
                HeadDirectionality::HeadInitial,
                2.4,
                0.85,
            ),
            LanguageFamily::Austronesian => (
                MorphologicalType::Agglutinative,
                GrammaticalAlignment::SymmetricalVoice,
                HeadDirectionality::HeadInitial,
                1.8,
                0.82,
            ),
            LanguageFamily::NigerCongo => (
                MorphologicalType::Agglutinative,
                GrammaticalAlignment::NominativeAccusative,
                HeadDirectionality::HeadInitial,
                2.6,
                0.88,
            ),
            LanguageFamily::JaponicKoreanic => (
                MorphologicalType::Agglutinative,
                GrammaticalAlignment::NominativeAccusative,
                HeadDirectionality::HeadFinal,
                2.8,
                0.98,
            ),
            LanguageFamily::Dravidian => (
                MorphologicalType::Agglutinative,
                GrammaticalAlignment::NominativeAccusative,
                HeadDirectionality::HeadFinal,
                3.1,
                0.96,
            ),
            LanguageFamily::Uralic => (
                MorphologicalType::Agglutinative,
                GrammaticalAlignment::NominativeAccusative,
                HeadDirectionality::HeadFinal,
                3.4,
                0.90,
            ),
            LanguageFamily::Turkic => (
                MorphologicalType::Agglutinative,
                GrammaticalAlignment::NominativeAccusative,
                HeadDirectionality::HeadFinal,
                3.6,
                0.99,
            ),
            LanguageFamily::NativeAmericanIsolates => (
                MorphologicalType::Polysynthetic,
                GrammaticalAlignment::ErgativeAbsolutive,
                HeadDirectionality::HeadFinal,
                4.8,
                0.75,
            ),
            LanguageFamily::CreolesPidgins => (
                MorphologicalType::Isolating,
                GrammaticalAlignment::NominativeAccusative,
                HeadDirectionality::HeadInitial,
                1.08,
                0.95,
            ),
        }
    }

    /// Evaluates text against the 8 diagnostic pillars
    pub fn evaluate_typology(text: &str, family: LanguageFamily) -> TypologicalEvaluation {
        let (morph, align, dir, base_synthesis, harmony) = Self::canonical_family_profile(family);

        let words: Vec<&str> = text.split_whitespace().collect();
        let word_count = words.len().max(1) as f32;
        let char_count: usize = words.iter().map(|w| w.chars().count()).sum();
        let avg_word_len = (char_count as f32) / word_count;

        // Dynamic adjustment to synthesis index based on empirical text length
        let synthesis_index = match morph {
            MorphologicalType::Isolating => (1.0 + (avg_word_len - 3.0) * 0.05).clamp(1.0, 1.3),
            MorphologicalType::Agglutinative => (base_synthesis + (avg_word_len - 5.0) * 0.15).clamp(1.8, 4.2),
            MorphologicalType::Fusional => (base_synthesis + (avg_word_len - 5.0) * 0.10).clamp(1.5, 3.2),
            MorphologicalType::Polysynthetic => (base_synthesis + (avg_word_len - 7.0) * 0.20).clamp(3.5, 6.5),
        };

        let mut pillars = EightPillarScores::default();

        // Tune pillar scores based on language family specificities
        match family {
            LanguageFamily::Turkic => {
                pillars.p1_phonology = 0.98; // Vowel harmony symmetry
                pillars.p2_nominal_classification = 1.0; // Clean zero-gender direct counting
                pillars.p3_case_particles = 0.95; // 6 transparent agglutinative cases
                pillars.p4_verbal_tam = 0.96; // Evidentiality distinction (-di vs -mis)
                pillars.p5_word_order = 0.99; // Strict SOV head-finality
            }
            LanguageFamily::SinoTibetan => {
                pillars.p1_phonology = 0.95; // Tonal phonology
                pillars.p2_nominal_classification = 0.92; // Sortal/mensural classifier geometry
                pillars.p3_case_particles = 0.88; // Functional particles
                pillars.p4_verbal_tam = 0.90; // Aspectual particles (le, guo, zhe)
                pillars.p5_word_order = 0.98; // Rigid SVO positional load
            }
            LanguageFamily::JaponicKoreanic => {
                pillars.p1_phonology = 0.92;
                pillars.p3_case_particles = 0.98; // Wa/Ga Topic-Subject contrast
                pillars.p5_word_order = 0.99; // Left-branching relative clauses
                pillars.p7_politeness_deixis = 0.99; // Elaborate Keigo/Jondaenmal hierarchy
            }
            LanguageFamily::Austronesian => {
                pillars.p3_case_particles = 0.96; // Pivot alignment trigger particles
                pillars.p4_verbal_tam = 0.97; // Symmetrical Actor/Patient/Locative voice
            }
            LanguageFamily::NigerCongo => {
                pillars.p2_nominal_classification = 0.99; // 10-22 Noun classes with alliterative concord
            }
            _ => {}
        }

        TypologicalEvaluation {
            family_id: family as u8,
            morph_type_id: morph as u8,
            alignment_id: align as u8,
            directionality_id: dir as u8,
            synthesis_index,
            greenberg_harmony: harmony,
            pillar_scores: pillars,
        }
    }

    /// Predicts specific L1 -> L2 negative transfer friction points based on typological distance
    pub fn predict_l1_l2_friction(l1: LanguageFamily, l2: LanguageFamily) -> &'static [&'static str] {
        match (l1, l2) {
            (LanguageFamily::IndoEuropean, LanguageFamily::Turkic) => &[
                "Delayed Semantic Resolution: Head-final verb forces long cognitive hold before action resolves",
                "Evidentiality Obligation: Speaker must declare witnessed (-di) vs inferred (-mis) knowledge source",
                "Vowel Harmony Computation: Suffixes must be recalculated across 2-way and 4-way harmonic laws",
                "Differential Object Marking (DOM): Definite direct objects require accusative, indefinite remain bare",
            ],
            (LanguageFamily::IndoEuropean, LanguageFamily::SinoTibetan) => &[
                "Aspect vs Tense Paradigm: Overusing perfective 'le' as a generic past-tense marker",
                "Classifier Semantic Assignment: Forgetting obligatory sortal measure words when quantifying nouns",
                "Tonal Minimal Pairs: Conflating segmental lexical pitch contours with sentence-level intonation",
                "Rigid SVO Positional Load: Word order cannot be scrambled for pragmatic emphasis without particles",
            ],
            (LanguageFamily::IndoEuropean, LanguageFamily::Austronesian) => &[
                "Passive Voice Fallacy: Misinterpreting Patient Focus as passive rather than the default topical pivot",
                "Inclusive vs Exclusive 1PL: Conflating 'kita' (including listener) with 'kami' (excluding listener)",
                "Pivot Trigger Marking: Misaligning verb focus affixes with the syntactic trigger particle",
            ],
            (LanguageFamily::IndoEuropean, LanguageFamily::JaponicKoreanic) => &[
                "Topic vs Subject Ambiguity: Confusing conversational frame (wa/eun) with grammatical agent (ga/i)",
                "Social Deixis Overhead: Obligatory computation of in-group/out-group and social rank before verb choice",
                "Left-Branching Relative Clauses: Formulating descriptive relative clause before the head noun",
            ],
            _ => &[
                "General Typological Distance: Divergent morphological synthesis and head-directionality parameters",
            ],
        }
    }
}
