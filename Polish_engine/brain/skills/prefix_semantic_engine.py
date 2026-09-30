"""
Polish Prefix Semantic Engine (PPSE) — Tier 8 Implementation
=============================================================
Verbal prefixes in Polish are NOT merely perfectivizers. Each prefix carries a
distinct spatial-semantic frame that changes the verb's core meaning:

  prze-  : motion through / doing over / transition across a boundary
  na-    : accumulation / doing thoroughly / saturation
  za-    : initiation / beginning of state / going behind/away
  od-    : return / reversal / completion of a round-trip
  wy-    : motion outward / completion directed outward
  po-    : doing for a while / distribution across set / light action
  u-     : completion / final result / away from speaker
  roz-   : distribution / dispersal / intensification
  s-/z-  : collection / coming together / completion

Aspect Enforcement:
  Perfective verbs CANNOT carry a present-tense continuity interpretation.
  *napiszę teraz* means "I will write [it] now" (future), not "I am writing now."
  If a perfective form appears alongside present-continuity adverbs, flag it.

This engine:
  1. Detects prefixed verb forms in input text
  2. Identifies the prefix's semantic frame
  3. Detects prefix misuse (e.g., confusing prze- with na- for "writing completely")
  4. Enforces aspect-tense compatibility
  5. Returns structured diagnostics for the grammar checker pipeline
"""

import re
from typing import Dict, Any, List, Optional, Tuple

# ─── Prefix Semantic Frame Definitions ───────────────────────────────────────
PREFIX_SEMANTIC_FRAMES: Dict[str, Dict[str, Any]] = {
    "prze": {
        "name": "prze-",
        "spatial_frame": "THROUGH_OR_ACROSS",
        "primary_meanings": [
            "motion through a space or boundary (przejść — pass through)",
            "repetition / doing over (przepisać — rewrite, copy over)",
            "transition across a state boundary (przespać — sleep through)",
            "excess / overdoing (przepracować się — overwork)",
        ],
        "prototypical_verbs": {
            "przeczytać":  "read through completely",
            "przepisać":   "rewrite / copy out",
            "przejść":     "pass through / transition",
            "przemyć":     "rinse through / wash thoroughly",
            "przetłumaczyć": "translate across languages",
        },
        "misuse_patterns": [
            "prze- used where na- (accumulation) is intended",
            "prze- used where od- (reversal) is intended",
        ]
    },
    "na": {
        "name": "na-",
        "spatial_frame": "ACCUMULATION_OR_SATURATION",
        "primary_meanings": [
            "accumulation / collecting a quantity (nazbierać — gather up enough)",
            "thorough saturation (namoczyć — soak thoroughly)",
            "surface contact / onto (nałożyć — put onto)",
            "completion by filling (napić się — drink one's fill)",
        ],
        "prototypical_verbs": {
            "napisać":    "write [it] down / complete the writing",
            "nabrać":     "take in / accumulate / gather",
            "namoczyć":   "soak thoroughly",
            "nałożyć":    "put on / apply onto",
            "najeść się": "eat one's fill",
        },
        "misuse_patterns": [
            "na- confused with prze- (napisać ≠ przepisać: write vs. rewrite/copy)",
            "na- with non-transitive verb (incorrect accumulation frame)",
        ]
    },
    "za": {
        "name": "za-",
        "spatial_frame": "INITIATION_OR_BEHIND",
        "primary_meanings": [
            "initiation of a state / beginning (zacząć — begin)",
            "going behind / into a hidden state (zaskoczyć — ambush / surprise)",
            "sealing / closing off (zamknąć — close / lock)",
            "excessive doing (zasiedziieć się — sit too long)",
        ],
        "prototypical_verbs": {
            "zadzwonić": "phone / initiate a call",
            "zamknąć":   "close / lock",
            "zapytać":   "ask / initiate a question",
            "zasnąć":    "fall asleep / enter sleep state",
            "zapomnieć": "forget",
        },
        "misuse_patterns": [
            "za- with motion verbs where wy- (outward) is intended",
        ]
    },
    "od": {
        "name": "od-",
        "spatial_frame": "REVERSAL_OR_RETURN",
        "primary_meanings": [
            "reversal of action / undoing (odkleić — unstick / peel off)",
            "return to origin (odpłynąć — sail away from / back)",
            "response / reply (odpisać — write back / reply in writing)",
            "separation / away from (odjechać — drive away)",
        ],
        "prototypical_verbs": {
            "odpisać":    "write back / reply",
            "odkleić":    "peel off / unstick",
            "odejść":     "walk away / leave",
            "odpowiedzieć": "answer back / reply verbally",
            "odmówić":    "refuse / decline",
        },
        "misuse_patterns": [
            "od- confused with na- for 'reply in writing' vs 'write down'",
        ]
    },
    "wy": {
        "name": "wy-",
        "spatial_frame": "OUTWARD_COMPLETION",
        "primary_meanings": [
            "motion outward / extracting (wyjść — go out / exit)",
            "completion directed outward (wypisać — write out / copy out)",
            "spending completely (wydać — spend all / give out)",
            "production / bringing forth (wybudować — build up / construct)",
        ],
        "prototypical_verbs": {
            "wypisać":   "write out / extract in writing",
            "wyjść":     "go out / exit",
            "wydać":     "spend / publish / give out",
            "wytłumaczyć": "explain thoroughly / exhaust the explanation",
            "wybrać":    "choose / select out",
        },
        "misuse_patterns": [
            "wy- confused with na- for written output (wypisać ≠ napisać: write out ≠ write)",
        ]
    },
    "po": {
        "name": "po-",
        "spatial_frame": "LIGHT_ACTION_OR_DISTRIBUTION",
        "primary_meanings": [
            "light / brief action (pobiegać — run around for a while)",
            "distribution across a set (porozdawać — hand out to everyone)",
            "sequential completion (pozjeżdżać — arrive one by one)",
            "beginning of motion (pojechać — set off / go)",
        ],
        "prototypical_verbs": {
            "pojechać":  "go / set off (by vehicle)",
            "powiedzieć": "say / tell",
            "pobrać":    "download / take away",
            "pomyśleć":  "think for a moment",
            "pomóc":     "help",
        },
        "misuse_patterns": [
            "po- (brief action) used where na- (thorough saturation) is intended",
        ]
    },
    "u": {
        "name": "u-",
        "spatial_frame": "FINAL_COMPLETION_OR_REMOVAL",
        "primary_meanings": [
            "final completion / achieving a result (udać się — succeed)",
            "away from speaker / removal (uciec — flee / escape)",
            "gradual damage / wearing away (ugotować — cook done)",
        ],
        "prototypical_verbs": {
            "udać się":   "succeed",
            "uciec":      "flee",
            "ubrać":      "dress",
            "umyć":       "wash (completely)",
            "umrzeć":     "die",
        },
        "misuse_patterns": [
            "u- confused with z-/s- for completive meaning",
        ]
    },
    "roz": {
        "name": "roz-",
        "spatial_frame": "DISPERSAL_OR_INTENSIFICATION",
        "primary_meanings": [
            "dispersal / spreading apart (rozejść się — disperse / spread)",
            "undoing a contained state (rozwinąć — unroll / develop)",
            "intensification of process (rozśmieszyć — make laugh hard)",
        ],
        "prototypical_verbs": {
            "rozwinąć":   "unroll / develop",
            "rozumieć":   "understand (lit. spread understanding)",
            "rozmawiać":  "converse / spread the talking",
            "rozbudować": "expand / build out",
        },
        "misuse_patterns": [
            "roz- used where prze- (through/across) is intended",
        ]
    },
}

# ─── Adverbs that signal present-continuity interpretation ────────────────────
PRESENT_CONTINUITY_ADVERBS = {
    "teraz", "właśnie", "aktualnie", "ciągle", "nadal", "jeszcze", "wciąż", "w tej chwili"
}

# ─── Perfective-only conjugated forms (cannot mean present continuity) ────────
# Pattern: perfective future forms that look like present tense
PERFECTIVE_FUTURE_FORMS_PATTERN = re.compile(
    r"\b(napiszę|napisze|napiszesz|przeczytam|przeczyta|zrobię|zrobi|zrobisz"
    r"|kupi|kupisz|wyjdę|wyjdzie|zadzwonię|powie|odmówię|wybiorę)\b",
    re.IGNORECASE
)


class PolishPrefixSemanticEngine:
    """
    Detects verbal prefix usage in Polish text, validates semantic frame
    compatibility, and enforces aspect-tense constraints.
    """

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Full prefix semantic analysis of the input text.
        Returns detected prefixes, semantic frames, misuse flags,
        and aspect-tense compatibility result.
        """
        words = text.lower().split()
        detected = self._detect_prefixed_verbs(words)
        misuses  = self._detect_misuse(text, words, detected)
        tense_violations = self._check_aspect_tense_compatibility(text, words)

        return {
            "detected_prefixed_verbs": detected,
            "prefix_misuse_flags":     misuses,
            "aspect_tense_violations": tense_violations,
            "prefix_semantics_ok":     len(misuses) == 0 and len(tense_violations) == 0
        }

    def get_semantic_frame(self, verb_lemma: str) -> Optional[Dict[str, Any]]:
        """
        Looks up the semantic frame for a specific prefixed verb lemma.
        Returns the frame definition or None if the verb is unknown / unprefixed.
        """
        low = verb_lemma.lower().strip()
        for prefix, frame in PREFIX_SEMANTIC_FRAMES.items():
            if low in frame["prototypical_verbs"]:
                return {
                    "verb":            low,
                    "prefix":          prefix,
                    "frame_name":      frame["spatial_frame"],
                    "meaning":         frame["prototypical_verbs"][low],
                    "primary_meanings": frame["primary_meanings"]
                }
        return None

    def explain_prefix(self, prefix: str) -> Optional[Dict[str, Any]]:
        """Returns the full semantic frame definition for a prefix string."""
        return PREFIX_SEMANTIC_FRAMES.get(prefix.lower().rstrip("-"))

    def _detect_prefixed_verbs(self, words: List[str]) -> List[Dict[str, Any]]:
        """Detects words that match known prefixed verb lemmas."""
        detected = []
        for w in words:
            for prefix, frame in PREFIX_SEMANTIC_FRAMES.items():
                if w in frame["prototypical_verbs"]:
                    detected.append({
                        "word":       w,
                        "prefix":     prefix,
                        "frame_name": frame["spatial_frame"],
                        "meaning":    frame["prototypical_verbs"][w],
                    })
                    break
        return detected

    def _detect_misuse(
        self, text: str, words: List[str], detected: List[Dict]
    ) -> List[str]:
        """
        Detects specific prefix confusion patterns.
        """
        misuses = []
        text_low = text.lower()

        # Pattern 1: napisać (na- = write down) vs. przepisać (prze- = rewrite/copy)
        if "napisać" in text_low and "ponownie" in text_low:
            misuses.append(
                "Prefix misuse candidate: 'napisać ponownie' is redundant. "
                "Use 'przepisać' (prze- = do over/copy) for 'rewrite'."
            )

        # Pattern 2: odpisać (od- = write back) vs. napisać (na- = write down)
        if "napisać" in text_low and any(w in text_low for w in ("odpowiedź", "odpowiedzi", "reply", "odpowiedz")):
            misuses.append(
                "Prefix misuse candidate: for 'write back / reply', prefer 'odpisać' "
                "(od- = reversal/response) over 'napisać' (na- = write down/accumulation)."
            )

        # Pattern 3: wypisać (wy- = write out/extract) vs. napisać (na- = write/compose)
        for d in detected:
            if d["word"] == "wypisać" and "list" in text_low:
                misuses.append(
                    "Note: 'wypisać' means 'write out / extract in writing'. "
                    "For 'compose a letter', prefer 'napisać list' (na- = bring into being)."
                )

        return misuses

    def _check_aspect_tense_compatibility(self, text: str, words: List[str]) -> List[str]:
        """
        Enforces: perfective forms CANNOT carry a present-continuity interpretation.
        Detects perfective future forms co-occurring with present-continuity adverbs.
        """
        violations = []
        pf_matches = PERFECTIVE_FUTURE_FORMS_PATTERN.findall(text)
        if not pf_matches:
            return violations

        adverb_matches = [w for w in words if w in PRESENT_CONTINUITY_ADVERBS]
        if adverb_matches and pf_matches:
            for pf_form in pf_matches:
                violations.append(
                    f"Aspect-Tense Violation: '{pf_form}' is a perfective future form "
                    f"and cannot express present continuity. "
                    f"Adverb(s) {adverb_matches} suggest present-continuity intent — "
                    f"use the imperfective counterpart (e.g., 'pisze' not 'napisze', "
                    f"'czyta' not 'przeczyta')."
                )
        return violations
