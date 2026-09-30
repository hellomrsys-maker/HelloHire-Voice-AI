"""
Italian Engine — Sentence Generation Skill
Synthesizes Italian sentences in canonical SVO order with accurate clitic placement and agreement.
"""

from typing import Optional, List
from .verb_conjugator import conjugate_verb
from .clitic_engine import combine_clitics, attach_enclitic
from .auxiliary_selector import select_auxiliary, compute_participle_concord

def generate_sentence(
    subject: Optional[str],
    verb_lemma: str,
    direct_object: Optional[str] = None,
    indirect_object: Optional[str] = None,
    tense: str = "presente",
    person: str = "3sg",
    clitic_direct: Optional[str] = None,
    clitic_indirect: Optional[str] = None,
    subject_gender: str = "m",
    subject_number: str = "sg"
) -> str:
    """
    Generate an Italian clause.
    Example: generate_sentence("Marco", "leggere", "il libro") -> "Marco legge il libro."
             generate_sentence(None, "andare", tense="passato_prossimo", person="3sg", subject_gender="f") -> "È andata."
    """
    parts = []
    
    # 1. Subject (optional pro-drop)
    if subject:
        parts.append(subject)
        
    # 2. Clitics (if present before finite verb)
    if clitic_indirect and clitic_direct:
        cluster = combine_clitics(clitic_indirect, clitic_direct)
        parts.append(cluster)
    elif clitic_indirect:
        parts.append(clitic_indirect)
    elif clitic_direct:
        parts.append(clitic_direct)
        
    # 3. Verb inflection
    if tense == "passato_prossimo":
        aux = select_auxiliary(verb_lemma)
        aux_form = conjugate_verb(aux, "presente", person)
        raw_participle = conjugate_verb(verb_lemma, "participio_passato")
        participle = compute_participle_concord(
            raw_participle,
            aux,
            subject_gender=subject_gender,
            subject_number=subject_number,
            preceding_clitic_gender=clitic_direct[0] if clitic_direct else None
        )
        parts.append(f"{aux_form} {participle}")
    else:
        v_form = conjugate_verb(verb_lemma, tense, person)
        parts.append(v_form)
        
    # 4. Objects
    if direct_object and not clitic_direct:
        parts.append(direct_object)
    if indirect_object and not clitic_indirect:
        parts.append(indirect_object)
        
    clause = " ".join(parts).strip()
    if clause and not clause.endswith((".", "!", "?")):
        clause += "."
    return clause[0].upper() + clause[1:] if clause else ""
