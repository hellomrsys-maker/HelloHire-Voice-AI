# Finite State Transducer (FST) - Japanese Particle Combinatorics & Selection
# Format: [State_From] [State_To] [Input_Particle] [Output_Role/Feature] [Cost/Weight]

# States:
# 0: NOUN_BASE
# 1: CASE_MARKED
# 2: TOPIC_CONTRAST_MARKED
# 3: CONJUNCTIVE_MARKED
# 4: FINAL_DELIMITER

# Case particles (格助詞)
0 1 が [NOMINATIVE_AGENT] 0.1
0 1 を [ACCUSATIVE_PATIENT] 0.1
0 1 に [DATIVE_LOC_GOAL] 0.1
0 1 で [INSTRUMENT_ACTION_LOC] 0.1
0 1 へ [DIRECTIONAL] 0.2
0 1 と [COMITATIVE] 0.2
0 1 から [ABLATIVE_SOURCE] 0.1
0 1 まで [TERMINATIVE_GOAL] 0.1
0 1 より [COMPARATIVE_SOURCE] 0.2

# Genitive particle (連体助詞)
0 0 の [GENITIVE_ADNOMINAL] 0.1

# Topic and focus particles (係助詞・副助詞) directly attached to noun
0 2 は [TOPIC_FOCUS] 0.1
0 2 も [ADDITIVE_ALSO] 0.1
0 2 こそ [EMPHASIS_COSO] 0.3
0 2 さえ [EXTREME_EVEN] 0.3
0 2 だけ [EXCLUSIVE_ONLY] 0.2
0 2 しか [EXCLUSIVE_NEGATIVE_BOUND] 0.2

# Stacking case + topic particles (e.g., には, では, からは, とは)
1 2 は [CONTRASTIVE_TOPIC] 0.15
1 2 も [ADDITIVE_INDIRECT] 0.15

# Sentence final particles (終助詞)
4 4 ね [CONFIRMATION_SEEKING] 0.1
4 4 よ [ASSERTIVE_INFORMING] 0.1
4 4 か [INTERROGATIVE] 0.1
4 4 な [PROHIBITION_OR_MONOLOGUE] 0.2
4 4 わ [AFFECTIVE_SOFTENING] 0.3
