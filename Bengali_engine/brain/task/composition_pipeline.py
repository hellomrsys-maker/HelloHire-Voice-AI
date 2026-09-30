"""
Bengali Composition Pipeline Task: Synthesizes multi-clause narrative, descriptive,
and expository Bengali prose using clause chaining and compound verbs.
"""

from typing import Dict, Any, List, Optional
from ..skills.generation import BengaliGenerator
from ..skills.compound_verb_engine import BengaliCompoundVerbEngine


class BengaliCompositionPipelineTask:
    """
    Generates coherent multi-clause Bengali prose with stylistic and aspectual richness.
    """

    def __init__(self):
        self.generator = BengaliGenerator()
        self.compound_engine = BengaliCompoundVerbEngine(self.generator.conjugator)

    def compose_narrative(
        self,
        topic: str = "daily_routine",
        subject: str = "আমি",
        tier: str = "1st",
        include_compound: bool = True
    ) -> Dict[str, Any]:
        """
        Generates a sequence of coordinated or chained Bengali sentences.
        """
        clauses = []

        if topic == "study":
            # Clause 1: I read the book
            c1 = self.generator.generate_clause(
                verb_lemma="পড়া",
                subject=subject,
                direct_object="বই",
                classifier="টি",
                tense="present_continuous"
            )
            clauses.append(c1)

            # Clause 2: He noted down the points (using vector verb রাখা)
            if include_compound:
                c2 = "আমি গুরুত্বপূর্ণ কথাগুলো খাতায় লিখে রাখছি।"
            else:
                c2 = "আমি খাতায় লিখছি।"
            clauses.append(c2)

            # Clause 3: Therefore everything will be clear
            c3 = "সুতরাং সবকিছু সহজে বুঝতে পারব।"
            clauses.append(c3)

        else:
            # Daily routine narrative
            c1 = "সকালে ঘুম থেকে উঠে আমি প্রাতরাশ করলাম।"
            c2 = "তারপর কাজ শেষ করে বিদ্যালয়ে গেলাম।"
            c3 = "সন্ধ্যার সময় বাড়ি ফিরে বিশ্রাম নিলাম।"
            clauses.extend([c1, c2, c3])

        composed_text = " ".join(clauses)

        return {
            "topic": topic,
            "subject": subject,
            "clauses": clauses,
            "composed_prose": composed_text
        }
