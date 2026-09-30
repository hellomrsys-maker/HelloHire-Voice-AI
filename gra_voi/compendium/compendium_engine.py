"""
Comprehensive Educational Grammar Document Engine.

Generates a fully self-contained, publication-grade educational grammar compendium
covering all 10 fundamental foundational pillars:
  1. Nature, Core Definition, and Universal Role of Grammar
  2. Complete Set of Universal Grammatical Building Blocks
  3. Sentence Formation, Structure, and Architecture (Written & Spoken)
  4. Grammar in Handwriting and Written Communication
  5. Universal Error Detection and Systematic Correction Methodologies
  6. Pronunciation, Phonetics, Stress, and Intonation
  7. Foundational and Non-Negotiable Grammar Rules of Human Language
  8. Cross-Linguistic Manifestations of Universal Grammar Principles
  9. The Role of Grammar in Deep Reading Comprehension
  10. Practical Verification Checklists and Mastery Frameworks.
"""

from typing import Dict, List, Optional
import os


class EducationalGrammarCompendium:
    """
    Exhaustive educational treatise generator.
    Requires no external references, network calls, or supplementary resources.
    """

    def __init__(self):
        self._chapters: Dict[int, Dict[str, str]] = {}
        self._build_chapters()

    def _build_chapters(self):
        # CHAPTER 1
        self._chapters[1] = {
            "title": "Chapter 1: The Nature, Core Definition, and Universal Role of Grammar",
            "content": """# Chapter 1: The Nature, Core Definition, and Universal Role of Grammar

## 1.1 What Grammar Is at Its Core
Grammar is the generative computational operating system of human thought. Far from being a mere arbitrary collection of etiquette rules or pedantic proscriptions against split infinitives, grammar is the biological and cognitive architecture that enables finite minds to produce and comprehend an infinite variety of meaningful expressions (Humboldt's principle of 'infinite use of finite means').

At its ontological core, grammar consists of four interconnected systems:
1. **Phonology & Morphology**: The combinatorial rules governing how discrete sound units (phonemes) combine into minimal meaningful units (morphemes), and how morphemes combine into words.
2. **Syntax**: The hierarchical rules of constituent assembly (Merge and Move) that structure words into phrases, clauses, and sentences.
3. **Semantics**: The compositional mapping that assigns truth conditions, thematic roles, and conceptual propositions to syntactic trees.
4. **Pragmatics**: The rules governing how context, speaker intention, and communicative conventions modulate literal meaning into active speech acts.

## 1.2 Why Every Human Language Has a Grammar System
No human language is 'primitive', 'grammarless', or 'unstructured'. Every natural spoken and signed language developed by human communities possesses a fully articulated, highly intricate grammatical system. 

Language exists to solve the fundamental problem of information transmission across physical space: human beings cannot directly transmit neural activations from brain to brain. Instead, complex conceptual structures must be serialized into a linear acoustic or visual medium (speech, sign, or text). Grammar is the universal mathematical codec that enables this serialization and subsequent reconstruction without catastrophic loss of meaning.

## 1.3 The Dual Truth: Universal Principles vs Parametric Diversity
Human languages display a profound dialectic between underlying structural unity and surface typological diversity:
- **Universal Grammar (UG)**: All human languages share invariant principles. Every language distinguishes predicates from arguments, organizes sentences hierarchically rather than as flat linear chains, possesses mechanisms for negation, interrogation, and recursion, and constrains syntactic movement through island conditions.
- **Parametric Variation**: Where languages differ, they do so not randomly, but along binary or constrained parameters. For example:
  - *Head-Directionality Parameter*: Does a governing head precede its complement (English VO: 'eat bread') or follow it (Japanese OV: 'pan o taberu')?
  - *Null-Subject (Pro-Drop) Parameter*: Can a finite clause omit an overt pronominal subject when verb agreement is rich (Spanish 'Hablo' vs English 'I speak')?
  - *Morphological Typology*: Does a language express relations through bound inflectional affixes (synthetic/fusional), chains of invariant morphemes (agglutinative), or rigid word order without affixes (isolating/analytic)?

Understanding this universal architecture liberates the language learner: learning a new language is not learning to think anew, but adjusting the parametric switches of our shared universal linguistic heritage."""
        }

        # CHAPTER 2
        self._chapters[2] = {
            "title": "Chapter 2: The Complete Set of Grammatical Building Blocks Across Languages",
            "content": """# Chapter 2: The Complete Set of Grammatical Building Blocks Across Languages

## 2.1 The Major Word Classes (Parts of Speech)
Across world languages, words fall into syntactic categories based on their distribution and functional projection:

### 1. Nouns and Noun Phrases (NP/DP)
- **Definition**: Denotes entities, objects, substances, individuals, locations, and abstract notions.
- **Subclasses**: Common vs Proper, Concrete vs Abstract, Countable vs Mass/Uncountable, Collective.
- **Universal Function**: Serves as the argument head for subjects, direct objects, indirect objects, and prepositional complements.
- **Cross-Linguistic Realization**: Marked for Case in Russian and Latin; marked for Noun Class (1-18) in Bantu languages like Swahili; marked by numeral classifiers in Sino-Tibetan and Austronesian languages.

### 2. Pronouns (Pro-Forms)
- **Definition**: Closed-class elements substituting for DPs, deriving reference from context or antecedent.
- **Subclasses**: Personal (I, you, they), Demonstrative (this, that), Relative (who, which, that), Interrogative (who, what), Reflexive (myself, herself), Reciprocal (each other), Indefinite (someone, none), Expletive/Dummy (it, there).
- **Universal Constraint**: Governed universally by Binding Principles A, B, and C.

### 3. Verbs and Verb Phrases (VP)
- **Definition**: Lexical heads encoding events, states, actions, and processes.
- **Valency & Argument Structure**: Intransitive (1 argument), Transitive (2 arguments: Agent + Patient), Ditransitive (3 arguments: Agent + Theme + Recipient), Copular (Subject + Attribute).
- **Auxiliaries and Modals**: Functional verbal heads encoding Tense, Aspect, Mood, and Epistemic/Deontic force.

### 4. Adjectives and Adjective Phrases (AP)
- **Definition**: Modifiers attributing qualities or states to nouns.
- **Distribution**: Attributive (inside NP: 'the swift runner') vs Predicative (governed by copula: 'the runner is swift').
- **Cross-Linguistic Note**: In languages like Korean and Igbo, adjectival concepts behave morphosyntactically as stative verbs.

### 5. Adverbs and Adverbial Phrases (AdvP)
- **Definition**: Modifiers qualifying verbs, adjectives, other adverbs, or entire propositions.
- **Categories**: Manner (swiftly), Temporal (now, yesterday), Locative (here, abroad), Degree (extremely), Modal/Sentence (perhaps, undeniably).

### 6. Adpositions (Prepositions, Postpositions, Circumpositions)
- **Definition**: Functional heads relating a nominal complement to a governing predicate in space, time, or logic.
- **Typological Correlation**: Head-initial languages feature Prepositions (English 'in the room', Spanish 'en la sala'); head-final languages feature Postpositions (Japanese 'heya de', Turkish 'evde').

### 7. Conjunctions
- **Coordinating**: Links syntactically equivalent units (and, but, or, nor, for, yet, so).
- **Subordinating**: Embeds a dependent clause into a matrix clause (because, although, if, while, since).
- **Correlative**: Paired connectives enforcing structural symmetry (either...or, neither...nor, not only...but also).

### 8. Determiners, Articles, and Quantifiers
- **Articles**: Definite (identifiable/unique referent: 'the') vs Indefinite (non-specific/novel referent: 'a/an') vs Partitive.
- **Quantifiers**: Universal (all, every), Existential (some, a), Proportional (most, few).

## 2.2 Morphosyntactic Features and Categories
1. **Tense**: Temporal anchoring of event time relative to speech time (Past, Present, Future).
2. **Aspect**: Internal temporal contour of the event (Perfective = completed whole; Imperfective/Progressive = ongoing process; Habitual = recurring state).
3. **Mood & Modality**: Epistemic certainty vs Deontic necessity vs Subjunctive counterfactuality.
4. **Voice & Diathesis**: Active (Agent in subject position) vs Passive (Patient promoted to subject; Agent demoted or deleted) vs Middle (subject undergoes action upon self).
5. **Number**: Singular, Plural, Dual (marking exactly two), Paucal (marking a few).
6. **Gender & Noun Classes**: Grammatical sorting of nominals triggering concord across determiners and predicates.
7. **Case**: Grammatical tagging of nominal roles (Nominative, Accusative, Genitive, Dative, Ablative, Instrumental, Locative, Ergative, Absolutive)."""
        }

        # CHAPTER 3
        self._chapters[3] = {
            "title": "Chapter 3: Sentence Formation, Structure, and Architecture in Written and Spoken Language",
            "content": """# Chapter 3: Sentence Formation, Structure, and Architecture

## 3.1 Sentence Taxonomies by Clausal Complexity
Every sentence in natural language is built from independent and dependent clauses:
1. **Simple Sentence**: Contains a single independent clause with a finite predicate:
   *Example*: 'The astronomer calculated the orbital trajectory.'
2. **Compound Sentence**: Contains two or more independent clauses joined paratactically by coordinating conjunctions or semicolons:
   *Example*: 'The laboratory recorded the seismic anomaly, but the analysis was delayed.'
3. **Complex Sentence**: Contains one matrix independent clause governing one or more dependent subordinate clauses:
   *Example*: 'Although the hypothesis was contentious, empirical trials substantiated its validity.'
4. **Compound-Complex Sentence**: Combines multiple independent clauses with at least one dependent clause:
   *Example*: 'Because the power grid collapsed, the servers shut down, and the telemetry was interrupted.'
5. **Cleft Sentences**: Divides a single proposition into two clauses to focalize an argument:
   *It-Cleft*: 'It was the sensor that failed.'
   *Wh-Cleft / Pseudo-Cleft*: 'What we discovered was an anomalous thermal reading.'

## 3.2 Universal Functional Components
- **Subject**: The external argument occupying the specifier position, triggering agreement.
- **Predicate**: The verb phrase asserting an event, state, or property of the subject.
- **Direct Object**: The internal argument receiving the direct action of a transitive verb.
- **Indirect Object**: The recipient, benefactive, or goal of a ditransitive action.
- **Subject / Object Complement**: Nominal or adjectival phrase completing the predicate after a copular or linking verb ('He became president'; 'They painted the house green').
- **Appositive**: A nominal phrase placed adjacent to another noun to explain or rename it ('Dr. Ellis, the chief researcher, arrived').
- **Adjunct Modifier**: Optional circumstantial elements specifying time, place, manner, or reason.

## 3.3 Word Order Typologies of the World
Human languages systematically order Subject (S), Verb (V), and Object (O):
- **SVO (42% of languages)**: English, Spanish, Mandarin, Swahili, Russian.
- **SOV (45% of languages)**: Japanese, Korean, Hindi, Turkish, Latin.
- **VSO (9% of languages)**: Classical Arabic, Irish, Welsh, Biblical Hebrew.
- **VOS (3% of languages)**: Malagasy, Fijian, Tzotzil.
- **OVS (<1% of languages)**: Hixkaryana, Urarina.
- **OSV (<1% of languages)**: Warao, Xavante.

## 3.4 Spoken vs Written Sentence Architecture
Spoken grammar differs fundamentally from written grammar due to real-time cognitive constraints:
- **Heads (Left-Dislocation)**: 'That professor, she is brilliant.' (Sets the cognitive topic first).
- **Tails (Right-Dislocation)**: 'It's breathtaking, that mountain range.' (Adds an clarifying noun phrase post-hoc).
- **Situational Ellipsis**: Omits predictable elements ('Got time?', 'Looks fine').
- **Disfluency and Repair**: Self-correction and hesitation fillers ('um', 'uh') that regulate cognitive turn-taking."""
        }

        # CHAPTER 4
        self._chapters[4] = {
            "title": "Chapter 4: Grammar in Handwriting and All Forms of Written Communication",
            "content": """# Chapter 4: Grammar in Handwriting and Written Communication

## 4.1 The Cognitive Demands of Written Discourse
Unlike spoken discourse, which is enriched by gestures, facial expressions, and immediate interactive feedback, written communication is autonomous. The text must construct its own context, resolve potential ambiguities through explicit syntax, and guide the reader's attention through structural signposts.

In handwriting, orthographic legibility, capitalization of proper nouns, and precise punctuation boundaries substitute for vocal pauses and prosodic pitch contours.

## 4.2 Structural Frameworks for Major Written Genres

### 1. The Academic Essay
- **Introduction**: General thematic context -> Narrowing theoretical problem -> Explicit, defensible Thesis Statement.
- **Body Paragraphs (PEEL / TEEC)**:
  - *Point*: Topic sentence stating the paragraph's central sub-claim.
  - *Evidence*: Empirical citation, textual quote, or factual proof.
  - *Explanation*: Critical analytical interpretation showing *why* the evidence supports the point.
  - *Link*: Synthesis returning to the overarching thesis.
- **Conclusion**: Restatement of synthesized thesis -> Broad theoretical or civilizational implication.

### 2. The Professional Business Email
- **Subject Line**: Categorized, actionable summary ('[APPROVAL NEEDED] Q3 Budget Revision').
- **Salutation**: Appropriate register ('Dear Director Vance,').
- **BLUF (Bottom Line Up Front)**: First sentence clearly states the purpose and desired outcome.
- **Key Takeaways**: Syntactically parallel bullet points to facilitate executive scanning.
- **Action Items & Deadlines**: Concrete identification of responsible owners and dates.

### 3. The Formal Letter and Analytical Report
- **Executive Summary**: Standalone summary providing immediate strategic decision-making context.
- **Methodology & Findings**: Declarative, impersonal syntax prioritizing active evidence over passive evasion.
- **Strategic Recommendations**: Categorized modal imperatives (must vs should vs may).

## 4.3 Cohesion and Coherence Strategies
- **Theme-Rheme Progression**: Introduce known information in the subject position (Theme), and new information in the predicate (Rheme). The new information becomes the known theme of the subsequent sentence.
- **Transitional Signposts**:
  - *Contrast*: However, Nevertheless, Conversely, On the contrary.
  - *Causation*: Consequently, Therefore, Hence, Accordingly.
  - *Concession*: Although, Granted that, Notwithstanding.
  - *Addition*: Furthermore, Moreover, In tandem with."""
        }

        # CHAPTER 5
        self._chapters[5] = {
            "title": "Chapter 5: How to Detect and Correct Grammatical Errors: A Systematic Guide",
            "content": """# Chapter 5: How to Detect and Correct Grammatical Errors

## 5.1 The Systematic Error Diagnostic Algorithm
To detect and correct errors in any passage of text, apply the five-stage verification pipeline:
1. **Sentence Boundary Scan**: Check for run-on sentences, comma splices, and fragments. Verify that every sentence has at least one independent finite clause.
2. **Subject-Predicate Alignment Scan**: Strip all intervening prepositional phrases and relative clauses; verify that the singular/plural feature of the head noun matches the finite verb.
3. **Tense and Aspect Sequence Scan**: Check whether shifts between past, present, and future are semantically justified or accidental temporal drifts.
4. **Modifier Attachment Scan**: Inspect all introductory participial phrases (-ing, -ed) to ensure that the immediately following subject noun is the true logical agent.
5. **Reference & Agreement Scan**: Verify that all pronouns agree in person, number, and gender with an unambiguous antecedent.

## 5.2 The 10 Most Critical Grammatical Errors and Step-by-Step Corrections

### 1. Subject-Verb Agreement with Intervening Phrases
- *Error*: 'The bundle of ancient manuscripts were damaged by water.'
- *Identification*: The plural noun 'manuscripts' is inside a prepositional adjunct. The true subject head is singular 'bundle'.
- *Correction*: 'The bundle of ancient manuscripts **was** damaged by water.'

### 2. Comma Splices
- *Error*: 'The experiment failed, the data was discarded.'
- *Identification*: Two independent clauses are joined solely by a comma.
- *Correction*: 'The experiment failed**;** the data was discarded.' (or: 'The experiment failed**, so** the data was discarded.')

### 3. Dangling Modifiers
- *Error*: 'Walking into the laboratory, the smell of sulfur hit Dr. Aris.'
- *Identification*: 'The smell of sulfur' is the grammatical subject, but a smell cannot walk.
- *Correction*: 'Walking into the laboratory, **Dr. Aris smelled** sulfur.'

### 4. Faulty Parallelism
- *Error*: 'She likes researching, analyzing, and to present.'
- *Identification*: Two gerunds (-ing) are coordinated with an infinitive (to + verb).
- *Correction*: 'She likes researching, analyzing, and **presenting**.'

### 5. Stative Verbs in Progressive Aspect
- *Error*: 'I am believing that your calculation is correct.'
- *Identification*: 'Believe' is a stative cognitive verb lacking dynamic progression.
- *Correction*: 'I **believe** that your calculation is correct.'

### 6. Homophone and Grammatical Spelling Confusion
- *Error*: 'Their going to see if the policy will effect there budget.'
- *Correction*: '**They're** going to see if the policy will **affect their** budget.'

### 7. Sentence Fragments
- *Error*: 'Because the archive was locked.'
- *Correction*: '**The researchers were delayed** because the archive was locked.'

### 8. Unpaired Correlatives
- *Error*: 'Neither the teacher or the student was informed.'
- *Correction*: 'Neither the teacher **nor** the student was informed.'

### 9. Article Phonetics ('a' vs 'an')
- *Error*: 'An university degree is a honest achievement.'
- *Correction*: '**A** university degree (phonetic /j/) is **an** honest achievement (silent h, vowel /ɒ/).'

### 10. Register Mismatches
- *Error*: 'The results ain't valid and we gonna need more tests.'
- *Correction*: 'The results **are not** valid, and we **will require** additional tests.'"""
        }

        # CHAPTER 6
        self._chapters[6] = {
            "title": "Chapter 6: Pronunciation, Phonetics, Stress, and Intonation",
            "content": """# Chapter 6: Pronunciation, Phonetics, Stress, and Intonation

## 6.1 The Architecture of Speech Sounds (Phonetics and Phonology)
Spoken language is constructed from discrete articulatory gestures:
- **Consonants**: Defined by Place of Articulation (Bilabial, Labiodental, Interdental, Alveolar, Velar, Glottal), Manner of Articulation (Plosive/Stop, Fricative, Affricate, Nasal, Liquid, Glide), and Voicing (Voiced vs Voiceless vocal fold vibration).
- **Vowels**: Defined by Tongue Height (High, Mid, Low), Tongue Backness (Front, Central, Back), Lip Rounding (Rounded vs Unrounded), and Tenseness/Length.

## 6.2 Syllable Anatomy and the Sonority Sequencing Principle
Every syllable comprises:
- **Onset**: Initial consonant(s).
- **Rhyme**:
  - **Nucleus**: The central acoustic peak of sonority (almost always a vowel).
  - **Coda**: Closing consonant(s).

*Universal Rule*: Sonority must rise from onset toward the nucleus and fall from the nucleus toward the coda (Sonority Sequencing Principle).

## 6.3 Prosody: Stress and Rhythm
1. **Lexical Word Stress**: Stressed syllables are louder, longer, higher in pitch, and feature full vowel quality.
2. **Grammatical Stress Shift**: In English, stress position systematically changes word class:
   - *Noun (Trochaic)*: /ˈrɛkərd/ (record), /ˈɒbdʒɪkt/ (object), /ˈprɛzənt/ (present).
   - *Verb (Iambic)*: /rɪˈkɔːrd/ (record), /əbˈdʒɛkt/ (object), /prɪˈzɛnt/ (present).
3. **Rhythm Typology**:
   - *Stress-Timed (English, German, Russian)*: Time between stressed syllables is constant; unstressed syllables undergo vowel reduction to schwa [ə].
   - *Syllable-Timed (Spanish, French, Italian)*: Every syllable takes equal time; vowels do not reduce to schwa.
   - *Mora-Timed (Japanese)*: Syllables are parsed into equal timing sub-units (morae).

## 6.4 Connected Speech Processes
In natural continuous speech, sounds interact across word boundaries:
- **Assimilation**: Sounds adapt to neighboring sounds ('ten boys' -> [tɛm bɔɪz]).
- **Elision**: Deletion of weak sounds in clusters ('next door' -> [nɛks dɔː]).
- **Liaison**: Insertion of transitional glides (/j/, /w/) or linking /r/.
- **Flapping**: Tapping of intervocalic /t/ and /d/ to voiced alveolar tap [ɾ] in American English ('water' -> [ˈwɑːɾər]).

## 6.5 Tone Systems Across World Languages
- **Contour Tonal Systems (Mandarin, Cantonese, Vietnamese)**: Syllables carry intrinsic pitch movements (Level, Rising, Dipping, Falling) that change lexical meaning entirely.
- **Register Tonal Systems (Yoruba, Igbo)**: Discrete level pitches (High, Mid, Low) that encode grammatical relations and verbal aspect."""
        }

        # CHAPTER 7
        self._chapters[7] = {
            "title": "Chapter 7: The Foundational and Non-Negotiable Grammar Rules of Human Language",
            "content": """# Chapter 7: Foundational and Non-Negotiable Grammar Rules

Across all languages and dialects, certain architectural principles are non-negotiable for intelligible communication:

## 1. The Extended Projection Principle (The Clause Mandate)
Every complete clause must possess an overt or covert Subject and a Predicate. Even in pro-drop languages where pronouns are phonologically null, the subject exists in the mental syntax and triggers agreement.

## 2. The Theta-Criterion (Argument Saturation)
Every predicate assigns a specific number of thematic roles (Agent, Patient, Experiencer), and every required role must be filled by exactly one argument DP. A transitive verb cannot discard its object without changing voice, nor can random nominals be added without adpositions.

## 3. Structural Dependency over Linear Sequence
All grammatical transformations operate on hierarchical constituent trees, never on serial word counts. When inverting an auxiliary for a question, the speaker must invert the *matrix clause* auxiliary, not the linearly first auxiliary.

## 4. The Principle of Endocentricity (Phrase Structure)
Every syntactic phrase must possess a unique categorical head that determines the properties of the whole phrase. A Noun Phrase is governed by a Noun; a Verb Phrase is governed by a Verb.

## 5. Island Extraction Constraints
Movement operations cannot extract words out of coordinate structures, complex noun phrases, or adjunct clauses. You cannot say: *'Who did you eat dinner and met?'

## 6. The Binding Principles
Reflexive pronouns (myself, himself) must be co-indexed and bound within their minimal clause domain (Principle A). Standard pronouns (he, him) must remain free in that domain (Principle B). Referential names must be free everywhere (Principle C)."""
        }

        # CHAPTER 8
        self._chapters[8] = {
            "title": "Chapter 8: Cross-Linguistic Manifestations of Universal Grammar Principles",
            "content": """# Chapter 8: Cross-Linguistic Manifestations of Universal Principles

To appreciate the harmony of human speech, examine how the same universal conceptual relations are realized across distinct linguistic families:

## 1. Expressing Definiteness and Givenness
- **English**: Uses the overt definite article 'the' (e.g., 'The book arrived').
- **Spanish**: Uses gendered definite articles 'el/la/los/las' (e.g., 'El libro llegó').
- **Arabic**: Uses the prefixal definite article 'al-' (e.g., 'وصل الكتابُ' / Waṣala al-kitābu).
- **Russian**: Lacks articles; places definite nouns at the beginning of the sentence as the discourse theme, and indefinite nouns at the end.
- **Mandarin**: Lacks articles; relies on demonstratives (这 zhè, 那 nà) or preverbal word order to mark definiteness.

## 2. Expressing Negation
- **English**: Employs dummy auxiliary do-support ('He does not know').
- **French**: Employs discontinuous circumfixal negation in formal writing ('Il ne sait pas') and postverbal 'pas' in speech ('Il sait pas').
- **Standard Arabic**: Employs negative particles matched to tense: 'lā' (present), 'lan' (future), 'lam' (past with jussive verb).
- **Japanese**: Conjugates the verb stem with the negative auxiliary suffix '-nai' ('Shiranai' = does not know).

## 3. Subject Honorifics and Social Deixis
- **English**: Expresses deference lexically via polite modals ('Would you be so kind as to...').
- **Spanish & French**: Uses T-V pronoun distinctions (Tú/Usted in Spanish; Tu/Vous in French).
- **Japanese & Korean**: Systematically inflects verb morphology (Sonkeigo, Kenjougo, Teineigo in Japanese; Hasoseo, Haeyo levels in Korean) to index social hierarchy."""
        }

        # CHAPTER 9
        self._chapters[9] = {
            "title": "Chapter 9: The Role of Grammar in Deep Reading Comprehension",
            "content": """# Chapter 9: The Role of Grammar in Deep Reading Comprehension

## 9.1 Grammar as the Key to Textual Decoding
Reading comprehension is not simply passive vocabulary recognition. Proficient readers deploy active grammatical parsing to reconstruct the author's logical architecture.

## 9.2 Critical Grammatical Cues for Reading Mastery

### 1. Identifying the Matrix Spine
In dense academic or legal prose, sentences are often laden with introductory adverbials, center-embedded relative clauses, and parenthetical interruptions. The skilled reader mentally brackets all dependent clauses to locate the **Core Subject - Matrix Verb - Core Object** spine before processing the qualifying modifiers.

### 2. Resolving Cross-Sentence Anaphora
Pronouns ('this', 'these', 'it', 'they') track referents introduced paragraphs earlier. Skilled readers use grammatical number, gender, and syntactic dominance to map pronouns back to their true nominal heads.

### 3. Interpreting Presupposition Triggers
Authors embed covert commitments into grammatical structures:
- *Factive Verbs* ('The minister acknowledged that the deficit expanded'): The author presupposes the deficit expansion as an objective fact.
- *Iterative Markers* ('The committee failed again'): Presupposes at least one prior documented failure.
- *Cleft Sentences* ('It was the treasury that authorized the transfer'): Presupposes that an authorization occurred, focusing solely on the identity of the agent.

### 4. Navigating Syntactic Ambiguity and Garden Paths
In sentences like *'The horse raced past the barn fell'*, the reader must recognize that 'raced past the barn' is a reduced passive relative clause ('The horse [that was] raced past the barn'), preserving cognitive coherence without becoming stalled by apparent double-verbs."""
        }

        # CHAPTER 10
        self._chapters[10] = {
            "title": "Chapter 10: Practical Verification Checklist and Rubric for Speaking and Writing",
            "content": """# Chapter 10: Practical Verification Checklist and Mastery Framework

Before submitting any written work or delivering an important formal speech, execute this standardized 10-Point Linguistic Audit:

## The 10-Point Verification Checklist

| Check # | Verification Item | Guiding Diagnostic Question |
|---|---|---|
| **1** | **Clausal Integrity** | Does every sentence contain an independent matrix clause with a finite predicate? Are there any accidental comma splices or fragments? |
| **2** | **Agreement & Concord** | Does the grammatical number (singular/plural) of the true subject head noun govern the finite verb, ignoring all intervening prepositional phrases? |
| **3** | **Tense Stability** | Is the primary temporal reference frame stable, and are all tense shifts semantically justified? |
| **4** | **Modifier Alignment** | Does every introductory participial phrase (-ing/-ed) logically and directly modify the immediate subject noun that follows? |
| **5** | **Parallelism** | Are all coordinated elements (in lists, bullet points, or across correlative conjunctions) cast in identical syntactic forms? |
| **6** | **Pronoun Precision** | Is every pronoun linked unambiguously to a single, clearly stated antecedent with matching person, number, and gender? |
| **7** | **Active Agency & Voice** | Is active voice utilized for clarity and accountability, reserving passive voice only when the recipient or action is the thematic focus? |
| **8** | **Cohesion & Signposts** | Does each paragraph feature an explicit topic sentence, followed by evidence, explanation, and logical transition signposts (Furthermore, Consequently, In contrast)? |
| **9** | **Register & Tone** | Is the register consistently aligned with the audience, avoiding colloquial contractions ('ain't', 'gonna') in formal documents? |
| **10** | **Phonetic & Punctuation Polish** | Are apostrophes reserved strictly for contractions and possessives? Are articles ('a' vs 'an') aligned with spoken phonetic onset? |

## The Four-Tier Proficiency Rubric
- **Level 1 (Novice)**: Relies on simple paratactic coordination; frequent local agreement and boundary errors; informal spoken register leakage.
- **Level 2 (Competent)**: Correct sentence boundaries; standard subject-verb agreement intact; limited subordination and transition variety.
- **Level 3 (Proficient)**: Sophisticated hypotactic subordination; flawless tense sequencing; deliberate register modulation; rich cohesive devices.
- **Level 4 (Mastery)**: Deep syntactic versatility (clefts, inversions, periodic sentences); effortless rhetorical device deployment; immaculate alignment across structural, semantic, and pragmatic levels."""
        }

    def get_chapter(self, chapter_number: int) -> Optional[str]:
        """Retrieve a specific chapter by number (1 to 10)."""
        data = self._chapters.get(chapter_number)
        return data["content"] if data else None

    def generate_full_document(self) -> str:
        """
        Synthesize the complete, self-contained educational compendium
        into a unified, publication-grade document.
        """
        header = (
            "# LINGUA SAPIENS: THE UNIVERSAL COMPENDIUM OF HUMAN GRAMMAR & LINGUISTIC INTELLIGENCE\n"
            "## An Exhaustive, Self-Contained Treatise on Language, Syntax, Phonology, and Rhetoric\n"
            "### Authored by Antigravity Autonomous Linguistic Intelligence\n\n"
            "---\n\n"
        )
        body = "\n\n---\n\n".join([self._chapters[i]["content"] for i in range(1, 11)])
        return header + body

    def export_to_file(self, filepath: str) -> str:
        """Write the complete compendium to a specified filesystem path."""
        doc = self.generate_full_document()
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(doc)
        return f"Successfully exported comprehensive grammar compendium to '{filepath}' ({len(doc.split())} words)."
