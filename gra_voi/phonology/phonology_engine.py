"""
Pronunciation, Phonetics, and Phonological Intelligence Module.

Covers:
  - Phonemic decomposition & IPA notation
  - Syllable anatomy (Onset, Nucleus, Coda) & Sonority Sequencing Principle
  - Lexical, compound, and nuclear sentence stress
  - Grammatical stress shifts changing word class (Noun-Verb diathesis)
  - Rhythm typologies: Stress-timed vs Syllable-timed vs Mora-timed
  - Connected speech processes (Assimilation, Elision, Liaison, Vowel Reduction, Flapping)
  - Tone systems in tonal languages (Mandarin, Yoruba, Vietnamese)
  - Cross-linguistic L1 transfer and mispronunciation diagnostic
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from ..common.models import (
    PhoneticAnalysis,
    SyllableStructure,
)


class PhonologyEngine:
    """
    Phonological intelligence system analyzing speech sounds, prosody,
    phonotactic constraints, connected speech, and grammar-pronunciation interactions.
    """

    def __init__(self):
        self._ipa_lexicon: Dict[str, Dict[str, Any]] = {
            # English entries with grammatical class alternations
            "record": {
                "noun": {"ipa": "ˈrɛk.ərd", "stress": "Initial (Trochaic)", "syllables": ["rɛk", "ərd"]},
                "verb": {"ipa": "rɪˈkɔːrd", "stress": "Final (Iambic)", "syllables": ["rɪ", "kɔːrd"]},
                "shift_explanation": "Initial stress /ˈrɛkərd/ marks the nominal entity; iambic stress shift /rɪˈkɔːrd/ marks verbal eventive predication."
            },
            "present": {
                "noun": {"ipa": "ˈprɛz.ənt", "stress": "Initial (Trochaic)", "syllables": ["prɛz", "ənt"]},
                "verb": {"ipa": "prɪˈzɛnt", "stress": "Final (Iambic)", "syllables": ["prɪ", "zɛnt"]},
                "shift_explanation": "Initial stress /ˈprɛzənt/ marks noun (gift) or adjective; final stress /prɪˈzɛnt/ marks transitive verb (to exhibit)."
            },
            "object": {
                "noun": {"ipa": "ˈɒb.dʒɪkt", "stress": "Initial (Trochaic)", "syllables": ["ɒb", "dʒɪkt"]},
                "verb": {"ipa": "əbˈdʒɛkt", "stress": "Final (Iambic)", "syllables": ["əb", "dʒɛkt"]},
                "shift_explanation": "Stress shift to final syllable /əbˈdʒɛkt/ signals verbalization accompanied by vowel reduction of initial syllable to schwa /ə/."
            },
            "conduct": {
                "noun": {"ipa": "ˈkɒn.dʌkt", "stress": "Initial (Trochaic)", "syllables": ["kɒn", "dʌkt"]},
                "verb": {"ipa": "kənˈdʌkt", "stress": "Final (Iambic)", "syllables": ["kən", "dʌkt"]},
                "shift_explanation": "Initial stress /ˈkɒndʌkt/ for noun (behavior); second-syllable stress /kənˈdʌkt/ for verb (to direct)."
            },
            "contrast": {
                "noun": {"ipa": "ˈkɒn.trɑːst", "stress": "Initial (Trochaic)", "syllables": ["kɒn", "trɑːst"]},
                "verb": {"ipa": "kənˈtrɑːst", "stress": "Final (Iambic)", "syllables": ["kən", "trɑːst"]},
                "shift_explanation": "Noun has full vowel and initial primary stress; verb shifts stress to root /trɑːst/ and reduces prefix to /kən/."
            },
            "philosophy": {
                "default": {"ipa": "fɪˈlɒs.ə.fi", "stress": "Antepenultimate (3rd from end)", "syllables": ["fɪ", "lɒs", "ə", "fi"]}
            },
            "linguistics": {
                "default": {"ipa": "lɪŋˈɡwɪs.tɪks", "stress": "Penultimate (2nd from end)", "syllables": ["lɪŋ", "ɡwɪs", "tɪks"]}
            },
            "communication": {
                "default": {"ipa": "kəˌmjuː.nɪˈkeɪ.ʃən", "stress": "Penultimate primary, initial secondary", "syllables": ["kə", "mjuː", "nɪ", "keɪ", "ʃən"]}
            }
        }

        self._tonal_language_profiles = {
            "Mandarin": {
                "type": "Contour Tone System (4 Lexical Tones + Neutral)",
                "tones": {
                    "Tone 1 (High Level)": {"pitch": "55 (High level)", "ipa_diacritic": "˥ (e.g., mā 妈 = mother)"},
                    "Tone 2 (Rising)": {"pitch": "35 (Mid-to-high rising)", "ipa_diacritic": "˧˥ (e.g., má 麻 = hemp)"},
                    "Tone 3 (Dipping)": {"pitch": "214 (Low falling-rising)", "ipa_diacritic": "˨˩˦ (e.g., mǎ 马 = horse)"},
                    "Tone 4 (Falling)": {"pitch": "51 (High falling)", "ipa_diacritic": "˥˩ (e.g., mà 骂 = scold)"},
                    "Neutral Tone": {"pitch": "Light, unstressed", "ipa_diacritic": "dot (e.g., ma 吗 = question particle)"}
                },
                "grammar_interaction": "Tone sandhi: When two 3rd tones occur consecutively (e.g., 你好 nǐ hǎo), the first automatically shifts phonetically to a 2nd tone (ní hǎo) without changing orthography."
            },
            "Yoruba": {
                "type": "Level Register Tone System (3 Contrastive Tones)",
                "tones": {
                    "High Tone (Ó)": {"pitch": "High pitch", "ipa_diacritic": "Acute accent / ́/"},
                    "Mid Tone (O)": {"pitch": "Mid pitch", "ipa_diacritic": "Unmarked"},
                    "Low Tone (Ò)": {"pitch": "Low pitch", "ipa_diacritic": "Grave accent / ̀/"}
                },
                "grammar_interaction": "Tone distinguishes grammatical subject and verb agreement; tone elision occurs across vowel-coalescing morpheme boundaries."
            },
            "Vietnamese": {
                "type": "Register-Contour System with Phonation Contrasts (6 Tones)",
                "tones": {
                    "Ngang (Level)": {"pitch": "Mid-level, modal voice"},
                    "Huyền (Hanging)": {"pitch": "Low falling, breathy voice"},
                    "Sắc (Sharp)": {"pitch": "High rising, tense voice"},
                    "Hỏi (Asking)": {"pitch": "Mid falling-rising, modal/glottalized"},
                    "Ngã (Tumbling)": {"pitch": "High rising with glottal break / creaky voice"},
                    "Nặng (Heavy)": {"pitch": "Low constricted / glottal stop drop"}
                },
                "grammar_interaction": "Tones function purely lexically; minimal tone pairs completely change morphemic identity (e.g., ma [ghost], má [mother], mà [which/but], mả [tomb], mã [horse], mạ [rice seedling])."
            }
        }

        self._rhythm_typologies = {
            "stress-timed": {
                "languages": ["English", "German", "Russian", "Dutch", "Arabic"],
                "principle": "Isochrony: The intervals between consecutive stressed syllables are approximately equal, regardless of the number of intervening unstressed syllables.",
                "consequence": "Unstressed syllables undergo extreme compression, vowel reduction to schwa [ə] or [ɪ], and consonant cluster elision."
            },
            "syllable-timed": {
                "languages": ["Spanish", "French", "Italian", "Cantonese", "Telugu"],
                "principle": "Each syllable takes roughly the same duration to pronounce, creating a machine-gun staccato rhythm.",
                "consequence": "Vowels in unstressed syllables retain their full vowel quality and length without reducing to schwa."
            },
            "mora-timed": {
                "languages": ["Japanese", "Luganda", "Ancient Greek"],
                "principle": "Each mora (sub-syllabic timing unit consisting of a short vowel, a coda nasal, or a geminate consonant) takes equal temporal duration.",
                "consequence": "Syllables are categorized as light (1 mora) or heavy (2 morae), regulating poetic meter and pitch accent assignment."
            }
        }

        self._mispronunciation_diagnostic = {
            "Spanish": {
                "phonological_transfer": "Spanish has only 5 pure vowel phonemes and disallows initial /s/ + consonant clusters.",
                "common_errors": [
                    "Epenthesis of /e/ before /s/-clusters ('eschool' for 'school', 'especial' for 'special').",
                    "Neutralization of /b/ and /v/ into bilabial fricative [β].",
                    "Pronouncing unstressed vowels with full phonetic quality instead of reducing to schwa /ə/.",
                    "Substituting dental stop [t̪] for voiceless interdental fricative /θ/ ('tink' for 'think')."
                ]
            },
            "Mandarin": {
                "phonological_transfer": "Mandarin permits only /n/ and /ŋ/ as syllable codas and lacks voiced stops /b, d, ɡ/ (distinguishing stops solely by aspiration).",
                "common_errors": [
                    "Deletion or glottalization of final stop consonants /p, t, k, d/ ('cat' -> [kæ]).",
                    "Neutralization of liquid consonants /l/ and /r/ in certain dialectal backgrounds.",
                    "Vowel epenthesis in complex consonant clusters ('st-reet' -> [sə-tri-tə]).",
                    "Imposing rigid lexical tone contours on English intonational pitch contours."
                ]
            },
            "French": {
                "phonological_transfer": "French has fixed phrase-final rhythmic stress and completely lacks the phoneme /h/.",
                "common_errors": [
                    "Omission of initial glottal fricative /h/ ('appy' for 'happy', 'eart' for 'heart') or hypercorrect intrusion of [h] where absent.",
                    "Replacing interdental fricatives /θ, ð/ with alveolar sibilants [s, z] ('sink' for 'think', 'ze' for 'the').",
                    "Lack of variable lexical word stress, placing uniform stress on the final syllable of every word."
                ]
            },
            "German": {
                "phonological_transfer": "German operates terminal devoicing (Auslautverhärtung) and uses labiodental /v/ for orthographic 'w'.",
                "common_errors": [
                    "Terminal devoicing of final voiced obstruents ('bad' -> [bæt], 'dog' -> [dɔk]).",
                    "Pronouncing English labiovelar glide /w/ as voiced labiodental fricative /v/ ('vater' for 'water').",
                    "Over-aspirating initial voiceless stops."
                ]
            }
        }

    def analyze_phonology(self, word_or_sentence: str, grammatical_role: str = "noun", language: str = "English") -> PhoneticAnalysis:
        """
        Produce a complete phonetic, syllable, stress, and rhythm analysis of the input.
        """
        token = word_or_sentence.strip().lower()

        # Check lexicon
        lex_data = self._ipa_lexicon.get(token, {})
        role_key = grammatical_role.lower()

        if role_key in lex_data:
            entry = lex_data[role_key]
            ipa_val = entry["ipa"]
            stress_pat = entry["stress"]
            syl_tokens = entry["syllables"]
            shift_note = lex_data.get("shift_explanation", "")
        elif "default" in lex_data:
            entry = lex_data["default"]
            ipa_val = entry["ipa"]
            stress_pat = entry["stress"]
            syl_tokens = entry["syllables"]
            shift_note = ""
        else:
            # Algorithmic phonetic approximation
            ipa_val = self._approximate_ipa(token)
            stress_pat = "Initial (Trochaic) default"
            syl_tokens = self._approximate_syllables(token)
            shift_note = ""

        # Build syllable structures
        syllables: List[SyllableStructure] = []
        for i, s in enumerate(syl_tokens):
            onset, nuc, coda = self._decompose_syllable(s)
            is_stressed = (i == 0 and "initial" in stress_pat.lower()) or (i == len(syl_tokens) - 1 and "final" in stress_pat.lower())
            syllables.append(SyllableStructure(
                onset=onset,
                nucleus=nuc,
                coda=coda,
                ipa=s,
                is_stressed=is_stressed
            ))

        # Connected speech and intonation
        connected = self._compute_connected_speech_effects(word_or_sentence)
        intonation = self._determine_intonation_contour(word_or_sentence)

        # L1 risks
        l1_risks = {lang: d["common_errors"][0] for lang, d in self._mispronunciation_diagnostic.items()}

        return PhoneticAnalysis(
            token=word_or_sentence,
            ipa=ipa_val,
            syllables=syllables,
            stress_pattern=stress_pat,
            rhythm_type="Stress-Timed (Isochronous foot duration)" if language == "English" else "Syllable-Timed",
            intonation_contour=intonation,
            connected_speech_effects=connected,
            grammatical_stress_shift_note=shift_note,
            l1_mispronunciation_risks=l1_risks
        )

    def _approximate_ipa(self, word: str) -> str:
        """Heuristic rule-based grapheme-to-phoneme transcription."""
        replacements = [
            ("ph", "f"), ("th", "θ"), ("sh", "ʃ"), ("ch", "tʃ"),
            ("ee", "iː"), ("oo", "uː"), ("ar", "ɑːr"), ("or", "ɔːr"),
            ("tion", "ʃən"), ("ing", "ɪŋ")
        ]
        res = word.lower()
        for g, p in replacements:
            res = res.replace(g, p)
        return f"/{res}/"

    def _approximate_syllables(self, word: str) -> List[str]:
        """Heuristic syllabification splitting on vowel nucleii."""
        chunks = re.findall(r"[^aeiouy]*[aeiouy]+[^aeiouy]*", word, re.IGNORECASE)
        return chunks if chunks else [word]

    def _decompose_syllable(self, syl: str) -> Tuple[str, str, str]:
        """Split a syllable into Onset, Nucleus, Coda."""
        m = re.match(r"^([^aeiouy]*)([aeiouy]+)(.*)$", syl, re.IGNORECASE)
        if m:
            return m.group(1), m.group(2), m.group(3)
        return "", syl, ""

    def _determine_intonation_contour(self, sentence: str) -> str:
        s = sentence.strip()
        if s.endswith("?"):
            if any(s.lower().startswith(w) for w in ["who", "what", "where", "when", "why", "how"]):
                return "Wh-Question Contour: High starting pitch falling to terminal Low Fall (↘)."
            return "Polar (Yes/No) Interrogative: Terminal High Rise (↗) signaling incompleteness/solicitation."
        elif s.endswith("!"):
            return "Exclamatory Contour: Rapid High Rise followed by steep terminal Fall (↗↘)."
        return "Declarative Assertion: Unmarked Final Cadence / Low Fall (↘)."

    def _compute_connected_speech_effects(self, sentence: str) -> List[str]:
        effects = []
        lower = sentence.lower()
        if "did you" in lower:
            effects.append("Coalescent Assimilation: /d/ + /j/ merges into affricate [dʒ] -> [dɪdʒuː].")
        if "ten boys" in lower or "in paris" in lower:
            effects.append("Regressive Place Assimilation: Alveolar nasal /n/ assimilates to bilabial [m] before bilabial stop [b/p].")
        if "next day" in lower or "last night" in lower:
            effects.append("Alveolar Stop Elision: Terminal /t/ in coda cluster deleted before initial consonant [n/d].")
        if "water" in lower or "city" in lower or "butter" in lower:
            effects.append("Intervocalic Flapping (North American): Intervocalic /t/ articulated as voiced alveolar tap [ɾ].")
        if not effects:
            effects.append("Vowel Reduction: Unstressed functional syllables undergo centralization to schwa [ə].")
        return effects

    def get_tonal_language_details(self, language: str) -> Dict[str, Any]:
        """Return tone system specifications for tonal languages."""
        return self._tonal_language_profiles.get(language, {})

    def get_l1_transfer_diagnostic(self, native_language: str) -> Dict[str, Any]:
        """Retrieve phonological transfer risks for a specific L1."""
        return self._mispronunciation_diagnostic.get(native_language, {})
