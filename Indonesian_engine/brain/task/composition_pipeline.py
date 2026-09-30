"""
Indonesian Engine — Composition Task Pipeline
Synthesizes prose with classical proverbs (peribahasa), stylistic markers, and dialect adaptation.
"""

from typing import Dict, Any, List
from ..skills.pragmatics_engine import adapt_gaul_to_baku

PERIBAHASA_LIST = [
    "ada udang di balik batu",
    "sambil menyelam minum air",
    "tong kosong nyaring bunyinya",
    "besar pasak daripada tiang",
    "air tenang menghanyutkan"
]

class IndonesianCompositionPipeline:
    """Task pipeline for Indonesian prose synthesis, literary peribahasa analysis, and dialect adaptation."""

    def compose_prose(self, topic: str, style: str = "standard_formal") -> str:
        """Compose stylized Indonesian prose."""
        if style == "rhetorical":
            return (
                f"Terkait dengan pengembangan {topic}, kita menyadari bahwa setiap langkah memerlukan "
                f"kebijaksanaan mendalam, bak pepatah sambil menyelam minum air demi mencapai hasil optimal."
            )
        return (
            f"Proyek mengenai {topic} berjalan sesuai dengan rencana strategis nasional. "
            f"Seluruh komponen telah terintegrasi dengan baik untuk menjamin keandalan sistem."
        )

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analyze literary and rhetorical features in Indonesian prose."""
        t_clean = text.lower()
        proverbs_found = []
        for p in PERIBAHASA_LIST:
            if p in t_clean:
                proverbs_found.append(p)
                
        is_rhetorical = len(proverbs_found) > 0 or any(
            m in t_clean for m in ["terkait dengan", "kebijaksanaan mendalam", "bak pepatah"]
        )
        
        return {
            "style": "classical_rhetorical" if is_rhetorical else "standard",
            "proverbs_found": proverbs_found,
            "has_rhetorical_markers": is_rhetorical
        }

    def adapt_dialect(self, text: str, target: str = "baku") -> str:
        """Normalize colloquial Jakartan slang (Bahasa Gaul) to standard formal Bahasa Baku."""
        return adapt_gaul_to_baku(text)
