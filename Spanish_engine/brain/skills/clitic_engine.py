"""
Spanish Clitic Pronoun Engine.
Handles clitic ordering (IO + DO), spurious 'se' conversion, and enclisis/proclisis.
"""

from typing import List, Dict, Any, Optional

IO_PRONOUNS = {"me", "te", "le", "nos", "os", "les", "se"}
DO_PRONOUNS = {"lo", "la", "los", "las", "me", "te", "nos", "os", "se"}


class CliticEngine:
    """
    Syntactic processor for Spanish clitic sequences and morphophonology.
    """

    def resolve_clitic_cluster(self, indirect_obj: str, direct_obj: str) -> Dict[str, Any]:
        """
        Combines indirect and direct clitics into a grammatically sound cluster.
        Applies the Spurious 'Se' rule (le/les + lo/la/los/las -> se + lo/la/los/las).
        """
        io = indirect_obj.lower().strip()
        do = direct_obj.lower().strip()

        spurious_applied = False
        surface_io = io

        if io in {"le", "les"} and do in {"lo", "la", "los", "las"}:
            surface_io = "se"
            spurious_applied = True

        cluster = f"{surface_io} {do}"
        cluster_enclitic = f"{surface_io}{do}"

        return {
            "original_io": io,
            "original_do": do,
            "spurious_se_applied": spurious_applied,
            "proclitic_cluster": cluster,
            "enclitic_cluster": cluster_enclitic,
        }

    def analyze_placement(self, verb_form: str, clitics: List[str]) -> Dict[str, Any]:
        """
        Determines whether clitics must be proclitic (pre-verbal) or enclitic (post-verbal attachment).
        """
        v = verb_form.lower().strip()
        is_infinitive = v.endswith(("ar", "er", "ir"))
        is_gerund = v.endswith(("ando", "iendo"))
        is_imperative_aff = v in {"di", "haz", "pon", "sal", "ten", "ven", "da", "dime", "mira", "canta", "come", "abre"}

        if is_infinitive or is_gerund or is_imperative_aff:
            placement = "enclitic"
            joined = "".join(clitics)
            surface_verb = f"{v}{joined}"
        else:
            placement = "proclitic"
            joined = " ".join(clitics)
            surface_verb = f"{joined} {v}"

        return {
            "verb_form": verb_form,
            "clitics": clitics,
            "placement": placement,
            "surface_verb": surface_verb,
        }
