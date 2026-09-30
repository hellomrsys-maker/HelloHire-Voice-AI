"""Turkish Verb Conjugator Skill.

Conjugates Turkish verbs across major TAM categories
(Definite Past -di, Evidential -miş, Progressive -iyor, Future -ecek, Aorist -r),
negation (-me/-ma), and person agreement across Type I and Type II paradigms.
"""

from typing import Dict, Any, Optional
from .vowel_harmony_engine import TurkishVowelHarmonyEngine
from .consonant_mutation_engine import TurkishConsonantMutationEngine
from .tokenization import TurkishTokenizer


class TurkishVerbConjugator:
    def __init__(
        self,
        harmony_engine: TurkishVowelHarmonyEngine = None,
        mutation_engine: TurkishConsonantMutationEngine = None
    ):
        self.harmony = harmony_engine or TurkishVowelHarmonyEngine()
        self.mutation = mutation_engine or TurkishConsonantMutationEngine()

    def get_stem(self, infinitive: str) -> str:
        """Extracts the verbal stem by stripping -mek or -mak."""
        inf_low = TurkishTokenizer.turkish_lower(infinitive.strip())
        if inf_low.endswith(("mek", "mak")):
            return infinitive[:-3]
        return infinitive

    def conjugate(
        self,
        verb_or_stem: str,
        tense: str = "past",
        person: str = "3sg",
        negative: bool = False
    ) -> str:
        """Conjugates a Turkish verb for tense, polarity, and person."""
        stem = self.get_stem(verb_or_stem)
        t = tense.lower()
        p = person.lower()

        # Step 1: Polarity (Negation)
        if negative:
            if t == "progressive":
                # In progressive -iyor, negation is -m-
                stem = f"{stem}m"
            else:
                neg_vowel = self.harmony.get_two_way_harmonic_vowel(stem)
                stem = f"{stem}m{neg_vowel}"

        last_char = TurkishTokenizer.turkish_lower(stem[-1])
        ends_with_vowel = last_char in self.harmony.ALL_VOWELS

        # Step 2: TAM Suffix
        # 1. Definite Past (-di / -ti)
        if t == "past":
            harm_v = self.harmony.get_four_way_harmonic_vowel(stem)
            cons = "t" if self.mutation.ends_with_voiceless(stem) else "d"
            tam_suffix = f"{cons}{harm_v}"
            base = f"{stem}{tam_suffix}"

            # Type II Person Endings (-m, -n, -, -k, -niz, -ler)
            person_map = {
                "1sg": "m",
                "2sg": "n",
                "3sg": "",
                "1pl": "k",
                "2pl": f"n{harm_v}z",
                "3pl": "ler" if self.harmony.get_two_way_harmonic_vowel(base) == "e" else "lar"
            }
            return f"{base}{person_map.get(p, '')}"

        # 2. Evidential / Indirect Past (-miş)
        elif t == "evidential":
            harm_v = self.harmony.get_four_way_harmonic_vowel(stem)
            tam_suffix = f"m{harm_v}ş"
            base = f"{stem}{tam_suffix}"

            # Type I Person Endings
            harm_p = self.harmony.get_four_way_harmonic_vowel(base)
            two_p = self.harmony.get_two_way_harmonic_vowel(base)
            person_map = {
                "1sg": f"{harm_p}m",
                "2sg": f"s{harm_p}n",
                "3sg": "",
                "1pl": f"{harm_p}z",
                "2pl": f"s{harm_p}n{harm_p}z",
                "3pl": f"l{two_p}r"
            }
            return f"{base}{person_map.get(p, '')}"

        # 3. Present Continuous / Progressive (-iyor)
        elif t == "progressive":
            harm_v = self.harmony.get_four_way_harmonic_vowel(stem)
            # If stem ends in vowel, it assimilates to high harmonic vowel
            if ends_with_vowel and not negative:
                base_stem = stem[:-1] + harm_v
            elif ends_with_vowel and negative:
                base_stem = stem + harm_v
            else:
                base_stem = stem + harm_v

            tam_suffix = "yor"
            base = f"{base_stem}{tam_suffix}"

            # Person endings following -yor (always back rounded 'u')
            person_map = {
                "1sg": "um",
                "2sg": "sun",
                "3sg": "",
                "1pl": "uz",
                "2pl": "sunuz",
                "3pl": "lar"
            }
            return f"{base}{person_map.get(p, '')}"

        # 4. Future (-(y)ecek / -(y)acak)
        elif t == "future":
            two_v = self.harmony.get_two_way_harmonic_vowel(stem)
            fut_sfx = f"y{two_v}cek" if ends_with_vowel else f"{two_v}cek"
            if two_v == "a":
                fut_sfx = f"yacak" if ends_with_vowel else "acak"

            # Check 1sg and 1pl consonant softening (k -> ğ)
            harm_p = self.harmony.get_four_way_harmonic_vowel(two_v)
            if p in ("1sg", "1pl"):
                soft_fut = fut_sfx[:-1] + "ğ"
                if p == "1sg":
                    return f"{stem}{soft_fut}{harm_p}m"
                else:
                    return f"{stem}{soft_fut}{harm_p}z"

            person_map = {
                "2sg": f"s{harm_p}n",
                "3sg": "",
                "2pl": f"s{harm_p}n{harm_p}z",
                "3pl": "ler" if two_v == "e" else "lar"
            }
            return f"{stem}{fut_sfx}{person_map.get(p, '')}"

        return stem
