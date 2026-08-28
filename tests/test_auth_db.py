"""Comprehensive tests for Price-My-Car auth_db module.

Tests password hashing, user CRUD, login/lockout, and admin operations.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    """Create a temporary users DB file."""
    db_path = tmp_path / "users_db.json"
    db = {
        "users": {},
        "meta": {
            "total_users": 0,
            "total_predictions": 0,
            "app_version": "6.0",
            "last_updated": datetime.now().isoformat(),
        },
    }
    db_path.write_text(json.dumps(db))
    return db_path


class TestPasswordHashing:
    """Test bcrypt password hashing and verification."""

    def test_hash_password_returns_string(self) -> None:
        from app.auth_db import hash_password

        result = hash_password("test123")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_password_is_deterministic_unique(self) -> None:
        from app.auth_db import hash_password

        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        # bcrypt salts are random, so hashes differ
        assert h1 != h2

    def test_verify_password_correct(self) -> None:
        from app.auth_db import hash_password, verify_password

        hashed = hash_password("correct_password")
        assert verify_password("correct_password", hashed) is True

    def test_verify_password_incorrect(self) -> None:
        from app.auth_db import hash_password, verify_password

        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_empty_string(self) -> None:
        from app.auth_db import hash_password, verify_password

        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("not_empty", hashed) is False


class TestUserCreation:
    """Test user creation and retrieval."""

    def test_create_user_new(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user

            result = create_user("testuser", "password123", "test@example.com")
            assert result is True

    def test_create_user_duplicate(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user

            create_user("testuser", "password123", "test@example.com")
            result = create_user("testuser", "password456", "other@example.com")
            assert result is False

    def test_get_user_by_username(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user, get_user_by_username

            create_user("testuser", "password123", "test@example.com")
            user = get_user_by_username("testuser")
            assert user is not None
            assert user["username"] == "testuser"
            assert user["email"] == "test@example.com"

    def test_get_user_nonexistent(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import get_user_by_username

            user = get_user_by_username("nonexistent")
            assert user is None

    def test_username_exists(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user, username_exists

            assert username_exists("testuser") is False
            create_user("testuser", "password123", "test@example.com")
            assert username_exists("testuser") is True

    def test_email_exists(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user, email_exists

            assert email_exists("test@example.com") is False
            create_user("testuser", "password123", "test@example.com")
            assert email_exists("test@example.com") is True


class TestLoginLockout:
    """Test login attempt tracking and lockout."""

    def test_login_success(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user, login_user

            create_user("testuser", "password123", "test@example.com")
            result = login_user("testuser", "password123")
            assert result is True

    def test_login_wrong_password(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user, login_user

            create_user("testuser", "password123", "test@example.com")
            result = login_user("testuser", "wrong_password")
            assert result is False

    def test_login_lockout_after_max_attempts(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user, login_user

            create_user("testuser", "password123", "test@example.com")
            for _ in range(5):
                login_user("testuser", "wrong_password")
            # Account should be locked
            result = login_user("testuser", "password123")
            assert result is False

    def test_delete_user(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user, delete_user, get_user_by_username

            create_user("testuser", "password123", "test@example.com")
            delete_user("testuser")
            assert get_user_by_username("testuser") is None


class TestUserUpdates:
    """Test user profile updates."""

    def test_update_user_profile(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user, get_user_by_username, update_user_profile

            create_user("testuser", "password123", "test@example.com")
            update_user_profile("testuser", display_name="Test User")
            user = get_user_by_username("testuser")
            assert user is not None

    def test_save_comparison(self, tmp_db: Path) -> None:
        with patch("app.auth_db.USERS_DB_PATH", tmp_db):
            from app.auth_db import create_user, save_comparison

            create_user("testuser", "password123", "test@example.com")
            # Should not raise
            save_comparison("testuser", {"car": "Toyota", "price": 500000})
