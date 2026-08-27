"""AutoIntel — Authentication pages (login, signup, forgot password)."""

from __future__ import annotations

import time

import streamlit as st

from app.auth_db import (
    create_user,
    email_exists,
    hash_password,
    load_users_db,
    login_user,
    save_users_db,
    username_exists,
    verify_password,
)

def render_login_page() -> None:
    """Full-page centered login form with glass-morphism card."""
    st.markdown(
        """
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem">
      <div style="max-width:420px;width:100%">
        <div style="text-align:center;margin-bottom:1.5rem">
          <div style="font-size:3rem">🚗</div>
          <h1 class="hero-title" style="font-size:2.2rem">AutoIntel</h1>
          <p style="color:#9da3b4;font-size:0.9rem">Your AI-powered used car intelligence platform</p>
        </div>
        <div class="auth-card">
          <h3 style="color:#e8eaf0;margin:0 0 1.5rem;text-align:center;font-size:1.3rem">Welcome Back</h3>
    """,
        unsafe_allow_html=True,
    )

    # Check login lockout (server-side persistent lockout is enforced in login_user())
    # This client-side check provides immediate feedback without a server round-trip
    lock_time = st.session_state.get("login_lock_time", 0)
    attempts = st.session_state.get("login_attempts", 0)
    if time.time() - lock_time < 15 * 60 and attempts >= 5:
        remaining_secs = int(15 * 60 - (time.time() - lock_time))
        remaining_min = remaining_secs // 60
        remaining_sec = remaining_secs % 60
        st.warning(
            f"⏳ Too many failed attempts. Please wait {remaining_min}m {remaining_sec}s before trying again."
        )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_pass",
        )
        st.checkbox(
            "Remember me",
            value=True,
            key="login_remember",
            disabled=True,
            help="Session persists until browser close",
        )
        submitted = st.form_submit_button("🔑 Sign In", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("❌ Please fill in all fields")
            else:
                db = load_users_db()
                success, msg, user = login_user(db, username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.login_attempts = 0
                    st.toast(
                        f"Welcome back, {user.get('full_name', username)}! 🚗",
                        icon="✅",
                    )
                    st.rerun()
                else:
                    st.session_state.login_attempts = attempts + 1
                    st.session_state.login_lock_time = time.time()
                    st.error(f"❌ {msg}")

    nav_cols = st.columns(2)
    with nav_cols[0]:
        if st.button(
            "Don't have an account? → Sign Up",
            key="auth_signup_btn2",
            use_container_width=True,
        ):
            st.session_state.auth_page = "signup"
            st.rerun()
    with nav_cols[1]:
        if st.button(
            "Forgot password?",
            key="auth_forgot_btn2",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.auth_page = "forgot"
            st.rerun()

    # Demo credentials hint
    st.markdown(
        """
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:0.75rem;margin-top:1rem;text-align:center">
      <p style="color:#9da3b4;font-size:0.75rem;margin:0">💡 Demo: username = <strong>demo</strong> | password = <strong>demo123</strong></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Ensure demo user exists
    db = load_users_db()
    if not username_exists(db, "demo"):
        create_user(db, "demo", "demo@example.com", "demo123", "Demo User")

    # "Back" flow for signup/forgot
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_signup_page() -> None:
    """Signup page with password strength meter and real-time validation."""
    st.markdown(
        """
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem">
      <div style="max-width:420px;width:100%">
        <div style="text-align:center;margin-bottom:1.5rem">
          <div style="font-size:3rem">🚗</div>
          <h1 class="hero-title" style="font-size:2.2rem">Create Account</h1>
          <p style="color:#9da3b4;font-size:0.9rem">Join AutoIntel today</p>
        </div>
        <div class="auth-card">
    """,
        unsafe_allow_html=True,
    )

    with st.form("signup_form", clear_on_submit=False):
        full_name = st.text_input("Full Name", placeholder="John Doe", key="su_name")
        username = st.text_input(
            "Username",
            placeholder="johndoe",
            key="su_user",
            help="Min 3 chars, alphanumeric + underscore only",
        )
        email = st.text_input("Email", placeholder="john@example.com", key="su_email")
        password = st.text_input("Password", type="password", key="su_pass")
        # Password strength meter (real-time, updates on each widget change)
        pwd_val = st.session_state.get("su_pass", "")
        if pwd_val:
            pwd_len = len(pwd_val)
            has_upper = any(c.isupper() for c in pwd_val)
            has_lower = any(c.islower() for c in pwd_val)
            has_digit = any(c.isdigit() for c in pwd_val)
            any(not c.isalnum() for c in pwd_val)
            if pwd_len < 6:
                strength_pct, strength_color, strength_label = 20, "#ef233c", "Weak"
            elif pwd_len < 10 or not (has_upper and has_lower and has_digit):
                strength_pct, strength_color, strength_label = 50, "#f48c06", "Medium"
            else:
                strength_pct, strength_color, strength_label = 90, "#52b788", "Strong"
            st.markdown(
                f"""
            <div class="pwd-strength">
              <div class="pwd-bar" style="width:{strength_pct}%;background:{strength_color}"></div>
            </div>
            <p style="color:{strength_color};font-size:0.75rem;margin:2px 0 8px">{strength_label}</p>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
            <div class="pwd-strength">
              <div class="pwd-bar" style="width:0%;background:#555"></div>
            </div>
            <p style="color:#5a6270;font-size:0.75rem;margin:2px 0 8px">Enter a password</p>
            """,
                unsafe_allow_html=True,
            )
        confirm = st.text_input("Confirm Password", type="password", key="su_confirm")
        # Real-time confirm match indicator
        conf_val = st.session_state.get("su_confirm", "")
        if conf_val:
            if pwd_val and pwd_val == conf_val:
                st.markdown(
                    '<p style="color:#52b788;font-size:0.75rem;margin:2px 0 8px">\U0001f7e2 Passwords match</p>',
                    unsafe_allow_html=True,
                )
            elif conf_val:
                st.markdown(
                    '<p style="color:#ef233c;font-size:0.75rem;margin:2px 0 8px">\u274c Passwords do not match</p>',
                    unsafe_allow_html=True,
                )
        agree = st.checkbox("I agree to terms", key="su_agree")
        submitted = st.form_submit_button(
            "🎉 Create Account", use_container_width=True, type="primary"
        )

        if submitted:
            errors = []
            if not full_name:
                errors.append("Full name is required")
            if len(username) < 3:
                errors.append("Username must be at least 3 characters")
            if not username.isalnum() and "_" not in username:
                errors.append("Username: letters, numbers, underscore only")
            if "@" not in email or "." not in email:
                errors.append("Invalid email format")
            if len(password) < 6:
                errors.append("Password must be at least 6 characters")
            if password != confirm:
                errors.append("Passwords do not match")
            if not agree:
                errors.append("You must agree to terms")

            db = load_users_db()
            if username_exists(db, username):
                errors.append("Username already taken")
            if email_exists(db, email):
                errors.append("Email already registered")

            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                user = create_user(db, username, email, password, full_name)
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.auth_page = "login"
                st.balloons()
                st.toast(f"🎉 Account created! Welcome, {full_name}!", icon="✅")

                # Welcome Tour modal (3-step overlay)
                st.markdown(
                    """
                <div style="background:rgba(0,0,0,0.8);position:fixed;top:0;left:0;right:0;bottom:0;z-index:9999;display:flex;align-items:center;justify-content:center">
                  <div class="auth-card" style="max-width:500px;text-align:center">
                    <h2 style="color:#e8eaf0">👋 Welcome to AutoIntel!</h2>
                    <p style="color:#c8ccd4">Here's what you can do:</p>
                    <div style="text-align:left;margin:1.5rem 0">
                      <p style="color:#e8eaf0">🔮 <strong>Predict car prices</strong> with AI in seconds</p>
                      <p style="color:#e8eaf0">📊 <strong>Explore market intelligence</strong> and trends</p>
                      <p style="color:#e8eaf0">🤖 <strong>Compare 8 ML models</strong> side by side</p>
                    </div>
                  </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.rerun()

    if st.button("← Back to Login", key="su_back"):
        st.session_state.auth_page = "login"
        st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_forgot_password_page() -> None:
    """Simple forgot password page (cosmetic — no actual email sending)."""
    st.markdown(
        """
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem">
      <div style="max-width:420px;width:100%">
        <div style="text-align:center;margin-bottom:1.5rem">
          <div style="font-size:3rem">🔐</div>
          <h1 class="hero-title" style="font-size:2rem">Reset Password</h1>
          <p style="color:#9da3b4;font-size:0.9rem">Enter your email to receive a reset link</p>
        </div>
        <div class="auth-card">
    """,
        unsafe_allow_html=True,
    )

    with st.form("forgot_form"):
        email = st.text_input("Email", placeholder="john@example.com", key="fp_email")
        submitted = st.form_submit_button(
            "📧 Send Reset Link", use_container_width=True, type="primary"
        )
        if submitted:
            db = load_users_db()
            if email_exists(db, email):
                st.success(
                    "✅ If that email exists, a reset link was sent (demo project — no actual email sent)"
                )
            else:
                st.info("ℹ️ If that email exists, a reset link was sent")

    if st.button("← Back to Login", key="fp_back"):
        st.session_state.auth_page = "login"
        st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
