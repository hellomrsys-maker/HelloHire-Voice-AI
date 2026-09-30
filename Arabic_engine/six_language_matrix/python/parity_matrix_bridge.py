"""
Arabic parity Six-Language Matrix bridge shim. Delegates to the shared
BaseSixLanguageMatrixBridge (Rust/C++/CUDA/Java/Julia/Python) with the Arabic
profile, synchronising the 64-byte AMSV. Magic id 0x41524149.
"""

from __future__ import annotations
from typing import Dict, Any, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from engine_common.base_components import BaseSixLanguageMatrixBridge
from engine_common.language_profile import get_profile


class ArabicParityMatrixBridge(BaseSixLanguageMatrixBridge):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None) -> None:
        super().__init__(profile=get_profile("Arabic_engine"), amsv_view=amsv_view)

    def execute_matrix_pipeline(self, text: str, request_id: str = "req-ar") -> Dict[str, Any]:
        return self.coordinate(text, request_id=request_id)
