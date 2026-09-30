"""
Universal Grammar Knowledge Base (UGKB).

Exhaustive, self-contained repository of grammatical concepts, categories,
features, universal principles, and cross-linguistic annotated paradigms.
"""

from typing import Dict, List, Optional, Any
from ..common.models import (
    GrammarConcept,
    ExampleAnnotation,
    PartOfSpeech,
    Tense,
    Aspect,
    Mood,
    Voice,
    Number,
    GrammaticalCase,
)


class UniversalGrammarKnowledgeBase:
    """
    Exhaustive Universal Grammar Knowledge Base covering all recognized
    grammatical categories, syntactic functions, and cross-linguistic variations.
    """

    def __init__(self):
        self._concepts: Dict[str, GrammarConcept] = {}
        self._universal_principles: Dict[str, Dict[str, Any]] = {}
        self._language_specific_rules: Dict[str, List[Dict[str, str]]] = {}
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """Populate the knowledge base with exhaustive grammatical taxonomies."""
        self._populate_parts_of_speech()
        self._populate_verbals_and_predication()
        self._populate_morphosyntactic_features()
        self._populate_syntactic_relations()
        self._populate_pragmatic_discourse_categories()
        self._populate_universal_principles()
        self._populate_language_specific_rules()

    def _populate_parts_of_speech(self):
        # 1. NOUN
        self.register_concept(GrammarConcept(
            name="Noun",
            category="Part of Speech",
            definition="A lexical class denoting an entity, person, place, thing, substance, quality, action, or abstract concept. Forms the core semantic head of a Noun Phrase (NP).",
            functional_role="Serves universally as the head of arguments in sentences (Subject, Direct Object, Indirect Object, Object of Preposition, Predicate Nominal).",
            universal_principle="Universally attested across all human languages, distinguished from verbs by serving as arguments rather than primary predicates, though lexical flexibility varies (e.g., in Salishan or Austronesian languages).",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="The philosopher questioned the foundation of truth.",
                    gloss="the philosopher questioned the foundation of truth",
                    translation="The philosopher questioned the foundation of truth.",
                    grammatical_breakdown="'philosopher' (common, concrete noun, subject head); 'foundation' (abstract noun, direct object head); 'truth' (abstract non-count noun, prepositional complement)."
                ),
                ExampleAnnotation(
                    language="Spanish",
                    target_sentence="El científico descubrió una galaxia distante.",
                    gloss="def.M.SG scientist discovered indef.F.SG galaxy distant.F.SG",
                    translation="The scientist discovered a distant galaxy.",
                    grammatical_breakdown="'científico' (masculine singular noun); 'galaxia' (feminine singular noun, direct object showing grammatical gender agreement with 'una' and 'distante')."
                ),
                ExampleAnnotation(
                    language="Japanese",
                    target_sentence="猫が静かに魚を食べた。(Neko ga shizuka ni sakana o tabeta.)",
                    gloss="cat NOM quietly fish ACC ate",
                    translation="The cat quietly ate the fish.",
                    grammatical_breakdown="'猫 (neko)' (noun marked with nominative case particle が); '魚 (sakana)' (noun marked with accusative case particle を)."
                ),
                ExampleAnnotation(
                    language="Swahili",
                    target_sentence="Mtoto anasoma kitabu kizuri.",
                    gloss="CL1.child CL1.PRS.read CL7.book CL7.good",
                    translation="The child is reading a good book.",
                    grammatical_breakdown="'Mtoto' (Noun Class 1, animate human); 'kitabu' (Noun Class 7, inanimate artifact showing prefix agreement on adjective 'kizuri')."
                ),
            ],
            language_specific_notes={
                "English": "Inflects primarily for number (-s/-es) and genitive case ('s); lacks grammatical gender inflection on common nouns.",
                "German": "Capitalizes all nouns orthographically; inflects for four cases (Nom, Acc, Gen, Dat) and three grammatical genders (M, F, N).",
                "Russian": "Has a six-case system with animate/inanimate distinctions affecting accusative case morphology.",
                "Mandarin": "No morphological number or case inflections; nouns rely on numeral classifiers (量词 liàngcí) for quantification (e.g., 一本书 yī běn shū)."
            },
            cross_references=["Pronoun", "Noun Class", "Case", "Determiner"]
        ))

        # 2. PRONOUN
        self.register_concept(GrammarConcept(
            name="Pronoun",
            category="Part of Speech",
            definition="A closed-class grammatical item that substitutes for a noun or noun phrase (determiner phrase DP), deriving its reference from linguistic context (anaphora/cataphora) or situational environment (deixis).",
            functional_role="Prevents redundant nominal repetition, tracks discourse entities, and encodes participant roles (speaker, addressee, third-party) along with person, number, gender, and case.",
            universal_principle="All languages possess personal pronouns distinguishing at minimum 1st and 2nd person; pronominal systems universalize deictic reference.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="She gave him herself in devotion.",
                    gloss="3SG.F.NOM gave 3SG.M.ACC 3SG.F.REFL in devotion",
                    translation="She gave him herself in devotion.",
                    grammatical_breakdown="'She' (subjective/nominative personal); 'him' (objective/accusative personal); 'herself' (reflexive pronoun bound locally within TP by Binding Principle A)."
                ),
                ExampleAnnotation(
                    language="French",
                    target_sentence="Je te le donnerai demain.",
                    gloss="1SG.NOM 2SG.DAT 3SG.M.ACC give.FUT.1SG tomorrow",
                    translation="I will give it to you tomorrow.",
                    grammatical_breakdown="Pronominal clitics 'te' (indirect object) and 'le' (direct object) precede the inflected verb in strict hierarchical order."
                ),
                ExampleAnnotation(
                    language="Arabic",
                    target_sentence="كَتَبَتْ لَهُ رِسَالَةً (Katabat lahu risālatan)",
                    gloss="wrote.3SG.F to-him letter.ACC",
                    translation="She wrote him a letter.",
                    grammatical_breakdown="Subject pronoun is null/pro-dropped (indicated by suffix -at); pronominal object is an enclitic pronoun -hu affixed to preposition li-."
                )
            ],
            language_specific_notes={
                "English": "Maintains distinction between subjective (I, he, she, we, they) and objective (me, him, her, us, them) case forms.",
                "Spanish": "Pro-drop language (null-subject parameter positive); subject pronouns are omitted unless emphatic or contrastive.",
                "Japanese": "Pronouns behave morphosyntactically like open-class nominals; honorific hierarchy determines selection."
            },
            cross_references=["Anaphora", "Deixis", "Binding Theory", "Case"]
        ))

        # 3. VERB
        self.register_concept(GrammarConcept(
            name="Verb",
            category="Part of Speech",
            definition="A central lexical class that encodes events, actions, processes, states of being, or relations between entities. Serves as the structural predicate and governor of the clause.",
            functional_role="Determines argument structure and theta-role assignment (Agent, Patient, Experiencer), anchoring the clause in time, aspectual shape, and modality.",
            universal_principle="Universally constitutes the predication nexus of human language. Governs valency (intransitive = 1 argument, transitive = 2 arguments, ditransitive = 3 arguments).",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="The scientist demonstrated that the hypothesis was false.",
                    gloss="the scientist demonstrated that the hypothesis was false",
                    translation="The scientist demonstrated that the hypothesis was false.",
                    grammatical_breakdown="'demonstrated' is a transitive cognitive verb taking an agentive subject and a clausal finite complement (CP)."
                ),
                ExampleAnnotation(
                    language="German",
                    target_sentence="Er hat gestern das Buch gelesen.",
                    gloss="he has yesterday the book read.PTCP",
                    translation="He read the book yesterday.",
                    grammatical_breakdown="V2 word order: auxiliary 'hat' in second position of main clause, past participle 'gelesen' at clause-final bracket (Satzklammer)."
                ),
                ExampleAnnotation(
                    language="Russian",
                    target_sentence="Она перечитала книгу за вечер. (Ona perechitala knigu za vecher.)",
                    gloss="she read-through.PFV book.ACC in evening",
                    translation="She read through the book in an evening.",
                    grammatical_breakdown="Prefix 'пере-' (pere-) encodes perfective telicity, emphasizing completion and thoroughness."
                )
            ],
            language_specific_notes={
                "English": "Morphologically impoverished verb inflection (only 3rd person singular present -s survives from historical inflection).",
                "Georgian": "Polypersonal verbal agreement where the verb indexes subject, direct object, and indirect object simultaneously.",
                "Mandarin": "Verbs do not inflect for person, number, or tense; aspect markers (了 le, 过 guò, 着 zhe) attach postverbally."
            },
            cross_references=["Tense", "Aspect", "Mood", "Voice", "Auxiliary Verb"]
        ))

        # 4. ADJECTIVE
        self.register_concept(GrammarConcept(
            name="Adjective",
            category="Part of Speech",
            definition="A word class that modifies or specifies a noun or pronoun, attributing qualities, states, or limits to the nominal referent.",
            functional_role="Functions either attributively (prenominal or postnominal modifier inside NP) or predicatively (complement to a copula/linking verb).",
            universal_principle="All languages have grammatical means to express adjectival concepts, though some languages (e.g., Igbo, Korean) treat them syntactically as stative verbs.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="The brilliant astronomer observed an ancient supernova.",
                    gloss="the brilliant astronomer observed an ancient supernova",
                    translation="The brilliant astronomer observed an ancient supernova.",
                    grammatical_breakdown="'brilliant' and 'ancient' are attributive adjectives preceding the noun heads."
                ),
                ExampleAnnotation(
                    language="French",
                    target_sentence="Une maison blanche et un beau livre.",
                    gloss="indef.F house white.F and indef.M beautiful.M book",
                    translation="A white house and a beautiful book.",
                    grammatical_breakdown="Most French adjectives follow the noun ('blanche'), but a small set (BAGS: Beauty, Age, Goodness, Size) precede it ('beau')."
                )
            ],
            language_specific_notes={
                "Spanish": "Shows strict gender and number agreement with the noun it modifies (e.g., casas blancas, libros blancos).",
                "English": "Zero morphological agreement for gender or number; strictly invariant except for comparative (-er) and superlative (-est) degrees."
            },
            cross_references=["Noun", "Agreement", "Adverb"]
        ))

        # 5. ADVERB
        self.register_concept(GrammarConcept(
            name="Adverb",
            category="Part of Speech",
            definition="A modifier modifying verbs, adjectives, other adverbs, prepositional phrases, or entire clauses, specifying manner, place, time, frequency, degree, or epistemic stance.",
            functional_role="Functions as an adjunct (optional structural modifier) providing circumstantial information or discourse framing.",
            universal_principle="Adjunct modification is structurally recursive and unbounded in human grammar.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="Inevitably, the orchestra played extraordinarily well tonight.",
                    gloss="inevitably the orchestra played extraordinarily well tonight",
                    translation="Inevitably, the orchestra played extraordinarily well tonight.",
                    grammatical_breakdown="'Inevitably' (sentence adverbial); 'extraordinarily' (degree adverb modifying adverb 'well'); 'well' (manner adverb modifying 'played'); 'tonight' (temporal adverb)."
                )
            ],
            language_specific_notes={
                "English": "Formed productively by suffixing -ly to adjectives, but flat adverbs (fast, hard) remain without suffix."
            },
            cross_references=["Adjective", "Verb", "Adjunct"]
        ))

        # 6. PREPOSITION / POSTPOSITION / ADPOSITION
        self.register_concept(GrammarConcept(
            name="Preposition and Postposition (Adposition)",
            category="Part of Speech",
            definition="A functional head that combines with a complement noun phrase (or DP) to form an adpositional phrase (PP), establishing spatial, temporal, instrumental, causal, or abstract semantic relations.",
            functional_role="Assigns inherent or structural case to its complement and anchors predicates to spatial/temporal domains.",
            universal_principle="Correlates typologically with word order: VO languages are predominantly prepositional (English, Spanish, Swahili), whereas OV languages are postpositional (Japanese, Turkish, Hindi).",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="She walked through the ancient gate into the courtyard.",
                    gloss="she walked through the ancient gate into the courtyard",
                    translation="She walked through the ancient gate into the courtyard.",
                    grammatical_breakdown="'through' and 'into' are prepositions heading PPs that function as directional locative adjuncts."
                ),
                ExampleAnnotation(
                    language="Japanese",
                    target_sentence="学校の中で友達と話した。(Gakkou no naka de tomodachi to hanashita.)",
                    gloss="school GEN inside LOC friend with talked",
                    translation="I talked with a friend inside the school.",
                    grammatical_breakdown="'で (de)' (locative postposition) and 'と (to)' (comitative postposition) follow their nominal complements."
                )
            ],
            language_specific_notes={
                "German": "Prepositions govern specific cases: Dative (mit, nach, von, zu), Accusative (durch, für, ohne), Genitive (während, trotz), or Two-Way Wechselpräpositionen (in, an, auf)."
            },
            cross_references=["Case", "Word Order Typology", "Adjunct"]
        ))

        # 7. CONJUNCTION
        self.register_concept(GrammarConcept(
            name="Conjunction",
            category="Part of Speech",
            definition="A connective syntactic element that joins words, phrases, or clauses. Subdivided into Coordinating (linking syntactically equivalent elements), Subordinating (introducing dependent clauses), and Correlative (paired conjunctions).",
            functional_role="Constructs compound structures, establishes logical dependencies (causal, concessive, conditional), and regulates information hierarchy.",
            universal_principle="Recursion in natural language relies crucially on coordination and subordination conjunction operations.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="Neither the director nor the actors consented, because the terms were unacceptable.",
                    gloss="neither the director nor the actors consented because the terms were unacceptable",
                    translation="Neither the director nor the actors consented, because the terms were unacceptable.",
                    grammatical_breakdown="'Neither ... nor' (correlative coordinating conjunction); 'because' (subordinating conjunction introducing causal adverbial clause)."
                )
            ],
            language_specific_notes={
                "English": "FANBOYS mnemonic (For, And, Nor, But, Or, Yet, So) represents primary coordinating conjunctions."
            },
            cross_references=["Clause", "Subordination", "Coordination"]
        ))

        # 8. ARTICLE, DETERMINER & QUANTIFIER
        self.register_concept(GrammarConcept(
            name="Article, Determiner and Quantifier",
            category="Part of Speech",
            definition="Grammatical elements that precede (or bind to) nouns to specify definiteness, specificity, proximity (deixis), possession, or quantity.",
            functional_role="Heads the Determiner Phrase (DP) in modern generative grammar, converting a bare predicate noun into a referential argument capable of entering syntactic relations.",
            universal_principle="Languages without overt articles (e.g., Russian, Latin, Mandarin) encode definiteness through word order, demonstratives, topic-comment articulation, or case alternation.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="Every student read the assigned book.",
                    gloss="every student read the assigned book",
                    translation="Every student read the assigned book.",
                    grammatical_breakdown="'Every' is a universal distributive quantifier/determiner; 'the' is a definite article picking out a uniquely identifiable referent."
                ),
                ExampleAnnotation(
                    language="Arabic",
                    target_sentence="الكتاب جديد (Al-kitābu jadīd)",
                    gloss="DEF-book.NOM new.NOM",
                    translation="The book is new.",
                    grammatical_breakdown="Definite article 'al-' (الـ) prefixes directly onto the noun."
                )
            ],
            language_specific_notes={
                "Russian": "Has no definite or indefinite articles; word order marks definiteness (Object before Verb often signals definite given information)."
            },
            cross_references=["Noun", "Deixis", "Quantifier Scope"]
        ))

        # 9. AUXILIARY, MODAL & COPULA
        self.register_concept(GrammarConcept(
            name="Auxiliary, Modal and Copular Verbs",
            category="Part of Speech / Predication",
            definition="Auxiliaries are helper verbs encoding tense, aspect, or voice (be, have, do). Modals express epistemic possibility, deontic obligation, or ability (can, must, should, may). Copulas link a subject to a non-verbal predicate complement (be, seem, become).",
            functional_role="Occupies functional head projections (T/INFL) in syntactic trees; governs subject-auxiliary inversion, negation support, and modal evaluation.",
            universal_principle="All languages possess functional mechanisms for modality and copulation, though copular linkage may be overt, zero/null (zero copula in Arabic, Russian present tense), or realized as verbal inflection.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="The committee must have been deliberating for hours.",
                    gloss="the committee must have been deliberating for hours",
                    translation="The committee must have been deliberating for hours.",
                    grammatical_breakdown="'must' (epistemic modal) + 'have' (perfective auxiliary) + 'been' (progressive auxiliary) + 'deliberating' (lexical main verb in progressive aspect)."
                ),
                ExampleAnnotation(
                    language="Russian",
                    target_sentence="Мой брат — инженер. (Moy brat — inzhener.)",
                    gloss="my brother engineer",
                    translation="My brother is an engineer.",
                    grammatical_breakdown="Zero copula in present tense indicative; subject and predicate nominal juxtaposed directly with em-dash in writing."
                )
            ],
            language_specific_notes={
                "English": "NICE properties of auxiliaries: Negation (takes 'not'), Inversion (inverts for questions), Code (verb phrase ellipsis), Emphasis (takes tonic stress)."
            },
            cross_references=["Verb", "Tense", "Aspect", "Mood"]
        ))

    def _populate_verbals_and_predication(self):
        # GERUND, INFINITIVE, PARTICIPLE
        self.register_concept(GrammarConcept(
            name="Gerund, Infinitive and Participle (Verbals)",
            category="Non-Finite Verb Forms",
            definition="Verbals are verb derivatives that function non-finitely without tense/agreement inflection: Gerunds function nominaly (-ing in English); Infinitives represent the base citation form (bare or with 'to'); Participles function adjectivally or in compound aspects (present active -ing, past passive -ed/-en).",
            functional_role="Enables clausal embedding and subordination with reduced syntactic structure, functioning as subject, object, adjective, or adverbial adjunct.",
            universal_principle="Languages universally employ non-finite or nominalized forms to compact propositional content into single arguments.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="Swimming across the frozen lake proved to be an exhausting endeavor.",
                    gloss="swimming across the frozen lake proved to be an exhausting endeavor",
                    translation="Swimming across the frozen lake proved to be an exhausting endeavor.",
                    grammatical_breakdown="'Swimming across the frozen lake' (gerund phrase functioning as syntactic subject); 'frozen' (past participle functioning as attributive adjective); 'to be' (infinitive complement); 'exhausting' (present participle functioning as adjective)."
                ),
                ExampleAnnotation(
                    language="Latin",
                    target_sentence="Caesare interfecto, res publica concidit.",
                    gloss="Caesar.ABL killed.PTCP.ABL republic fell",
                    translation="Caesar having been killed, the republic collapsed.",
                    grammatical_breakdown="Ablative absolute construction using the perfect passive participle 'interfecto' in concord with 'Caesare'."
                )
            ],
            language_specific_notes={
                "English": "Gerunds vs Present Participles are morphologically identical (-ing) but syntactically distinct (Gerund = nominal distribution; Participle = adjectival/aspectual distribution)."
            },
            cross_references=["Verb", "Nominalization", "Clause"]
        ))

    def _populate_morphosyntactic_features(self):
        # TENSE
        self.register_concept(GrammarConcept(
            name="Tense",
            category="Morphosyntactic Feature",
            definition="A grammatical category that locates an event or state in time relative to the moment of utterance (Speech Time) or a temporal reference point (Reference Time).",
            functional_role="Deictically anchors the truth value of the proposition along the temporal timeline: Past, Present, Future.",
            universal_principle="Distinguished cross-linguistically between absolute tense (anchored to speech time) and relative tense (anchored to another reference point). Languages can be tensed or tenseless (aspect-prominent, e.g., Mandarin).",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="She had departed before the meeting commenced.",
                    gloss="she had departed before the meeting commenced",
                    translation="She had departed before the meeting commenced.",
                    grammatical_breakdown="'had departed' expresses past-in-the-past (Pluperfect/Past Perfect), ordering Event Time prior to Reference Time in the past."
                ),
                ExampleAnnotation(
                    language="Mandarin",
                    target_sentence="他昨天来我家。(Tā zuótiān lái wǒ jiā.)",
                    gloss="he yesterday come my home",
                    translation="He came to my home yesterday.",
                    grammatical_breakdown="No verbal tense inflection; past temporality is established purely by temporal adverbial '昨天 (yesterday)'."
                )
            ],
            language_specific_notes={
                "English": "Morphologically possesses only two tenses: Past (marked by -ed/ablaut) and Non-Past/Present. Future is marked periphrastically using modal auxiliaries (will/shall) or aspectual constructions (going to)."
            },
            cross_references=["Aspect", "Mood", "Verb"]
        ))

        # ASPECT
        self.register_concept(GrammarConcept(
            name="Aspect",
            category="Morphosyntactic Feature",
            definition="A category denoting the internal temporal contour or constituency of an event (whether it is ongoing, completed, repeated, habitual, beginning, or momentary), independent of time location.",
            functional_role="Differentiates Perfective (viewing event as an indivisible completed whole) from Imperfective (viewing event from within: progressive, continuous, habitual, iterative).",
            universal_principle="All languages distinguish aspectual viewpoint and lexical aspect (Aktionsart: stative, activity, accomplishment, achievement).",
            annotated_examples=[
                ExampleAnnotation(
                    language="Spanish",
                    target_sentence="Ayer leía cuando de repente sonó el teléfono.",
                    gloss="yesterday read.IMPF.1SG when suddenly rang.PFV.3SG the phone",
                    translation="Yesterday I was reading when suddenly the phone rang.",
                    grammatical_breakdown="'leía' (imperfective aspect, background ongoing process) vs 'sonó' (preterite/perfective aspect, punctual foreground event interrupting)."
                ),
                ExampleAnnotation(
                    language="Russian",
                    target_sentence="Я писал (imperf.) письмо, когда он принёс (perf.) посылку.",
                    gloss="I wrote.IMPF letter when he brought.PFV parcel",
                    translation="I was writing a letter when he brought the parcel.",
                    grammatical_breakdown="Russian systematically pairs verbs into imperfective and perfective aspectual partner stems."
                )
            ],
            language_specific_notes={
                "English": "Distinguishes Progressive aspect (be + V-ing) and Perfect aspect (have + V-en)."
            },
            cross_references=["Tense", "Mood", "Verb"]
        ))

        # MOOD
        self.register_concept(GrammarConcept(
            name="Mood and Modality",
            category="Morphosyntactic Feature",
            definition="Grammatical marking reflecting the speaker's epistemic attitude toward the factual status, likelihood, desirability, necessity, or contingency of the proposition.",
            functional_role="Encompasses Indicative (factual assertion), Subjunctive (hypothetical, counterfactual, desiderative), Imperative (directive/command), Conditional (contingent), and Optative (wish).",
            universal_principle="Modality is universally divided into Epistemic (evaluation of knowledge/probability) and Deontic (evaluation of obligation/permission/morality).",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="If the manager were here, she would approve the grant.",
                    gloss="if the manager were.SUBJ here she would approve the grant",
                    translation="If the manager were here, she would approve the grant.",
                    grammatical_breakdown="'were' is the surviving past subjunctive expressing counterfactual conditionality; 'would approve' expresses hypothetical conditional consequence."
                ),
                ExampleAnnotation(
                    language="Spanish",
                    target_sentence="Espero que tengas éxito.",
                    gloss="hope.1SG that have.SUBJ.2SG success",
                    translation="I hope that you succeed.",
                    grammatical_breakdown="'tengas' is in the present subjunctive, triggered by the matrix verb of volition/desire 'espero'."
                )
            ],
            language_specific_notes={
                "English": "Subjunctive mood has largely eroded in modern colloquial English, surviving in mandative clauses ('I insist that he be present') and counterfactual conditionals ('if I were you')."
            },
            cross_references=["Tense", "Aspect", "Modal"]
        ))

        # VOICE
        self.register_concept(GrammarConcept(
            name="Voice",
            category="Morphosyntactic Feature",
            definition="A syntactic-semantic diathesis that alters the mapping between semantic thematic roles (Agent, Patient) and syntactic grammatical relations (Subject, Object).",
            functional_role="Includes Active (Agent = Subject), Passive (Patient = Subject; Agent demoted to oblique or deleted), Middle (Subject acts upon itself or undergoes an event), and Antipassive (Patient demoted in ergative systems).",
            universal_principle="Passivization or valency reduction is universal across human languages to serve discourse topicalization and information packaging needs.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="The theorem was proven by the young mathematician.",
                    gloss="the theorem was proven by the young mathematician",
                    translation="The theorem was proven by the young mathematician.",
                    grammatical_breakdown="Passive voice: Patient 'The theorem' promoted to subject position; Agent 'the young mathematician' demoted into an optional prepositional 'by'-phrase."
                ),
                ExampleAnnotation(
                    language="Classical Greek",
                    target_sentence="Λούομαι (Loúomai)",
                    gloss="wash.1SG.MID",
                    translation="I wash myself (or get washed).",
                    grammatical_breakdown="Middle voice morphology encoding reflexive/self-affecting action without periphrastic reflexive pronouns."
                )
            ],
            language_specific_notes={
                "English": "Formed periphrastically using auxiliary 'be' + past participle (-ed/-en), or colloquially with 'get' ('he got arrested')."
            },
            cross_references=["Grammatical Role", "Verb", "Thematic Roles"]
        ))

        # CASE
        self.register_concept(GrammarConcept(
            name="Case (Morphological and Abstract)",
            category="Morphosyntactic Feature",
            definition="A morphological or syntactic marking on nominals (nouns, pronouns, adjectives) that encodes their grammatical role and relationship to the governing predicate or head.",
            functional_role="Universal alignment systems: Nominative-Accusative (Nom = Subject of intransitive & transitive; Acc = Object) vs Ergative-Absolutive (Erg = Subject of transitive; Abs = Subject of intransitive & Object of transitive). Also encodes Oblique cases: Genitive (possession), Dative (recipient), Ablative (source), Locative (location), Instrumental (means), Vocative (direct address).",
            universal_principle="Case Filter (Chomsky): Every phonetically realized DP must be assigned abstract case (structural or inherent) to be syntactically licensed.",
            annotated_examples=[
                ExampleAnnotation(
                    language="German",
                    target_sentence="Der Lehrer gab dem Schüler das Buch des Vaters.",
                    gloss="the.M.NOM teacher gave the.M.DAT student the.N.ACC book the.M.GEN father",
                    translation="The teacher gave the student the father's book.",
                    grammatical_breakdown="'Der Lehrer' (Nominative subject); 'dem Schüler' (Dative indirect object); 'das Buch' (Accusative direct object); 'des Vaters' (Genitive possessive modifier)."
                ),
                ExampleAnnotation(
                    language="Basque",
                    target_sentence="Gizonak liburua irakurri du. / Gizona etorri da.",
                    gloss="man.ERG book.ABS read has / man.ABS come is",
                    translation="The man read the book. / The man came.",
                    grammatical_breakdown="Ergative-Absolutive alignment: Transitive subject takes ergative suffix -ak ('Gizonak'); intransitive subject takes absolutive ('Gizona'), matching transitive object ('liburua')."
                )
            ],
            language_specific_notes={
                "English": "Morphological case survives only in personal pronouns (he/him/his) and the genitive clitic ('s)."
            },
            cross_references=["Agreement", "Grammatical Role", "Word Order Typology"]
        ))

        # NUMBER AND GENDER
        self.register_concept(GrammarConcept(
            name="Number, Gender and Noun Classes",
            category="Morphosyntactic Feature",
            definition="Number quantifies entities grammatically (Singular, Plural, Dual, Paucal). Gender or Noun Class is a nominal classification system grouping nouns into categories (Masculine/Feminine/Neuter, Animate/Inanimate, or 10-20 semantic classes in Bantu languages) triggering concord on associated determiners, adjectives, and verbs.",
            functional_role="Enforces agreement across the syntactic constituent, binding dependent words to their nominal head.",
            universal_principle="Agreement tracking resolves referential ambiguity in complex discourse by linking pronominal and adjectival forms uniquely to their head noun class.",
            annotated_examples=[
                ExampleAnnotation(
                    language="Arabic",
                    target_sentence="كِتَابَانِ جَدِيدَانِ (Kitābāni jadīdāni)",
                    gloss="book.DUAL.NOM new.DUAL.NOM",
                    translation="Two new books.",
                    grammatical_breakdown="Dual number morphology (-āni) explicitly marking precisely two entities with concord on the adjective."
                ),
                ExampleAnnotation(
                    language="Swahili",
                    target_sentence="Watu wazuri wamefika.",
                    gloss="CL2.people CL2.good CL2.PERF.arrive",
                    translation="The good people have arrived.",
                    grammatical_breakdown="Class 2 (human plural prefix wa-) exhibits strict alliterative concord across noun, adjective, and verb prefix."
                )
            ],
            language_specific_notes={
                "English": "Grammatical gender was lost in Middle English; only semantic natural gender is tracked via 3rd-person pronouns (he, she, it)."
            },
            cross_references=["Agreement", "Noun", "Pronoun"]
        ))

    def _populate_syntactic_relations(self):
        # AGREEMENT & CONCORD
        self.register_concept(GrammarConcept(
            name="Agreement and Concord",
            category="Syntactic Relation",
            definition="The morphological covariance between a syntactic head and a dependent word or between a subject and its predicate, matching features of person, number, gender, or case.",
            functional_role="Overcomes linear word distance to explicitly mark syntactic co-dependency and structural constituency.",
            universal_principle="Spec-Head agreement or Probe-Goal search in minimalist syntax formalizes how unvalued features on functional heads receive values from nominal goals.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="The list of participants is complete, but the results of the study are pending.",
                    gloss="the list of participants is complete but the results of the study are pending",
                    translation="The list of participants is complete, but the results of the study are pending.",
                    grammatical_breakdown="Subject-verb agreement: 'list' (singular head) triggers singular verb 'is' despite intervening plural 'participants'; 'results' (plural head) triggers plural verb 'are'."
                ),
                ExampleAnnotation(
                    language="French",
                    target_sentence="Les fleurs que j'ai cueillies sont magnifiques.",
                    gloss="the flowers that I have picked.F.PL are magnificent",
                    translation="The flowers that I picked are magnificent.",
                    grammatical_breakdown="Past participle 'cueillies' agrees in gender and number (feminine plural) with the preceding direct object relative pronoun 'que' referring to 'fleurs'."
                )
            ],
            language_specific_notes={
                "English": "Subject-verb agreement applies only in the 3rd person singular present indicative (-s), with exception of the copula 'to be'."
            },
            cross_references=["Case", "Number and Gender", "Subject-Verb Agreement Error"]
        ))

        # ELLIPSIS & GAPPING
        self.register_concept(GrammarConcept(
            name="Ellipsis and Gapping",
            category="Syntactic Relation",
            definition="The omission from a clause of one or more words that are nevertheless understood in the context of the remaining elements, including VP-ellipsis, pseudogapping, sluicing, and stripping.",
            functional_role="Maximizes communicative economy, prevents redundant verbalization, and tightens discourse coherence.",
            universal_principle="Identity condition: Elliptical structures require syntactic or semantic identity with an antecedent in the discourse.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="Arthur studied physics, and Clara [studied] mathematics.",
                    gloss="Arthur studied physics and Clara studied mathematics",
                    translation="Arthur studied physics, and Clara mathematics.",
                    grammatical_breakdown="Gapping: The second conjunct omits the identical transitive verb 'studied', leaving remnants 'Clara' (subject) and 'mathematics' (object)."
                ),
                ExampleAnnotation(
                    language="English",
                    target_sentence="Someone knocked on the door, but I don't know who [knocked on the door].",
                    gloss="someone knocked on the door but I don't know who",
                    translation="Someone knocked on the door, but I don't know who.",
                    grammatical_breakdown="Sluicing: Ellipsis of the entire IP/TP complement of an interrogative CP, leaving only the wh-phrase 'who'."
                )
            ],
            language_specific_notes={
                "English": "VP-ellipsis requires an overt auxiliary or dummy operator 'do' (e.g., 'She will not leave, but he will [leave]')."
            },
            cross_references=["Anaphora", "Coordination", "Deep Thinking"]
        ))

        # ANAPHORA, CATAPHORA & DEIXIS
        self.register_concept(GrammarConcept(
            name="Anaphora, Cataphora and Deixis",
            category="Syntactic and Pragmatic Relation",
            definition="Anaphora refers backward to a previously introduced discourse entity (antecedent). Cataphora refers forward to an entity introduced later. Deixis anchors linguistic expressions directly to the extra-linguistic spatio-temporal situation of the speaker (Person, Spatial, Temporal, Social, Discourse deixis).",
            functional_role="Creates coreferential coherence across sentences and bridges linguistic code to physical reality.",
            universal_principle="Governed structurally by Chomsky's Binding Principles A, B, and C.",
            annotated_examples=[
                ExampleAnnotation(
                    language="English",
                    target_sentence="When he arrived at the station, Julian realized he had forgotten his ticket.",
                    gloss="when he arrived at the station Julian realized he had forgotten his ticket",
                    translation="When he arrived at the station, Julian realized he had forgotten his ticket.",
                    grammatical_breakdown="First 'he' is cataphoric, referring forward to 'Julian'; second 'he' and 'his' are anaphoric, referring backward to 'Julian'."
                ),
                ExampleAnnotation(
                    language="Spanish",
                    target_sentence="Aquí, ahora y contigo.",
                    gloss="here now and with-you.SG",
                    translation="Here, now, and with you.",
                    grammatical_breakdown="Spatial deixis ('aquí' = proximate to speaker), temporal deixis ('ahora' = simultaneous with speech act), person deixis ('contigo' = 2nd person addressee)."
                )
            ],
            language_specific_notes={
                "English": "Pronoun-antecedent agreement requires matching in gender, number, and person, while avoiding ambiguous multiple antecedents."
            },
            cross_references=["Binding Theory", "Pronoun", "Pragmatics"]
        ))

    def _populate_pragmatic_discourse_categories(self):
        # EVIDENTIALITY & HONORIFICS
        self.register_concept(GrammarConcept(
            name="Evidentiality and Honorifics",
            category="Grammaticalized Pragmatics",
            definition="Evidentiality is grammatical marking indicating the information source of the speaker's claim (direct sensory witness, hearsay/reported, inference/deduction). Honorifics are grammaticalized markers indexing social status, hierarchy, formality, and respect between interlocutors.",
            functional_role="Embeds epistemological authority and social hierarchy directly into the morphosyntax of the clause.",
            universal_principle="Languages universally negotiate interpersonal stance, whether through grammatical affixes, particles, or lexical hedges.",
            annotated_examples=[
                ExampleAnnotation(
                    language="Turkish",
                    target_sentence="Ahmet gelmiş. (Ahmet came [reportedly/inferentially])",
                    gloss="Ahmet come.PST.INDIR",
                    translation="Ahmet has come (I didn't see it myself; I heard it or inferred it).",
                    grammatical_breakdown="The indirect past suffix -miş encodes evidential hearsay or surprise (mirativity), in contrast to direct past -di ('Ahmet geldi')."
                ),
                ExampleAnnotation(
                    language="Korean",
                    target_sentence="선생님께서 진지를 잡수십니다. (Seonsaengnim-kkeseo jinji-reul japsusimnida.)",
                    gloss="teacher.HON.NOM meal.HON.ACC eat.HON.FORMAL",
                    translation="The teacher is eating a meal.",
                    grammatical_breakdown="Subject honorific marker 께서 (-kkeseo), honorific lexical item 진지 (jinji instead of bap), and honorific verb 잡수시다 (japsusida) reflect deferential speech level."
                )
            ],
            language_specific_notes={
                "Japanese": "Elaborate tripartite system: Sonkeigo (respectful language for others), Kenjougo (humble language for oneself), and Teineigo (polite register marked with desu/masu)."
            },
            cross_references=["Mood", "Pragmatic Competence", "Register"]
        ))

    def _populate_universal_principles(self):
        self._universal_principles = {
            "Structure Dependency": {
                "name": "Principle of Structure Dependency",
                "formulation": "All grammatical operations in all human languages depend on hierarchical structural relationships (constituent trees, c-command, dominance), never on linear serial order or string word counts.",
                "significance": "Disproves naive linear-chain associative models of language. Explains why question formation inverts the matrix auxiliary, not the linearly first auxiliary: 'The dog that is barking will bite' -> 'Will the dog that is barking bite?' (NOT: *'Is the dog that barking will bite?')."
            },
            "X-Bar Schema": {
                "name": "X-Bar Theory and Endocentricity",
                "formulation": "Every syntactic phrase XP is endocentric, containing a unique lexical head X, which projects to an intermediate bar-level X' with its Complement, and then to a maximal projection XP with its Specifier.",
                "significance": "Unifies noun phrases (NP), verb phrases (VP), adjective phrases (AP), prepositional phrases (PP), and functional projections (CP, TP, DP) under a single recursive blueprint."
            },
            "Binding Theory": {
                "name": "Binding Theory (Principles A, B, C)",
                "formulation": "Governs structural conditions under which noun phrases and pronouns can corefer: Principle A: An anaphor (reflexive/reciprocal) must be bound locally in its governing category. Principle B: A pronominal must be free locally. Principle C: An R-expression (referential name) must be free everywhere.",
                "significance": "Explains why *'John likes himself' is valid, but *'John likes him' cannot mean John, and *'He likes John' is completely ungrammatical under coreference."
            },
            "Island Constraints": {
                "name": "Subjacency and Syntactic Islands",
                "formulation": "Constituents cannot be extracted (moved) out of certain structural domains (islands): Coordinate Structure Island, Complex NP Island, Wh-Island, Adjunct Island.",
                "significance": "Explains universal limits on sentence formation: *'Who did you see the man who arrested?' is strictly blocked in all languages."
            },
            "Head-Directionality Parameter": {
                "name": "Head-Directionality Parameter",
                "formulation": "Languages systematically choose whether heads precede their complements (Head-Initial: VO, Prepositions, Noun-Adjective) or follow their complements (Head-Final: OV, Postpositions, Adjective-Noun).",
                "significance": "Explains typological clustering: English and Spanish are head-initial; Japanese and Turkish are head-final."
            },
            "Null Subject (Pro-Drop) Parameter": {
                "name": "Null Subject / Pro-Drop Parameter",
                "formulation": "Languages vary as to whether the pronominal subject of a finite clause may be phonologically null (omitted) when agreement inflection is rich enough to recover its features.",
                "significance": "Spanish/Italian/Arabic/Hindi are +Pro-Drop ('Hablo' = 'I speak'); English/French/German are -Pro-Drop ('I speak' requires overt 'I', unless imperative)."
            }
        }

    def _populate_language_specific_rules(self):
        self._language_specific_rules = {
            "English": [
                {"rule": "Third Person Singular -s", "desc": "Present tense regular verbs take suffix -s/-es when subject is 3rd person singular."},
                {"rule": "Do-Support", "desc": "Negation and interrogative inversion in non-auxiliary finite verbs require auxiliary 'do' ('She does not know', 'Does she know?')."},
                {"rule": "Strict SVO Constituent Order", "desc": "Core argument order is strictly Subject - Verb - Object; scrambling causes ungrammaticality or alters meaning."}
            ],
            "Spanish": [
                {"rule": "Pro-Drop (Null Subject)", "desc": "Subject pronouns are omitted by default, used only for emphasis or disambiguation."},
                {"rule": "Personal 'A'", "desc": "Direct objects denoting specific human beings or pets require the marker 'a' ('Veo a María')."},
                {"rule": "Gender & Number Concord", "desc": "Determiners and adjectives must agree with nouns in gender (M/F) and number (SG/PL)."}
            ],
            "German": [
                {"rule": "Verb-Second (V2) in Main Clauses", "desc": "The finite verb must always occupy the exact second structural position in a declarative main clause."},
                {"rule": "Verb-Final in Subordinate Clauses", "desc": "In subordinate clauses introduced by complementizers (weil, dass, ob), the finite verb shifts to the absolute end of the clause."},
                {"rule": "Four-Case Declension", "desc": "Articles, pronouns, and adjective endings systematically decline across Nominative, Accusative, Dative, and Genitive cases."}
            ],
            "Japanese": [
                {"rule": "Strict SOV & Head-Final", "desc": "Verbs, auxiliaries, and copulas must stand at the sentence-final position."},
                {"rule": "Postpositional Particles", "desc": "Grammatical roles are signaled by particles: は (topic wa), が (subject ga), を (object o), に (direction/recipient ni), で (locative de)."},
                {"rule": "Politeness Honorific Stems", "desc": "Verbal suffixes (-masu, -desu) conjugate to reflect relational social distance between speaker and listener."}
            ],
            "Mandarin Chinese": [
                {"rule": "Topic-Comment Prominence", "desc": "Sentences are structured around a discourse Topic followed by a Comment, rather than strict grammatical subject-predicate."},
                {"rule": "Classifier (Measure Word) Requirement", "desc": "A numeral cannot directly modify a noun without an intervening classifier suited to the noun's semantic class (e.g., 本 běn for books, 张 zhāng for flat objects)."},
                {"rule": "Aspect Particles instead of Tense", "desc": "Events are marked aspectually with 了 (completed action/change of state), 过 (experiential), 着 (continuous), without verbal conjugation."}
            ]
        }

    def register_concept(self, concept: GrammarConcept):
        """Add or update a grammar concept in the knowledge base."""
        self._concepts[concept.name.lower()] = concept

    def get_concept(self, name: str) -> Optional[GrammarConcept]:
        """Look up a concept by exact or fuzzy name."""
        key = name.strip().lower()
        if key in self._concepts:
            return self._concepts[key]
        for k, v in self._concepts.items():
            if key in k or any(key in cr.lower() for cr in v.cross_references):
                return v
        return None

    def list_all_concepts(self) -> List[str]:
        """Return the names of all indexed grammatical concepts."""
        return [c.name for c in self._concepts.values()]

    def search_concepts(self, query: str) -> List[GrammarConcept]:
        """Search concepts by keyword across definition, role, and principles."""
        q = query.lower()
        matches = []
        for c in self._concepts.values():
            if (q in c.name.lower() or
                q in c.definition.lower() or
                q in c.functional_role.lower() or
                q in c.universal_principle.lower()):
                matches.append(c)
        return matches

    def get_universal_principles(self) -> Dict[str, Dict[str, Any]]:
        """Return all Universal Grammar foundational principles."""
        return self._universal_principles

    def get_language_specific_rules(self, language: str) -> List[Dict[str, str]]:
        """Return language-specific rules and constraints."""
        return self._language_specific_rules.get(language, [])
