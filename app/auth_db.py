"""AutoIntel — User authentication & database helpers.

Extracted from streamlit_app.py to avoid circular imports between
page modules and the main orchestrator.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
import streamlit as st

USERS_DB_PATH = Path("users_db.json")

def load_users_db() -> dict:
    if not USERS_DB_PATH.exists():
        db = {
            "users": {},
            "meta": {
                "total_users": 0,
                "total_predictions": 0,
                "app_version": "6.0",
                "last_updated": datetime.now().isoformat(),
            },
        }
        save_users_db(db)
        return db
    with open(USERS_DB_PATH, "r") as f:
        return json.load(f)


def save_users_db(db: dict) -> None:
    db["meta"]["last_updated"] = datetime.now().isoformat()
    with open(USERS_DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, AttributeError):
        return False


def username_exists(db: dict, username: str) -> bool:
    return any(u["username"].lower() == username.lower() for u in db["users"].values())


def email_exists(db: dict, email: str) -> bool:
    return any(u["email"].lower() == email.lower() for u in db["users"].values())


def get_user_by_username(db: dict, username: str) -> dict | None:
    for u in db["users"].values():
        if u["username"].lower() == username.lower():
            return u
    return None


AVATAR_COLORS = ["#e85d04", "#4895ef", "#52b788", "#9b5de5", "#f48c06", "#ff6b6b"]


def create_user(db: dict, username: str, email: str, password: str, full_name: str) -> dict:
    uid = str(uuid.uuid4())
    user = {
        "user_id": uid,
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "role": "admin" if len(db["users"]) == 0 else "user",
        "avatar_color": AVATAR_COLORS[len(db["users"]) % len(AVATAR_COLORS)],
        "created_at": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat(),
        "login_count": 1,
        "preferences": {
            "default_model": "xgboost",
            "confidence_interval": "±15%",
            "expert_mode": False,
            "theme_accent": "#e85d04",
        },
        "prediction_history": [],
        "saved_comparisons": [],
        "page_visits": {},
    }
    db["users"][uid] = user
    db["meta"]["total_users"] = len(db["users"])
    save_users_db(db)
    return user


def login_user(db: dict, username: str, password: str) -> tuple:
    """
    Authenticate a user with rate limiting and lockout protection.
    Tracks failed attempts persistently in the database.
    """
    user = get_user_by_username(db, username)
    if not user:
        return False, "Username not found.", {}

    user["user_id"]

    # Check persistent lockout
    lock_until = user.get("lock_until")
    if lock_until:
        try:
            lock_dt = datetime.fromisoformat(lock_until)
            if datetime.now() < lock_dt:
                remaining_minutes = int((lock_dt - datetime.now()).total_seconds() / 60)
                return (
                    False,
                    f"Account locked due to too many failed attempts. Try again in {remaining_minutes} minute(s).",
                    {},
                )
        except (ValueError, TypeError):
            pass  # malformed timestamp, ignore lock

    # Reset lock if lockout period has expired
    if lock_until:
        try:
            lock_dt = datetime.fromisoformat(lock_until)
            if datetime.now() >= lock_dt:
                user["failed_attempts"] = 0
                user["lock_until"] = None
        except (ValueError, TypeError):
            pass

    if not verify_password(password, user["password_hash"]):
        # Track failed attempt persistently
        attempts = user.get("failed_attempts", 0) + 1
        user["failed_attempts"] = attempts
        if attempts >= MAX_LOGIN_ATTEMPTS:
            lock_time = datetime.now() + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
            user["lock_until"] = lock_time.isoformat()
            save_users_db(db)
            return (
                False,
                f"Maximum login attempts exceeded. Account locked for {LOGIN_LOCKOUT_MINUTES} minutes.",
                {},
            )
        save_users_db(db)
        remaining = MAX_LOGIN_ATTEMPTS - attempts
        return False, f"Incorrect password. {remaining} attempt(s) remaining.", {}

    # Successful login — reset failed attempts
    user["failed_attempts"] = 0
    user["lock_until"] = None
    user["last_login"] = datetime.now().isoformat()
    user["login_count"] = user.get("login_count", 0) + 1
    db["users"][user["user_id"]] = user
    save_users_db(db)
    return True, "Login successful!", user


def save_prediction_to_history(user_id: str, prediction: dict) -> None:
    db = load_users_db()
    if user_id in db["users"]:
        db["users"][user_id]["prediction_history"].append(prediction)
        db["meta"]["total_predictions"] += 1
        save_users_db(db)


def update_user_preferences(user_id: str, prefs: dict) -> None:
    db = load_users_db()
    if user_id in db["users"]:
        db["users"][user_id]["preferences"].update(prefs)
        save_users_db(db)


def track_page_visit(user_id: str, page_name: str) -> None:
    db = load_users_db()
    if user_id in db["users"]:
        visits = db["users"][user_id].get("page_visits", {})
        visits[page_name] = visits.get(page_name, 0) + 1
        db["users"][user_id]["page_visits"] = visits
        save_users_db(db)


def save_comparison(user_id: str, name: str, car_a: dict, car_b: dict) -> None:
    db = load_users_db()
    if user_id in db["users"]:
        comp = {
            "comparison_id": str(uuid.uuid4()),
            "name": name,
            "car_a": car_a,
            "car_b": car_b,
            "created_at": datetime.now().isoformat(),
        }
        db["users"][user_id]["saved_comparisons"].append(comp)
        save_users_db(db)


def delete_user(user_id: str) -> None:
    db = load_users_db()
    if user_id in db["users"]:
        del db["users"][user_id]
        db["meta"]["total_users"] = len(db["users"])
        save_users_db(db)


def require_admin() -> bool:
    """
    Server-side admin authorization check.
    Verifies the current user's role directly from the database,
    not from session state (prevents client-side role tampering).
    """
    user = st.session_state.get("user", {})
    user_id = user.get("user_id")
    if not user_id:
        return False
    db = load_users_db()
    db_user = db["users"].get(user_id)
    return not (not db_user or db_user.get("role") != "admin")


def update_user_profile(user_id: str, full_name: str, email: str, avatar_color: str) -> None:
    db = load_users_db()
    if user_id in db["users"]:
        db["users"][user_id]["full_name"] = full_name
        db["users"][user_id]["email"] = email
        db["users"][user_id]["avatar_color"] = avatar_color
        save_users_db(db)


