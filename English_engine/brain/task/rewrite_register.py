"""
Register and Style Transfer Engine.
Rewrites English text across communicative registers:
Informal <-> Formal Academic <-> Professional Corporate <-> Conversational.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from English_engine.brain.rules.rules_engine import RulesEngine, RegisterProfile


@dataclass
class RewriteResult:
    original_text: str
    target_register: str
    rewritten_text: str
    transformations_applied: List[str]
    initial_register: RegisterProfile
    final_register: RegisterProfile


class RegisterRewriter:
    """
    Transforms lexical, syntactic, and tonal elements to shift discourse register.
    """

    def __init__(self) -> None:
        self.rules_engine = RulesEngine()

        # Informal to Formal mappings
        self.informal_to_formal = {
            r"\bgonna\b": "going to",
            r"\bwanna\b": "wish to",
            r"\bgotta\b": "must",
            r"\bkinda\b": "somewhat",
            r"\byeah\b": "yes",
            r"\banyway\b": "nevertheless",
            r"\bfigure out\b": "determine",
            r"\blook into\b": "investigate",
            r"\bput off\b": "postpone",
            r"\bshow up\b": "arrive",
            r"\bbad\b": "suboptimal",
            r"\bgreat\b": "exemplary",
            r"\bbig\b": "substantial",
            r"\bkids\b": "children",
            r"\bguy\b": "individual",
            r"\blot of\b": "significant volume of",
            r"\blots of\b": "numerous",
        }

        # Formal to Conversational mappings
        self.formal_to_informal = {
            r"\bfurthermore\b": "also",
            r"\bconsequently\b": "so",
            r"\bhypothesize\b": "guess",
            r"\bsubstantiate\b": "back up",
            r"\bcommence\b": "start",
            r"\bterminate\b": "end",
            r"\butilize\b": "use",
            r"\bfacilitate\b": "help",
            r"\bdemonstrate\b": "show",
            r"\belucidate\b": "explain",
            r"\bpursuant to\b": "following",
        }

        # Contractions expansion dictionary
        self.contractions_expand = {
            r"\bdon't\b": "do not",
            r"\bdoesn't\b": "does not",
            r"\bdidn't\b": "did not",
            r"\bcan't\b": "cannot",
            r"\bwon't\b": "will not",
            r"\bit's\b": "it is",
            r"\bthat's\b": "that is",
            r"\bthere's\b": "there is",
            r"\bwe're\b": "we are",
            r"\bthey're\b": "they are",
            r"\bi'm\b": "I am",
        }

    def rewrite(self, text: str, target_register: str = "formal_academic") -> RewriteResult:
        initial_reg = self.rules_engine.detect_register(text)
        rewritten = text
        transforms: List[str] = []

        target_lower = target_register.lower()

        if "formal" in target_lower or "academic" in target_lower:
            # 1. Expand contractions
            for pat, repl in self.contractions_expand.items():
                if re.search(pat, rewritten, flags=re.IGNORECASE):
                    rewritten = re.sub(pat, repl, rewritten, flags=re.IGNORECASE)
                    transforms.append(f"Expanded contraction '{pat}' -> '{repl}'")

            # 2. Replace informal phrasal verbs and slang with Latinate vocabulary
            for pat, repl in self.informal_to_formal.items():
                if re.search(pat, rewritten, flags=re.IGNORECASE):
                    rewritten = re.sub(pat, repl, rewritten, flags=re.IGNORECASE)
                    transforms.append(f"Elevated lexical register '{pat}' -> '{repl}'")

            # 3. Add formal discourse markers if simple sentence
            if not any(w in rewritten.lower() for w in ["furthermore", "consequently", "therefore", "thus"]):
                rewritten = "Furthermore, " + rewritten[0].lower() + rewritten[1:]
                transforms.append("Appended cohesive formal discourse connector")

        elif "conversational" in target_lower or "informal" in target_lower:
            # 1. Replace formal Latinate words with Anglo-Saxon / casual alternatives
            for pat, repl in self.formal_to_informal.items():
                if re.search(pat, rewritten, flags=re.IGNORECASE):
                    rewritten = re.sub(pat, repl, rewritten, flags=re.IGNORECASE)
                    transforms.append(f"Softened formal register '{pat}' -> '{repl}'")

            # 2. Contract words where appropriate
            for pat, repl in [("do not", "don't"), ("cannot", "can't"), ("it is", "it's"), ("that is", "that's")]:
                if pat in rewritten.lower():
                    rewritten = re.sub(rf"\b{pat}\b", repl, rewritten, flags=re.IGNORECASE)
                    transforms.append(f"Contracted '{pat}' -> '{repl}'")

        final_reg = self.rules_engine.detect_register(rewritten)

        return RewriteResult(
            original_text=text,
            target_register=target_register,
            rewritten_text=rewritten,
            transformations_applied=transforms,
            initial_register=initial_reg,
            final_register=final_reg,
        )
