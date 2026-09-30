"""
Indonesian Engine — Email Task Pipeline
Generates and audits formal surat resmi (official letters) or informal correspondence.
"""

from typing import Dict, Any, Optional
from ..skills.tokenization import tokenize_words
from ..skills.pragmatics_engine import format_salutation, format_closing, classify_register

class IndonesianEmailPipeline:
    """Task pipeline for Indonesian formal letters and email correspondence."""

    def compose(
        self,
        form: str = "formal",
        recipient_name: str = "Santoso",
        recipient_title: str = "Direktur Utama",
        body: str = "",
        sender_name: str = "Budi Wijaya",
        organization: Optional[str] = "Solo Rock"
    ) -> str:
        """Compose a structured Indonesian email or official letter."""
        is_formal = form.lower() == "formal"
        salutation = format_salutation(recipient_title, recipient_name, formal=is_formal)
        closing = format_closing(formal=is_formal)
        
        lines = [salutation, ""]
        if is_formal:
            lines.append("Sehubungan dengan rencana pelaksanaan proyek kerja sama,")
            lines.append(body if body else "bersama ini kami sampaikan laporan teknis implementasi sistem.")
            lines.append("")
            lines.append(closing)
            lines.append("")
            lines.append(f"{sender_name}")
            if organization:
                lines.append(f"{organization}")
        else:
            lines.append("Semoga kabarmu baik selalu.")
            lines.append(body if body else "Saya menulis pesan ini untuk mengabarkan kemajuan proyek kita.")
            lines.append("")
            lines.append(closing)
            lines.append(f"{sender_name}")
            
        return "\n".join(lines)

    def audit(self, email_text: str) -> Dict[str, Any]:
        """Audit register consistency in an Indonesian email."""
        reg = classify_register(email_text)
        has_formal_salutation = any(
            s in email_text for s in ["Dengan hormat", "Yang terhormat", "Yth."]
        )
        has_formal_closing = any(
            c in email_text for c in ["Hormat kami", "Hormat saya", "terima kasih"]
        )
        words = set(tokenize_words(email_text.lower()))
        has_gaul_leak = any(
            g in words for g in ["nggak", "gak", "kagak", "banget", "udah", "belom", "gue", "lu", "dong", "sih", "kok", "deh"]
        )
        
        is_consistent = not (has_formal_salutation and has_gaul_leak)
        
        return {
            "register": reg["register"],
            "has_formal_salutation": has_formal_salutation,
            "has_formal_closing": has_formal_closing,
            "is_consistent": is_consistent,
            "passed": is_consistent
        }
