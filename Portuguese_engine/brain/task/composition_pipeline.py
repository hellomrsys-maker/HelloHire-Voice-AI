"""
Portuguese Composition Pipeline Task: Synthesizes multi-clause narrative, descriptive,
and argumentative prose with personal infinitives and progressive aspect.
"""

from typing import Dict, Any, List, Optional
from ..skills.generation import PortugueseGenerator
from ..skills.verb_conjugator import PortugueseVerbConjugator


class PortugueseCompositionPipelineTask:
    """
    Generates coherent Portuguese prose with stylistic and aspectual richness.
    """

    def __init__(self):
        self.generator = PortugueseGenerator()
        self.conjugator = PortugueseVerbConjugator()

    def compose_narrative(
        self,
        topic: str = "daily_work",
        subject: str = "Nós",
        dialect: str = "pt_br"
    ) -> Dict[str, Any]:
        """
        Synthesizes a sequence of coordinated or subordinate Portuguese sentences.
        """
        clauses = []

        if topic == "project":
            # Clause 1 with personal infinitive: Para nós fazermos o projeto...
            c1 = "Para nós fazermos o projeto com excelência, analisamos todos os dados."
            # Clause 2 with progressive aspect:
            if dialect == "pt_pt":
                c2 = "Estamos a preparar o relatório com grande atenção aos detalhes."
            else:
                c2 = "Estamos preparando o relatório com grande atenção aos detalhes."
            # Clause 3 with future subjunctive:
            c3 = "Quando eles chegarem, apresentaremos os resultados finais."
            clauses.extend([c1, c2, c3])
        else:
            c1 = "Começamos o dia com uma reunião produtiva sobre os objetivos."
            c2 = "Em seguida, trabalhamos nas tarefas essenciais da equipe."
            c3 = "Concluímos o trabalho com sucesso e satisfação."
            clauses.extend([c1, c2, c3])

        composed_text = " ".join(clauses)

        return {
            "topic": topic,
            "subject": subject,
            "dialect": dialect,
            "clauses": clauses,
            "composed_prose": composed_text
        }
