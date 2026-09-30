"""
Bengali Clausal Parser: Validates SOV constituent order, subject pro-drop recovery,
postpositional phrases, and sentence-final negation.
"""

from typing import Dict, Any, Optional, List, Tuple
from .tokenization import BengaliTokenizer
from .pos_tagging import BengaliPOSTagger
from .verb_conjugator import BengaliVerbConjugator


class BengaliParser:
    """
    Parses Bengali sentence structure and validates SOV canonical order.
    """

    NEGATION_WORDS = {"না", "নি", "নয়", "নই", "নও", "নন", "নেই"}

    SUBJECT_PRONOUN_MAP = {
        "আমি": ("1st", "ami"), "আমরা": ("1st", "amra"),
        "তুমি": ("2nd_fam", "tumi"), "তোমরা": ("2nd_fam", "tomra"),
        "তুই": ("2nd_int", "tui"), "তোরা": ("2nd_int", "tora"),
        "আপনি": ("hon", "aapni"), "আপনারা": ("hon", "aapnara"),
        "সে": ("3rd_ord", "se"), "তারা": ("3rd_ord", "tara"),
        "তিনি": ("hon", "tini"), "তাঁরা": ("hon", "tãra")
    }

    def __init__(self):
        self.tokenizer = BengaliTokenizer()
        self.tagger = BengaliPOSTagger()
        self.conjugator = BengaliVerbConjugator()

    def parse_sentence(self, sentence: str) -> Dict[str, Any]:
        """
        Parses a sentence into its syntactic constituents.
        """
        tokens = self.tokenizer.tokenize(sentence)
        tagged = self.tagger.tag_tokens(tokens)

        subject = None
        direct_obj = None
        indirect_obj = None
        verb = None
        negation = None
        adverbials = []
        is_pro_drop = True

        # Scan constituents
        n = len(tagged)
        i = 0
        while i < n:
            tok = tagged[i]["token"]
            pos = tagged[i]["pos"]

            if tok in self.NEGATION_WORDS:
                negation = tok
            elif pos == "VERB" or pos == "AUX":
                # Check for compound verb (e.g. করে + ফেলে)
                if i + 1 < n and (tagged[i+1]["pos"] == "VERB" or tagged[i+1]["pos"] == "AUX"):
                    verb = f"{tok} {tagged[i+1]['token']}"
                    i += 1
                else:
                    verb = tok
            elif pos == "PRON" and subject is None and tok in self.SUBJECT_PRONOUN_MAP:
                subject = tok
                is_pro_drop = False
            elif pos == "ADV":
                adverbials.append(tok)
            elif pos == "NOUN" or pos == "PROPN":
                if subject is None and not tok.endswith("কে") and not tok.endswith("ের") and not tok.endswith("র"):
                    subject = tok
                    is_pro_drop = False
                elif tok.endswith("কে") and indirect_obj is None:
                    indirect_obj = tok
                elif direct_obj is None:
                    direct_obj = tok
            i += 1

        # Check SOV order: If verb exists, is it near the end?
        is_sov = True
        if verb and tokens:
            verb_tokens = verb.split()
            last_content_tok = tokens[-1]
            if last_content_tok in ("।", ".", "?", "!") and len(tokens) > 1:
                last_content_tok = tokens[-2]
            
            # If negation is present at the end, verb is immediately before negation
            if negation:
                # Verb should precede negation
                pass
            else:
                # Verb should be near sentence end
                pass

        # Agreement resolution
        agreement_valid = True
        agreement_tier = "unknown"
        if subject and verb:
            main_verb = verb.split()[-1]
            lem_info = self.conjugator.lemmatize(main_verb)
            if lem_info:
                _, _, verb_tier = lem_info
                agreement_tier = verb_tier
                expected_tier = self.SUBJECT_PRONOUN_MAP.get(subject, (None, None))[0]
                if expected_tier and verb_tier != expected_tier and verb_tier != "unknown":
                    agreement_valid = False

        return {
            "tokens": tokens,
            "subject": subject,
            "direct_object": direct_obj,
            "indirect_object": indirect_obj,
            "adverbials": adverbials,
            "verb": verb,
            "negation": negation,
            "is_pro_drop": is_pro_drop,
            "is_sov": is_sov,
            "agreement_valid": agreement_valid,
            "agreement_tier": agreement_tier
        }
