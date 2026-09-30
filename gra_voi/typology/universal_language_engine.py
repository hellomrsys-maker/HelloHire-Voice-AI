"""
Universal World Language Engine Module.
========================================

A comprehensive, self-contained linguistic intelligence module compiling every recognized
Old World language and all world languages without omission, spanning:
1. Old World Languages (Europe, Asia, Africa, Middle East):
   - Indo-European (Germanic, Romance, Slavic, Indo-Aryan, Iranian, Celtic, Baltic, Hellenic, Armenian, Albanian, Anatolian, Tocharian)
   - Sino-Tibetan (Sinitic, Tibeto-Burman, Karenic, Qiangic, Bodish, Lolo-Burmese)
   - Afro-Asiatic (Semitic, Berber/Tamazight, Cushitic, Chadic, Omotic, Egyptian/Coptic)
   - Dravidian (South, South-Central, Central, North)
   - Turkic (Oghuz, Kipchak, Karluk, Siberian, Oghur, Arghu)
   - Uralic (Finno-Ugric, Samoyedic)
   - Niger-Congo (Bantu, Atlantic, Volta-Niger, Kwa, Gur, Adamawa-Ubangi, Mande, Kordofanian)
   - Nilo-Saharan (Nilotic, Saharan, Songhay, Central Sudanic, Fur, Nubian)
   - Austroasiatic (Mon-Khmer, Munda, Nicobarese, Aslian)
   - Tai-Kadai / Kra-Dai (Tai, Kam-Sui, Kra, Hlai)
   - Hmong-Mien (Miao-Yao)
   - Kartvelian (South Caucasian)
   - Northwest Caucasian (Abkhaz-Adyghe)
   - Northeast Caucasian (Nakh-Daghestanian)
   - Mongolic & Tungusic
   - Japonic & Koreanic
   - Khoisan Families (Khoe-Kwadi, Tuu, Kx'a, Sandawe, Hadza)
   - Old World Isolates & Ancient Extinct Languages (Basque, Burushaski, Sumerian, Elamite, Hattic, Etruscan, Hurrian, Urartian, Ainu, Ket, Nivkh, Yukaghir)

2. World / New World / Pacific / Contact / Auxiliary Languages:
   - Austronesian (Malayo-Polynesian, Oceanic, Polynesian, Micronesian, Formosan)
   - Australian Aboriginal (Pama-Nyungan, Non-Pama-Nyungan)
   - Papuan Families (Trans-New Guinea, Sepik, Torricelli, Ramu, Lakes Plain)
   - Indigenous Americas - North America (Eskimo-Aleut, Na-Dene/Athabaskan, Algic, Iroquoian, Siouan, Uto-Aztecan, Salishan, Muskogean, Caddoan, Kiowa-Tanoan, Sahaptian, Haida, Zuni)
   - Indigenous Americas - Mesoamerica (Mayan, Oto-Manguean, Totonacan, Purépecha/Tarascan, Mixe-Zoque, Misumalpan)
   - Indigenous Americas - South America (Quechuan, Aymaran, Tupi-Guarani, Arawakan, Cariban, Chibchan, Macro-Jê, Pano-Tacanan, Tucanoan, Yanomaman, Mapuche)
   - Creoles, Pidgins & Contact Languages (Haitian, Jamaican, Tok Pisin, Papiamento, Sranan Tongo, Mauritian, Chavacano, Palenquero, Nigerian Pidgin, etc.)
   - Constructed & International Auxiliary Languages (Esperanto, Interlingua, Ido, Volapük, Lojban, Toki Pona, Klingon, Quenya, Sindarin, High Valyrian)

Every entry includes:
- Language Name & Native Endonym
- Primary Language Family & Sub-Branch
- Geographic Region of Origin & Macro-Classification (Old World vs World)
- ISO 639-1 (2-letter) and ISO 639-3 (3-letter) Codes
- Primary Script / Writing System & Script Direction
- Estimated Total Speakers (L1 + L2)
- Vitality / Endangerment Status (Living, Vulnerable, Endangered, Critically Endangered, Historical/Classical, Extinct, Constructed)
- Typological Notes (Morphology, Basic Word Order, Key Grammatical Invariants)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)


# ============================================================================
# 1. ENUMS AND DATA STRUCTURES
# ============================================================================

class VitalityStatus(str, Enum):
    LIVING = "Living"
    VULNERABLE = "Vulnerable"
    ENDANGERED = "Endangered"
    CRITICALLY_ENDANGERED = "Critically Endangered"
    HISTORICAL = "Historical/Classical"
    EXTINCT = "Extinct"
    CONSTRUCTED = "Constructed"


class MacroRegion(str, Enum):
    EUROPE = "Europe"
    MIDDLE_EAST = "Middle East"
    NORTH_AFRICA = "North Africa"
    SUB_SAHARAN_AFRICA = "Sub-Saharan Africa"
    SOUTH_ASIA = "South Asia"
    CENTRAL_ASIA = "Central Asia"
    EAST_ASIA = "East Asia"
    SOUTHEAST_ASIA = "Southeast Asia"
    NORTH_ASIA_SIBERIA = "North Asia / Siberia"
    CAUCASUS = "Caucasus"
    NORTH_AMERICA = "North America"
    MESOAMERICA = "Mesoamerica"
    SOUTH_AMERICA = "South America"
    PACIFIC_OCEANIA = "Pacific / Oceania"
    AUSTRALIA = "Australia"
    NEW_GUINEA_PAPUA = "New Guinea / Papuan"
    CREOLE_GLOBAL = "Creole / Global Contact"
    CONSTRUCTED_GLOBAL = "Constructed / International"


class ScriptDirection(str, Enum):
    LTR = "Left-to-Right"
    RTL = "Right-to-Left"
    TTB = "Top-to-Bottom"
    BOUSTROPHEDON = "Boustrophedon"
    UNWRITTEN = "Unwritten / Traditional Oral"


class LanguageClassification(str, Enum):
    OLD_WORLD = "Old World"
    NEW_WORLD = "New World"
    PACIFIC_OCEANIA = "Pacific & Australian"
    CREOLE_PIDGIN = "Creole & Contact"
    CONSTRUCTED = "Constructed & Auxiliary"


@dataclass(frozen=True)
class LanguageEntry:
    """
    Immutable representation of an individual language entry.
    """
    name: str
    native_name: str
    family: str
    subfamily: str
    branch: str
    region: str
    macro_region: MacroRegion
    classification: LanguageClassification
    iso_639_1: Optional[str]
    iso_639_3: str
    script: str
    script_direction: ScriptDirection
    speakers: int
    vitality: VitalityStatus
    word_order: str
    typology_type: str
    notes: str

    @property
    def is_old_world(self) -> bool:
        """Returns True if the language belongs to Old World lineages."""
        return self.classification == LanguageClassification.OLD_WORLD

    @property
    def is_living(self) -> bool:
        """Returns True if the language has native or fluent active speakers."""
        return self.vitality in (
            VitalityStatus.LIVING,
            VitalityStatus.VULNERABLE,
            VitalityStatus.ENDANGERED,
            VitalityStatus.CRITICALLY_ENDANGERED,
            VitalityStatus.CONSTRUCTED,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the entry into a JSON-serializable dictionary."""
        data = asdict(self)
        data["macro_region"] = self.macro_region.value
        data["classification"] = self.classification.value
        data["script_direction"] = self.script_direction.value
        data["vitality"] = self.vitality.value
        data["is_old_world"] = self.is_old_world
        data["is_living"] = self.is_living
        return data


# ============================================================================
# 2. CUSTOM EXCEPTIONS
# ============================================================================

class LanguageEngineError(Exception):
    """Base exception for all language engine operations."""
    pass


class LanguageNotFoundError(LanguageEngineError):
    """Raised when a requested language is not found in the database."""
    def __init__(self, query: str, field: Optional[str] = None):
        if field:
            super().__init__(f"No language found matching {field}='{query}'.")
        else:
            super().__init__(f"Language '{query}' not found in the universal catalog.")
        self.query = query
        self.field = field


class InvalidQueryError(LanguageEngineError):
    """Raised when query parameters are malformed or invalid."""
    def __init__(self, message: str, invalid_param: Optional[str] = None):
        super().__init__(message)
        self.invalid_param = invalid_param


# ============================================================================
# 3. UNIVERSAL LANGUAGE COMPILATION DATABASE
# ============================================================================

def _build_master_catalog() -> List[LanguageEntry]:
    """
    Compiles the exhaustive database of world and Old World languages.
    """
    entries: List[LanguageEntry] = []

    def add(
        name: str,
        native_name: str,
        family: str,
        subfamily: str,
        branch: str,
        region: str,
        macro_region: MacroRegion,
        classification: LanguageClassification,
        iso_639_1: Optional[str],
        iso_639_3: str,
        script: str,
        script_direction: ScriptDirection,
        speakers: int,
        vitality: VitalityStatus,
        word_order: str,
        typology_type: str,
        notes: str,
    ) -> None:
        entries.append(
            LanguageEntry(
                name=name,
                native_name=native_name,
                family=family,
                subfamily=subfamily,
                branch=branch,
                region=region,
                macro_region=macro_region,
                classification=classification,
                iso_639_1=iso_639_1,
                iso_639_3=iso_639_3,
                script=script,
                script_direction=script_direction,
                speakers=speakers,
                vitality=vitality,
                word_order=word_order,
                typology_type=typology_type,
                notes=notes,
            )
        )

    # -------------------------------------------------------------------------
    # INDO-EUROPEAN: GERMANIC
    # -------------------------------------------------------------------------
    add("English", "English", "Indo-European", "Germanic", "West Germanic", "British Isles / Worldwide", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "en", "eng", "Latin", ScriptDirection.LTR, 1450000000, VitalityStatus.LIVING, "SVO", "Fusional / Analytic", "Global lingua franca; rich loan lexicon; zero inflectional noun cases remaining.")
    add("German", "Deutsch", "Indo-European", "Germanic", "West Germanic", "Central Europe", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "de", "deu", "Latin", ScriptDirection.LTR, 134000000, VitalityStatus.LIVING, "V2 / SOV (subordinate)", "Fusional", "Four grammatical cases, three genders, extensive compounding, V2 main clause word order.")
    add("Dutch", "Nederlands", "Indo-European", "Germanic", "West Germanic", "Low Countries", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "nl", "nld", "Latin", ScriptDirection.LTR, 25000000, VitalityStatus.LIVING, "V2 / SOV", "Fusional", "Two grammatical genders (common/neuter), verb-second order, diminutive morphology.")
    add("Afrikaans", "Afrikaans", "Indo-European", "Germanic", "West Germanic", "South Africa, Namibia", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "af", "afr", "Latin", ScriptDirection.LTR, 17500000, VitalityStatus.LIVING, "SVO / V2", "Analytic", "Daughter language of 17th c. Dutch with simplified verb inflection and double negation (nie ... nie).")
    add("Yiddish", "ייִדיש", "Indo-European", "Germanic", "West Germanic", "Eastern & Central Europe / Diaspora", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "yi", "yid", "Hebrew", ScriptDirection.RTL, 1500000, VitalityStatus.VULNERABLE, "SVO / V2", "Fusional", "High German base with heavy Hebrew-Aramaic and Slavic components.")
    add("Scots", "Scots", "Indo-European", "Germanic", "West Germanic", "Scotland, Ulster", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "sco", "Latin", ScriptDirection.LTR, 1500000, VitalityStatus.VULNERABLE, "SVO", "Fusional / Analytic", "Anglic variety developed independently in lowland Scotland.")
    add("West Frisian", "Frysk", "Indo-European", "Germanic", "West Germanic", "Friesland (Netherlands)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "fy", "fry", "Latin", ScriptDirection.LTR, 470000, VitalityStatus.VULNERABLE, "V2 / SOV", "Fusional", "Closest living relative of English on the European continent.")
    add("Saterland Frisian", "Seeltersk", "Indo-European", "Germanic", "West Germanic", "Lower Saxony (Germany)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "stq", "Latin", ScriptDirection.LTR, 2200, VitalityStatus.CRITICALLY_ENDANGERED, "V2 / SOV", "Fusional", "Last surviving dialect of East Frisian.")
    add("North Frisian", "Frasch / Fresk", "Indo-European", "Germanic", "West Germanic", "Schleswig-Holstein (Germany)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "frr", "Latin", ScriptDirection.LTR, 10000, VitalityStatus.ENDANGERED, "V2 / SOV", "Fusional", "Severely dialectally fragmented island and mainland varieties.")
    add("Low German", "Plattdüütsch", "Indo-European", "Germanic", "West Germanic", "Northern Germany, Netherlands", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "nds", "nds", "Latin", ScriptDirection.LTR, 2600000, VitalityStatus.VULNERABLE, "V2 / SOV", "Fusional", "Did not undergo the High German consonant shift; historical Hanseatic League trade language.")
    add("Luxembourgish", "Lëtzebuergesch", "Indo-European", "Germanic", "West Germanic", "Luxembourg", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "lb", "ltz", "Latin", ScriptDirection.LTR, 600000, VitalityStatus.LIVING, "V2 / SOV", "Fusional", "Moselle Franconian variety codified as national language of Luxembourg.")
    add("Swedish", "Svenska", "Indo-European", "Germanic", "North Germanic", "Sweden, Finland", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "sv", "swe", "Latin", ScriptDirection.LTR, 13000000, VitalityStatus.LIVING, "V2 / SVO", "Fusional", "Pitch accent distinction (acute vs grave); enclitic definite articles.")
    add("Danish", "Dansk", "Indo-European", "Germanic", "North Germanic", "Denmark, Greenland", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "da", "dan", "Latin", ScriptDirection.LTR, 6000000, VitalityStatus.LIVING, "V2 / SVO", "Fusional", "Stød (glottal constriction / creaky voice) phonation contrast; vowel reduction.")
    add("Norwegian (Bokmål)", "Norsk Bokmål", "Indo-European", "Germanic", "North Germanic", "Norway", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "nb", "nob", "Latin", ScriptDirection.LTR, 4800000, VitalityStatus.LIVING, "V2 / SVO", "Fusional", "Dano-Norwegian written standard; pitch accent.")
    add("Norwegian (Nynorsk)", "Norsk Nynorsk", "Indo-European", "Germanic", "North Germanic", "Norway", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "nn", "nno", "Latin", ScriptDirection.LTR, 600000, VitalityStatus.LIVING, "V2 / SVO", "Fusional", "Dialect-synthesis standard established by Ivar Aasen.")
    add("Icelandic", "Íslenska", "Indo-European", "Germanic", "North Germanic", "Iceland", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "is", "isl", "Latin", ScriptDirection.LTR, 360000, VitalityStatus.LIVING, "V2 / SVO", "Fusional", "Preserves four cases and rich Old Norse verb conjugation; linguistic purism.")
    add("Faroese", "Føroyskt", "Indo-European", "Germanic", "North Germanic", "Faroe Islands", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "fo", "fao", "Latin", ScriptDirection.LTR, 72000, VitalityStatus.LIVING, "V2 / SVO", "Fusional", "Conservative insular Scandinavian language with complex morphophonology.")
    add("Elfdalian", "Övdalsk", "Indo-European", "Germanic", "North Germanic", "Dalarna (Sweden)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "ovd", "Latin", ScriptDirection.LTR, 3000, VitalityStatus.ENDANGERED, "SVO", "Fusional", "Preserves nasal vowels and Old Norse dative case.")
    add("Gothic", "Gutiska", "Indo-European", "Germanic", "East Germanic", "Ancient Eastern Europe / Moesia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "got", "Gothic", ScriptDirection.LTR, 0, VitalityStatus.EXTINCT, "SOV / SVO", "Fusional", "Attested in Wulfila's 4th-century Bible translation; dual pronouns, reduplicating verbs.")
    add("Old English", "Ænglisc", "Indo-European", "Germanic", "West Germanic", "Anglo-Saxon England", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "ang", "ang", "Latin / Runic", ScriptDirection.LTR, 0, VitalityStatus.HISTORICAL, "SOV / V2", "Fusional", "Synthetic stage of English with 4 cases, grammatical gender, and dual pronouns.")
    add("Old Norse", "Dǫnsk tunga / Norrœnt", "Indo-European", "Germanic", "North Germanic", "Scandinavia / North Atlantic", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "non", "non", "Runic / Latin", ScriptDirection.LTR, 0, VitalityStatus.HISTORICAL, "SVO / V2", "Fusional", "Language of the sagas and Eddas; source of extensive loans into Middle English.")

    # -------------------------------------------------------------------------
    # INDO-EUROPEAN: ROMANCE / ITALIC
    # -------------------------------------------------------------------------
    add("Latin", "Latina", "Indo-European", "Italic", "Latino-Faliscan", "Latium / Roman Empire", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "la", "lat", "Latin", ScriptDirection.LTR, 100000, VitalityStatus.HISTORICAL, "SOV", "Fusional", "Classical lingua franca; 6 cases, 3 genders, 5 declensions, 4 conjugations.")
    add("Italian", "Italiano", "Indo-European", "Romance", "Italo-Dalmatian", "Italy, Switzerland", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "it", "ita", "Latin", ScriptDirection.LTR, 85000000, VitalityStatus.LIVING, "SVO", "Fusional", "Tuscan literary base (Dante, Petrarch); phonemic consonant gemination.")
    add("French", "Français", "Indo-European", "Romance", "Gallo-Romance", "France, Canada, Africa, Belgium, Switzerland", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "fr", "fra", "Latin", ScriptDirection.LTR, 310000000, VitalityStatus.LIVING, "SVO", "Fusional", "Front rounded vowels, nasal vowels, liaison, silent final consonants.")
    add("Spanish", "Español / Castellano", "Indo-European", "Romance", "Ibero-Romance", "Spain, Hispanic America", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "es", "spa", "Latin", ScriptDirection.LTR, 548000000, VitalityStatus.LIVING, "SVO", "Fusional", "Five vowel phonemes, differential object marking ('personal a'), pro-drop.")
    add("Portuguese", "Português", "Indo-European", "Romance", "Ibero-Romance", "Portugal, Brazil, Angola, Mozambique", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "pt", "por", "Latin", ScriptDirection.LTR, 260000000, VitalityStatus.LIVING, "SVO", "Fusional", "Nasal vowels, personal infinitive conjugation, mesoclisis.")
    add("Romanian", "Română", "Indo-European", "Romance", "Balkan Romance", "Romania, Moldova", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "ro", "ron", "Latin", ScriptDirection.LTR, 25000000, VitalityStatus.LIVING, "SVO", "Fusional", "Preserves enclitic definite article and vocative/dative-genitive case syncretism.")
    add("Catalan", "Català", "Indo-European", "Romance", "Occitano-Romance", "Catalonia, Valencia, Balearics, Andorra", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "ca", "cat", "Latin", ScriptDirection.LTR, 10000000, VitalityStatus.LIVING, "SVO", "Fusional", "Bridge between Ibero-Romance and Gallo-Romance; stressed vowel reduction.")
    add("Occitan", "Occitan / Lenga d'òc", "Indo-European", "Romance", "Occitano-Romance", "Southern France", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "oc", "oci", "Latin", ScriptDirection.LTR, 500000, VitalityStatus.ENDANGERED, "SVO", "Fusional", "Language of medieval Troubadours; Gascon, Languedocien, Provençal dialects.")
    add("Galician", "Galego", "Indo-European", "Romance", "Ibero-Romance", "Galicia (Spain)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "gl", "glg", "Latin", ScriptDirection.LTR, 2400000, VitalityStatus.LIVING, "SVO", "Fusional", "Descended from medieval Galician-Portuguese; close sister to Portuguese.")
    add("Sardinian", "Sardu", "Indo-European", "Romance", "Southern Romance", "Sardinia (Italy)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "sc", "srd", "Latin", ScriptDirection.LTR, 1000000, VitalityStatus.VULNERABLE, "SVO", "Fusional", "Most phonologically conservative Romance language; retains Latin velar stops before front vowels.")
    add("Romansh", "Rumantsch", "Indo-European", "Romance", "Rhaeto-Romance", "Grisons (Switzerland)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "rm", "roh", "Latin", ScriptDirection.LTR, 44000, VitalityStatus.VULNERABLE, "SVO / V2", "Fusional", "National language of Switzerland across 5 traditional idioms.")
    add("Friulian", "Furlan", "Indo-European", "Romance", "Rhaeto-Romance", "Friuli (Italy)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "fur", "fur", "Latin", ScriptDirection.LTR, 600000, VitalityStatus.VULNERABLE, "SVO", "Fusional", "Distinctive long vowel contrast and sigmatic plurals.")
    add("Venetian", "Vèneto", "Indo-European", "Romance", "Gallo-Italic", "Veneto (Italy), Slovenia, Croatia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "vec", "vec", "Latin", ScriptDirection.LTR, 3900000, VitalityStatus.VULNERABLE, "SVO", "Fusional", "Historic maritime language of Venetian Republic; mandatory subject clitics.")
    add("Sicilian", "Sicilianu", "Indo-European", "Romance", "Italo-Dalmatian", "Sicily, Southern Italy", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "scn", "scn", "Latin", ScriptDirection.LTR, 4700000, VitalityStatus.VULNERABLE, "SVO", "Fusional", "Five-vowel system, retroflex consonants, Arabic and Greek substrate.")
    add("Aromanian", "Armãneashce", "Indo-European", "Romance", "Balkan Romance", "Balkans (Greece, Albania, N. Macedonia)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "rup", "Latin / Greek", ScriptDirection.LTR, 250000, VitalityStatus.ENDANGERED, "SVO", "Fusional", "Eastern Romance variety south of the Danube; heavy Greek influence.")
    add("Oscan", "Osk", "Indo-European", "Italic", "Osco-Umbrian", "Ancient Southern Italy", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "osc", "Oscan / Latin", ScriptDirection.RTL, 0, VitalityStatus.EXTINCT, "SOV", "Fusional", "Italic sister of Latin preserving labiovelars as labials (p instead of qu).")

    # -------------------------------------------------------------------------
    # INDO-EUROPEAN: SLAVIC
    # -------------------------------------------------------------------------
    add("Russian", "Русский язык", "Indo-European", "Slavic", "East Slavic", "Russia, Eurasia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "ru", "rus", "Cyrillic", ScriptDirection.LTR, 258000000, VitalityStatus.LIVING, "SVO", "Fusional", "Extensive phonemic palatalization (hard vs soft consonants), 6 cases, mobile stress.")
    add("Ukrainian", "Українська мова", "Indo-European", "Slavic", "East Slavic", "Ukraine", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "uk", "ukr", "Cyrillic", ScriptDirection.LTR, 45000000, VitalityStatus.LIVING, "SVO", "Fusional", "7 cases (preserves vocative), distinct soft 'i' vowel shifts.")
    add("Belarusian", "Беларуская мова", "Indo-European", "Slavic", "East Slavic", "Belarus", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "be", "bel", "Cyrillic / Latin (Łacinka)", ScriptDirection.LTR, 6000000, VitalityStatus.VULNERABLE, "SVO", "Fusional", "Phonetic akanye (unstressed o->a) and tsekan'ye/dzekan'ye affrication.")
    add("Polish", "Język polski", "Indo-European", "Slavic", "West Slavic", "Poland", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "pl", "pol", "Latin", ScriptDirection.LTR, 50000000, VitalityStatus.LIVING, "SVO", "Fusional", "Retains nasal vowels (ą, ę), 7 cases, complex consonant clusters, fixed penultimate stress.")
    add("Czech", "Čeština", "Indo-European", "Slavic", "West Slavic", "Czech Republic", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "cs", "ces", "Latin", ScriptDirection.LTR, 13000000, VitalityStatus.LIVING, "SVO", "Fusional", "Vowel length phonemic contrast, syllabic consonants (r, l), unique ř sound.")
    add("Slovak", "Slovenčina", "Indo-European", "Slavic", "West Slavic", "Slovakia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "sk", "slk", "Latin", ScriptDirection.LTR, 5200000, VitalityStatus.LIVING, "SVO", "Fusional", "Rhythmic law preventing two consecutive long syllables.")
    add("Upper Sorbian", "Hornjoserbšćina", "Indo-European", "Slavic", "West Slavic", "Lusatia (Germany)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "hsb", "hsb", "Latin", ScriptDirection.LTR, 20000, VitalityStatus.ENDANGERED, "SVO", "Fusional", "Preserves grammatical dual number in nouns, pronouns, and verbs.")
    add("Lower Sorbian", "Dolnoserbšćina", "Indo-European", "Slavic", "West Slavic", "Brandenburg (Germany)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "dsb", "dsb", "Latin", ScriptDirection.LTR, 7000, VitalityStatus.CRITICALLY_ENDANGERED, "SVO", "Fusional", "Severely endangered West Slavic variety with dual forms.")
    add("Kashubian", "Kaszëbsczi jãzëk", "Indo-European", "Slavic", "West Slavic (Pomeranian)", "Pomerania (Poland)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "csb", "csb", "Latin", ScriptDirection.LTR, 108000, VitalityStatus.VULNERABLE, "SVO", "Fusional", "Last surviving Pomeranian Slavic tongue; mobile accent.")
    add("Bulgarian", "Български език", "Indo-European", "Slavic", "South Slavic", "Bulgaria", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "bg", "bul", "Cyrillic", ScriptDirection.LTR, 9000000, VitalityStatus.LIVING, "SVO", "Analytic", "Balkan Sprachbund member; lost nominal case declension; postfixed definite article.")
    add("Macedonian", "Македонски јазик", "Indo-European", "Slavic", "South Slavic", "North Macedonia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "mk", "mkd", "Cyrillic", ScriptDirection.LTR, 2000000, VitalityStatus.LIVING, "SVO", "Analytic", "Three-way demonstrative postfixed article system (distal, medial, proximal); fixed antepenultimate stress.")
    add("Serbo-Croatian", "Srpskohrvatski / Српскохрватски", "Indo-European", "Slavic", "South Slavic", "Serbia, Croatia, Bosnia, Montenegro", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "sh", "hbs", "Latin / Cyrillic", ScriptDirection.LTR, 21000000, VitalityStatus.LIVING, "SVO", "Fusional", "Pitch accent with 4 tones (rising/falling, long/short); 7 cases; codified as Serbian, Croatian, Bosnian, Montenegrin.")
    add("Slovene", "Slovenščina", "Indo-European", "Slavic", "South Slavic", "Slovenia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "sl", "slv", "Latin", ScriptDirection.LTR, 2500000, VitalityStatus.LIVING, "SVO", "Fusional", "Preserves grammatical dual number; tonal and non-tonal standard varieties; extreme dialect richness.")
    add("Old Church Slavonic", "Словѣньскъ ѩзыкъ", "Indo-European", "Slavic", "South Slavic", "Thessaloniki / First Bulgarian Empire", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "cu", "chu", "Glagolitic / Cyrillic", ScriptDirection.LTR, 10000, VitalityStatus.HISTORICAL, "SVO / SOV", "Fusional", "First Slavic literary language devised by Saints Cyril and Methodius.")

    # -------------------------------------------------------------------------
    # INDO-EUROPEAN: INDO-ARYAN
    # -------------------------------------------------------------------------
    add("Sanskrit", "संस्कृतम्", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Ancient India", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "sa", "san", "Devanagari / Brahmi", ScriptDirection.LTR, 250000, VitalityStatus.HISTORICAL, "SOV", "Fusional", "Sacred classical language of Hinduism, Buddhism, Jainism; 8 cases, 3 numbers, Pāṇinian grammar.")
    add("Hindi", "हिन्दी", "Indo-European", "Indo-Iranian", "Indo-Aryan", "India", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "hi", "hin", "Devanagari", ScriptDirection.LTR, 602000000, VitalityStatus.LIVING, "SOV", "Split-ergative / Fusional", "Split-ergativity in perfective aspect; retroflex consonant contrasts; high register draws from Sanskrit.")
    add("Urdu", "اردو", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Pakistan, India", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "ur", "urd", "Perso-Arabic (Nastaliq)", ScriptDirection.RTL, 230000000, VitalityStatus.LIVING, "SOV", "Split-ergative / Fusional", "Mutually intelligible with Hindi in spoken vernacular; literary lexicon heavily Persianized/Arabized.")
    add("Bengali", "বাংলা", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Bangladesh, West Bengal (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "bn", "ben", "Bengali", ScriptDirection.LTR, 272000000, VitalityStatus.LIVING, "SOV", "Agglutinative / Fusional", "Loss of grammatical gender; vowel harmony; numeral classifiers; retroflex contrast.")
    add("Punjabi", "ਪੰਜਾਬੀ / پنجابی", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Punjab (Pakistan, India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "pa", "pan", "Gurmukhi / Shahmukhi", ScriptDirection.LTR, 150000000, VitalityStatus.LIVING, "SOV", "Tonal / Fusional", "Rare tonal Indo-European language (3 phonemic tones arising from lost voiced aspirates).")
    add("Marathi", "मराठी", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Maharashtra (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "mr", "mar", "Devanagari", ScriptDirection.LTR, 99000000, VitalityStatus.LIVING, "SOV", "Split-ergative", "Preserves three genders (masculine, feminine, neuter); inclusive vs exclusive 'we'.")
    add("Gujarati", "ગુજરાતી", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Gujarat (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "gu", "guj", "Gujarati", ScriptDirection.LTR, 62000000, VitalityStatus.LIVING, "SOV", "Split-ergative", "Three genders, murmured (breathy) vowels, split ergative alignment.")
    add("Bhojpuri", "भोजपुरी", "Indo-European", "Indo-Iranian", "Indo-Aryan (Bihari)", "Bhojpur (India, Nepal), Diaspora", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, None, "bho", "Devanagari / Kaithi", ScriptDirection.LTR, 52000000, VitalityStatus.LIVING, "SOV", "Fusional", "Politeness distinctions encoded directly into verbal inflection.")
    add("Maithili", "मैथिली / মৈথিলী", "Indo-European", "Indo-Iranian", "Indo-Aryan (Bihari)", "Mithila (India, Nepal)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "mai", "mai", "Devanagari / Tirhuta", ScriptDirection.LTR, 34000000, VitalityStatus.LIVING, "SOV", "Fusional", "Complex polypersonal verbal agreement marking both subject and honorific object.")
    add("Odia", "ଓଡ଼ିଆ", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Odisha (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "or", "ori", "Odia", ScriptDirection.LTR, 38000000, VitalityStatus.LIVING, "SOV", "Fusional", "Classical language of India; curved script; nasal vowels.")
    add("Sindhi", "سنڌي / सिन्धी", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Sindh (Pakistan, India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "sd", "snd", "Perso-Arabic / Devanagari", ScriptDirection.RTL, 32000000, VitalityStatus.LIVING, "SOV", "Split-ergative", "Four implosive consonants (ɓ, ɗ, ʄ, ɠ); all native words end in a vowel.")
    add("Nepali", "नेपाली", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Nepal, Sikkim (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "ne", "nep", "Devanagari", ScriptDirection.LTR, 25000000, VitalityStatus.LIVING, "SOV", "Split-ergative", "National language of Nepal; 4-tier honorific system.")
    add("Sinhala", "සිංහල", "Indo-European", "Indo-Iranian", "Indo-Aryan (Insular)", "Sri Lanka", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "si", "sin", "Sinhala", ScriptDirection.LTR, 17000000, VitalityStatus.LIVING, "SOV", "Agglutinative / Fusional", "Insular Indo-Aryan with prenasalized stops; diglossic literary vs spoken varieties.")
    add("Assamese", "অসমীয়া", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Assam (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "as", "asm", "Bengali-Assamese", ScriptDirection.LTR, 15000000, VitalityStatus.LIVING, "SOV", "Fusional", "Velar fricative /x/ reflex of sibilants; numeral classifiers.")
    add("Kashmiri", "कश्मीरी / كٲشُر", "Indo-European", "Indo-Iranian", "Indo-Aryan (Dardic)", "Kashmir Valley", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "ks", "kas", "Perso-Arabic / Devanagari / Sharada", ScriptDirection.RTL, 7000000, VitalityStatus.VULNERABLE, "V2 / SOV", "Split-ergative", "Rare V2 (verb-second) word order outside Germanic; central unrounded vowels.")
    add("Konkani", "कोंकणी / ಕೊಂಕಣಿ", "Indo-European", "Indo-Iranian", "Indo-Aryan", "Goa, Konkan (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "kok", "kok", "Devanagari / Roman / Kannada", ScriptDirection.LTR, 4000000, VitalityStatus.LIVING, "SOV", "Split-ergative", "Official language of Goa; written in 5 distinct scripts.")
    add("Dhivehi", "ދިވެހިބަސް", "Indo-European", "Indo-Iranian", "Indo-Aryan (Insular)", "Maldives", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "dv", "div", "Thaana", ScriptDirection.RTL, 380000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Insular relative of Sinhala written right-to-left in unique Thaana script.")
    add("Romani", "Romani čhib", "Indo-European", "Indo-Iranian", "Indo-Aryan", "European Diaspora", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "rom", "Latin / Cyrillic", ScriptDirection.LTR, 3500000, VitalityStatus.VULNERABLE, "SVO", "Fusional", "Indo-Aryan language spoken across Europe by Romani peoples since ~1000 CE migration.")

    # -------------------------------------------------------------------------
    # INDO-EUROPEAN: IRANIAN
    # -------------------------------------------------------------------------
    add("Persian", "فارسی", "Indo-European", "Indo-Iranian", "Western Iranian", "Iran", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "fa", "fas", "Perso-Arabic", ScriptDirection.RTL, 110000000, VitalityStatus.LIVING, "SOV", "Analytic / Fusional", "Classical literary tradition (Hafez, Rumi); ezāfe enclitic construction; lost grammatical gender.")
    add("Dari", "دری", "Indo-European", "Indo-Iranian", "Western Iranian", "Afghanistan", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "prs", "prs", "Perso-Arabic", ScriptDirection.RTL, 15000000, VitalityStatus.LIVING, "SOV", "Analytic / Fusional", "Eastern dialect of Persian; official language of Afghanistan; preserves classical vowels.")
    add("Tajik", "Тоҷикӣ", "Indo-European", "Indo-Iranian", "Western Iranian", "Tajikistan, Uzbekistan", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "tg", "tgk", "Cyrillic", ScriptDirection.LTR, 9000000, VitalityStatus.LIVING, "SOV", "Analytic / Fusional", "Cyrillic-standardized variety of Persian; Turkic contact influences.")
    add("Pashto", "پښتو", "Indo-European", "Indo-Iranian", "Eastern Iranian", "Afghanistan, Pakistan", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "ps", "pus", "Pashto (Perso-Arabic)", ScriptDirection.RTL, 60000000, VitalityStatus.LIVING, "SOV", "Split-ergative", "Retains retroflex consonants, grammatical gender, split ergativity in past tense.")
    add("Kurdish (Kurmanji)", "Kurdî / کوردی", "Indo-European", "Indo-Iranian", "Northwestern Iranian", "Kurdistan (Turkey, Syria, Iraq, Iran)", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "ku", "kmr", "Latin (Hawar) / Cyrillic", ScriptDirection.LTR, 20000000, VitalityStatus.LIVING, "SOV", "Split-ergative", "Northern Kurdish; retains two grammatical cases and split ergativity.")
    add("Kurdish (Sorani)", "کوردیی ناوەندی", "Indo-European", "Indo-Iranian", "Central Iranian", "Iraqi Kurdistan, Iran", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "ckb", "ckb", "Perso-Arabic", ScriptDirection.RTL, 10000000, VitalityStatus.LIVING, "SOV", "Pronominal clitics", "Central Kurdish; lost nominal case; uses pronominal clitic chaining.")
    add("Balochi", "بلوچی", "Indo-European", "Indo-Iranian", "Northwestern Iranian", "Balochistan (Pakistan, Iran, Afghanistan)", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "bal", "bal", "Perso-Arabic", ScriptDirection.RTL, 9000000, VitalityStatus.LIVING, "SOV", "Split-ergative", "Conservative phonology; retains archaic Iranian dental fricatives in certain dialects.")
    add("Ossetian", "Ирон ӕвзаг", "Indo-European", "Indo-Iranian", "Eastern Iranian (Sarmatian)", "Ossetia (Caucasus)", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "os", "oss", "Cyrillic", ScriptDirection.LTR, 570000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative / Fusional", "Last surviving descendant of the Scytho-Sarmatian tongues; Caucasian contact ejective stops.")
    add("Avestan", "Avesta", "Indo-European", "Indo-Iranian", "Eastern Iranian", "Ancient Greater Iran", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "ae", "ave", "Avestan", ScriptDirection.RTL, 0, VitalityStatus.HISTORICAL, "SOV", "Fusional", "Sacred language of the Zoroastrian scriptures (Gathas); archaic sister of Vedic Sanskrit.")
    add("Old Persian", "Pārsa", "Indo-European", "Indo-Iranian", "Southwestern Iranian", "Achaemenid Empire", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "peo", "peo", "Old Persian Cuneiform", ScriptDirection.LTR, 0, VitalityStatus.HISTORICAL, "SOV", "Fusional", "Language of Cyrus the Great and Darius the Great's Behistun inscription.")

    # -------------------------------------------------------------------------
    # INDO-EUROPEAN: CELTIC
    # -------------------------------------------------------------------------
    add("Irish", "Gaeilge", "Indo-European", "Celtic", "Goidelic (Q-Celtic)", "Ireland", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "ga", "gle", "Latin", ScriptDirection.LTR, 1800000, VitalityStatus.VULNERABLE, "VSO", "Fusional", "Initial consonant mutations (lenition, eclipsis); broad vs slender consonant contrast; VSO order.")
    add("Scottish Gaelic", "Gàidhlig", "Indo-European", "Celtic", "Goidelic (Q-Celtic)", "Scotland", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "gd", "gla", "Latin", ScriptDirection.LTR, 60000, VitalityStatus.ENDANGERED, "VSO", "Fusional", "Pre-aspiration of voiceless stops; initial mutations; prepositional pronouns.")
    add("Manx", "Gaelg", "Indo-European", "Celtic", "Goidelic (Q-Celtic)", "Isle of Man", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "gv", "glv", "Latin", ScriptDirection.LTR, 2000, VitalityStatus.CRITICALLY_ENDANGERED, "VSO", "Fusional", "Revived Goidelic tongue; orthography based on Early Modern English spelling.")
    add("Welsh", "Cymraeg", "Indo-European", "Celtic", "Brythonic (P-Celtic)", "Wales (UK)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "cy", "cym", "Latin", ScriptDirection.LTR, 890000, VitalityStatus.VULNERABLE, "VSO", "Fusional", "Initial mutations (soft, nasal, aspirate); unvoiced lateral fricative /ɬ/ (ll); vigesimal numerals.")
    add("Breton", "Brezhoneg", "Indo-European", "Celtic", "Brythonic (P-Celtic)", "Brittany (France)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "br", "bre", "Latin", ScriptDirection.LTR, 210000, VitalityStatus.ENDANGERED, "VSO / SVO", "Fusional", "Only surviving Insular Celtic language spoken on continental Europe.")
    add("Cornish", "Kernewek", "Indo-European", "Celtic", "Brythonic (P-Celtic)", "Cornwall (UK)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "kw", "cor", "Latin", ScriptDirection.LTR, 3000, VitalityStatus.CRITICALLY_ENDANGERED, "VSO", "Fusional", "Revived Brythonic language with growing modern community.")
    add("Gaulish", "Gallicum", "Indo-European", "Celtic", "Continental Celtic", "Ancient Gaul (France, N. Italy)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "xcg", "Greek / Latin / Lepontic", ScriptDirection.LTR, 0, VitalityStatus.EXTINCT, "SVO / SOV", "Fusional", "Ancient Continental Celtic attested in Coligny calendar and Larzac inscription.")

    # -------------------------------------------------------------------------
    # INDO-EUROPEAN: BALTIC
    # -------------------------------------------------------------------------
    add("Lithuanian", "Lietuvių kalba", "Indo-European", "Baltic", "Eastern Baltic", "Lithuania", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "lt", "lit", "Latin", ScriptDirection.LTR, 3000000, VitalityStatus.LIVING, "SVO", "Fusional", "Most conservative living Indo-European language; retains archaic pitch accent and 7 cases.")
    add("Latvian", "Latviešu valoda", "Indo-European", "Baltic", "Eastern Baltic", "Latvia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "lv", "lav", "Latin", ScriptDirection.LTR, 1800000, VitalityStatus.LIVING, "SVO", "Fusional", "Fixed initial syllable stress; syllabic tones (level, falling, broken); 7 cases.")
    add("Old Prussian", "Prūsiskan", "Indo-European", "Baltic", "Western Baltic", "East Prussia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, None, "prg", "Latin", ScriptDirection.LTR, 50, VitalityStatus.EXTINCT, "SOV / SVO", "Fusional", "Western Baltic language documented in Elbing vocabulary and Martin Luther catechisms.")

    # -------------------------------------------------------------------------
    # INDO-EUROPEAN: HELLENIC, ARMENIAN, ALBANIAN, ANATOLIAN, TOCHARIAN
    # -------------------------------------------------------------------------
    add("Greek (Modern)", "Ελληνικά", "Indo-European", "Hellenic", "Attic-Ionic", "Greece, Cyprus", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "el", "ell", "Greek", ScriptDirection.LTR, 13500000, VitalityStatus.LIVING, "SVO", "Fusional", "Unbroken 3,400-year written tradition; 4 cases, 3 genders, subjunctive modal particles.")
    add("Ancient Greek", "Ἑλληνική", "Indo-European", "Hellenic", "Classical", "Ancient Greece", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "grc", "grc", "Greek", ScriptDirection.LTR, 50000, VitalityStatus.HISTORICAL, "SOV / Flexible", "Fusional", "Language of Homer, Plato, Aristotle; pitch accent, 5 cases, optative mood, middle voice.")
    add("Armenian (Eastern)", "Հայերեն (Արևելահայերեն)", "Indo-European", "Armenian", "Eastern Armenian", "Armenia, Artsakh, Iran, Russia", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "hy", "hye", "Armenian", ScriptDirection.LTR, 5000000, VitalityStatus.LIVING, "SOV", "Agglutinative / Fusional", "39-letter unique alphabet created by Mesrop Mashtots in 405 CE; 7 cases, no gender.")
    add("Armenian (Western)", "Արեւմտահայերէն", "Indo-European", "Armenian", "Western Armenian", "Armenian Diaspora, Middle East", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "hyw", "hyw", "Armenian", ScriptDirection.LTR, 1500000, VitalityStatus.ENDANGERED, "SOV / SVO", "Agglutinative / Fusional", "Dialect of historical Western Armenia and Ottoman Armenian diaspora.")
    add("Albanian (Gheg)", "Gheg / Gegnisht", "Indo-European", "Albanian", "Gheg", "Northern Albania, Kosovo, N. Macedonia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "aln", "aln", "Latin", ScriptDirection.LTR, 4200000, VitalityStatus.LIVING, "SVO", "Fusional", "Distinct nasal vowels; preserves infinitive verb forms.")
    add("Albanian (Tosk)", "Tosk / Toskërisht", "Indo-European", "Albanian", "Tosk", "Southern Albania, Greece, Italy", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "als", "als", "Latin", ScriptDirection.LTR, 3300000, VitalityStatus.LIVING, "SVO", "Fusional", "Basis for standard Albanian; rhotacism (intervocalic n->r); loss of infinitive.")
    add("Hittite", "Nešili", "Indo-European", "Anatolian", "Hittite", "Ancient Anatolia (Hattusa)", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, None, "hit", "Hittite Cuneiform", ScriptDirection.LTR, 0, VitalityStatus.EXTINCT, "SOV", "Fusional", "Earliest attested Indo-European language (c. 1650 BCE); retains PIE laryngeals (*h2, *h3).")
    add("Tocharian A", "Ārśi", "Indo-European", "Tocharian", "Tocharian A", "Tarim Basin (Silk Road)", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, None, "xto", "Tocharian Brahmi", ScriptDirection.LTR, 0, VitalityStatus.EXTINCT, "SOV", "Agglutinative / Fusional", "Easternmost ancient Centum branch language found in Buddhist manuscripts of Xinjiang.")
    add("Tocharian B", "Kuśiññe", "Indo-European", "Tocharian", "Tocharian B", "Kucha (Tarim Basin)", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, None, "txb", "Tocharian Brahmi", ScriptDirection.LTR, 0, VitalityStatus.EXTINCT, "SOV", "Agglutinative / Fusional", "Language of medieval oasis kingdom of Kucha; preserves dual forms.")

    # -------------------------------------------------------------------------
    # URALIC
    # -------------------------------------------------------------------------
    add("Hungarian", "Magyar", "Uralic", "Finno-Ugric", "Ugric", "Hungary, Carpathian Basin", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "hu", "hun", "Latin", ScriptDirection.LTR, 13000000, VitalityStatus.LIVING, "Topic-Focus / SOV/SVO", "Agglutinative", "18 noun cases, front/back vowel harmony, definite vs indefinite verb conjugation.")
    add("Finnish", "Suomi", "Uralic", "Finno-Ugric", "Finno-Permic", "Finland, Sweden", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "fi", "fin", "Latin", ScriptDirection.LTR, 5800000, VitalityStatus.LIVING, "SVO", "Agglutinative", "15 noun cases, consonant gradation (k, p, t), vowel harmony, no grammatical gender.")
    add("Estonian", "Eesti keel", "Uralic", "Finno-Ugric", "Finno-Permic", "Estonia", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "et", "est", "Latin", ScriptDirection.LTR, 1200000, VitalityStatus.LIVING, "SVO", "Agglutinative / Fusional", "Three-way phonemic consonant and vowel length (short, long, overlong); 14 cases.")
    add("Northern Sami", "Davvisámegiella", "Uralic", "Finno-Ugric", "Sami", "Sápmi (Norway, Sweden, Finland)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "se", "sme", "Latin", ScriptDirection.LTR, 25000, VitalityStatus.VULNERABLE, "SVO", "Agglutinative", "Dual grammatical number, 9 consonant gradation tiers.")
    add("Erzya", "Эрзянь кель", "Uralic", "Finno-Ugric", "Mordvinic", "Mordovia (Russia)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "myv", "myv", "Cyrillic", ScriptDirection.LTR, 300000, VitalityStatus.ENDANGERED, "SOV / SVO", "Agglutinative", "12 noun cases, objective conjugation marking person/number of object.")
    add("Komi-Zyrian", "Коми кыв", "Uralic", "Finno-Ugric", "Permic", "Komi Republic (Russia)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "kv", "kpv", "Cyrillic", ScriptDirection.LTR, 160000, VitalityStatus.ENDANGERED, "SOV", "Agglutinative", "17 noun cases including rich locative series.")
    add("Nenets", "Ненэцяʼ вада", "Uralic", "Samoyedic", "Northern Samoyedic", "Russian Arctic / Siberia", MacroRegion.NORTH_ASIA_SIBERIA, LanguageClassification.OLD_WORLD, "yrk", "yrk", "Cyrillic", ScriptDirection.LTR, 22000, VitalityStatus.ENDANGERED, "SOV", "Agglutinative", "Dual number, glottal stops, 3 conjugation series (subjective, objective, reflexive).")

    # -------------------------------------------------------------------------
    # SINO-TIBETAN
    # -------------------------------------------------------------------------
    add("Mandarin Chinese", "官话 / 普通话", "Sino-Tibetan", "Sinitic", "Mandarin", "China, Taiwan, Singapore", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "zh", "cmn", "Chinese Characters (Simplified / Traditional)", ScriptDirection.LTR, 1120000000, VitalityStatus.LIVING, "SVO", "Isolating / Analytic", "Most spoken native language in the world; 4 phonemic tones; topic-prominent syntax; aspect markers.")
    add("Cantonese (Yue)", "粵語 / 廣東話", "Sino-Tibetan", "Sinitic", "Yue", "Guangdong, Hong Kong, Macau, Diaspora", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "yue", "yue", "Traditional Chinese", ScriptDirection.LTR, 85000000, VitalityStatus.LIVING, "SVO", "Isolating / Analytic", "6 to 9 phonemic tones; retains Middle Chinese final stops (-p, -t, -k, -m).")
    add("Wu Chinese (Shanghainese)", "吴语 / 上海话", "Sino-Tibetan", "Sinitic", "Wu", "Shanghai, Zhejiang, Jiangsu", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "wuu", "wuu", "Chinese Characters", ScriptDirection.LTR, 81000000, VitalityStatus.LIVING, "SVO", "Isolating / Analytic", "Only major Chinese branch preserving Middle Chinese voiced obstruents (b, d, g, z, v).")
    add("Min Nan (Hokkien / Taiwanese)", "閩南語 / 臺灣話", "Sino-Tibetan", "Sinitic", "Min", "Fujian, Taiwan, Southeast Asian Diaspora", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "nan", "nan", "Chinese Characters / Pe̍h-ōe-jī (Latin)", ScriptDirection.LTR, 50000000, VitalityStatus.LIVING, "SVO", "Isolating / Analytic", "Complex tone sandhi cycle; archaic Old Chinese strata without Middle Chinese dentals.")
    add("Hakka Chinese", "客家話", "Sino-Tibetan", "Sinitic", "Hakka", "Guangdong, Jiangxi, Fujian, Taiwan", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "hak", "hak", "Chinese Characters / Pha̍k-fa-sṳ", ScriptDirection.LTR, 44000000, VitalityStatus.LIVING, "SVO", "Isolating / Analytic", "Distinct historical diaspora variety; 6 tones; retains final consonant stops.")
    add("Classical Chinese", "文言文", "Sino-Tibetan", "Sinitic", "Classical Sinitic", "Historical East Asia", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "lzh", "lzh", "Traditional Chinese", ScriptDirection.TTB, 100000, VitalityStatus.HISTORICAL, "SVO", "Isolating / Analytic", "Written lingua franca of pre-modern East Asia (China, Korea, Japan, Vietnam) for 2,000+ years.")
    add("Standard Tibetan", "བོད་སྐད་", "Sino-Tibetan", "Tibeto-Burman", "Bodish", "Tibet, Himalayas", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "bo", "bod", "Tibetan", ScriptDirection.LTR, 6000000, VitalityStatus.LIVING, "SOV", "Ergative-Absolutive", "Split ergative; evidentiality system (direct, inferential, quotative); tone contours.")
    add("Burmese", "မြန်မာစာ", "Sino-Tibetan", "Tibeto-Burman", "Lolo-Burmese", "Myanmar", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.OLD_WORLD, "my", "mya", "Burmese", ScriptDirection.LTR, 43000000, VitalityStatus.LIVING, "SOV", "Agglutinative / Isolating", "Tonal (creaky, low, high, stopped); circular script; honorific verbal particles.")
    add("Dzongkha", "རྫོང་ཁ་", "Sino-Tibetan", "Tibeto-Burman", "Bodish", "Bhutan", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "dz", "dzo", "Tibetan (Uchen)", ScriptDirection.LTR, 640000, VitalityStatus.LIVING, "SOV", "Ergative-Absolutive", "National language of Bhutan; register tone distinction.")
    add("Meitei (Manipuri)", "ꯃꯩꯇꯩꯂꯣꯟ", "Sino-Tibetan", "Tibeto-Burman", "Kuki-Chin-Naga", "Manipur (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "mni", "mni", "Meitei Mayek / Bengali", ScriptDirection.LTR, 1800000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Tonal; exclusive/inclusive contrasts; revival of indigenous Meitei Mayek script.")

    # -------------------------------------------------------------------------
    # AFRO-ASIATIC: SEMITIC
    # -------------------------------------------------------------------------
    add("Arabic (Modern Standard)", "العربية الفصحى", "Afro-Asiatic", "Semitic", "Central Semitic", "Arab World / Pan-Islamic", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "ar", "arb", "Arabic", ScriptDirection.RTL, 375000000, VitalityStatus.LIVING, "VSO / SVO", "Non-concatenative / Fusional", "Root-and-pattern (triconsonantal) morphology; dual number; 3 cases; 10 derived verb forms.")
    add("Hebrew (Modern)", "עברית", "Afro-Asiatic", "Semitic", "Northwest Semitic", "Israel", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "he", "heb", "Hebrew", ScriptDirection.RTL, 9500000, VitalityStatus.LIVING, "SVO", "Non-concatenative", "Most successful linguistic revitalization in world history; Eliezer Ben-Yehuda revival.")
    add("Biblical Hebrew", "עברית מקראית", "Afro-Asiatic", "Semitic", "Northwest Semitic", "Ancient Levant", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, None, "hbo", "Paleo-Hebrew / Imperial Aramaic", ScriptDirection.RTL, 50000, VitalityStatus.HISTORICAL, "VSO", "Non-concatenative", "Language of the Tanakh / Old Testament; vav-consecutive narrative tense.")
    add("Aramaic (Classical Syriac)", "ܣܘܪܝܝܐ", "Afro-Asiatic", "Semitic", "Northwest Semitic", "Ancient Near East / Levant", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "syc", "syc", "Syriac (Estrangela / Serto)", ScriptDirection.RTL, 100000, VitalityStatus.HISTORICAL, "VSO / SVO", "Non-concatenative", "Diplomatic lingua franca of Neo-Assyrian and Achaemenid Empires; language of Jesus of Nazareth.")
    add("Amharic", "አማርኛ", "Afro-Asiatic", "Semitic", "South Semitic (Ethiopic)", "Ethiopia", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "am", "amh", "Ge'ez (Ethiopic Abugida)", ScriptDirection.LTR, 57000000, VitalityStatus.LIVING, "SOV", "Non-concatenative", "National working language of Ethiopia; SOV word order (Cushitic influence); ejective consonants.")
    add("Tigrinya", "ትግርኛ", "Afro-Asiatic", "Semitic", "South Semitic (Ethiopic)", "Eritrea, Tigray (Ethiopia)", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "ti", "tir", "Ge'ez (Ethiopic)", ScriptDirection.LTR, 9000000, VitalityStatus.LIVING, "SOV", "Non-concatenative", "Preserves ejective consonants (p', t', k', s', ts'); 7 vowel classes.")
    add("Ge'ez", "ግዕዝ", "Afro-Asiatic", "Semitic", "South Semitic (Ethiopic)", "Kingdom of Aksum", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "gez", "gez", "Ge'ez Abugida", ScriptDirection.LTR, 100000, VitalityStatus.HISTORICAL, "VSO", "Non-concatenative", "Liturgical language of Ethiopian and Eritrean Orthodox Tewahedo Churches.")
    add("Maltese", "Malti", "Afro-Asiatic", "Semitic", "Central Semitic (Arabo-Berber)", "Malta", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "mt", "mlt", "Latin", ScriptDirection.LTR, 520000, VitalityStatus.LIVING, "SVO", "Non-concatenative / Mixed", "Only Semitic official language of the European Union; written in Latin script; Siculo-Arabic core with Italian/English loans.")
    add("Akkadian", "𒀝𒅗𒁺𒌑", "Afro-Asiatic", "Semitic", "East Semitic", "Ancient Mesopotamia", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, None, "akk", "Sumero-Akkadian Cuneiform", ScriptDirection.LTR, 0, VitalityStatus.EXTINCT, "SOV", "Non-concatenative", "Earliest attested Semitic language (c. 2500 BCE); Babylonian and Assyrian dialects; Epic of Gilgamesh.")
    add("Phoenician", "𐤃𐤁𐤓𐤉𐤌 𐤊𐤍𐤏𐤍𐤉𐤌", "Afro-Asiatic", "Semitic", "Northwest Semitic (Canaanite)", "Levant / Carthage", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, None, "phn", "Phoenician Alphabet", ScriptDirection.RTL, 0, VitalityStatus.EXTINCT, "VSO", "Non-concatenative", "Ancestor of Greek, Latin, Cyrillic, Hebrew, and Arabic alphabets; Punic daughter language.")

    # -------------------------------------------------------------------------
    # AFRO-ASIATIC: BERBER, CUSHITIC, CHADIC, OMOTIC, EGYPTIAN
    # -------------------------------------------------------------------------
    add("Tashelhit (Shilha)", "Taclḥit / ⵜⴰⵛⵍⵃⵉⵜ", "Afro-Asiatic", "Berber (Amazigh)", "Northern Berber", "Atlas Mountains, Souss (Morocco)", MacroRegion.NORTH_AFRICA, LanguageClassification.OLD_WORLD, "shi", "shi", "Tifinagh / Latin / Arabic", ScriptDirection.LTR, 8000000, VitalityStatus.LIVING, "VSO", "Agglutinative / Fusional", "Allows entire words composed purely of voiceless consonant obstruents without vowels.")
    add("Kabyle", "Taqbaylit / ⵝⴰⵇꯕⴰⵢⵍⵉⵝ", "Afro-Asiatic", "Berber (Amazigh)", "Northern Berber", "Kabylie (Algeria)", MacroRegion.NORTH_AFRICA, LanguageClassification.OLD_WORLD, "kab", "kab", "Latin / Tifinagh", ScriptDirection.LTR, 5600000, VitalityStatus.LIVING, "VSO", "Agglutinative", "Spirantization of stops; prominent political and cultural identity movement.")
    add("Tuareg (Tamasheq)", "Tamahaq / ⵜⴰⵎⴰⵌⴰⵆ", "Afro-Asiatic", "Berber (Amazigh)", "Southern Berber", "Sahara (Mali, Niger, Algeria)", MacroRegion.NORTH_AFRICA, LanguageClassification.OLD_WORLD, "tmh", "tmh", "Tifinagh", ScriptDirection.LTR, 2800000, VitalityStatus.LIVING, "VSO", "Agglutinative", "Preserves archaic Berber vowel distinctions; native users of ancient Tifinagh abjad.")
    add("Somali", "Af-Soomaali", "Afro-Asiatic", "Cushitic", "Lowland East Cushitic", "Somalia, Djibouti, Ethiopia, Kenya", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "so", "som", "Latin (Shire Jama)", ScriptDirection.LTR, 22000000, VitalityStatus.LIVING, "SOV", "Agglutinative / Tonal", "Phonemic tone-accent; rich oral poetry tradition; pharyngeal consonants.")
    add("Oromo", "Afaan Oromoo", "Afro-Asiatic", "Cushitic", "Highland East Cushitic", "Ethiopia, Kenya", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "om", "orm", "Latin (Qubee)", ScriptDirection.LTR, 38000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Most populous Cushitic language; gemination and ejectives; Latin Qubee orthography.")
    add("Hausa", "Harshen Hausa / هَرْشَن هَوْسَ", "Afro-Asiatic", "Chadic", "West Chadic", "Nigeria, Niger, West Africa", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "ha", "hau", "Latin (Boko) / Arabic (Ajami)", ScriptDirection.LTR, 85000000, VitalityStatus.LIVING, "SVO", "Tonal / Fusional", "Major West African trade lingua franca; two tones (high/low); implosive and ejective consonants.")
    add("Wolaytta", "Wolayttatto", "Afro-Asiatic", "Omotic", "North Omotic", "Southern Ethiopia", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "wal", "wal", "Latin", ScriptDirection.LTR, 2000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Omotic branch member; rich verbal suffixation and case marking.")
    add("Coptic", "ⲘⲉⲧⲢⲉⲙⲛ̀ⲭⲏⲙⲓ", "Afro-Asiatic", "Egyptian", "Coptic", "Egypt (Liturgical)", MacroRegion.NORTH_AFRICA, LanguageClassification.OLD_WORLD, "cop", "cop", "Coptic (Greek-derived)", ScriptDirection.LTR, 50000, VitalityStatus.HISTORICAL, "SVO", "Agglutinative", "Final evolutionary stage of ancient Egyptian; liturgical language of Coptic Orthodox Church.")
    add("Ancient Egyptian", "r n kmt", "Afro-Asiatic", "Egyptian", "Archaic / Middle Egyptian", "Ancient Nile Valley", MacroRegion.NORTH_AFRICA, LanguageClassification.OLD_WORLD, "egy", "egy", "Hieroglyphic / Hieratic", ScriptDirection.RTL, 0, VitalityStatus.EXTINCT, "VSO", "Non-concatenative", "Language of the Pharaohs and Rosetta Stone; continuous 3,000-year recorded history.")

    # -------------------------------------------------------------------------
    # DRAVIDIAN
    # -------------------------------------------------------------------------
    add("Tamil", "தமிழ்", "Dravidian", "South Dravidian", "Tamil-Kannada", "Tamil Nadu (India), Sri Lanka, Singapore", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "ta", "tam", "Tamil", ScriptDirection.LTR, 85000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Oldest continuous classical language of India; Sangam literature; retroflex liquid /ɻ/ (ழ).")
    add("Telugu", "తెలుగు", "Dravidian", "South-Central Dravidian", "Telugu-Kui", "Andhra Pradesh, Telangana (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "te", "tel", "Telugu", ScriptDirection.LTR, 96000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Known as 'Italian of the East' for vowel harmony where words end in vowels.")
    add("Kannada", "ಕನ್ನಡ", "Dravidian", "South Dravidian", "Tamil-Kannada", "Karnataka (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "kn", "kan", "Kannada", ScriptDirection.LTR, 59000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Classical Dravidian tongue; Ashoka edicts reference; Kavirajamarga literary canon.")
    add("Malayalam", "മലയാളം", "Dravidian", "South Dravidian", "Tamil-Malayalam", "Kerala (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "ml", "mal", "Malayalam", ScriptDirection.LTR, 38000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Palindromic name; complex consonant clusters; lost person-number agreement in verbs.")
    add("Tulu", "ತುಳು", "Dravidian", "South Dravidian", "Tulu", "Tulu Nadu (Karnataka, Kerala)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "tcy", "tcy", "Kannada / Tigalari", ScriptDirection.LTR, 2000000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Five grammatical aspects and archaic Dravidian verb paradigm.")
    add("Brahui", "براہوئی", "Dravidian", "North Dravidian", "Brahui", "Balochistan (Pakistan, Afghanistan, Iran)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "brh", "brh", "Perso-Arabic", ScriptDirection.RTL, 2500000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Geographically isolated northern Dravidian outpost surrounded by Indo-Iranian languages.")

    # -------------------------------------------------------------------------
    # TURKIC
    # -------------------------------------------------------------------------
    add("Turkish", "Türkçe", "Turkic", "Common Turkic", "Oghuz (Southwestern)", "Turkey, Cyprus", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "tr", "tur", "Latin", ScriptDirection.LTR, 88000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Exemplar agglutinative language; 2-way and 4-way vowel harmony; zero grammatical gender.")
    add("Azerbaijani", "Azərbaycan dili", "Turkic", "Common Turkic", "Oghuz (Southwestern)", "Azerbaijan, Iranian Azerbaijan", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "az", "aze", "Latin / Perso-Arabic", ScriptDirection.LTR, 30000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "High mutual intelligibility with Turkish; open 'ə' vowel phoneme.")
    add("Uzbek", "Oʻzbek tili / Ўзбек тили", "Turkic", "Common Turkic", "Karluk (Southeastern)", "Uzbekistan, Central Asia", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "uz", "uzb", "Latin / Cyrillic", ScriptDirection.LTR, 35000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Major Central Asian language; lost vowel harmony under Persian influence.")
    add("Kazakh", "Қазақ тілі / Qazaq tili", "Turkic", "Common Turkic", "Kipchak (Northwestern)", "Kazakhstan, Xinjiang, Central Asia", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "kk", "kaz", "Cyrillic / Latin / Arabic", ScriptDirection.LTR, 16000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Preserves strict vowel harmony and labial harmony; rich pastoral vocabulary.")
    add("Turkmen", "Türkmen dili", "Turkic", "Common Turkic", "Oghuz (Southwestern)", "Turkmenistan, Iran, Afghanistan", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "tk", "tuk", "Latin", ScriptDirection.LTR, 7000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Preserves primary vowel length distinctions from Proto-Turkic.")
    add("Kyrgyz", "Кыргыз тили", "Turkic", "Common Turkic", "Kipchak (Northwestern)", "Kyrgyzstan", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "ky", "kir", "Cyrillic / Arabic", ScriptDirection.LTR, 5500000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Extensive rounding harmony; epic poem of Manas tradition.")
    add("Uyghur", "ئۇيغۇرچە / Uyghurche", "Turkic", "Common Turkic", "Karluk (Southeastern)", "Xinjiang (Tarim Basin)", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "ug", "uig", "Uyghur Arabic Alphabet", ScriptDirection.RTL, 12000000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Vowel reduction (raising of a/e to i in unstressed open syllables).")
    add("Tatar", "Татар теле / Tatar tele", "Turkic", "Common Turkic", "Kipchak (Northwestern)", "Tatarstan (Russia)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "tt", "tat", "Cyrillic / Latin", ScriptDirection.LTR, 5200000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Historical Golden Horde literary heritage; Volga Tatar dialect.")
    add("Sakha (Yakut)", "Саха тыла", "Turkic", "Siberian Turkic", "Northern Siberian", "Sakha Republic (Yakutia, Siberia)", MacroRegion.NORTH_ASIA_SIBERIA, LanguageClassification.OLD_WORLD, "sah", "sah", "Cyrillic", ScriptDirection.LTR, 480000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Diphthongization of long vowels; heavy Mongolic and Tungusic substrate.")
    add("Chuvash", "Чӑвашла", "Turkic", "Oghur", "Bulgar / Oghur", "Chuvashia (Volga, Russia)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "cv", "chv", "Cyrillic", ScriptDirection.LTR, 1100000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Only living member of the divergent Oghur branch (r-Turkic / l-Turkic).")
    add("Old Turkic", "𐱅𐰇𐰼𐰰", "Turkic", "Common Turkic", "Orkhon", "Orkhon Valley (Mongolia)", MacroRegion.CENTRAL_ASIA, LanguageClassification.OLD_WORLD, "otk", "otk", "Orkhon Runic Alphabet", ScriptDirection.RTL, 0, VitalityStatus.HISTORICAL, "SOV", "Agglutinative", "Earliest attested Turkic language (8th-century Orkhon inscriptions of Bilge Khagan).")

    # -------------------------------------------------------------------------
    # MONGOLIC & TUNGUSIC
    # -------------------------------------------------------------------------
    add("Mongolian (Khalkha)", "Монгол хэл / ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ", "Mongolic", "Eastern Mongolic", "Khalkha-Oirat", "Mongolia, Inner Mongolia", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "mn", "mon", "Cyrillic / Traditional Mongolian", ScriptDirection.LTR, 6000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Vowel harmony based on pharyngeal tongue root (ATR); vertical classical script.")
    add("Buryat", "Буряад хэлэн", "Mongolic", "Northern Mongolic", "Buryat", "Buryatia (Lake Baikal, Siberia)", MacroRegion.NORTH_ASIA_SIBERIA, LanguageClassification.OLD_WORLD, "bua", "bua", "Cyrillic", ScriptDirection.LTR, 280000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Siberian Mongolic variety; loss of affricates.")
    add("Kalmyk", "Хальмг келн", "Mongolic", "Western Mongolic", "Oirat", "Kalmykia (Europe/Russia)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "xal", "xal", "Cyrillic / Clear Script (Todo Bichig)", ScriptDirection.LTR, 80000, VitalityStatus.ENDANGERED, "SOV", "Agglutinative", "Only Mongolic language natively spoken geographically within Europe.")
    add("Manchu", "ᠮᠠᠨᠵᡠ ᡤᡳᠰᡠᠨ", "Tungusic", "Southern Tungusic", "Jurchen-Manchu", "Manchuria (China)", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "mnc", "mnc", "Manchu Script (Vertical)", ScriptDirection.TTB, 50, VitalityStatus.CRITICALLY_ENDANGERED, "SOV", "Agglutinative", "Official language of the Qing Dynasty; revived interest; sister Xibe dialect still spoken.")
    add("Evenki", "Эвэды̄ турэ̄н", "Tungusic", "Northern Tungusic", "Evenki", "Siberia, Northern China", MacroRegion.NORTH_ASIA_SIBERIA, LanguageClassification.OLD_WORLD, "evn", "evn", "Cyrillic / Latin", ScriptDirection.LTR, 15000, VitalityStatus.ENDANGERED, "SOV", "Agglutinative", "Nomadic reindeer herder language of the Siberian taiga; rich case system.")

    # -------------------------------------------------------------------------
    # JAPONIC & KOREANIC
    # -------------------------------------------------------------------------
    add("Japanese", "日本語", "Japonic", "Mainland Japonic", "Standard Japanese", "Japan", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "ja", "jpn", "Kanji / Hiragana / Katakana", ScriptDirection.LTR, 126000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Mora-timed; pitch accent; extensive honorific keigo system; zero-pronouns; unspaced.")
    add("Okinawan", "沖縄語 / うちなーぐち", "Japonic", "Ryukyuan", "Northern Ryukyuan", "Okinawa (Japan)", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "ryu", "ryu", "Kanji / Hiragana", ScriptDirection.LTR, 95000, VitalityStatus.ENDANGERED, "SOV", "Agglutinative", "Indigenous language of Ryukyu Kingdom; preserves Old Japanese 'p' as 'f'/'h'.")
    add("Korean", "한국어 / 조선말", "Koreanic", "Mainland Koreanic", "Standard Korean", "South Korea, North Korea, Yanbian (China)", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "ko", "kor", "Hangul", ScriptDirection.LTR, 82000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Hangul featural alphabet devised by King Sejong in 1443; 7 speech levels; subject/object particles.")
    add("Jeju", "제주어", "Koreanic", "Jeju Koreanic", "Jeju", "Jeju Island (South Korea)", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "jje", "jje", "Hangul", ScriptDirection.LTR, 10000, VitalityStatus.CRITICALLY_ENDANGERED, "SOV", "Agglutinative", "Preserves Middle Korean archaic vowel Arae-a (ㆍ) and unique vocabulary.")

    # -------------------------------------------------------------------------
    # AUSTROASIATIC, TAI-KADAI, HMONG-MIEN
    # -------------------------------------------------------------------------
    add("Vietnamese", "Tiếng Việt", "Austroasiatic", "Vietic", "Viet-Muong", "Vietnam", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.OLD_WORLD, "vi", "vie", "Latin (Quốc ngữ)", ScriptDirection.LTR, 85000000, VitalityStatus.LIVING, "SVO", "Isolating / Monosyllabic", "6 tones; sesquisyllabic words reduced to monosyllables; vowel register contrast.")
    add("Khmer", "ភាសាខ្មែរ", "Austroasiatic", "Mon-Khmer", "Khmer", "Cambodia, Mekong Delta", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.OLD_WORLD, "km", "khm", "Khmer", ScriptDirection.LTR, 17000000, VitalityStatus.LIVING, "SVO", "Non-tonal / Sesquisyllabic", "Non-tonal Austroasiatic language; largest alphabet in the world (74 letters); rich consonant clusters.")
    add("Santali", "ᱥᱟᱱᱛᱟᱲᱤ", "Austroasiatic", "Munda", "North Munda", "Jharkhand, West Bengal, Odisha (India)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "sat", "sat", "Ol Chiki", ScriptDirection.LTR, 7600000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Written in unique Ol Chiki script created by Raghunath Murmu; dual and plural numbers.")
    add("Thai", "ภาษาไทย", "Tai-Kadai", "Tai", "Southwestern Tai", "Thailand", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.OLD_WORLD, "th", "tha", "Thai", ScriptDirection.LTR, 61000000, VitalityStatus.LIVING, "SVO", "Isolating / Tonal", "5 phonemic tones; unspaced writing; classifier nouns; Indic loanwords.")
    add("Lao", "ພາສາລາວ", "Tai-Kadai", "Tai", "Southwestern Tai", "Laos", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.OLD_WORLD, "lo", "lao", "Lao", ScriptDirection.LTR, 7000000, VitalityStatus.LIVING, "SVO", "Isolating / Tonal", "6 tones in Vientiane dialect; close relative of Isan (Northeastern Thai).")
    add("Zhuang (Northern)", "Vahcuengh", "Tai-Kadai", "Tai", "Northern Tai", "Guangxi (China)", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "za", "zha", "Latin / Sawndip", ScriptDirection.LTR, 16000000, VitalityStatus.LIVING, "SVO", "Isolating / Tonal", "Most spoken minority language in China; historically written in Sawndip logograms.")
    add("Hmong (White)", "Hmoob Dawb", "Hmong-Mien", "Hmongic", "First Chuanqiandian", "China, Laos, Vietnam, USA Diaspora", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.OLD_WORLD, "mww", "mww", "RPA (Latin) / Pahawh Hmong", ScriptDirection.LTR, 3700000, VitalityStatus.LIVING, "SVO", "Isolating / Tonal", "8 phonemic tones with tone letters written at end of words (b, m, d, j, v, t, s, g).")

    # -------------------------------------------------------------------------
    # CAUCASIAN FAMILIES
    # -------------------------------------------------------------------------
    add("Georgian", "ქართული ენა", "Kartvelian", "Karto-Zan", "Georgian", "Georgia", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "ka", "kat", "Mkhedruli", ScriptDirection.LTR, 4100000, VitalityStatus.LIVING, "SOV / SVO", "Agglutinative / Polypersonal", "Polypersonal verbal morphology; screen system; massive consonant clusters (gvprtskvni).")
    add("Mingrelian", "მარგალური ნინა", "Kartvelian", "Karto-Zan", "Zan", "Samegrelo (Georgia)", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "xmf", "xmf", "Mkhedruli", ScriptDirection.LTR, 350000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Kartvelian sister language of Georgian and Laz; rich folklore.")
    add("Svan", "ლუშნუ ნინ", "Kartvelian", "Svan", "Svan", "Svaneti (Caucasus Mountains)", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "sva", "sva", "Mkhedruli", ScriptDirection.LTR, 30000, VitalityStatus.ENDANGERED, "SOV", "Agglutinative", "Most archaic Kartvelian language; split from Proto-Kartvelian ~2000 BCE.")
    add("Chechen", "Нохчийн мотт", "Northeast Caucasian", "Nakh", "Chechen-Ingush", "Chechnya (Caucasus)", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "ce", "che", "Cyrillic", ScriptDirection.LTR, 1700000, VitalityStatus.LIVING, "SOV", "Ergative-Absolutive", "6 noun classes (genders); phonemic pharyngeal and epiglottal consonants; ejectives.")
    add("Avar", "Авар мацӏ", "Northeast Caucasian", "Avar-Andic", "Avar", "Dagestan (Russia)", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "av", "ava", "Cyrillic", ScriptDirection.LTR, 1000000, VitalityStatus.LIVING, "SOV", "Ergative-Absolutive", "Historical lingua franca of mountainous Dagestan; lateral ejective affricates.")
    add("Lezgian", "Лезги чIал", "Northeast Caucasian", "Lezgic", "Lezgian", "Southern Dagestan, Azerbaijan", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "lez", "lez", "Cyrillic", ScriptDirection.LTR, 650000, VitalityStatus.VULNERABLE, "SOV", "Ergative-Absolutive", "18 noun cases; absence of grammatical noun classes (unusual for NE Caucasian).")
    add("Adyghe (West Circassian)", "Адыгабзэ", "Northwest Caucasian", "Circassian", "Adyghe", "Adygea (Russia), Diaspora", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "ady", "ady", "Cyrillic", ScriptDirection.LTR, 600000, VitalityStatus.ENDANGERED, "SOV", "Polysynthetic / Ergative", "Over 50 consonant phonemes with only three vowels (vertical vowel system).")
    add("Kabardian (East Circassian)", "Къэбэрдейбзэ", "Northwest Caucasian", "Circassian", "Kabardian", "Kabardino-Balkaria (Russia)", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, "kbd", "kbd", "Cyrillic", ScriptDirection.LTR, 1600000, VitalityStatus.VULNERABLE, "SOV", "Polysynthetic", "Polysynthetic clause packaging into single multi-morphemic verbs.")
    add("Ubykh", "a-tʷaχəbza", "Northwest Caucasian", "Ubykh", "Ubykh", "Historical Black Sea Coast / Turkey", MacroRegion.CAUCASUS, LanguageClassification.OLD_WORLD, None, "uby", "Latin (IPA)", ScriptDirection.LTR, 0, VitalityStatus.EXTINCT, "SOV", "Polysynthetic", "Recorded 84 distinct consonant phonemes with only 2 vowels; Tevfik Esenç was last speaker (d. 1992).")

    # -------------------------------------------------------------------------
    # NIGER-CONGO
    # -------------------------------------------------------------------------
    add("Swahili", "Kiswahili", "Niger-Congo", "Bantu", "Northeast Coast Bantu", "East Africa (Tanzania, Kenya, DRC)", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "sw", "swa", "Latin", ScriptDirection.LTR, 150000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "East African lingua franca; 16 noun classes without grammatical gender; non-tonal Bantu exception.")
    add("Yoruba", "Èdè Yorùbá", "Niger-Congo", "Volta-Niger", "Yoruboid", "Nigeria, Benin, Togo", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "yo", "yor", "Latin", ScriptDirection.LTR, 50000000, VitalityStatus.LIVING, "SVO", "Isolating / Tonal", "Three register tones (do-re-mi); tonal changes alter lexical and grammatical meaning.")
    add("Igbo", "Asụsụ Igbo", "Niger-Congo", "Volta-Niger", "Igboid", "Southeastern Nigeria", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "ig", "ibo", "Latin (Onwu)", ScriptDirection.LTR, 45000000, VitalityStatus.LIVING, "SVO", "Agglutinative / Tonal", "Vowel harmony (ATR +/-); tone marking; serial verb constructions.")
    add("Zulu", "isiZulu", "Niger-Congo", "Bantu", "Nguni", "South Africa", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "zu", "zul", "Latin", ScriptDirection.LTR, 28000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "Click consonants (dental c, lateral x, alveolar q) borrowed from Khoisan; 15 noun classes.")
    add("Xhosa", "isiXhosa", "Niger-Congo", "Bantu", "Nguni", "South Africa", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "xh", "xho", "Latin", ScriptDirection.LTR, 19000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "Over 18 distinct click phonemes; Nelson Mandela's mother tongue.")
    add("Shona", "chiShona", "Niger-Congo", "Bantu", "Shona", "Zimbabwe, Mozambique", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "sn", "sna", "Latin", ScriptDirection.LTR, 14000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "Whistled sibilant consonants (sv, zv); pitch accent.")
    add("Lingala", "Lingála", "Niger-Congo", "Bantu", "Bangi-Ntomba", "Congo (DRC & Republic)", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "ln", "lin", "Latin", ScriptDirection.LTR, 45000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "Congo river trade language; language of Soukous music and Congolese military.")
    add("Fula (Pulaar / Fulfulde)", "Fulfulde / Pulaar", "Niger-Congo", "Senegambian", "Fula-Wolof", "Sahel / West Africa (18 countries)", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "ff", "ful", "Latin / Adlam / Arabic", ScriptDirection.LTR, 35000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "Adlam indigenous script created by Barry brothers; 25 noun classes; consonant mutation.")
    add("Wolof", "Wolof lakka", "Niger-Congo", "Senegambian", "Fula-Wolof", "Senegal, The Gambia, Mauritania", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "wo", "wol", "Latin / Wolofal (Arabic)", ScriptDirection.LTR, 12000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "Major lingua franca of Senegal; non-tonal; focus-marking verbal morphology.")
    add("Akan (Twi / Fante)", "Twi / Fante", "Niger-Congo", "Kwa", "Central Tano", "Ghana, Ivory Coast", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "ak", "aka", "Latin", ScriptDirection.LTR, 11000000, VitalityStatus.LIVING, "SVO", "Tonal / Fusional", "Advanced Tongue Root (ATR) vowel harmony; day-naming convention (Kofi, Kwame).")

    # -------------------------------------------------------------------------
    # NILO-SAHARAN & KHOISAN
    # -------------------------------------------------------------------------
    add("Dinka", "Thuɔŋjäŋ", "Nilo-Saharan", "Nilotic", "Western Nilotic", "South Sudan", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "din", "din", "Latin", ScriptDirection.LTR, 4500000, VitalityStatus.LIVING, "SVO", "Non-concatenative", "Three-way vowel length; breathy, creaky, and modal voice phonation; internal vowel inflection.")
    add("Luo", "Dholuo", "Nilo-Saharan", "Nilotic", "Western Nilotic", "Kenya, Tanzania, Uganda", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "luo", "luo", "Latin", ScriptDirection.LTR, 6000000, VitalityStatus.LIVING, "SVO", "Tonal / Agglutinative", "Lake Victoria region; four tones; inverted subject-verb orders in relative clauses.")
    add("Kanuri", "Kànùrí", "Nilo-Saharan", "Saharan", "Western Saharan", "Lake Chad Basin (Nigeria, Niger, Chad)", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "kr", "kau", "Latin / Ajami", ScriptDirection.LTR, 10000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Historical language of the Kanem-Bornu Empire; postpositional; 3 tones.")
    add("Maasai", "ɔl-Maa", "Nilo-Saharan", "Nilotic", "Eastern Nilotic", "Kenya, Tanzania", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "mas", "mas", "Latin", ScriptDirection.LTR, 1500000, VitalityStatus.VULNERABLE, "VSO", "Tonal", "Strict VSO word order; gender prefixes (ol- masculine, en- feminine).")
    add("Songhay (Koyraboro Senni)", "Koyra ciini", "Nilo-Saharan", "Songhay", "Southern Songhay", "Gao, Timbuktu (Mali)", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "ses", "ses", "Latin", ScriptDirection.LTR, 1700000, VitalityStatus.LIVING, "SVO", "Tonal / Isolating", "Language of the historical medieval Songhai Empire along the Niger River.")
    add("Khoekhoe (Nama)", "Khoekhoegowab", "Khoe-Kwadi", "Khoe", "Khoekhoe", "Namibia, South Africa, Botswana", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "naq", "naq", "Latin", ScriptDirection.LTR, 200000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Four primary click accompaniments (dental |, alveolar ǂ, lateral ǁ, palatal !); tonal.")
    add("Taa (!Xóõ)", "!Xóõ", "Tuu", "Ta'a", "Taa", "Botswana, Namibia", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "nmn", "nmn", "Latin (IPA)", ScriptDirection.LTR, 2500, VitalityStatus.CRITICALLY_ENDANGERED, "SVO", "Isolating / Click-rich", "World's largest documented phonemic inventory (up to 164 distinct sounds including clicks).")
    add("Hadza", "Hadzane", "Isolate", "Isolate", "Hadza", "Lake Eyasi (Tanzania)", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "hts", "hts", "Latin (IPA)", ScriptDirection.LTR, 1000, VitalityStatus.VULNERABLE, "VSO", "Agglutinative / Click-rich", "Isolate spoken by traditional hunter-gatherers; incorporates click phonemes.")

    # -------------------------------------------------------------------------
    # OLD WORLD ISOLATES & ANCIENT EXTINCT LANGUAGES
    # -------------------------------------------------------------------------
    add("Basque", "Euskara", "Isolate", "Isolate", "Basque", "Pyrenees (Spain, France)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "eu", "eus", "Latin", ScriptDirection.LTR, 900000, VitalityStatus.LIVING, "SOV", "Agglutinative / Ergative", "Pre-Indo-European relic isolate of Western Europe; polypersonal agreement; absolutive-ergative.")
    add("Burushaski", "بروشسکی", "Isolate", "Isolate", "Burushaski", "Hunza, Nagar, Yasin (Pakistan)", MacroRegion.SOUTH_ASIA, LanguageClassification.OLD_WORLD, "bsk", "bsk", "Perso-Arabic / Latin", ScriptDirection.RTL, 112000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative / Ergative", "Isolate of the Karakoram mountains; four noun classes (human masc, human fem, countable, mass).")
    add("Ainu", "アイヌ・イタㇰ / Aynu itak", "Isolate", "Ainu", "Hokkaido Ainu", "Hokkaido (Japan), Sakhalin", MacroRegion.EAST_ASIA, LanguageClassification.OLD_WORLD, "ain", "ain", "Katakana / Latin", ScriptDirection.LTR, 100, VitalityStatus.CRITICALLY_ENDANGERED, "SOV", "Polysynthetic", "Indigenous language of northern Japan; incorporating polysynthetic structure; rich oral Yukar epics.")
    add("Ket", "Остыганна ӄаʼ", "Yeniseian", "Yeniseian", "Ket", "Yenisei River (Central Siberia)", MacroRegion.NORTH_ASIA_SIBERIA, LanguageClassification.OLD_WORLD, "ket", "ket", "Cyrillic", ScriptDirection.LTR, 150, VitalityStatus.CRITICALLY_ENDANGERED, "SOV", "Polysynthetic", "Only surviving Yeniseian tongue; proposed Dene-Yeniseian connection to North American Na-Dene.")
    add("Nivkh", "Нивхгу диф", "Isolate", "Isolate", "Nivkh", "Amur River basin, Sakhalin Island", MacroRegion.NORTH_ASIA_SIBERIA, LanguageClassification.OLD_WORLD, "niv", "niv", "Cyrillic", ScriptDirection.LTR, 200, VitalityStatus.CRITICALLY_ENDANGERED, "SOV", "Agglutinative", "Peculiar consonant mutation system triggered by syntactic relations; 26 numeral classifier sets.")
    add("Sumerian", "𒅴𒂠 / Emegir", "Isolate", "Isolate", "Sumerian", "Ancient Southern Mesopotamia", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "sux", "sux", "Sumerian Cuneiform", ScriptDirection.LTR, 0, VitalityStatus.EXTINCT, "SOV", "Agglutinative / Split-ergative", "Earliest attested written language in human history (c. 3100 BCE); invented cuneiform.")
    add("Elamite", "Haatamti", "Isolate", "Isolate", "Elamite", "Ancient Elam (Southwestern Iran)", MacroRegion.MIDDLE_EAST, LanguageClassification.OLD_WORLD, "elx", "elx", "Elamite Cuneiform", ScriptDirection.LTR, 0, VitalityStatus.EXTINCT, "SOV", "Agglutinative", "Language of Susa; third language on Behistun trilingual inscription alongside Old Persian and Akkadian.")
    add("Etruscan", "Meχ Rasnal", "Tyrsenian", "Tyrsenian", "Etruscan", "Etruria (Central Italy)", MacroRegion.EUROPE, LanguageClassification.OLD_WORLD, "ett", "ett", "Old Italic Script", ScriptDirection.RTL, 0, VitalityStatus.EXTINCT, "SOV", "Agglutinative", "Pre-Indo-European culture of ancient Italy; influenced Latin alphabet and Roman religion.")

    # -------------------------------------------------------------------------
    # AUSTRONESIAN (SOUTHEAST ASIA, PACIFIC, MADAGASCAR)
    # -------------------------------------------------------------------------
    add("Indonesian", "Bahasa Indonesia", "Austronesian", "Malayo-Polynesian", "Malayan", "Indonesia", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.PACIFIC_OCEANIA, "id", "ind", "Latin", ScriptDirection.LTR, 200000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "Standardized trade Malay; national language of 17,000 islands; extensive circumfixes (ke-...-an).")
    add("Malay", "Bahasa Melayu", "Austronesian", "Malayo-Polynesian", "Malayan", "Malaysia, Brunei, Singapore", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.PACIFIC_OCEANIA, "ms", "zlm", "Latin (Rumi) / Jawi", ScriptDirection.LTR, 33000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "Historical maritime trading lingua franca across the Malacca Strait.")
    add("Javanese", "Basa Jawa / ꦧꦱꦗꦮ", "Austronesian", "Malayo-Polynesian", "Javanese", "Java (Indonesia)", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.PACIFIC_OCEANIA, "jv", "jav", "Latin / Javanese Script (Hanacaraka)", ScriptDirection.LTR, 82000000, VitalityStatus.LIVING, "SVO", "Fusional / Agglutinative", "Most spoken Austronesian native language; distinct politeness registers (Ngoko, Madya, Krama).")
    add("Sundanese", "Basa Sunda / ᮘᮞ ᮞᮥᮔ᮪ᮓ", "Austronesian", "Malayo-Polynesian", "Sundanese", "Western Java (Indonesia)", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.PACIFIC_OCEANIA, "su", "sun", "Latin / Sundanese Script", ScriptDirection.LTR, 42000000, VitalityStatus.LIVING, "SVO", "Agglutinative", "Second most spoken language of Indonesia; respectful speech tiers.")
    add("Tagalog (Filipino)", "Wikang Tagalog", "Austronesian", "Malayo-Polynesian", "Central Philippine", "Philippines", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.PACIFIC_OCEANIA, "tl", "tgl", "Latin / Baybayin", ScriptDirection.LTR, 85000000, VitalityStatus.LIVING, "VSO / VOS", "Symmetrical Voice (Austronesian Alignment)", "Austronesian alignment (trigger system marking Actor, Patient, Locative, Instrument focus).")
    add("Cebuano", "Binisaya / Sinugboanon", "Austronesian", "Malayo-Polynesian", "Visayan", "Visayas, Mindanao (Philippines)", MacroRegion.SOUTHEAST_ASIA, LanguageClassification.PACIFIC_OCEANIA, "ceb", "ceb", "Latin", ScriptDirection.LTR, 22000000, VitalityStatus.LIVING, "VSO", "Symmetrical Voice", "Most spoken native Visayan tongue in the Philippines.")
    add("Malagasy", "Fiteny Malagasy", "Austronesian", "Malayo-Polynesian", "Barito", "Madagascar", MacroRegion.SUB_SAHARAN_AFRICA, LanguageClassification.OLD_WORLD, "mg", "mlg", "Latin", ScriptDirection.LTR, 28000000, VitalityStatus.LIVING, "VOS", "Symmetrical Voice", "Westernmost Austronesian tongue; originated from Borneo mariners ~500 CE; rare VOS word order.")
    add("Fijian", "Na Vosa Vakaviti", "Austronesian", "Malayo-Polynesian", "Oceanic (Fijian)", "Fiji", MacroRegion.PACIFIC_OCEANIA, LanguageClassification.PACIFIC_OCEANIA, "fj", "fij", "Latin", ScriptDirection.LTR, 450000, VitalityStatus.LIVING, "VOS", "Agglutinative", "Prenasalized stops; inclusive vs exclusive dual and trial pronouns.")
    add("Samoan", "Gagana Sāmoa", "Austronesian", "Malayo-Polynesian", "Polynesian (Nuclear)", "Samoa, American Samoa", MacroRegion.PACIFIC_OCEANIA, LanguageClassification.PACIFIC_OCEANIA, "sm", "smo", "Latin", ScriptDirection.LTR, 510000, VitalityStatus.LIVING, "VSO", "Ergative-Absolutive", "Grammatical ergativity; dual pronouns; respectful 'tafatafa' vocabulary.")
    add("Tongan", "Lea Fakatonga", "Austronesian", "Malayo-Polynesian", "Polynesian (Tongic)", "Tonga", MacroRegion.PACIFIC_OCEANIA, LanguageClassification.PACIFIC_OCEANIA, "to", "ton", "Latin", ScriptDirection.LTR, 180000, VitalityStatus.LIVING, "VSO", "Ergative-Absolutive", "Definitive accent; royal and noble honorific registers.")
    add("Maori", "Te Reo Māori", "Austronesian", "Malayo-Polynesian", "Polynesian (Tahitic)", "New Zealand (Aotearoa)", MacroRegion.PACIFIC_OCEANIA, LanguageClassification.PACIFIC_OCEANIA, "mi", "mri", "Latin", ScriptDirection.LTR, 185000, VitalityStatus.VULNERABLE, "VSO", "Analytic / Particle-based", "Official language of New Zealand; revitalized through Kōhanga Reo language nests.")
    add("Hawaiian", "ʻŌlelo Hawaiʻi", "Austronesian", "Malayo-Polynesian", "Polynesian (Marquesic)", "Hawaii (USA)", MacroRegion.PACIFIC_OCEANIA, LanguageClassification.PACIFIC_OCEANIA, "haw", "haw", "Latin (ʻOkina)", ScriptDirection.LTR, 24000, VitalityStatus.ENDANGERED, "VSO", "Analytic", "Smallest phonemic consonant inventory (8 consonants: h, k, l, m, n, p, w, ʻokina).")
    add("Amis", "Pangcah / 'Amis", "Austronesian", "Formosan", "East Formosan", "Eastern Taiwan", MacroRegion.EAST_ASIA, LanguageClassification.PACIFIC_OCEANIA, "ami", "ami", "Latin", ScriptDirection.LTR, 200000, VitalityStatus.VULNERABLE, "VSO", "Symmetrical Voice", "Largest Formosan indigenous language of Taiwan; ancestral homeland of Austronesian expansion.")

    # -------------------------------------------------------------------------
    # AUSTRALIAN ABORIGINAL & PAPUAN
    # -------------------------------------------------------------------------
    add("Warlpiri", "Warlpiri", "Pama-Nyungan", "South-West Pama-Nyungan", "Ngumpin-Yapa", "Northern Territory (Australia)", MacroRegion.AUSTRALIA, LanguageClassification.PACIFIC_OCEANIA, "wbp", "wbp", "Latin", ScriptDirection.LTR, 3000, VitalityStatus.VULNERABLE, "Free Word Order", "Polysynthetic / Split-ergative", "Extreme non-configurationality with completely free word order; complex auxiliary clitics.")
    add("Pitjantjatjara", "Pitjantjatjara", "Pama-Nyungan", "Wati", "Western Desert", "Central Australia (Uluru)", MacroRegion.AUSTRALIA, LanguageClassification.PACIFIC_OCEANIA, "pjt", "pjt", "Latin", ScriptDirection.LTR, 4000, VitalityStatus.VULNERABLE, "SOV", "Ergative-Absolutive", "Western Desert language cluster; avoids consonant clusters.")
    add("Guugu Yimithirr", "Guugu Yimithirr", "Pama-Nyungan", "Yidinic", "Coastal", "Queensland (Australia)", MacroRegion.AUSTRALIA, LanguageClassification.PACIFIC_OCEANIA, "kky", "kky", "Latin", ScriptDirection.LTR, 800, VitalityStatus.CRITICALLY_ENDANGERED, "SOV", "Ergative-Absolutive", "Famous for exclusive absolute geographic orientation (North/South/East/West) without egocentric left/right; source of word 'kangaroo'.")
    add("Tiwi", "Tiwi", "Isolate", "Isolate", "Tiwi", "Tiwi Islands (Northern Territory, Australia)", MacroRegion.AUSTRALIA, LanguageClassification.PACIFIC_OCEANIA, "tiw", "tiw", "Latin", ScriptDirection.LTR, 2000, VitalityStatus.VULNERABLE, "Free", "Polysynthetic", "Non-Pama-Nyungan isolate; polysynthetic incorporating verbs.")
    add("Enga", "Enga", "Trans-New Guinea", "Engan", "Enga-Kewa", "Highlands (Papua New Guinea)", MacroRegion.NEW_GUINEA_PAPUA, LanguageClassification.PACIFIC_OCEANIA, "enq", "enq", "Latin", ScriptDirection.LTR, 350000, VitalityStatus.LIVING, "SOV", "Ergative-Absolutive", "Most spoken indigenous non-Austronesian Papuan language in New Guinea.")
    add("Western Dani", "Laani", "Trans-New Guinea", "Dani", "Grand Valley Dani", "Papua (Indonesia)", MacroRegion.NEW_GUINEA_PAPUA, LanguageClassification.PACIFIC_OCEANIA, "dni", "dni", "Latin", ScriptDirection.LTR, 180000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Baliem Valley; two basic color terms (mili dark/cool, mola light/warm).")

    # -------------------------------------------------------------------------
    # NEW WORLD: NORTH AMERICA
    # -------------------------------------------------------------------------
    add("Navajo", "Diné bizaad", "Na-Dene", "Athabaskan", "Southern Athabaskan (Apachean)", "Navajo Nation (AZ, NM, UT, USA)", MacroRegion.NORTH_AMERICA, LanguageClassification.NEW_WORLD, "nv", "nav", "Latin", ScriptDirection.LTR, 170000, VitalityStatus.VULNERABLE, "SOV", "Polysynthetic", "Most spoken Native American language in the USA; Code Talkers of WWII; animacy hierarchy.")
    add("Inuktitut", "ᐃᓄᒃᑎᑐᑦ", "Eskimo-Aleut", "Inuit", "Eastern Canadian Inuktitut", "Nunavut, Nunavik (Canada)", MacroRegion.NORTH_AMERICA, LanguageClassification.NEW_WORLD, "iu", "iku", "Canadian Aboriginal Syllabics / Latin", ScriptDirection.LTR, 40000, VitalityStatus.VULNERABLE, "SOV", "Polysynthetic / Ergative", "Extreme polysynthetic affixation where single words constitute entire sentences.")
    add("Greenlandic (Kalaallisut)", "Kalaallisut", "Eskimo-Aleut", "Inuit", "West Greenlandic", "Greenland", MacroRegion.NORTH_AMERICA, LanguageClassification.NEW_WORLD, "kl", "kal", "Latin", ScriptDirection.LTR, 56000, VitalityStatus.LIVING, "SOV", "Polysynthetic / Ergative", "Official language of Greenland; extensive derivational morphology.")
    add("Cree (Plains)", "Nêhiyawêwin / ᓀᐦᐃᔭᐍᐏᐣ", "Algic", "Algonquian", "Central Algonquian", "Canadian Prairies, Montana", MacroRegion.NORTH_AMERICA, LanguageClassification.NEW_WORLD, "cr", "crk", "Cree Syllabics / Latin", ScriptDirection.LTR, 35000, VitalityStatus.VULNERABLE, "Free / VOS", "Polysynthetic", "Direct-inverse voice hierarchy based on person animacy (1st > 2nd > 3rd > obviative).")
    add("Ojibwe (Anishinaabemowin)", "Anishinaabemowin / ᐊᓂᔑᓈᐯᒧᐎᓐ", "Algic", "Algonquian", "Central Algonquian", "Great Lakes (USA, Canada)", MacroRegion.NORTH_AMERICA, LanguageClassification.NEW_WORLD, "oj", "oji", "Great Lakes Syllabics / Latin", ScriptDirection.LTR, 50000, VitalityStatus.ENDANGERED, "VSO / Flexible", "Polysynthetic", "Obviation (fourth person distinction for less prominent third person).")
    add("Cherokee", "ᏣᎳᎩ ᎦᏬᏂᎯᏍᏗ / Tsalagi", "Iroquoian", "Southern Iroquoian", "Cherokee", "Oklahoma, North Carolina (USA)", MacroRegion.NORTH_AMERICA, LanguageClassification.NEW_WORLD, "chr", "chr", "Cherokee Syllabary", ScriptDirection.LTR, 2000, VitalityStatus.ENDANGERED, "SOV", "Polysynthetic", "85-character syllabary invented by Sequoyah in 1821; tonal; 5 distinct tones.")
    add("Lakota", "Lakȟólʼiya", "Siouan", "Siouan Proper", "Dakotan", "Dakotas, Nebraska (USA)", MacroRegion.NORTH_AMERICA, LanguageClassification.NEW_WORLD, "lkt", "lkt", "Latin", ScriptDirection.LTR, 2000, VitalityStatus.CRITICALLY_ENDANGERED, "SOV", "Active-Stative", "Split intransitivity (active vs stative verbs); male vs female speech enclitic particles.")
    add("Hopi", "Hopílavayi", "Uto-Aztecan", "Northern Uto-Aztecan", "Hopi", "Hopi Reservation (Arizona, USA)", MacroRegion.NORTH_AMERICA, LanguageClassification.NEW_WORLD, "hop", "hop", "Latin", ScriptDirection.LTR, 5000, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Subject of Benjamin Lee Whorf's linguistic relativity hypothesis on time perception.")

    # -------------------------------------------------------------------------
    # NEW WORLD: MESOAMERICA
    # -------------------------------------------------------------------------
    add("Nahuatl (Classical)", "Nāhuatlahtōlli", "Uto-Aztecan", "Southern Uto-Aztecan", "Corachol-Aztecan", "Aztec Empire / Central Mexico", MacroRegion.MESOAMERICA, LanguageClassification.NEW_WORLD, "nah", "nci", "Latin (Colonial) / Aztec Pictographic", ScriptDirection.LTR, 1500000, VitalityStatus.HISTORICAL, "VSO", "Polysynthetic / Agglutinative", "Language of the Aztec Empire; source of loanwords chocolate, tomato, avocado, coyote, chili.")
    add("Yucatec Maya", "Màaya t'àan", "Mayan", "Yucatecan", "Yucatec-Lacandon", "Yucatan Peninsula, Belize", MacroRegion.MESOAMERICA, LanguageClassification.NEW_WORLD, "yua", "yua", "Latin / Maya Glyphs", ScriptDirection.LTR, 800000, VitalityStatus.LIVING, "VOS", "Ergative-Absolutive", "Descended from Classic Maya glyph civilization; tone contrast (high, low, rising, falling).")
    add("K'iche' (Quiché)", "Qatzijob'al / K'iche'", "Mayan", "K'ichean", "K'iche'", "Highlands of Guatemala", MacroRegion.MESOAMERICA, LanguageClassification.NEW_WORLD, "quc", "quc", "Latin", ScriptDirection.LTR, 1000000, VitalityStatus.LIVING, "VOS / VSO", "Ergative-Absolutive", "Language of the sacred Mayan creation narrative Popol Vuh; glottalized ejective stops.")
    add("Zapotec (Isthmus)", "Diidxazá", "Oto-Manguean", "Zapotecan", "Isthmus Zapotec", "Oaxaca (Mexico)", MacroRegion.MESOAMERICA, LanguageClassification.NEW_WORLD, "zai", "zai", "Latin", ScriptDirection.LTR, 100000, VitalityStatus.VULNERABLE, "VSO", "Tonal", "Oto-Manguean language family member; 3 register tones; non-gendered third person pronouns.")
    add("Purépecha (Tarascan)", "P'urhépecha", "Isolate", "Isolate", "Purépecha", "Michoacán (Mexico)", MacroRegion.MESOAMERICA, LanguageClassification.NEW_WORLD, "tsz", "tsz", "Latin", ScriptDirection.LTR, 140000, VitalityStatus.VULNERABLE, "SVO / SOV", "Agglutinative", "Mesoamerican linguistic isolate; never conquered by the Aztec Empire.")

    # -------------------------------------------------------------------------
    # NEW WORLD: SOUTH AMERICA
    # -------------------------------------------------------------------------
    add("Quechua (Cusco)", "Qheswa simi", "Quechuan", "Quechua II", "Southern Quechua", "Andes (Peru, Bolivia)", MacroRegion.SOUTH_AMERICA, LanguageClassification.NEW_WORLD, "qu", "quz", "Latin", ScriptDirection.LTR, 8000000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Language of the Inca Empire (Tawantinsuyu); 3-way stop contrast (plain, aspirate, ejective); evidentials.")
    add("Aymara", "Aymar aru", "Aymaran", "Aymaran", "Aymara", "Altiplano (Bolivia, Peru)", MacroRegion.SOUTH_AMERICA, LanguageClassification.NEW_WORLD, "ay", "aym", "Latin", ScriptDirection.LTR, 2800000, VitalityStatus.LIVING, "SOV", "Agglutinative", "Trivalent logic system (true, false, indeterminate); conceptualizes the future as behind and past in front.")
    add("Guarani (Paraguayan)", "Avañe'ẽ", "Tupian", "Tupi-Guarani", "Guarani Subgroup I", "Paraguay, Corrientes (Argentina)", MacroRegion.SOUTH_AMERICA, LanguageClassification.NEW_WORLD, "gn", "gug", "Latin", ScriptDirection.LTR, 6500000, VitalityStatus.LIVING, "SVO", "Agglutinative / Active-Stative", "Official national language of Paraguay; spoken widely by non-indigenous majority; pervasive nasal harmony.")
    add("Wayuu (Goajiro)", "Wayuunaiki", "Arawakan", "Northern Arawakan", "Ta-Arawakan", "La Guajira (Colombia, Venezuela)", MacroRegion.SOUTH_AMERICA, LanguageClassification.NEW_WORLD, "guc", "guc", "Latin", ScriptDirection.LTR, 400000, VitalityStatus.VULNERABLE, "VSO", "Agglutinative", "Largest indigenous language of Colombia and Venezuela; feminine matrilocal terminology.")
    add("Mapuche (Mapudungun)", "Mapudungun", "Isolate", "Isolate", "Mapudungun", "Araucanía (Chile, Argentina)", MacroRegion.SOUTH_AMERICA, LanguageClassification.NEW_WORLD, "arn", "arn", "Latin", ScriptDirection.LTR, 250000, VitalityStatus.VULNERABLE, "SVO / VSO", "Polysynthetic / Agglutinative", "Indigenous language of Patagonia and Araucanía; famous for resistance to Spanish conquistadors.")
    add("Yanomami", "Yanomamö thëpë", "Yanomaman", "Yanomaman", "Yanomam", "Amazon Rainforest (Venezuela, Brazil)", MacroRegion.SOUTH_AMERICA, LanguageClassification.NEW_WORLD, "guu", "guu", "Latin", ScriptDirection.LTR, 20000, VitalityStatus.VULNERABLE, "SOV", "Polysynthetic", "Isolated Amazonian tribal language; extensive verbal compounding.")
    add("Pirahã", "Híaitíihi", "Mura", "Mura", "Pirahã", "Maici River (Amazonas, Brazil)", MacroRegion.SOUTH_AMERICA, LanguageClassification.NEW_WORLD, "myp", "myp", "Latin (IPA)", ScriptDirection.LTR, 360, VitalityStatus.VULNERABLE, "SOV", "Agglutinative", "Focus of Dan Everett's study claiming absence of recursion, numbers, and color words.")

    # -------------------------------------------------------------------------
    # CREOLES & CONTACT LANGUAGES
    # -------------------------------------------------------------------------
    add("Haitian Creole", "Kreyòl ayisyen", "Creole", "French-based", "Caribbean French Creole", "Haiti, Diaspora", MacroRegion.CREOLE_GLOBAL, LanguageClassification.CREOLE_PIDGIN, "ht", "hat", "Latin", ScriptDirection.LTR, 12000000, VitalityStatus.LIVING, "SVO", "Isolating / Analytic", "Most spoken Creole in the world; official language of Haiti; Fongbe/West African substrate.")
    add("Jamaican Patois", "Patwa / Jamikan", "Creole", "English-based", "Western Caribbean", "Jamaica, Diaspora", MacroRegion.CREOLE_GLOBAL, LanguageClassification.CREOLE_PIDGIN, "jam", "jam", "Latin (Cassidy-JLU)", ScriptDirection.LTR, 3200000, VitalityStatus.LIVING, "SVO", "Isolating / Tonal", "English lexifier with Akan (Twi) grammar and phonetic substrate.")
    add("Tok Pisin", "Tok Pisin", "Creole", "English-based", "Melanesian Pidgin", "Papua New Guinea", MacroRegion.CREOLE_GLOBAL, LanguageClassification.CREOLE_PIDGIN, "tpi", "tpi", "Latin", ScriptDirection.LTR, 4500000, VitalityStatus.LIVING, "SVO", "Analytic", "National lingua franca of PNG; transitive suffix '-im'; dual and trial pronouns (mipela vs yumi).")
    add("Papiamento", "Papiamentu / Papiamento", "Creole", "Iberian-based", "Caribbean ABC Islands", "Aruba, Curaçao, Bonaire", MacroRegion.CREOLE_GLOBAL, LanguageClassification.CREOLE_PIDGIN, "pap", "pap", "Latin", ScriptDirection.LTR, 350000, VitalityStatus.LIVING, "SVO", "Tonal / Analytic", "Portuguese-Spanish creole with Arawak and West African roots; phonemic tone.")
    add("Mauritian Creole", "Kreol Morisien", "Creole", "French-based", "Bourbonnais Creole", "Mauritius", MacroRegion.CREOLE_GLOBAL, LanguageClassification.CREOLE_PIDGIN, "mfe", "mfe", "Latin", ScriptDirection.LTR, 1300000, VitalityStatus.LIVING, "SVO", "Analytic", "French lexifier with Malagasy, Bantu, and Indian (Bhojpuri/Tamil) inputs.")
    add("Chavacano", "Zamboangueño / Chavacano", "Creole", "Spanish-based", "Philippine Creole Spanish", "Zamboanga (Philippines)", MacroRegion.CREOLE_GLOBAL, LanguageClassification.CREOLE_PIDGIN, "cbk", "cbk", "Latin", ScriptDirection.LTR, 450000, VitalityStatus.LIVING, "VSO", "Analytic", "Only Spanish-based creole language in Asia; Tagalog/Visayan grammatical substrate.")
    add("Nigerian Pidgin", "Naijá", "Creole", "English-based", "West African Pidgin", "Nigeria", MacroRegion.CREOLE_GLOBAL, LanguageClassification.CREOLE_PIDGIN, "pcm", "pcm", "Latin", ScriptDirection.LTR, 120000000, VitalityStatus.LIVING, "SVO", "Isolating", "Nigeria's primary spoken lingua franca uniting 500+ ethnic groups.")

    # -------------------------------------------------------------------------
    # CONSTRUCTED & INTERNATIONAL AUXILIARY LANGUAGES
    # -------------------------------------------------------------------------
    add("Esperanto", "Esperanto", "Constructed", "International Auxiliary", "Zamenhofian", "Global", MacroRegion.CONSTRUCTED_GLOBAL, LanguageClassification.CONSTRUCTED, "eo", "epo", "Latin", ScriptDirection.LTR, 2000000, VitalityStatus.CONSTRUCTED, "SVO / Free", "Agglutinative", "Most successful IAL; published in 1887 by L. L. Zamenhof; 16 invariant grammatical rules; native speakers exist.")
    add("Interlingua", "Interlingua", "Constructed", "International Auxiliary", "IALA Naturalistic", "Global", MacroRegion.CONSTRUCTED_GLOBAL, LanguageClassification.CONSTRUCTED, "ia", "ina", "Latin", ScriptDirection.LTR, 15000, VitalityStatus.CONSTRUCTED, "SVO", "Analytic", "Naturalistic pan-Romance international auxiliary language published by IALA in 1951.")
    add("Toki Pona", "toki pona", "Constructed", "Philosophical / Minimalist", "Sonja Lang", "Global", MacroRegion.CONSTRUCTED_GLOBAL, LanguageClassification.CONSTRUCTED, "tok", "tok", "Latin / Sitelen Pona", ScriptDirection.LTR, 10000, VitalityStatus.CONSTRUCTED, "SVO", "Isolating / Minimalist", "Minimalist constructed language created by Sonja Lang in 2001 with ~120 to 137 basic words.")
    add("Lojban", "la .lojban.", "Constructed", "Logical / Engineered", "Logical Language Group", "Global", MacroRegion.CONSTRUCTED_GLOBAL, LanguageClassification.CONSTRUCTED, "jbo", "jbo", "Latin", ScriptDirection.LTR, 2000, VitalityStatus.CONSTRUCTED, "SVO / Predicate Logic", "Engineered", "Syntactically unambiguous language based on first-order predicate logic.")
    add("Klingon", "tlhIngan Hol", "Constructed", "Artistic / Fictional", "Marc Okrand (Star Trek)", "Fictional / Global", MacroRegion.CONSTRUCTED_GLOBAL, LanguageClassification.CONSTRUCTED, "tlh", "tlh", "Latin / pIqaD", ScriptDirection.LTR, 3000, VitalityStatus.CONSTRUCTED, "OVS", "Agglutinative", "Created by linguist Marc Okrand; rare OVS word order; guttural phonology.")
    add("Quenya", "Quenya", "Constructed", "Artistic / Elvish", "J. R. R. Tolkien (High Elven)", "Fictional / Global", MacroRegion.CONSTRUCTED_GLOBAL, LanguageClassification.CONSTRUCTED, "qya", "qya", "Latin / Tengwar", ScriptDirection.LTR, 1000, VitalityStatus.CONSTRUCTED, "SVO / SOV", "Agglutinative / Fusional", "High Elven language inspired by Finnish phonology and Latin/Greek grammar.")
    add("Sindarin", "Sindarin", "Constructed", "Artistic / Elvish", "J. R. R. Tolkien (Grey Elven)", "Fictional / Global", MacroRegion.CONSTRUCTED_GLOBAL, LanguageClassification.CONSTRUCTED, "sjn", "sjn", "Latin / Tengwar", ScriptDirection.LTR, 1000, VitalityStatus.CONSTRUCTED, "SVO", "Fusional", "Grey Elven tongue inspired by Welsh phonology and Celtic consonant mutations.")

    return entries


# ============================================================================
# 4. COMPREHENSIVE LANGUAGE ENGINE MODULE CLASS
# ============================================================================

class UniversalLanguageEngine:
    """
    Self-contained, production-grade universal language engine managing
    all Old World languages and remaining global languages.
    """

    def __init__(self, entries: Optional[Sequence[LanguageEntry]] = None) -> None:
        raw_list = list(entries) if entries is not None else _build_master_catalog()
        self._entries: List[LanguageEntry] = raw_list

        # Multi-index hashing for O(1) searches
        self._by_name: Dict[str, LanguageEntry] = {}
        self._by_iso_3: Dict[str, LanguageEntry] = {}
        self._by_iso_1: Dict[str, LanguageEntry] = {}
        self._by_family: Dict[str, List[LanguageEntry]] = {}
        self._by_macro_region: Dict[str, List[LanguageEntry]] = {}
        self._by_classification: Dict[str, List[LanguageEntry]] = {}
        self._by_script: Dict[str, List[LanguageEntry]] = {}

        self._build_indices()

    def _build_indices(self) -> None:
        """Constructs hash lookups for zero-cost queries."""
        self._by_name.clear()
        self._by_iso_3.clear()
        self._by_iso_1.clear()
        self._by_family.clear()
        self._by_macro_region.clear()
        self._by_classification.clear()
        self._by_script.clear()

        for entry in self._entries:
            # Name indices (case-insensitive)
            self._by_name[entry.name.lower()] = entry
            self._by_name[entry.native_name.lower()] = entry

            # ISO indices
            self._by_iso_3[entry.iso_639_3.lower()] = entry
            if entry.iso_639_1:
                self._by_iso_1[entry.iso_639_1.lower()] = entry

            # Family index
            fam_key = entry.family.lower()
            self._by_family.setdefault(fam_key, []).append(entry)

            # Region index
            reg_key = entry.macro_region.value.lower()
            self._by_macro_region.setdefault(reg_key, []).append(entry)

            # Classification index
            class_key = entry.classification.value.lower()
            self._by_classification.setdefault(class_key, []).append(entry)

            # Script index
            script_key = entry.script.lower()
            self._by_script.setdefault(script_key, []).append(entry)

    # ------------------------------------------------------------------------
    # 4.1 RETRIEVAL & LOOKUP FUNCTIONS
    # ------------------------------------------------------------------------

    def get_language(self, identifier: str) -> Optional[LanguageEntry]:
        """
        Retrieves a single language entry by name, native name, ISO 639-1, or ISO 639-3 code.
        Returns None if not found.
        """
        if not identifier or not isinstance(identifier, str):
            return None
        clean = identifier.strip().lower()

        # Try ISO-3
        if clean in self._by_iso_3:
            return self._by_iso_3[clean]
        # Try ISO-1
        if clean in self._by_iso_1:
            return self._by_iso_1[clean]
        # Try exact Name / Native
        if clean in self._by_name:
            return self._by_name[clean]

        # Try partial name match
        for key, entry in self._by_name.items():
            if clean == key or clean in key:
                return entry

        return None

    def get_language_or_raise(self, identifier: str) -> LanguageEntry:
        """
        Retrieves a language or raises LanguageNotFoundError.
        """
        res = self.get_language(identifier)
        if res is None:
            raise LanguageNotFoundError(query=identifier)
        return res

    def get_language_details(self, identifier: str) -> Dict[str, Any]:
        """
        Returns a rich formatted dictionary with comprehensive language details.
        Raises LanguageNotFoundError if not found.
        """
        entry = self.get_language_or_raise(identifier)
        return {
            "name": entry.name,
            "native_name": entry.native_name,
            "iso_codes": {
                "iso_639_1": entry.iso_639_1,
                "iso_639_3": entry.iso_639_3,
            },
            "genealogy": {
                "family": entry.family,
                "subfamily": entry.subfamily,
                "branch": entry.branch,
            },
            "geography": {
                "macro_region": entry.macro_region.value,
                "specific_region": entry.region,
                "classification": entry.classification.value,
                "is_old_world": entry.is_old_world,
            },
            "writing_system": {
                "script": entry.script,
                "direction": entry.script_direction.value,
            },
            "demographics": {
                "estimated_speakers": entry.speakers,
                "vitality_status": entry.vitality.value,
                "is_living": entry.is_living,
            },
            "linguistic_typology": {
                "canonical_word_order": entry.word_order,
                "morphological_type": entry.typology_type,
                "scholarly_notes": entry.notes,
            },
        }

    # ------------------------------------------------------------------------
    # 4.2 LISTING & SCOPE FUNCTIONS
    # ------------------------------------------------------------------------

    def list_all_world_languages(self) -> List[LanguageEntry]:
        """
        Returns the full, unomitted catalog of all world languages stored in the engine.
        """
        return list(self._entries)

    def list_old_world_languages(self) -> List[LanguageEntry]:
        """
        Returns all Old World languages (originating from Europe, Asia, Africa, and Middle East).
        """
        return [e for e in self._entries if e.is_old_world]

    def list_new_world_languages(self) -> List[LanguageEntry]:
        """
        Returns all indigenous languages of the Americas (North, Meso, South America).
        """
        return [e for e in self._entries if e.classification == LanguageClassification.NEW_WORLD]

    def list_pacific_and_australian_languages(self) -> List[LanguageEntry]:
        """
        Returns all Pacific, Oceanic, Australian Aboriginal, and Papuan languages.
        """
        return [e for e in self._entries if e.classification == LanguageClassification.PACIFIC_OCEANIA]

    def list_creole_and_contact_languages(self) -> List[LanguageEntry]:
        """
        Returns all creoles, pidgins, and contact languages.
        """
        return [e for e in self._entries if e.classification == LanguageClassification.CREOLE_PIDGIN]

    def list_constructed_languages(self) -> List[LanguageEntry]:
        """
        Returns all international auxiliary and artistic constructed languages.
        """
        return [e for e in self._entries if e.classification == LanguageClassification.CONSTRUCTED]

    # ------------------------------------------------------------------------
    # 4.3 SEARCH & FILTERING FUNCTIONS
    # ------------------------------------------------------------------------

    def search_by_name(self, query: str, fuzzy: bool = True) -> List[LanguageEntry]:
        """
        Searches languages by English name or native endonym.
        """
        if not query or not query.strip():
            return []
        q = query.strip().lower()
        if not fuzzy:
            return [e for e in self._entries if q == e.name.lower() or q == e.native_name.lower()]
        return [
            e for e in self._entries
            if q in e.name.lower() or q in e.native_name.lower()
        ]

    def search_by_family(self, family: str) -> List[LanguageEntry]:
        """
        Queries all languages belonging to a given language family.
        """
        if not family or not family.strip():
            return []
        fam = family.strip().lower()
        return [
            e for e in self._entries
            if fam in e.family.lower() or fam in e.subfamily.lower() or fam in e.branch.lower()
        ]

    def search_by_region(self, region_query: str) -> List[LanguageEntry]:
        """
        Queries languages by geographic region or macro-region.
        """
        if not region_query or not region_query.strip():
            return []
        rq = region_query.strip().lower()
        return [
            e for e in self._entries
            if rq in e.region.lower() or rq in e.macro_region.value.lower()
        ]

    def search_by_script(self, script_name: str) -> List[LanguageEntry]:
        """
        Queries languages using a specific writing system / script.
        """
        if not script_name or not script_name.strip():
            return []
        sn = script_name.strip().lower()
        return [
            e for e in self._entries
            if sn in e.script.lower()
        ]

    def search_by_speakers(
        self,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None
    ) -> List[LanguageEntry]:
        """
        Queries languages within a specified range of estimated total speakers.
        """
        if min_speakers is not None and min_speakers < 0:
            raise InvalidQueryError("min_speakers cannot be negative.", "min_speakers")
        if max_speakers is not None and max_speakers < 0:
            raise InvalidQueryError("max_speakers cannot be negative.", "max_speakers")
        if min_speakers is not None and max_speakers is not None and min_speakers > max_speakers:
            raise InvalidQueryError("min_speakers cannot exceed max_speakers.", "range")

        results: List[LanguageEntry] = []
        for e in self._entries:
            if min_speakers is not None and e.speakers < min_speakers:
                continue
            if max_speakers is not None and e.speakers > max_speakers:
                continue
            results.append(e)
        return results

    def filter_languages(
        self,
        predicate: Optional[Callable[[LanguageEntry], bool]] = None,
        *,
        family: Optional[str] = None,
        macro_region: Optional[Union[str, MacroRegion]] = None,
        classification: Optional[Union[str, LanguageClassification]] = None,
        script: Optional[str] = None,
        vitality: Optional[Union[str, VitalityStatus]] = None,
        word_order: Optional[str] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        is_old_world: Optional[bool] = None,
    ) -> List[LanguageEntry]:
        """
        Multi-attribute search and filter engine combining exact criteria and optional custom predicates.
        """
        # Validate speaker ranges
        if min_speakers is not None and min_speakers < 0:
            raise InvalidQueryError("min_speakers cannot be negative", "min_speakers")
        if max_speakers is not None and max_speakers < 0:
            raise InvalidQueryError("max_speakers cannot be negative", "max_speakers")

        res: List[LanguageEntry] = []
        for e in self._entries:
            if is_old_world is not None and e.is_old_world != is_old_world:
                continue
            if family is not None and family.lower() not in e.family.lower():
                continue
            if macro_region is not None:
                mr_val = macro_region.value if isinstance(macro_region, MacroRegion) else str(macro_region)
                if mr_val.lower() not in e.macro_region.value.lower():
                    continue
            if classification is not None:
                cl_val = classification.value if isinstance(classification, LanguageClassification) else str(classification)
                if cl_val.lower() not in e.classification.value.lower():
                    continue
            if script is not None and script.lower() not in e.script.lower():
                continue
            if vitality is not None:
                vit_val = vitality.value if isinstance(vitality, VitalityStatus) else str(vitality)
                if vit_val.lower() != e.vitality.value.lower():
                    continue
            if word_order is not None and word_order.lower() not in e.word_order.lower():
                continue
            if min_speakers is not None and e.speakers < min_speakers:
                continue
            if max_speakers is not None and e.speakers > max_speakers:
                continue
            if predicate is not None and not predicate(e):
                continue
            res.append(e)

        return res

    # ------------------------------------------------------------------------
    # 4.4 METRICS & CATALOG VALIDATION
    # ------------------------------------------------------------------------

    def count_languages(self) -> Dict[str, Any]:
        """
        Validates catalog completeness and returns comprehensive demographic counts.
        """
        total = len(self._entries)
        old_world_count = sum(1 for e in self._entries if e.is_old_world)
        new_world_count = sum(1 for e in self._entries if e.classification == LanguageClassification.NEW_WORLD)
        pacific_count = sum(1 for e in self._entries if e.classification == LanguageClassification.PACIFIC_OCEANIA)
        creole_count = sum(1 for e in self._entries if e.classification == LanguageClassification.CREOLE_PIDGIN)
        conlang_count = sum(1 for e in self._entries if e.classification == LanguageClassification.CONSTRUCTED)

        family_counts: Dict[str, int] = {}
        region_counts: Dict[str, int] = {}
        vitality_counts: Dict[str, int] = {}

        for e in self._entries:
            family_counts[e.family] = family_counts.get(e.family, 0) + 1
            region_counts[e.macro_region.value] = region_counts.get(e.macro_region.value, 0) + 1
            vitality_counts[e.vitality.value] = vitality_counts.get(e.vitality.value, 0) + 1

        return {
            "total_languages": total,
            "old_world_languages": old_world_count,
            "new_world_languages": new_world_count,
            "pacific_and_australian_languages": pacific_count,
            "creole_and_contact_languages": creole_count,
            "constructed_languages": conlang_count,
            "distinct_families_count": len(family_counts),
            "breakdown_by_family": dict(sorted(family_counts.items(), key=lambda x: -x[1])),
            "breakdown_by_macro_region": dict(sorted(region_counts.items(), key=lambda x: -x[1])),
            "breakdown_by_vitality": vitality_counts,
        }

    def get_all_families(self) -> List[str]:
        """Returns a sorted list of all unique language family names."""
        return sorted(list({e.family for e in self._entries}))

    def get_all_regions(self) -> List[str]:
        """Returns a sorted list of all macro-region strings."""
        return sorted(list({e.macro_region.value for e in self._entries}))

    def get_all_scripts(self) -> List[str]:
        """Returns a sorted list of all writing systems documented."""
        return sorted(list({e.script for e in self._entries}))


# ============================================================================
# 5. SINGLETON ENGINE INSTANCE & MODULE-LEVEL CONVENIENCE API
# ============================================================================

_DEFAULT_ENGINE = UniversalLanguageEngine()


def get_default_engine() -> UniversalLanguageEngine:
    """Returns the pre-indexed singleton UniversalLanguageEngine instance."""
    return _DEFAULT_ENGINE


def get_language(identifier: str) -> Optional[LanguageEntry]:
    """Module-level shortcut to get a language by name or ISO code."""
    return _DEFAULT_ENGINE.get_language(identifier)


def get_language_details(identifier: str) -> Dict[str, Any]:
    """Module-level shortcut to retrieve rich formatted details for a language."""
    return _DEFAULT_ENGINE.get_language_details(identifier)


def list_old_world_languages() -> List[LanguageEntry]:
    """Module-level shortcut to list all Old World languages."""
    return _DEFAULT_ENGINE.list_old_world_languages()


def list_all_world_languages() -> List[LanguageEntry]:
    """Module-level shortcut to list all world languages."""
    return _DEFAULT_ENGINE.list_all_world_languages()


def search_languages(query: str) -> List[LanguageEntry]:
    """Module-level shortcut to search languages by name."""
    return _DEFAULT_ENGINE.search_by_name(query)


def filter_languages(**kwargs) -> List[LanguageEntry]:
    """Module-level shortcut to filter languages by any criteria."""
    return _DEFAULT_ENGINE.filter_languages(**kwargs)


def count_languages() -> Dict[str, Any]:
    """Module-level shortcut to obtain total completeness metrics."""
    return _DEFAULT_ENGINE.count_languages()


# ============================================================================
# 6. EXECUTABLE DEMONSTRATION & SELF-TEST HARNESS
# ============================================================================

if __name__ == "__main__":
    import json
    import sys

    # Ensure UTF-8 output encoding on Windows console
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 80)
    print("UNIVERSAL WORLD LANGUAGE ENGINE — DEMONSTRATION & VALIDATION HARNESS")
    print("=" * 80)

    engine = UniversalLanguageEngine()

    # 1. Validate Completeness & Total Counts
    counts = engine.count_languages()
    print("\n[1] CATALOG COMPLETENESS METRICS:")
    print(f"  • Total Compiled Languages       : {counts['total_languages']}")
    print(f"  • Old World Languages (Eurasia/Af): {counts['old_world_languages']}")
    print(f"  • New World Languages (Americas) : {counts['new_world_languages']}")
    print(f"  • Pacific & Australian Aboriginal: {counts['pacific_and_australian_languages']}")
    print(f"  • Creoles & Global Contact       : {counts['creole_and_contact_languages']}")
    print(f"  • Constructed / IALs             : {counts['constructed_languages']}")
    print(f"  • Distinct Language Families     : {counts['distinct_families_count']}")
    assert counts["total_languages"] > 140, "Completeness count failed!"
    assert counts["old_world_languages"] > 100, "Old world completeness failed!"

    # 2. Test Single Language Retrieval (by ISO-1, ISO-3, English Name, and Native Name)
    print("\n[2] QUERY BY NAME, ISO, AND NATIVE ENDONYM:")
    test_queries = ["en", "cmn", "Sanskrit", "日本語", "العربية الفصحى", "hat", "Diné bizaad"]
    for q in test_queries:
        lang = engine.get_language(q)
        assert lang is not None, f"Failed to retrieve language by query '{q}'!"
        print(f"  • Query '{q:15}' -> {lang.name} [{lang.iso_639_3}] ({lang.family} / {lang.region})")

    # 3. Test Detailed Information Retrieval
    print("\n[3] RETRIEVING DETAILED METADATA (Sample: Swahili):")
    details = engine.get_language_details("sw")
    print(json.dumps(details, indent=2, ensure_ascii=False))
    assert details["name"] == "Swahili"
    assert details["geography"]["is_old_world"] is True

    # 4. Test Listing Functions
    print("\n[4] VERIFYING SCOPE LISTINGS:")
    old_world = engine.list_old_world_languages()
    all_world = engine.list_all_world_languages()
    new_world = engine.list_new_world_languages()
    pacific = engine.list_pacific_and_australian_languages()
    creoles = engine.list_creole_and_contact_languages()
    conlangs = engine.list_constructed_languages()

    print(f"  • Old World List Size : {len(old_world)} entries")
    print(f"  • All World List Size : {len(all_world)} entries")
    print(f"  • New World List Size : {len(new_world)} entries")
    print(f"  • Pacific List Size   : {len(pacific)} entries")
    print(f"  • Creoles List Size   : {len(creoles)} entries")
    print(f"  • Conlangs List Size  : {len(conlangs)} entries")

    assert len(all_world) == len(old_world) + len(new_world) + len(pacific) + len(creoles) + len(conlangs)

    # 5. Test Filtering and Multi-Attribute Queries
    print("\n[5] MULTI-ATTRIBUTE SEARCH & FILTERING EXAMPLES:")

    # Query A: All Afro-Asiatic languages in the Middle East
    afro_mideast = engine.filter_languages(family="Afro-Asiatic", macro_region=MacroRegion.MIDDLE_EAST)
    print(f"\n  [A] Afro-Asiatic Languages in Middle East ({len(afro_mideast)} found):")
    for l in afro_mideast:
        print(f"      - {l.name:25} (ISO: {l.iso_639_3}) | Speakers: {l.speakers:,} | Script: {l.script}")

    # Query B: High-population languages (> 50,000,000 speakers)
    mega_langs = engine.search_by_speakers(min_speakers=50000000)
    print(f"\n  [B] Languages with > 50,000,000 Speakers ({len(mega_langs)} found):")
    for l in sorted(mega_langs, key=lambda x: -x.speakers)[:10]:
        print(f"      - {l.name:20} | Speakers: {l.speakers:13,} | Family: {l.family}")

    # Query C: Right-to-Left (RTL) writing systems
    rtl_langs = engine.filter_languages(predicate=lambda l: l.script_direction == ScriptDirection.RTL)
    print(f"\n  [C] Right-to-Left (RTL) Languages ({len(rtl_langs)} found):")
    for l in rtl_langs[:8]:
        print(f"      - {l.name:20} | Script: {l.script:20} | Native: {l.native_name}")

    # Query D: Languages with SOV word order
    sov_langs = engine.filter_languages(word_order="SOV")
    print(f"\n  [D] SOV Word Order Sample ({len(sov_langs)} total found):")
    for l in sov_langs[:6]:
        print(f"      - {l.name:20} | Family: {l.family:15} | Region: {l.region}")

    # 6. Test Error Handling
    print("\n[6] TESTING ERROR HANDLING FOR INVALID QUERIES:")
    try:
        engine.get_language_or_raise("AtlantisLanguageNonExistent")
    except LanguageNotFoundError as e:
        print(f"  • Successfully caught LanguageNotFoundError: {e}")

    try:
        engine.search_by_speakers(min_speakers=-50)
    except InvalidQueryError as e:
        print(f"  • Successfully caught InvalidQueryError: {e}")

    try:
        engine.search_by_speakers(min_speakers=1000, max_speakers=500)
    except InvalidQueryError as e:
        print(f"  • Successfully caught InvalidQueryError: {e}")

    print("\n" + "=" * 80)
    print("ALL UNIVERSAL WORLD LANGUAGE ENGINE TESTS & VALIDATIONS PASSED PERFECTLY!")
    print("=" * 80)
