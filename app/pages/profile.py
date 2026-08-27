"""AutoIntel — User Profile page."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.auth_db import (
    hash_password,
    load_users_db,
    save_users_db,
    update_user_preferences,
    update_user_profile,
    verify_password,
)
from app.chart_utils import show_chart
from app.helpers import fmt_inr

def render_profile_page() -> None:
    """User profile page with 6 tabs."""
    user = st.session_state.get("user", {})
    uid = user.get("user_id", "")
    initials = (
        "".join(w[0].upper() for w in user.get("full_name", "U").split()[:2])
        if user.get("full_name")
        else "U"
    )
    avatar_color = user.get("avatar_color", "#e85d04")
    role = user.get("role", "user")
    created = user.get("created_at", "")[:10]
    last_login = user.get("last_login", "")[:19]
    login_count = user.get("login_count", 1)
    pred_history = user.get("prediction_history", [])
    saved_comps = user.get("saved_comparisons", [])

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown(
            f"""
        <div style="text-align:center;padding:1.5rem">
          <div class="avatar-circle" style="background:{avatar_color};width:90px;height:90px;font-size:2rem">{initials}</div>
          <h3 style="color:#e8eaf0;margin:0.5rem 0 0">{user.get("full_name", "User")}</h3>
          <p style="color:#9da3b4;font-size:0.8rem">@{user.get("username", "")}</p>
          <p style="color:#9da3b4;font-size:0.8rem">{user.get("email", "")}</p>
          <p style="margin:0.5rem 0">{"👑 Admin" if role == "admin" else "👤 User"}</p>
          <p style="color:#9da3b4;font-size:0.75rem">Member since {created}</p>
          <p style="color:#9da3b4;font-size:0.75rem">Logins: {login_count} | Last: {last_login[:10]}</p>
          <p style="color:#e85d04;font-weight:600">Total Predictions: {len(pred_history)}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_right:
        tabs = st.tabs(
            [
                "✏️ Edit Profile",
                "🔐 Change Password",
                "⚙️ Preferences",
                "📜 Prediction History",
                "💾 Saved Comparisons",
                "🗑️ Danger Zone",
            ]
        )

        with tabs[0]:
            with st.form("edit_profile"):
                new_name = st.text_input("Full Name", value=user.get("full_name", ""))
                new_email = st.text_input("Email", value=user.get("email", ""))
                colors_html = '<div style="display:flex;gap:8px;margin:8px 0">'
                avatar_colors = [
                    "#e85d04",
                    "#4895ef",
                    "#52b788",
                    "#9b5de5",
                    "#f48c06",
                    "#ff6b6b",
                ]
                for c in avatar_colors:
                    selected = (
                        "border:3px solid white"
                        if c == avatar_color
                        else "border:2px solid transparent"
                    )
                    colors_html += f'<div style="width:30px;height:30px;border-radius:50%;background:{c};{selected};cursor:pointer" title="{c}"></div>'
                colors_html += "</div>"
                st.markdown(colors_html, unsafe_allow_html=True)
                new_color = st.selectbox(
                    "Avatar Color",
                    avatar_colors,
                    index=avatar_colors.index(avatar_color) if avatar_color in avatar_colors else 0,
                )
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    update_user_profile(uid, new_name, new_email, new_color)
                    user["full_name"] = new_name
                    user["email"] = new_email
                    user["avatar_color"] = new_color
                    st.session_state.user = user
                    st.success("✅ Profile updated!")

        with tabs[1], st.form("change_pwd"):
            cur_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            conf_pwd = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("🔄 Update Password", use_container_width=True):
                if not verify_password(cur_pwd, user.get("password_hash", "")):
                    st.error("❌ Current password is incorrect")
                elif len(new_pwd) < 6:
                    st.error("❌ New password must be at least 6 characters")
                elif new_pwd != conf_pwd:
                    st.error("❌ Passwords do not match")
                else:
                    db = load_users_db()
                    db["users"][uid]["password_hash"] = hash_password(new_pwd)
                    save_users_db(db)
                    st.success("✅ Password updated! Please log in again.")
                    st.info("Relogin to continue")

        with tabs[2], st.form("prefs_form"):
            default_model = st.selectbox(
                "Default Model",
                [
                    "xgboost",
                    "linear_regression",
                    "ridge",
                    "gradient_boosting",
                    "random_forest",
                ],
                index=[
                    "xgboost",
                    "linear_regression",
                    "ridge",
                    "gradient_boosting",
                    "random_forest",
                ].index(user.get("preferences", {}).get("default_model", "xgboost")),
            )
            ci = st.select_slider(
                "Confidence Interval",
                ["±10%", "±15%", "±20%"],
                value=user.get("preferences", {}).get("confidence_interval", "±15%"),
            )
            expert_mode = st.toggle(
                "Expert Mode",
                value=user.get("preferences", {}).get("expert_mode", False),
            )
            accent = st.selectbox(
                "Theme Accent",
                ["#e85d04", "#f48c06", "#4895ef", "#52b788", "#9b5de5"],
                index=["#e85d04", "#f48c06", "#4895ef", "#52b788", "#9b5de5"].index(
                    user.get("preferences", {}).get("theme_accent", "#e85d04")
                ),
            )
            if st.form_submit_button("💾 Save Preferences", use_container_width=True):
                update_user_preferences(
                    uid,
                    {
                        "default_model": default_model,
                        "confidence_interval": ci,
                        "expert_mode": expert_mode,
                        "theme_accent": accent,
                    },
                )
                st.session_state.expert_mode = expert_mode
                st.success("✅ Preferences saved!")

        with tabs[3]:
            if pred_history:
                ph_df = pd.DataFrame(pred_history)
                ph_df = ph_df.sort_values("timestamp", ascending=False)
                st.dataframe(ph_df, use_container_width=True)
                # Mini line chart
                if "predicted_price" in ph_df.columns and "timestamp" in ph_df.columns:
                    ph_df["date"] = pd.to_datetime(ph_df["timestamp"])
                    chart_df = ph_df.sort_values("date")
                    fig = go.Figure(
                        data=[
                            go.Scatter(
                                x=chart_df["date"],
                                y=chart_df["predicted_price"],
                                mode="lines+markers",
                                line={"color": "#e85d04"},
                            )
                        ]
                    )
                    fig.update_layout(title="Prediction History", height=250)
                    show_chart(fig, 250)
                if st.checkbox("Confirm clear history", key="clear_hist"):
                    if st.button("🗑️ Clear History", use_container_width=True):
                        db = load_users_db()
                        db["users"][uid]["prediction_history"] = []
                        save_users_db(db)
                        st.success("✅ History cleared!")
                        st.rerun()
            else:
                st.info("No prediction history yet.")

        with tabs[4]:
            if saved_comps:
                for comp in saved_comps:
                    with st.expander(
                        f"📋 {comp.get('name', 'Comparison')} ({comp.get('created_at', '')[:10]})"
                    ):
                        st.json(comp)
            else:
                st.info("No saved comparisons yet.")

        with tabs[5]:
            st.markdown("### ⚠️ Danger Zone")
            st.warning("This action is irreversible. Type your username to confirm.")
            confirm_name = st.text_input("Type username to confirm deletion", key="danger_confirm")
            if st.button("🗑️ Delete My Account", use_container_width=True, type="primary"):
                if confirm_name == user.get("username"):
                    delete_user(uid)
                    for k in list(st.session_state.keys()):
                        del st.session_state[k]
                    st.rerun()
                else:
                    st.error("❌ Username does not match")
