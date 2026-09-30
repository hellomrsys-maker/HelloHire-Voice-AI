"""Russian Composition Pipeline.

Orchestrates multi-clause composition, narrative sequencing,
aspectual progressions, and numerical specifications into coherent Russian paragraphs.
"""

from typing import Dict, Any, List, Optional
from ..skills.case_engine import RussianCaseEngine
from ..skills.verb_aspect_conjugator import RussianVerbAspectConjugator
from ..skills.numeral_concord_engine import RussianNumeralConcordEngine
from ..skills.generation import RussianSentenceGenerator


class RussianCompositionPipeline:
    def __init__(self):
        self.case_engine = RussianCaseEngine()
        self.verb_conjugator = RussianVerbAspectConjugator()
        self.numeral_engine = RussianNumeralConcordEngine(self.case_engine)
        self.generator = RussianSentenceGenerator(
            self.case_engine, self.verb_conjugator, self.numeral_engine
        )

    def compose_report(
        self,
        engineer_name: str,
        task_count: int,
        component_lemma: str = "модуль",
        status: str = "completed"
    ) -> Dict[str, Any]:
        """Composes a brief Russian technical status report with numeral concord and aspectual verbs."""
        # Numeral concord: task_count + задача
        task_phrase = self.numeral_engine.combine(
            number=task_count,
            lemma="задача",
            gender="fem",
            declension="1st"
        )

        # Module concord
        mod_phrase = self.numeral_engine.combine(
            number=task_count,
            lemma=component_lemma,
            gender="masc",
            declension="2nd"
        )

        sent1 = f"Инженер {engineer_name} успешно завершил {task_phrase}."
        sent2 = f"В ходе работы было обновлено {mod_phrase}."
        sent3 = "Все функциональные тесты успешно пройдены без ошибок."

        full_text = f"{sent1} {sent2} {sent3}"

        return {
            "author": engineer_name,
            "tasks": task_count,
            "sentences": [sent1, sent2, sent3],
            "full_text": full_text
        }
