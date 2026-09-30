"""
French Auxiliary & Agreement Cognitive Analyzer.
Analyzes compound tense constructions to verify auxiliary selection (être vs avoir)
and past participle concordance rules.
"""

from typing import Dict, Any, List, Optional
from ..skills.verb_conjugator import FrenchVerbConjugator
from ..skills.agreement_engine import FrenchAgreementEngine


class AuxiliaryAgreementAnalyzer:
    """
    Cognitive analyzer diagnosing compound tense correctness and past participle concord.
    """

    def __init__(self):
        self.conjugator = FrenchVerbConjugator()
        self.agreement_engine = FrenchAgreementEngine()

    def analyze_construction(
        self,
        verb_lemma: str,
        auxiliary_used: str,  # "est", "a", "sont", "ont", etc.
        participle_surface: str,
        subject_gender: str = "M",
        subject_number: str = "SG",
        cod_precedes: bool = False,
        cod_gender: Optional[str] = None,
        cod_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validates whether the chosen auxiliary matches the lemma's argument structure
        and whether the participle displays correct inflectional concord.
        """
        expected_aux_type = self.conjugator.get_auxiliary(verb_lemma)
        aux_low = auxiliary_used.lower()

        # Check auxiliary category
        is_etre_form = aux_low in {"suis", "es", "est", "sommes", "êtes", "sont", "étais", "était"}
        is_avoir_form = aux_low in {"ai", "as", "a", "avons", "avez", "ont", "avais", "avait"}

        actual_aux_type = "être" if is_etre_form else ("avoir" if is_avoir_form else "unknown")
        aux_correct = actual_aux_type == expected_aux_type

        # Check participle agreement
        base_participle = self.conjugator.get_past_participle(verb_lemma)

        if expected_aux_type == "être":
            agreement_result = self.agreement_engine.evaluate_participle_with_etre(
                subject_gender=subject_gender,
                subject_number=subject_number,
                participle_base=base_participle,
                participle_surface=participle_surface
            )
        else:
            agreement_result = self.agreement_engine.evaluate_participle_with_avoir(
                cod_precedes=cod_precedes,
                cod_gender=cod_gender,
                cod_number=cod_number,
                participle_base=base_participle,
                participle_surface=participle_surface
            )

        overall_valid = aux_correct and agreement_result["is_valid"]

        return {
            "verb_lemma": verb_lemma,
            "expected_auxiliary": expected_aux_type,
            "actual_auxiliary": actual_aux_type,
            "auxiliary_correct": aux_correct,
            "participle_agreement": agreement_result,
            "is_grammatically_sound": overall_valid,
            "diagnostic_message": (
                "Construction verbale composée parfaitement conforme."
                if overall_valid
                else f"Anomalie détectée: Auxiliaire {'incorrect' if not aux_correct else 'valide'}, Participe {'incorrect' if not agreement_result['is_valid'] else 'valide'}."
            )
        }
