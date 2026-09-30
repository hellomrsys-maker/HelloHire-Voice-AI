"""Turkish Case Engine Skill.

Applies the 6 Turkish nominal cases (Nom, Acc, Dat, Loc, Abl, Gen)
incorporating 2-way and 4-way vowel harmony, buffer consonants (y, n),
consonant lenition, and consonant assimilation.
"""

from typing import Dict, Any, Optional
from .vowel_harmony_engine import TurkishVowelHarmonyEngine
from .consonant_mutation_engine import TurkishConsonantMutationEngine
from .tokenization import TurkishTokenizer


class TurkishCaseEngine:
    CASES = ["nom", "acc", "dat", "loc", "abl", "gen"]

    def __init__(
        self,
        harmony_engine: TurkishVowelHarmonyEngine = None,
        mutation_engine: TurkishConsonantMutationEngine = None
    ):
        self.harmony = harmony_engine or TurkishVowelHarmonyEngine()
        self.mutation = mutation_engine or TurkishConsonantMutationEngine()

    def inflect_noun(
        self,
        stem: str,
        case: str,
        is_proper: bool = False
    ) -> str:
        """Inflects a Turkish noun stem with the target grammatical case."""
        c = case.lower()
        if c == "nom" or not stem:
            return stem

        last_char = TurkishTokenizer.turkish_lower(stem[-1])
        ends_with_vowel = last_char in self.harmony.ALL_VOWELS

        # 1. Accusative (-(y)i / -(y)ı / -(y)ü / -(y)u)
        if c == "acc":
            harm_vowel = self.harmony.get_four_way_harmonic_vowel(stem)
            if ends_with_vowel:
                suffix = f"y{harm_vowel}"
                base = stem
            else:
                base = stem if is_proper else self.mutation.apply_lenition(stem)
                suffix = harm_vowel

            return f"{stem}'{suffix}" if is_proper else f"{base}{suffix}"

        # 2. Dative (-(y)e / -(y)a)
        elif c == "dat":
            harm_vowel = self.harmony.get_two_way_harmonic_vowel(stem)
            if ends_with_vowel:
                suffix = f"y{harm_vowel}"
                base = stem
            else:
                base = stem if is_proper else self.mutation.apply_lenition(stem)
                suffix = harm_vowel

            return f"{stem}'{suffix}" if is_proper else f"{base}{suffix}"

        # 3. Locative (-de / -da / -te / -ta)
        elif c == "loc":
            harm_vowel = self.harmony.get_two_way_harmonic_vowel(stem)
            cons = "t" if self.mutation.ends_with_voiceless(stem) else "d"
            suffix = f"{cons}{harm_vowel}"
            return f"{stem}'{suffix}" if is_proper else f"{stem}{suffix}"

        # 4. Ablative (-den / -dan / -ten / -tan)
        elif c == "abl":
            harm_vowel = self.harmony.get_two_way_harmonic_vowel(stem)
            cons = "t" if self.mutation.ends_with_voiceless(stem) else "d"
            suffix = f"{cons}{harm_vowel}n"
            return f"{stem}'{suffix}" if is_proper else f"{stem}{suffix}"

        # 5. Genitive (-(n)in / -(n)ın / -(n)ün / -(n)un)
        elif c == "gen":
            harm_vowel = self.harmony.get_four_way_harmonic_vowel(stem)
            if ends_with_vowel:
                suffix = f"n{harm_vowel}n"
                base = stem
            else:
                base = stem if is_proper else self.mutation.apply_lenition(stem)
                suffix = f"{harm_vowel}n"

            return f"{stem}'{suffix}" if is_proper else f"{base}{suffix}"

        return stem

    def check_dom(self, is_definite: bool) -> str:
        """Differential Object Marking (DOM): Definite objects take accusative, indefinite remain nominative."""
        return "acc" if is_definite else "nom"
