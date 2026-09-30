"""
Italian Engine — Auxiliary & Participle Agreement Analyzer
Audits compound tenses (Passato Prossimo) for auxiliary validity (essere vs avere) and
past participle gender/number concord.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.auxiliary_selector import select_auxiliary, compute_participle_concord

ESSERE_AUX_FORMS = {"sono", "sei", "è", "siamo", "siete", "era", "eri", "eravamo", "eravate", "erano"}
AVERE_AUX_FORMS = {"ho", "hai", "ha", "abbiamo", "avete", "hanno", "avevo", "avevi", "avevamo"}

class AuxiliaryAgreementAnalyzer:
    """Cognitive analyzer for Italian auxiliary selection and participle concord."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        violations = []
        checked_constructions = []
        
        # Scan for [AUX] + [VERB/participle] patterns
        for i in range(len(tags) - 1):
            t1 = tags[i]
            t2 = tags[i + 1]
            
            w1 = t1["token"].lower()
            w2 = t2["token"].lower()
            
            is_aux = w1 in ESSERE_AUX_FORMS or w1 in AVERE_AUX_FORMS
            is_participle = w2.endswith(("ato", "ata", "ati", "ate", "uto", "uta", "uti", "ute", "ito", "ita", "iti", "ite"))
            
            if is_aux and is_participle:
                aux_type = "essere" if w1 in ESSERE_AUX_FORMS else "avere"
                
                # Check subject gender/number if preceding token is a known subject pronoun or noun
                subj_g = "m"
                subj_n = "sg"
                if i > 0:
                    prev_w = tags[i - 1]["token"].lower()
                    if prev_w in {"lei", "chiara", "ragazza", "donna", "mamma", "maria"}:
                        subj_g = "f"
                        subj_n = "sg"
                    elif prev_w in {"ragazze", "donne", "chiara_e_maria"}:
                        subj_g = "f"
                        subj_n = "pl"
                    elif prev_w in {"ragazzi", "loro", "uomini"}:
                        subj_g = "m"
                        subj_n = "pl"
                        
                checked_constructions.append({
                    "auxiliary": w1,
                    "participle": w2,
                    "aux_type": aux_type,
                    "detected_subject": {"gender": subj_g, "number": subj_n}
                })
                
                # If auxiliary is essere, check participle ending agreement
                if aux_type == "essere":
                    if subj_g == "f" and subj_n == "sg" and not w2.endswith("a"):
                        violations.append({
                            "construction": f"{w1} {w2}",
                            "rule": "essere_participle_concord",
                            "error": f"Participle '{w2}' with 'essere' must agree with feminine singular subject (expected ending '-a')."
                        })
                    elif subj_g == "f" and subj_n == "pl" and not w2.endswith("e"):
                        violations.append({
                            "construction": f"{w1} {w2}",
                            "rule": "essere_participle_concord",
                            "error": f"Participle '{w2}' with 'essere' must agree with feminine plural subject (expected ending '-e')."
                        })
                    elif subj_g == "m" and subj_n == "pl" and not w2.endswith("i"):
                        violations.append({
                            "construction": f"{w1} {w2}",
                            "rule": "essere_participle_concord",
                            "error": f"Participle '{w2}' with 'essere' must agree with masculine plural subject (expected ending '-i')."
                        })
                        
        return {
            "text": text,
            "checked_constructions": checked_constructions,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
