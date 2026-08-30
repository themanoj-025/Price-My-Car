"""Tests for shared context module."""

import pandas as pd
import pytest

from app.pages.shared import SharedContext


class TestSharedContext:
    """Tests for SharedContext dataclass."""

    def test_creation(self) -> None:
        ctx = SharedContext(
            df=pd.DataFrame({"price": [100000]}),
            preprocessor=None,
            models={},
            pp_data={},
            gs_results={},
            companies=["Maruti"],
            fuel_types=["Petrol"],
        )
        assert ctx.demo_mode is False
        assert ctx.current_year == 2025

    def test_demo_mode(self) -> None:
        ctx = SharedContext(
            df=pd.DataFrame(),
            preprocessor=None,
            models={},
            pp_data={},
            gs_results={},
            companies=[],
            fuel_types=[],
            demo_mode=True,
        )
        assert ctx.demo_mode is True

    def test_custom_year(self) -> None:
        ctx = SharedContext(
            df=pd.DataFrame(),
            preprocessor=None,
            models={},
            pp_data={},
            gs_results={},
            companies=[],
            fuel_types=[],
            current_year=2026,
        )
        assert ctx.current_year == 2026

    def test_models_dict(self) -> None:
        ctx = SharedContext(
            df=pd.DataFrame(),
            preprocessor=None,
            models={"linear": "m1", "rf": "m2"},
            pp_data={},
            gs_results={},
            companies=[],
            fuel_types=[],
        )
        assert len(ctx.models) == 2
        assert "linear" in ctx.models
