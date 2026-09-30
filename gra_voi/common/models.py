"""
Linguistic Data Structures and Universal Representations.

Defines the fundamental data models, enumerations, and structural primitives
used throughout the Lingua Sapiens architecture.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class PartOfSpeech(str, Enum):
    NOUN = "noun"
    PRONOUN = "pronoun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PREPOSITION = "preposition"
    POSTPOSITION = "postposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    ARTICLE = "article"
    DETERMINER = "determiner"
    QUANTIFIER = "quantifier"
    AUXILIARY = "auxiliary"
    MODAL = "modal"
    COPULA = "copula"
    GERUND = "gerund"
    INFINITIVE = "infinitive"
    PARTICIPLE = "participle"
    PARTICLE = "particle"


class SentenceType(str, Enum):
    SIMPLE = "simple"
    COMPOUND = "compound"
    COMPLEX = "complex"
    COMPOUND_COMPLEX = "compound_complex"
    NOMINALIZED = "nominalized"
    CLEFT = "cleft"
    INVERTED = "inverted"


class WordOrder(str, Enum):
    SVO = "SVO"  # Subject - Verb - Object (English, Spanish, Mandarin, Swahili)
    SOV = "SOV"  # Subject - Object - Verb (Japanese, Korean, Hindi, Turkish, Latin)
    VSO = "VSO"  # Verb - Subject - Object (Classical Arabic, Irish, Welsh, Biblical Hebrew)
    VOS = "VOS"  # Verb - Object - Subject (Malagasy, Fijian, Tzotzil)
    OVS = "OVS"  # Object - Verb - Subject (Hixkaryana, Urarina)
    OSV = "OSV"  # Object - Subject - Verb (Warao, Xavante, poetic inversion)
    FREE = "FREE"  # Richly case-marked non-configurational (Warlpiri, Russian colloquial)


class ClauseType(str, Enum):
    INDEPENDENT = "independent"
    DEPENDENT_NOUN = "dependent_noun"
    DEPENDENT_RELATIVE = "dependent_relative"
    DEPENDENT_ADVERBIAL = "dependent_adverbial"
    NON_FINITE_PARTICIPIAL = "non_finite_participial"
    NON_FINITE_INFINITIVE = "non_finite_infinitive"
    NON_FINITE_GERUNDIVE = "non_finite_gerundive"


class PhraseType(str, Enum):
    NP = "Noun Phrase"
    VP = "Verb Phrase"
    PP = "Prepositional Phrase"
    AP = "Adjective Phrase"
    ADVP = "Adverb Phrase"
    CP = "Complementizer Phrase"
    TP = "Tense Phrase"


class GrammaticalRole(str, Enum):
    SUBJECT = "subject"
    PREDICATE = "predicate"
    DIRECT_OBJECT = "direct_object"
    INDIRECT_OBJECT = "indirect_object"
    SUBJECT_COMPLEMENT = "subject_complement"
    OBJECT_COMPLEMENT = "object_complement"
    APPOSITIVE = "appositive"
    ADJUNCT_MODIFIER = "adjunct_modifier"
    PARENTICAL = "parenthetical"


class Tense(str, Enum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class Aspect(str, Enum):
    SIMPLE = "simple"
    PROGRESSIVE = "progressive"
    PERFECT = "perfect"
    PERFECT_PROGRESSIVE = "perfect_progressive"
    HABITUAL = "habitual"
    INCEPTIVE = "inceptive"
    GNOMIC = "gnomic"


class Mood(str, Enum):
    INDICATIVE = "indicative"
    SUBJUNCTIVE = "subjunctive"
    IMPERATIVE = "imperative"
    CONDITIONAL = "conditional"
    OPTATIVE = "optative"
    DUBITATIVE = "dubitative"


class Voice(str, Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    MIDDLE = "middle"
    ANTIPASSIVE = "antipassive"
    CAUSATIVE = "causative"


class Number(str, Enum):
    SINGULAR = "singular"
    PLURAL = "plural"
    DUAL = "dual"
    PAUCAL = "paucal"


class GrammaticalCase(str, Enum):
    NOMINATIVE = "nominative"
    ACCUSATIVE = "accusative"
    GENITIVE = "genitive"
    DATIVE = "dative"
    ABLATIVE = "ablative"
    LOCATIVE = "locative"
    INSTRUMENTAL = "instrumental"
    VOCATIVE = "vocative"
    ERGATIVE = "ergative"
    ABSOLUTIVE = "absolutive"


class Register(str, Enum):
    VERY_FORMAL = "very_formal"
    FORMAL_ACADEMIC = "formal_academic"
    PROFESSIONAL = "professional"
    NEUTRAL = "neutral"
    CASUAL = "casual"
    INTIMATE = "intimate"
    ARCHAIC = "archaic"


class WritingFormat(str, Enum):
    ESSAY_ARGUMENTATIVE = "essay_argumentative"
    ESSAY_EXPOSITORY = "essay_expository"
    ACADEMIC_ABSTRACT = "academic_abstract"
    BUSINESS_EMAIL = "business_email"
    FORMAL_LETTER = "formal_letter"
    EXECUTIVE_REPORT = "executive_report"
    SUMMARY_SYNTHESIS = "summary_synthesis"
    PERSUASIVE_ORATION = "persuasive_oration"
    NARRATIVE_PROSE = "narrative_prose"


class ErrorCategory(str, Enum):
    SUBJECT_VERB_AGREEMENT = "subject_verb_agreement"
    TENSE_INCONSISTENCY = "tense_inconsistency"
    ASPECT_MISMATCH = "aspect_mismatch"
    VOICE_CONFUSION = "voice_confusion"
    PRONOUN_ANTECEDENT = "pronoun_antecedent_disagreement"
    DANGLING_MODIFIER = "dangling_or_misplaced_modifier"
    RUN_ON_SENTENCE = "run_on_sentence"
    COMMA_SPLICE = "comma_splice"
    SENTENCE_FRAGMENT = "sentence_fragment"
    FAULTY_PARALLELISM = "faulty_parallelism"
    ARTICLE_MISUSE = "article_misuse"
    PREPOSITION_ERROR = "preposition_misuse"
    CONJUNCTION_ERROR = "conjunction_error"
    PUNCTUATION_ERROR = "punctuation_error"
    CAPITALIZATION_ERROR = "capitalization_error"
    HOMOPHONE_SPELLING = "homophone_or_grammatical_spelling"
    REGISTER_MISMATCH = "register_mismatch"


@dataclass
class ExampleAnnotation:
    language: str
    target_sentence: str
    gloss: str
    translation: str
    grammatical_breakdown: str


@dataclass
class GrammarConcept:
    name: str
    category: str
    definition: str
    functional_role: str
    universal_principle: str
    annotated_examples: List[ExampleAnnotation]
    language_specific_notes: Dict[str, str] = field(default_factory=dict)
    cross_references: List[str] = field(default_factory=list)


@dataclass
class SyntacticConstituent:
    text: str
    role: GrammaticalRole
    phrase_type: PhraseType
    head_word: str
    lemma: str = ""
    part_of_speech: Optional[PartOfSpeech] = None
    case: Optional[GrammaticalCase] = None
    number: Optional[Number] = None
    children: List["SyntacticConstituent"] = field(default_factory=list)
    semantic_role: Optional[str] = None  # Agent, Patient, Experiencer, etc.
    explanation: str = ""


@dataclass
class ClauseAnalysis:
    text: str
    clause_type: ClauseType
    is_main: bool
    subject: str
    predicate: str
    complement_or_object: str = ""
    subordinating_conjunction: str = ""
    function_in_sentence: str = ""


@dataclass
class SentenceAnalysis:
    raw_text: str
    sentence_type: SentenceType
    word_order_typology: WordOrder
    constituents: List[SyntacticConstituent]
    clauses: List[ClauseAnalysis]
    deep_reasoning_explanation: str
    derivation_steps: List[str]
    syntactic_tree_ascii: str


@dataclass
class GrammarError:
    category: ErrorCategory
    start_char: int
    end_char: int
    problematic_text: str
    definition: str
    explanation: str
    rule_violated: str
    suggested_fix: str
    confidence: float = 1.0


@dataclass
class CorrectionResult:
    original_text: str
    corrected_text: str
    errors: List[GrammarError]
    pedagogical_summary: str
    step_by_step_reasoning: List[str]
    diff_view: str


@dataclass
class SyllableStructure:
    onset: str
    nucleus: str
    coda: str
    ipa: str
    is_stressed: bool


@dataclass
class PhoneticAnalysis:
    token: str
    ipa: str
    syllables: List[SyllableStructure]
    stress_pattern: str
    rhythm_type: str  # stress-timed, syllable-timed, mora-timed
    intonation_contour: str
    connected_speech_effects: List[str]
    grammatical_stress_shift_note: str = ""
    l1_mispronunciation_risks: Dict[str, str] = field(default_factory=dict)


@dataclass
class ContrastiveInsight:
    source_language: str
    target_language: str
    grammatical_domain: str
    typological_contrast: str
    positive_transfer_factors: List[str]
    negative_interference_risks: List[str]
    common_learner_errors: List[str]
    pedagogical_remediation_strategy: str


@dataclass
class AssessmentQuestion:
    question_id: str
    question_type: str  # multiple_choice, cloze, sentence_correction, transformation
    prompt: str
    target_concept: str
    cefr_level: str  # A1, A2, B1, B2, C1, C2
    options: List[str] = field(default_factory=list)
    correct_answer: str = ""
    distractor_explanations: Dict[str, str] = field(default_factory=dict)
    full_explanation: str = ""
    grammar_rule_reference: str = ""


@dataclass
class LearnerProfile:
    learner_id: str
    target_language: str
    native_language: str
    proficiency_level: str
    domain_mastery: Dict[str, float] = field(default_factory=dict)  # category -> 0.0 to 1.0
    error_frequency: Dict[str, int] = field(default_factory=dict)
    recommended_roadmap: List[str] = field(default_factory=list)


class LanguageFamilyEnum(str, Enum):
    INDO_EUROPEAN = "Indo-European"
    SINO_TIBETAN = "Sino-Tibetan"
    AFRO_ASIATIC = "Afro-Asiatic"
    AUSTRONESIAN = "Austronesian"
    NIGER_CONGO = "Niger-Congo"
    JAPONIC_KOREANIC = "Japonic/Koreanic"
    DRAVIDIAN = "Dravidian"
    URALIC = "Uralic"
    TURKIC = "Turkic"
    NATIVE_AMERICAN_ISOLATES = "Native American & Isolates"
    CREOLES_PIDGINS = "Creoles and Pidgins"


class MorphologicalTypeEnum(str, Enum):
    ISOLATING = "Isolating/Analytic"
    AGGLUTINATIVE = "Agglutinative"
    FUSIONAL = "Fusional/Inflectional"
    POLYSYNTHETIC = "Polysynthetic"


class GrammaticalAlignmentEnum(str, Enum):
    NOMINATIVE_ACCUSATIVE = "Nominative-Accusative"
    ERGATIVE_ABSOLUTIVE = "Ergative-Absolutive"
    ACTIVE_STATIVE = "Active-Stative (Split-S)"
    SYMMETRICAL_VOICE = "Symmetrical Voice (Philippine Pivot)"


class HeadDirectionalityEnum(str, Enum):
    HEAD_INITIAL = "Head-Initial (Right-Branching)"
    HEAD_FINAL = "Head-Final (Left-Branching)"


@dataclass
class TypologicalReport:
    text: str
    language_family: LanguageFamilyEnum
    morphological_type: MorphologicalTypeEnum
    grammatical_alignment: GrammaticalAlignmentEnum
    head_directionality: HeadDirectionalityEnum
    synthesis_index: float
    greenberg_harmony: float
    pillar_scores: Dict[str, float]  # P1..P8
    transfer_frictions: List[str] = field(default_factory=list)
    diagnostic_summary: str = ""

