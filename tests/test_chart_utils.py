import pytest

pytestmark = pytest.mark.unit

"""Tests for Price-My-Car chart_utils module.

Tests Plotly chart configuration and helper functions.
"""

from unittest.mock import MagicMock, patch


class TestApplyPlotlyConfig:
    """Test Plotly chart configuration application."""

    def test_apply_config_sets_template(self) -> None:
        from app.chart_utils import apply_plotly_config

        mock_fig = MagicMock()
        result = apply_plotly_config(mock_fig)
        mock_fig.update_layout.assert_called_once()
        assert result == mock_fig

    def test_apply_config_custom_height(self) -> None:
        from app.chart_utils import apply_plotly_config

        mock_fig = MagicMock()
        apply_plotly_config(mock_fig, height=500)
        call_kwargs = mock_fig.update_layout.call_args[1]
        assert call_kwargs["height"] == 500

    def test_apply_config_default_height(self) -> None:
        from app.chart_utils import apply_plotly_config

        mock_fig = MagicMock()
        apply_plotly_config(mock_fig)
        call_kwargs = mock_fig.update_layout.call_args[1]
        assert call_kwargs["height"] == 350


class TestShowChart:
    """Test chart display helper."""

    def test_show_chart_calls_st_plotly(self) -> None:
        from app.chart_utils import show_chart

        mock_fig = MagicMock()
        with patch("app.chart_utils.st") as mock_st:
            show_chart(mock_fig)
            mock_st.plotly_chart.assert_called_once()
