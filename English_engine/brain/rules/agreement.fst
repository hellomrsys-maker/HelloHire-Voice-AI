# agreement.fst - Finite State Transducer specification for Subject-Verb & Pronoun-Antecedent Agreement
# States: S0 (Start), S1 (Subj_3SG), S2 (Subj_Non3SG), S3 (Verb_3SG_Match), S4 (Verb_Non3SG_Match), S_ERR (Mismatch)

# State Transitions:
S0  -> S1  : [he, she, it, man, woman, cat, system, engine] / {number: SG, person: 3}
S0  -> S2  : [i, you, we, they, men, women, cats, systems, engines] / {number: PL_or_1_2, person: non_3sg}

# Subject-Verb Agreement:
S1  -> S3  : [runs, writes, is, has, does, builds, analyzes] / {agreement: PASS}
S1  -> S_ERR: [run, write, are, have, do, build, analyze] / {error: SUBJECT_VERB_AGREEMENT_EXPECTED_3SG}

S2  -> S4  : [run, write, are, have, do, build, analyze] / {agreement: PASS}
S2  -> S_ERR: [runs, writes, is, has, does, builds, analyzes] / {error: SUBJECT_VERB_AGREEMENT_EXPECTED_PLURAL}

# Pronoun-Antecedent Gender Unification:
S1_M -> [he, him, his] / {pronoun_agreement: PASS}
S1_F -> [she, her, hers] / {pronoun_agreement: PASS}
S1_N -> [it, its] / {pronoun_agreement: PASS}
S2_PL -> [they, them, their] / {pronoun_agreement: PASS}
