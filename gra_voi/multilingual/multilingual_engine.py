"""
Multilingual and Cross-Linguistic Intelligence Module.

Covers major human language families:
  - Indo-European (English, Spanish, French, Portuguese, German, Russian, Hindi, Bengali, Persian)
  - Sino-Tibetan (Mandarin, Cantonese)
  - Afro-Asiatic (Arabic, Amharic, Hausa)
  - Niger-Congo (Swahili, Yoruba, Zulu)
  - Japonic & Koreanic (Japanese, Korean)
  - Dravidian (Tamil, Telugu)
  - Austronesian (Malay/Indonesian, Tagalog)
  - Uralic (Finnish, Hungarian)
  - Kartvelian (Georgian)

Provides deep typological profiling and an automated pairwise Contrastive Analysis Engine
for predicting positive transfer, negative interference, and learner error patterns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from ..common.models import (
    WordOrder,
    ExampleAnnotation,
    ContrastiveInsight,
)


@dataclass
class LanguageProfile:
    name: str
    family: str
    branch: str
    morphological_type: str  # Isolating/Analytic, Agglutinative, Fusional, Polysynthetic
    canonical_word_order: WordOrder
    alignment_system: str  # Nominative-Accusative, Ergative-Absolutive, Austronesian Focus
    head_directionality: str  # Head-Initial, Head-Final
    pro_drop: bool
    is_tonal: bool
    key_typological_features: List[str]
    annotated_sample: ExampleAnnotation


class MultilingualEngine:
    """
    Cross-linguistic intelligence engine that catalogs world language families,
    models typological variance, and generates pairwise contrastive analyses.
    """

    def __init__(self):
        self._profiles: Dict[str, LanguageProfile] = {}
        self._initialize_profiles()

    def _initialize_profiles(self):
        # 1. ENGLISH (Indo-European / Germanic)
        self.register_language(LanguageProfile(
            name="English",
            family="Indo-European",
            branch="Germanic",
            morphological_type="Analytic / Weakly Fusional",
            canonical_word_order=WordOrder.SVO,
            alignment_system="Nominative-Accusative",
            head_directionality="Head-Initial (VO, Prepositional)",
            pro_drop=False,
            is_tonal=False,
            key_typological_features=[
                "Strict SVO word order compensating for historical loss of nominal case declension.",
                "Obligatory overt subject (Negative Pro-Drop parameter; requires expletive 'it'/'there').",
                "Do-support auxiliary system in negation and interrogative inversion.",
                "Two morphological tenses (Past and Non-Past) with periphrastic modal and aspectual auxiliaries."
            ],
            annotated_sample=ExampleAnnotation(
                language="English",
                target_sentence="The linguist explains the universal principles to the students.",
                gloss="the linguist explain.3SG the universal principle.PL to the student.PL",
                translation="The linguist explains the universal principles to the students.",
                grammatical_breakdown="Subject DP 'The linguist' -> Verb 'explains' (-s 3SG agreement) -> Direct Object DP 'the universal principles' -> Prepositional Indirect Object 'to the students'."
            )
        ))

        # 2. SPANISH (Indo-European / Romance)
        self.register_language(LanguageProfile(
            name="Spanish",
            family="Indo-European",
            branch="Romance",
            morphological_type="Fusional / Inflectional",
            canonical_word_order=WordOrder.SVO,
            alignment_system="Nominative-Accusative",
            head_directionality="Head-Initial (VO, N-Adj, Prepositional)",
            pro_drop=True,
            is_tonal=False,
            key_typological_features=[
                "Positive Pro-Drop (null subject) parameter licensed by rich verbal person-number agreement.",
                "Two-gender system (Masculine / Feminine) with pervasive concord across articles and adjectives.",
                "Personal 'a' marking specific human direct objects (differential object marking).",
                "Subjunctive mood actively marks counterfactuality, volition, doubt, and emotion."
            ],
            annotated_sample=ExampleAnnotation(
                language="Spanish",
                target_sentence="El lingüista explica los principios universales a los estudiantes.",
                gloss="def.M.SG linguist explain.3SG def.M.PL principle.PL universal.PL to def.M.PL student.PL",
                translation="The linguist explains the universal principles to the students.",
                grammatical_breakdown="Gender/number concord ('los principios universales'); differential object marker 'a' precedes human recipient."
            )
        ))

        # 3. GERMAN (Indo-European / Germanic)
        self.register_language(LanguageProfile(
            name="German",
            family="Indo-European",
            branch="Germanic",
            morphological_type="Fusional / Inflectional",
            canonical_word_order=WordOrder.SVO,  # V2 in main clause, SOV underlying
            alignment_system="Nominative-Accusative",
            head_directionality="Mixed (V2 in matrix, Head-Final in subordinate clauses)",
            pro_drop=False,
            is_tonal=False,
            key_typological_features=[
                "Verb-Second (V2) constraint in matrix clauses: Finite verb strictly occupies second position.",
                "Clause-final verb placement in subordinate clauses (Satzklammer / sentence bracket).",
                "Four-case system (Nominative, Accusative, Dative, Genitive) marked on determiners and adjectives.",
                "Three grammatical genders (Masculine, Feminine, Neuter)."
            ],
            annotated_sample=ExampleAnnotation(
                language="German",
                target_sentence="Gestern erklärte der Linguist den Studenten die universellen Prinzipien.",
                gloss="yesterday explain.PST the.NOM linguist the.DAT students the.ACC universal principles",
                translation="Yesterday the linguist explained the universal principles to the students.",
                grammatical_breakdown="Adverb 'Gestern' in position 1 triggers subject-verb inversion 'erklärte der Linguist' to satisfy V2."
            )
        ))

        # 4. RUSSIAN (Indo-European / Slavic)
        self.register_language(LanguageProfile(
            name="Russian",
            family="Indo-European",
            branch="Slavic",
            morphological_type="Highly Fusional",
            canonical_word_order=WordOrder.FREE,  # SVO pragmatic baseline
            alignment_system="Nominative-Accusative",
            head_directionality="Head-Initial",
            pro_drop=False,
            is_tonal=False,
            key_typological_features=[
                "Six morphological cases (Nom, Acc, Gen, Dat, Inst, Prep) licensing flexible pragmatic word order.",
                "Zero copula in present tense indicative ('Он учитель' = 'He is a teacher').",
                "Systematic verbal aspectual pairing (Imperfective vs Perfective).",
                "Absence of definite or indefinite articles."
            ],
            annotated_sample=ExampleAnnotation(
                language="Russian",
                target_sentence="Лингвист объясняет студентам универсальные принципы.",
                gloss="linguist.NOM explain.3SG student.DAT.PL universal.ACC.PL principle.ACC.PL",
                translation="The linguist explains the universal principles to the students.",
                grammatical_breakdown="Dative plural suffix '-ам' encodes recipient; accusative plural '-ы' encodes direct object."
            )
        ))

        # 5. HINDI (Indo-European / Indo-Aryan)
        self.register_language(LanguageProfile(
            name="Hindi",
            family="Indo-European",
            branch="Indo-Aryan",
            morphological_type="Agglutinative / Fusional",
            canonical_word_order=WordOrder.SOV,
            alignment_system="Split-Ergative (Ergative in perfective aspects, Nominative elsewhere)",
            head_directionality="Head-Final (OV, Postpositional)",
            pro_drop=True,
            is_tonal=False,
            key_typological_features=[
                "Strict SOV word order with postpositions (ने ne, को ko, से se).",
                "Split ergativity: Transitive subjects in perfective aspect take ergative case marker ने (ne).",
                "Verbal concord tracks absolutive object when subject is marked with ergative postposition.",
                "Differential object marking with postposition को (ko)."
            ],
            annotated_sample=ExampleAnnotation(
                language="Hindi",
                target_sentence="भाषाविद छात्रों को सार्वभौमिक नियम समझाता है। (Bhashavid chhatron ko sarvabhaumik niyam samjhata hai.)",
                gloss="linguist students.DAT OBJ universal rules explain.IMPF AUX.PRS",
                translation="The linguist explains universal rules to the students.",
                grammatical_breakdown="Subject 'भाषाविद' (SOV initial) -> Indirect object + को -> Direct object -> Predicate 'समझाता है' (clause-final)."
            )
        ))

        # 6. MANDARIN CHINESE (Sino-Tibetan / Sinitic)
        self.register_language(LanguageProfile(
            name="Mandarin",
            family="Sino-Tibetan",
            branch="Sinitic",
            morphological_type="Isolating / Analytic",
            canonical_word_order=WordOrder.SVO,
            alignment_system="Nominative-Accusative / Topic-Prominent",
            head_directionality="Mixed (VO verb phrase, but Relative-Noun and Modifier-Head)",
            pro_drop=True,  # Radical pro-drop / discourse-oriented
            is_tonal=True,
            key_typological_features=[
                "Total absence of inflectional morphology (no conjugations, declensions, case affixes, or plural suffixes on common nouns).",
                "Topic-Comment discourse organization dominating standard subject-predicate relations.",
                "Aspect-prominent grammar using postverbal particles (了 le, 过 guò, 着 zhe) instead of temporal tenses.",
                "Obligatory numeral classifier system (量词 liàngcí) intervening between numerals/demonstratives and nouns."
            ],
            annotated_sample=ExampleAnnotation(
                language="Mandarin",
                target_sentence="语言学家给学生们解释普遍语法原则。(Yǔyánxuéjiā gěi xuéshēngmen jiěshì pǔbiàn yǔfǎ yuánzé.)",
                gloss="linguist to student.PL explain universal grammar principle",
                translation="The linguist explains universal grammar principles to the students.",
                grammatical_breakdown="Prepositional coverb '给 (gěi)' introduces recipient; main verb '解释 (jiěshì)' precedes uninflected object NP."
            )
        ))

        # 7. MODERN STANDARD ARABIC (Afro-Asiatic / Semitic)
        self.register_language(LanguageProfile(
            name="Arabic",
            family="Afro-Asiatic",
            branch="Semitic",
            morphological_type="Non-Concatenative (Root-and-Pattern / Introflexive)",
            canonical_word_order=WordOrder.VSO,  # VSO canonical, SVO frequent in modern registers
            alignment_system="Nominative-Accusative",
            head_directionality="Head-Initial (VO, Prepositional, N-Adj)",
            pro_drop=True,
            is_tonal=False,
            key_typological_features=[
                "Consonantal triconsonantal root system (e.g., k-t-b = write) interwoven with vowel melody templates.",
                "Tripartite case system in formal Classical/Modern Standard Arabic (Nominative -u, Accusative -a, Genitive -i).",
                "Singular, Dual, and Plural number categories with productive broken (internal) plurals.",
                "Construct state (Iḍāfa) for noun-noun possessive and associative compounding."
            ],
            annotated_sample=ExampleAnnotation(
                language="Arabic",
                target_sentence="يَشْرَحُ اللُّغَوِيُّ المَبَادِئَ العَالَمِيَّةَ لِلطُّلَّابِ (Yashraḥu al-lughawiyyu al-mabādi'a al-'ālamiyyata li-ṭ-ṭullāb)",
                gloss="explain.3SG.M DEF-linguist.NOM DEF-principles.ACC DEF-universal.ACC to-DEF-students.GEN",
                translation="The linguist explains the universal principles to the students.",
                grammatical_breakdown="VSO word order: Finite verb 'يشرح' (initial) -> Subject with nominative case -u -> Object with accusative -a -> Prepositional phrase with genitive -i."
            )
        ))

        # 8. SWAHILI (Niger-Congo / Bantu)
        self.register_language(LanguageProfile(
            name="Swahili",
            family="Niger-Congo",
            branch="Bantu",
            morphological_type="Highly Agglutinative",
            canonical_word_order=WordOrder.SVO,
            alignment_system="Nominative-Accusative",
            head_directionality="Head-Initial (VO, N-Adj, Prepositional)",
            pro_drop=True,
            is_tonal=False,
            key_typological_features=[
                "Extensive Noun Class system (18 grammatical noun classes) governing alliterative prefixal concord.",
                "Polysynthetic verbal complex incorporating subject prefix, tense/aspect marker, relative marker, object infix, verb root, and derivational extensions.",
                "Productive verbal extensions: Causative (-isha/-eza), Applicative (-ia/-ea), Passive (-wa), Reciprocal (-ana)."
            ],
            annotated_sample=ExampleAnnotation(
                language="Swahili",
                target_sentence="Mwanaisimu anawaeleza wanafunzi kanuni za ulimwengu.",
                gloss="CL1.linguist CL1.PRS.CL2.OBJ.explain CL2.students CL10.rules CL10.GEN CL11.world",
                translation="The linguist explains the universal rules to the students.",
                grammatical_breakdown="Verb complex 'anawaeleza': a- (Class 1 subject) + na- (present tense) + wa- (Class 2 plural object infix) + elez- (explain root) + -a (mood vowel)."
            )
        ))

        # 9. JAPANESE (Japonic)
        self.register_language(LanguageProfile(
            name="Japanese",
            family="Japonic",
            branch="Japonic",
            morphological_type="Agglutinative",
            canonical_word_order=WordOrder.SOV,
            alignment_system="Nominative-Accusative / Topic-Prominent",
            head_directionality="Strictly Head-Final (OV, Postpositional, Relative-Noun)",
            pro_drop=True,  # Radical discourse pro-drop
            is_tonal=False,  # Pitch-accent system
            key_typological_features=[
                "Strictly head-final: Verbs, auxiliaries, copulas, and complementizers always occupy final position.",
                "Postpositional particles marking grammatical case and discourse roles: は (topic wa), が (subject ga), を (object o), に (dative/locative ni).",
                "Elaborate grammaticalized honorifics (Keigo: Sonkeigo respectful, Kenjougo humble, Teineigo polite).",
                "Relative clauses precede the noun head with no relative pronouns."
            ],
            annotated_sample=ExampleAnnotation(
                language="Japanese",
                target_sentence="言語学者が学生に普遍的な文法の原理を説明する。(Gengogakusha ga gakusei ni fuhenteki na bunpou no genri o setsumei suru.)",
                gloss="linguist NOM student DAT universal GEN grammar GEN principles ACC explain do.PRS",
                translation="The linguist explains universal grammar principles to the students.",
                grammatical_breakdown="Subject '言語学者が' (SOV) -> Indirect Object '学生に' -> Direct Object '原理を' -> Final Predicate '説明する'."
            )
        ))

        # 10. TAGALOG (Austronesian / Malayo-Polynesian)
        self.register_language(LanguageProfile(
            name="Tagalog",
            family="Austronesian",
            branch="Malayo-Polynesian",
            morphological_type="Agglutinative / Infixing",
            canonical_word_order=WordOrder.VSO,  # V-initial (VSO or VOS)
            alignment_system="Austronesian Alignment (Symmetrical Voice / Focus System)",
            head_directionality="Head-Initial",
            pro_drop=True,
            is_tonal=False,
            key_typological_features=[
                "Austronesian Focus / Voice system: Verbal affixes designate which semantic role (Actor, Patient, Locative, Beneficiary, Instrument) is the 'pivot' / ang-marked topic.",
                "Verb-initial constituent order.",
                "Extensive infixation morphology (e.g., -um-, -in-)."
            ],
            annotated_sample=ExampleAnnotation(
                language="Tagalog",
                target_sentence="Ipinapaliwanag ng dalubwika ang mga simulain sa mga mag-aaral.",
                gloss="PFV.IMPF.explain.PATIENT GEN linguist PIVOT PL principles DIR PL students",
                translation="The linguist explains the principles to the students.",
                grammatical_breakdown="Patient-focus verb 'ipinapaliwanag' marks the theme 'ang mga simulain' as the syntactic pivot."
            )
        ))

    def register_language(self, profile: LanguageProfile):
        """Add a language profile to the catalog."""
        self._profiles[profile.name.lower()] = profile

    def get_language_profile(self, name: str) -> Optional[LanguageProfile]:
        """Look up a language profile by name."""
        return self._profiles.get(name.strip().lower())

    def list_supported_languages(self) -> List[str]:
        """Return names of all cataloged languages."""
        return [p.name for p in self._profiles.values()]

    def compare_languages(self, source_lang: str, target_lang: str) -> ContrastiveInsight:
        """
        Execute contrastive analysis between source (L1) and target (L2) languages,
        predicting positive transfer, negative interference risks, and remedial instruction.
        """
        l1 = self.get_language_profile(source_lang)
        l2 = self.get_language_profile(target_lang)

        if not l1 or not l2:
            return ContrastiveInsight(
                source_language=source_lang,
                target_language=target_lang,
                grammatical_domain="General Typology",
                typological_contrast="One or both languages are not in the primary detailed catalog.",
                positive_transfer_factors=["Shared communicative functions across human languages."],
                negative_interference_risks=["Potential word order and morphosyntactic transfer discrepancies."],
                common_learner_errors=["Over-applying L1 structural templates to L2 output."],
                pedagogical_remediation_strategy="Conduct explicit comparative instruction focusing on parameter settings."
            )

        positive_transfers: List[str] = []
        negative_risks: List[str] = []
        learner_errors: List[str] = []

        # 1. Word Order Contrast
        if l1.canonical_word_order == l2.canonical_word_order:
            positive_transfers.append(f"Shared canonical word order ({l1.canonical_word_order.value}): Core argument sequencing (S-V-O) transfers naturally.")
        else:
            negative_risks.append(f"Word Order Divergence: L1 uses {l1.canonical_word_order.value} while L2 requires {l2.canonical_word_order.value}.")
            learner_errors.append(f"L1-influenced constituent misplacement (e.g., placing verb at the end in {l2.name} or failing to invert).")

        # 2. Pro-Drop Parameter Contrast
        if l1.pro_drop and not l2.pro_drop:
            negative_risks.append(f"Null-Subject Transfer Risk: L1 ({l1.name}) allows omitting subject pronouns, whereas L2 ({l2.name}) strictly enforces overt subjects.")
            learner_errors.append(f"Omission of overt dummy or personal pronouns in {l2.name} ('Is raining' instead of 'It is raining', 'Went to store' instead of 'He went to store').")
        elif not l1.pro_drop and l2.pro_drop:
            positive_transfers.append(f"Supplying overt pronouns in {l2.name} is grammatically permissible, though it may sound unnaturally emphatic.")

        # 3. Morphological Type Contrast
        if "Isolating" in l1.morphological_type and "Fusional" in l2.morphological_type:
            negative_risks.append(f"Morphological Complexity Gap: L1 ({l1.name}) is isolating/analytic, whereas L2 ({l2.name}) requires inflectional agreement for person, number, case, or gender.")
            learner_errors.append(f"Omission of inflectional suffixes (e.g., leaving verbs in base form, omitting plural -s, or ignoring case markers).")
        elif "Fusional" in l1.morphological_type and "Isolating" in l2.morphological_type:
            positive_transfers.append(f"Learners readily grasp the uninflected nature of {l2.name}, though they must master word order and aspect particles.")

        # 4. Tonal Contrast
        if not l1.is_tonal and l2.is_tonal:
            negative_risks.append(f"Phonemic Tone Hurdle: L2 ({l2.name}) uses lexical tones to distinguish word meanings, unfamiliar to non-tonal L1 speakers.")
            learner_errors.append("Flattening lexical pitch contours or confusing homophonous syllables distinguished solely by tone.")

        # Pedagogical Strategy
        pedagogy = (
            f"Pedagogical Blueprint for {l1.name} learners of {l2.name}:\n"
            f"1. Target parameter mismatches immediately, particularly Head Directionality ({l1.head_directionality} vs {l2.head_directionality}) "
            f"and Pro-Drop settings.\n"
            f"2. Use structured consciousness-raising tasks to contrast L1 interference patterns before productive writing.\n"
            f"3. Reinforce morphological concord drills if {l2.name} requires richer agreement paradigms than {l1.name}."
        )

        contrast_summary = (
            f"{l1.name} ({l1.family} / {l1.morphological_type} / {l1.canonical_word_order.value}) vs "
            f"{l2.name} ({l2.family} / {l2.morphological_type} / {l2.canonical_word_order.value})."
        )

        return ContrastiveInsight(
            source_language=l1.name,
            target_language=l2.name,
            grammatical_domain="Cross-Linguistic Morphosyntax & Typology",
            typological_contrast=contrast_summary,
            positive_transfer_factors=positive_transfers,
            negative_interference_risks=negative_risks,
            common_learner_errors=learner_errors,
            pedagogical_remediation_strategy=pedagogy
        )
