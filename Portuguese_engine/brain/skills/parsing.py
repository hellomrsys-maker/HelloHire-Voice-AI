"""
Portuguese Clausal Parser: Validates SVO order, pro-drop subject recovery,
and subjunctive mood triggers.
"""

from typing import Dict, Any, Optional, List, Tuple
from .tokenization import PortugueseTokenizer
from .pos_tagging import PortuguesePOSTagger
from .verb_conjugator import PortugueseVerbConjugator


class PortugueseParser:
    """
    Parses Portuguese clauses, identifies constituents, and evaluates mood triggers.
    """

    SUBJUNCTIVE_TRIGGERS = {
        "future_subjunctive": {"quando", "se", "assim que", "logo que", "enquanto"},
        "present_subjunctive": {"espero que", "quero que", "duvido que", "é preciso que", "embora", "para que"}
    }

    SUBJECT_PRONOUNS = {
        "eu": "1st_sg", "tu": "2nd_sg", "ele": "3rd_sg", "ela": "3rd_sg",
        "você": "3rd_sg", "nós": "1st_pl", "vós": "2nd_pl", "eles": "3rd_pl",
        "elas": "3rd_pl", "vocês": "3rd_pl"
    }

    def __init__(self):
        self.tokenizer = PortugueseTokenizer()
        self.tagger = PortuguesePOSTagger()
        self.conjugator = PortugueseVerbConjugator()

    def parse_sentence(self, sentence: str) -> Dict[str, Any]:
        """
        Parses a sentence into constituents and evaluates syntactic properties.
        """
        tokens = self.tokenizer.tokenize(sentence)
        tagged = self.tagger.tag_tokens(tokens)

        subject = None
        verb = None
        direct_obj = None
        is_pro_drop = True
        has_clitic = False
        subjunctive_trigger_found = False

        low_sentence = sentence.lower()
        for trig_type, triggers in self.SUBJUNCTIVE_TRIGGERS.items():
            for trig in triggers:
                if trig in low_sentence:
                    subjunctive_trigger_found = True
                    break

        for item in tagged:
            tok = item["token"]
            pos = item["pos"]
            low = tok.lower()

            if "-" in tok:
                has_clitic = True

            if pos == "PRON" and subject is None and low in self.SUBJECT_PRONOUNS:
                subject = tok
                is_pro_drop = False
            elif pos == "NOUN" and subject is None:
                subject = tok
                is_pro_drop = False
            elif pos == "VERB" and verb is None:
                verb = tok
            elif (pos == "NOUN" or pos == "PRON") and verb is not None and direct_obj is None:
                direct_obj = tok

        # Pro-drop recovery from verb inflection if subject was omitted
        recovered_subject = None
        if is_pro_drop and verb:
            clean_v = verb.split("-")[0].lower()
            lem_info = self.conjugator.lemmatize(clean_v)
            if lem_info:
                _, _, _, p = lem_info
                recovered_subject = p

        # Check SVO order: Did subject precede verb?
        is_svo = True
        if subject and verb:
            subj_idx = low_sentence.find(subject.lower())
            verb_idx = low_sentence.find(verb.lower())
            if subj_idx > verb_idx and subj_idx != -1 and verb_idx != -1:
                is_svo = False

        return {
            "tokens": tokens,
            "subject": subject,
            "recovered_subject": recovered_subject,
            "verb": verb,
            "direct_object": direct_obj,
            "is_pro_drop": is_pro_drop,
            "is_svo": is_svo,
            "has_clitic": has_clitic,
            "subjunctive_trigger": subjunctive_trigger_found
        }
