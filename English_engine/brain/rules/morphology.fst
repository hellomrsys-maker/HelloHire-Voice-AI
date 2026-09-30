# morphology.fst - English Inflectional & Derivational Morphological Allomorphy FST

# Plural and 3SG Verb Allomorphy (/s/, /z/, /ɪz/):
RULE s_allomorphy:
  AFTER [s, z, sh, ch, x, j]  -> INSERT "es"  # bus -> buses, watch -> watches (/ɪz/)
  AFTER [p, t, k, f, th_voiceless] -> INSERT "s" # cat -> cats, book -> books (/s/)
  DEFAULT                     -> INSERT "s"   # dog -> dogs, run -> runs (/z/)

# Consonant Doubling (CVC Final Stressed Syllable):
RULE consonant_doubling:
  PATTERN: Consonant + ShortVowel + Consonant (single) + VowelSuffix
  EXAMPLES:
    stop + ed  -> stopped
    run + ing  -> running
    fit + est  -> fittest
    refer + ed -> referred

# Silent 'e' Deletion:
RULE silent_e_deletion:
  PATTERN: Root ending in silent 'e' + VowelSuffix (-ing, -ed, -er, -able)
  EXAMPLES:
    write + ing -> writing
    love + ed   -> loved
    make + er   -> maker

# 'y' to 'i' Alternation:
RULE y_to_i:
  PATTERN: Consonant + 'y' + Suffix (-es, -ed, -er, -est, -ly)
  EXCEPT: Before -ing (studying, flying)
  EXAMPLES:
    study + es -> studies
    carry + ed -> carried
    happy + ly -> happily
