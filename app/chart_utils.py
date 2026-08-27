"""AutoIntel — Plotly chart helpers (Streamlit-dependent).

Extracted from streamlit_app.py so page modules can import them without
creating circular dependencies.
"""

from __future__ import annotations

import streamlit as st


def apply_plotly_config(fig: object, height: int | None = None) -> object:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,16,25,0.8)",
        font={"family": "DM Sans", "color": "#e8eaf0"},
        height=height or 350,
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 10},
        },
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", gridwidth=1, title_font={"size": 11})
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", gridwidth=1, title_font={"size": 11})
    for trace in fig.data:
        if trace.__class__.__name__ not in (
            "Heatmap",
            "Heatmapgl",
            "Histogram2d",
            "Histogram2dContour",
        ):
            trace.update(marker={"line": {"width": 0}})
    fig.update_layout(showlegend=False)
    fig.update_layout(legend={"font": {"size": 9}})
    fig.update_layout(hoverlabel={"bgcolor": "#1a1d24", "font_size": 12, "font_family": "DM Sans"})
    return fig


def show_chart(fig: object, height: int | None = None) -> None:
    fig = apply_plotly_config(fig, height)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
