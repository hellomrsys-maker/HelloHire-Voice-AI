"""
data_sources.py — Open-Source Training Data Source Registry.
=============================================================

Maps every language engine to authentic, openly-licensed data sources so the
neural Sub-AIs can be trained on REAL multilingual text (not synthetic targets):

  * Tatoeba  — crowd-sourced example sentences, 400+ languages.
               License: CC BY 2.0 FR  (attribution required, commercial OK).
               https://tatoeba.org/  — bulk exports at https://downloads.tatoeba.org/
  * Universal Dependencies (UD) — annotated treebanks, 180+ languages, CoNLL-U.
               License: MIXED per treebank (CC BY-SA, CC BY-NC-SA, etc.).
               https://universaldependencies.org/

Attribution / compliance:
  - Tatoeba data: "Sentences sourced from the Tatoeba Project (https://tatoeba.org),
    licensed CC BY 2.0 FR." Recorded in each engine's data_provenance.json.
  - UD data: per-treebank license recorded from the downloaded LICENSE file.
  - ``commercial_safe=True`` (default) skips UD treebanks whose license contains
    NonCommercial (NC); Tatoeba (CC BY) is always allowed.

Content descriptions here were written for this project; dataset facts were
summarised from the official Tatoeba and Universal Dependencies sites.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


TATOEBA_LICENSE = "CC BY 2.0 FR"
TATOEBA_ATTRIBUTION = ("Sentences sourced from the Tatoeba Project (https://tatoeba.org), "
                       "licensed CC BY 2.0 FR.")
UD_HOME = "https://universaldependencies.org/"


@dataclass
class EngineDataSource:
    engine_dir: str
    iso639_1: str                 # 2-letter code (engine profile)
    tatoeba_code: str             # Tatoeba 3-letter (ISO 639-3) code
    ud_treebanks: List[str] = field(default_factory=list)  # UD repo names, best first
    note: str = ""

    @property
    def tatoeba_sentence_url(self) -> str:
        # Per-language sentence export (tab-separated: id, lang, text), bz2-compressed.
        return f"https://downloads.tatoeba.org/exports/per_language/{self.tatoeba_code}/{self.tatoeba_code}_sentences.tsv.bz2"

    def ud_zip_url(self, treebank: str, tag: str = "r2.14") -> str:
        # UD treebanks are mirrored on GitHub; a release tag gives a stable zip.
        return f"https://github.com/UniversalDependencies/{treebank}/archive/refs/heads/master.zip"


# ISO 639-3 codes used by Tatoeba per language, plus the primary UD treebank(s).
# Chosen treebanks favour permissive (non-NC) licenses where possible.
_SOURCES: Dict[str, EngineDataSource] = {}


def _s(engine, iso1, tat, treebanks, note=""):
    _SOURCES[engine] = EngineDataSource(engine, iso1, tat, treebanks, note)


_s("English_engine", "en", "eng", ["UD_English-EWT", "UD_English-GUM"])
_s("Spanish_engine", "es", "spa", ["UD_Spanish-GSD", "UD_Spanish-AnCora"])
_s("French_engine", "fr", "fra", ["UD_French-GSD"])
_s("Italian_engine", "it", "ita", ["UD_Italian-ISDT"])
_s("Portuguese_engine", "pt", "por", ["UD_Portuguese-Bosque", "UD_Portuguese-GSD"])
_s("Romanian_engine", "ro", "ron", ["UD_Romanian-RRT"])
_s("German_engine", "de", "deu", ["UD_German-GSD"])
_s("Dutch_engine", "nl", "nld", ["UD_Dutch-Alpino"])
_s("Swedish_engine", "sv", "swe", ["UD_Swedish-Talbanken"])
_s("Danish_engine", "da", "dan", ["UD_Danish-DDT"])
_s("Russian_engine", "ru", "rus", ["UD_Russian-GSD", "UD_Russian-SynTagRus"])
_s("Ukrainian_engine", "uk", "ukr", ["UD_Ukrainian-IU"])
_s("Polish_engine", "pl", "pol", ["UD_Polish-PDB"])
_s("Czech_engine", "cs", "ces", ["UD_Czech-PDT"])
_s("Greek_engine", "el", "ell", ["UD_Greek-GDT"])
_s("Finnish_engine", "fi", "fin", ["UD_Finnish-TDT"])
_s("Hungarian_engine", "hu", "hun", ["UD_Hungarian-Szeged"])
_s("Turkish_engine", "tr", "tur", ["UD_Turkish-BOUN", "UD_Turkish-IMST"])
_s("Arabic_engine", "ar", "ara", ["UD_Arabic-PADT"], note="UD_Arabic-PADT is CC BY-NC-SA")
_s("Hebrew_engine", "he", "heb", ["UD_Hebrew-HTB"])
_s("Amharic_engine", "am", "amh", ["UD_Amharic-ATT"], note="UD_Amharic-ATT is CC BY-NC-SA")
_s("Persian_engine", "fa", "pes", ["UD_Persian-Seraji", "UD_Persian-PerDT"])
_s("Hindustani_engine", "hi", "hin", ["UD_Hindi-HDTB"])
_s("Bengali_engine", "bn", "ben", ["UD_Bengali-BRU"])
_s("Marathi_engine", "mr", "mar", ["UD_Marathi-UFAL"])
_s("Gujarati_engine", "gu", "guj", ["UD_Gujarati-GujTB"])
_s("Punjabi_engine", "pa", "pan", ["UD_Punjabi-Rang", "UD_Punjabi-CS"])
_s("Odia_engine", "or", "ori", ["UD_Odia-ODTB"])
_s("Tamil_engine", "ta", "tam", ["UD_Tamil-TTB"])
_s("Telugu_engine", "te", "tel", ["UD_Telugu-MTG"])
_s("Kannada_engine", "kn", "kan", [], note="No UD treebank in v2.18; Tatoeba only")
_s("Malayalam_engine", "ml", "mal", ["UD_Malayalam-UFAL"])
_s("Japanese_engine", "ja", "jpn", ["UD_Japanese-GSD"])
_s("Korean_engine", "ko", "kor", ["UD_Korean-Kaist", "UD_Korean-GSD"])
_s("Mandarin_engine", "zh", "cmn", ["UD_Chinese-GSD", "UD_Chinese-GSDSimp"])
_s("Cantonese_engine", "yue", "yue", ["UD_Cantonese-HK"])
_s("Vietnamese_engine", "vi", "vie", ["UD_Vietnamese-VTB"])
_s("Thai_engine", "th", "tha", ["UD_Thai-PUD"])
_s("Burmese_engine", "my", "mya", [])
_s("Indonesian_engine", "id", "ind", ["UD_Indonesian-GSD"])
_s("Malay_engine", "ms", "zsm", [])
_s("Tagalog_engine", "tl", "tgl", ["UD_Tagalog-TRG", "UD_Tagalog-Ugnayan"])
_s("Swahili_engine", "sw", "swh", [], note="No UD treebank in v2.18; Tatoeba only")
_s("Hausa_engine", "ha", "hau", ["UD_Hausa-NorthernAutogramm"])
_s("Yoruba_engine", "yo", "yor", ["UD_Yoruba-YTB"])


def get_source(engine_dir: str) -> EngineDataSource:
    if engine_dir not in _SOURCES:
        raise KeyError(f"No data source registered for '{engine_dir}'")
    return _SOURCES[engine_dir]


def all_sources() -> Dict[str, EngineDataSource]:
    return dict(_SOURCES)


def is_commercial_safe_ud(license_text: str) -> bool:
    """A UD treebank is commercial-safe if its license is NOT NonCommercial."""
    if not license_text:
        return False
    t = license_text.upper()
    return ("NC" not in t) and ("NONCOMMERCIAL" not in t)
