"""
Amharic parity Six-Language Matrix bridge shim. Delegates to the shared
BaseSixLanguageMatrixBridge (Rust/C++/CUDA/Java/Julia/Python) with the Amharic
profile, synchronising the 64-byte AMSV. Magic id 0x414d4841.
"""

from __future__ import annotations
from typing import Dict, Any, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from engine_common.base_components import BaseSixLanguageMatrixBridge
from engine_common.language_profile import get_profile


class AmharicParityMatrixBridge(BaseSixLanguageMatrixBridge):
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None) -> None:
        super().__init__(profile=get_profile("Amharic_engine"), amsv_view=amsv_view)

    def execute_matrix_pipeline(self, text: str, request_id: str = "req-am") -> Dict[str, Any]:
        return self.coordinate(text, request_id=request_id)
