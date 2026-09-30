"""
Hindustani Ergative Alignment Cognitive Analyzer.
Diagnoses split-ergative alignment violations, verifying that transitive verbs
in the perfective aspect carry the overt 'ne' postposition on the subject
and that verbal agreement pivots to the unmarked direct object.
"""

from typing import Dict, Any, List, Optional
from ..skills.tokenization import HindustaniTokenizer
from ..skills.pos_tagging import HindustaniPOSTagger
from ..skills.parsing import HindustaniParser, HindustaniSentenceStructure
from ..skills.ergative_engine import ErgativeSplitEngine


class ErgativeAlignmentAnalyzer:
    """
    Cognitive diagnostic module enforcing the Indo-Aryan split-ergative paradigm.
    """

    def __init__(self):
        self.tokenizer = HindustaniTokenizer()
        self.tagger = HindustaniPOSTagger()
        self.parser = HindustaniParser()
        self.ergative_engine = ErgativeSplitEngine()

    def analyze_clause(
        self,
        subject: str,
        verb_lemma: str,
        aspect: str,
        obj: Optional[str] = None,
        object_gender: str = "M",
        object_number: str = "SG",
        verb_surface: str = ""
    ) -> Dict[str, Any]:
        subj_tokens = self.tokenizer.tokenize(subject)
        obj_tokens = self.tokenizer.tokenize(obj) if obj else []

        eval_res = self.ergative_engine.evaluate_clause(
            subject_phrase=subj_tokens,
            verb_lemma=verb_lemma,
            aspect=aspect,
            object_phrase=obj_tokens,
            object_gender=object_gender,
            object_number=object_number,
            verb_surface=verb_surface
        )

        return eval_res
