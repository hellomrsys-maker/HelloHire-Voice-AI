# Finite State Transducer (FST) - Japanese 6-Stem Verb Conjugation Paradigm
# Stems: 1: Mizenkei (未然), 2: Ren'youkei (連用), 3: Shuushikei (終止), 4: Rentaikei (連体), 5: Kateikei (仮定), 6: Meireikei (命令)

# Base Godan (e.g., 書く k-ak-u)
0 1 書か [STEM_MIZEN] 0.1
0 2 書き [STEM_RENYOU] 0.1
0 3 書く [STEM_SHUUSHI] 0.1
0 4 書く [STEM_RENTAI] 0.1
0 5 書け [STEM_KATEI] 0.1
0 6 書け [STEM_MEIREI] 0.1

# Base Ichidan (e.g., 食べる tabe-ru)
0 1 食べ [STEM_MIZEN] 0.1
0 2 食べ [STEM_RENYOU] 0.1
0 3 食べる [STEM_SHUUSHI] 0.1
0 4 食べる [STEM_RENTAI] 0.1
0 5 食べれ [STEM_KATEI] 0.1
0 6 食べろ [STEM_MEIREI] 0.1

# Base Kuru (カ行変格)
0 1 こ [STEM_MIZEN] 0.1
0 2 き [STEM_RENYOU] 0.1
0 3 くる [STEM_SHUUSHI] 0.1
0 4 くる [STEM_RENTAI] 0.1
0 5 くれ [STEM_KATEI] 0.1
0 6 こい [STEM_MEIREI] 0.1

# Base Suru (サ行変格)
0 1 し [STEM_MIZEN] 0.1
0 2 し [STEM_RENYOU] 0.1
0 3 する [STEM_SHUUSHI] 0.1
0 4 する [STEM_RENTAI] 0.1
0 5 すれ [STEM_KATEI] 0.1
0 6 しろ [STEM_MEIREI] 0.1

# Suffix Transitions from Mizenkei (1)
1 10 ない [NEGATIVE_PRESENT] 0.1
1 10 なかった [NEGATIVE_PAST] 0.2
1 11 れる [PASSIVE_GODAN] 0.3
1 11 られる [PASSIVE_ICHIDAN] 0.3
1 12 せる [CAUSATIVE_GODAN] 0.3
1 12 させる [CAUSATIVE_ICHIDAN] 0.3
1 13 う [VOLITIONAL_GODAN] 0.2
1 13 よう [VOLITIONAL_ICHIDAN] 0.2

# Suffix Transitions from Ren'youkei (2)
2 20 ます [POLITE_NONPAST] 0.1
2 20 ました [POLITE_PAST] 0.1
2 20 ません [POLITE_NEGATIVE] 0.1
2 21 たい [DESIDERATIVE] 0.2
2 22 て [GERUNDIVE_TE] 0.1
2 23 た [PERFECTIVE_TA] 0.1

# Suffix Transitions from Kateikei (5)
5 30 ば [CONDITIONAL_BA] 0.1
