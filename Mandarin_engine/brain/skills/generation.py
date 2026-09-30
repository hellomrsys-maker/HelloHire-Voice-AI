"""
Mandarin Sentence Generation Skill.
Synthesizes grammatically valid Chinese sentences under aspectual and pragmatic constraints.
"""

from typing import Dict, Any, Optional


class MandarinGenerator:
    """
    Template and rule-guided Mandarin sentence generator.
    """

    def generate(
        self,
        subject: str,
        verb: str,
        obj: str,
        aspect: Optional[str] = None,
        is_ba: bool = False,
        is_bei: bool = False,
        polite: bool = False
    ) -> str:
        """
        Synthesizes a Mandarin clause respecting aspect and construction rules.
        """
        subj = ("您" if polite else subject) if subject in {"你", "您"} else subject
        asp_str = aspect if aspect in {"了", "着", "过"} else ""
        prefix = "请" if polite else ""

        if is_ba:
            # S + 把 + O + V + aspect / result
            return f"{prefix}{subj}把{obj}{verb}{asp_str or '了'}。"
        elif is_bei:
            # O + 被 + S + V + aspect
            return f"{obj}被{subj}{verb}{asp_str or '了'}。"
        else:
            # Canonical SVO: S + V + aspect + O
            if asp_str:
                return f"{prefix}{subj}{verb}{asp_str}{obj}。"
            return f"{prefix}{subj}{verb}{obj}。"
