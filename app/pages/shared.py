"""Shared state for all AutoIntel page modules.

Each page function receives a ``ctx`` :class:`SharedContext` containing the
data, models, and configuration needed to render.  The main
``streamlit_app.py`` orchestrator creates this once and passes it to every
page renderer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SharedContext:
    """Immutable bundle of state shared across all page modules."""

    df: Any  # pd.DataFrame
    preprocessor: Any
    models: dict[str, Any]
    pp_data: dict[str, Any]
    gs_results: dict[str, Any]
    companies: list[str]
    fuel_types: list[str]
    demo_mode: bool = False
    current_year: int = 2025
