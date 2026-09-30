"""
Italian Engine — Email Task Pipeline
Generates and audits formal institutional and diplomatic correspondence (dare del Lei)
or informal personal letters (dare del tu).
"""

from typing import Dict, Any, Optional
from ..skills.pragmatics_engine import format_salutation, format_closing, classify_register

class ItalianEmailPipeline:
    """Task pipeline for Italian email and epistolary correspondence."""

    def compose(
        self,
        form: str = "formal",
        recipient_surname: str = "Rossi",
        recipient_title: str = "Dottore",
        body: str = "",
        sender_name: str = "Marco Bianchi",
        organization: Optional[str] = "Solo Rock"
    ) -> str:
        """Compose a structured Italian email."""
        is_formal = form.lower() == "formal"
        salutation = format_salutation(recipient_title, recipient_surname, formal=is_formal)
        closing = format_closing(formal=is_formal)
        
        lines = [salutation, ""]
        if is_formal:
            lines.append("La ringrazio per la Sua cortese attenzione.")
            lines.append(body if body else "Le trasmetto in allegato la documentazione tecnica richiesta.")
            lines.append("")
            lines.append(closing)
            lines.append("")
            lines.append(f"{sender_name}")
            if organization:
                lines.append(f"{organization}")
        else:
            lines.append("Spero che tutto proceda bene.")
            lines.append(body if body else "Ti scrivo per aggiornarti sulle novità del progetto.")
            lines.append("")
            lines.append(closing)
            lines.append(f"{sender_name}")
            
        return "\n".join(lines)

    def audit(self, email_text: str) -> Dict[str, Any]:
        """Audit register consistency in an Italian email."""
        reg = classify_register(email_text)
        has_formal_salutation = any(
            s in email_text for s in ["Gentile", "Egregio", "Chiarissimo", "Egregia"]
        )
        has_formal_closing = any(
            c in email_text for c in ["Cordiali saluti", "Distinti saluti", "cortese riscontro"]
        )
        has_informal_leak = any(
            i in email_text.lower() for i in ["ciao", "ti scrivo", "il tuo", "un abbraccio", "baci"]
        )
        
        is_consistent = not (has_formal_salutation and has_informal_leak)
        
        return {
            "register": reg["register"],
            "has_formal_salutation": has_formal_salutation,
            "has_formal_closing": has_formal_closing,
            "is_consistent": is_consistent,
            "passed": is_consistent
        }
