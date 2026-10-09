"""AutoIntel — Admin Panel."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.auth_db import USERS_DB_PATH, load_users_db, save_users_db
from app.chart_utils import show_chart


def render_admin_panel() -> None:
    """Admin-only panel with users, analytics, and settings tabs."""
    st.markdown("## 🛡️ Admin Panel")
    db = load_users_db()
    users = list(db["users"].values())

    tabs = st.tabs(["👥 All Users", "📊 Usage Analytics", "🔧 App Settings"])

    with tabs[0]:
        st.metric("Total Users", len(users))
        if users:
            u_df = pd.DataFrame(users)
            cols = [
                "username",
                "email",
                "full_name",
                "role",
                "created_at",
                "login_count",
                "user_id",
            ]
            cols = [c for c in cols if c in u_df.columns]
            display = u_df[cols].copy() if cols else u_df.copy()
            st.dataframe(display, use_container_width=True)
            # Export
            csv_out = u_df.to_csv(index=False).encode()
            st.download_button(
                "📥 Export Users CSV",
                csv_out,
                "users_export.csv",
                "text/csv",
                use_container_width=True,
            )

    with tabs[1]:
        total_preds = db.get("meta", {}).get("total_predictions", 0)
        st.metric("Total Predictions (All Users)", total_preds)
        # Model usage pie (from prediction_history)
        all_preds = []
        for u in users:
            all_preds.extend(u.get("prediction_history", []))
        if all_preds:
            model_counts = {}
            for p in all_preds:
                m = p.get("model_used", "unknown")
                model_counts[m] = model_counts.get(m, 0) + 1
            if model_counts:
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=list(model_counts.keys()),
                            values=list(model_counts.values()),
                            marker={
                                "colors": [
                                    "#e85d04",
                                    "#4895ef",
                                    "#52b788",
                                    "#9b5de5",
                                    "#f48c06",
                                ]
                            },
                            hole=0.4,
                        )
                    ]
                )
                fig.update_layout(title="Model Usage Distribution", height=300)
                show_chart(fig, 300)

    with tabs[2]:
        st.markdown(f"**App Version:** {db.get('meta', {}).get('app_version', '6.0')}")
        st.markdown(f"**DB Path:** `{USERS_DB_PATH.resolve()}`")
        st.markdown(f"**Last Updated:** {db.get('meta', {}).get('last_updated', '')}")
        # Backup DB
        with open(USERS_DB_PATH, "rb") as f:
            st.download_button(
                "📦 Backup DB",
                f.read(),
                "users_db_backup.json",
                "application/json",
                use_container_width=True,
            )
        if st.button("🗑️ Clear All Prediction Histories", use_container_width=True):
            for u in db["users"].values():
                u["prediction_history"] = []
            save_users_db(db)
            st.success("✅ All prediction histories cleared!")
