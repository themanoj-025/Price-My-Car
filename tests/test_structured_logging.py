"""
Unit tests for AutoIntel — Structured JSON Logging (structured_logging.py).

Covers: JSONFormatter, setup_logger, request ID context, extra fields,
exception formatting, and logger caching behavior.
"""

import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.logging.structured_logging import (
    JSONFormatter,
    _configured_loggers,
    get_request_id,
    request_id_var,
    set_request_id,
    setup_logger,
)


def _close_all_handlers() -> None:
    """Close and remove all handlers from all loggers."""
    for name in list(logging.Logger.manager.loggerDict):
        logger = logging.getLogger(name)
        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)


@pytest.fixture(autouse=True)
def _clear_loggers() -> None:
    """Reset logger cache and context before each test."""
    _configured_loggers.clear()
    request_id_var.set(None)
    _close_all_handlers()
    yield
    _configured_loggers.clear()
    request_id_var.set(None)
    _close_all_handlers()


# ── JSONFormatter Tests ───────────────────────────────────────────────────

class TestJSONFormatter:
    def test_formats_basic_log_record(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="Hello world", args=(), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Hello world"
        assert "timestamp" in data

    def test_includes_module_and_function(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="/app/module.py",
            lineno=42, msg="Warning message", args=(), exc_info=None,
        )
        record.module = "module"
        record.funcName = "my_function"
        data = json.loads(formatter.format(record))
        assert data["module"] == "module"
        assert data["function"] == "my_function"
        assert data["line"] == 42

    def test_includes_request_id_from_context(self) -> None:
        formatter = JSONFormatter()
        request_id_var.set("abc-123")
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="With request ID", args=(), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        assert data["request_id"] == "abc-123"

    def test_no_request_id_when_not_set(self) -> None:
        formatter = JSONFormatter()
        request_id_var.set(None)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="No request ID", args=(), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        assert "request_id" not in data

    def test_includes_exception_info(self) -> None:
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py",
            lineno=1, msg="Error occurred", args=(), exc_info=exc_info,
        )
        data = json.loads(formatter.format(record))
        assert "exception" in data
        assert data["exception"]["type"] == "ValueError"
        assert data["exception"]["value"] == "test error"
        assert "traceback" in data["exception"]

    def test_no_exception_when_none(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="No error", args=(), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        assert "exception" not in data

    def test_extra_fields_merged(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="With extras", args=(), exc_info=None,
        )
        record.extra_fields = {"user_id": 42, "action": "login"}
        data = json.loads(formatter.format(record))
        assert data["user_id"] == 42
        assert data["action"] == "login"

    def test_message_with_args(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="User %s logged in from %s",
            args=("alice", "192.168.1.1"), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        assert data["message"] == "User alice logged in from 192.168.1.1"

    def test_valid_json_output(self) -> None:
        formatter = JSONFormatter()
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            record = logging.LogRecord(
                name="test", level=level, pathname="test.py",
                lineno=1, msg=f"Level {level}", args=(), exc_info=None,
            )
            data = json.loads(formatter.format(record))
            assert data["level"] == logging.getLevelName(level)


# ── setup_logger Tests (use per-test temp dirs, no shared fixture) ─────────

class TestSetupLogger:
    def _make_logger(self, name, **kwargs) -> tuple[object, ...]:
        """Create a logger and return it + a cleanup function."""
        tmpdir = tempfile.mkdtemp()
        logger = setup_logger(name, log_dir=tmpdir, **kwargs)
        return logger, tmpdir

    def _cleanup(self, logger, tmpdir) -> None:
        """Close handlers and remove temp dir."""
        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_creates_logger_with_name(self) -> None:
        logger, tmpdir = self._make_logger("test-api")
        try:
            assert logger.name == "test-api"
            assert logger.level == logging.INFO
        finally:
            self._cleanup(logger, tmpdir)

    def test_logger_has_file_handler(self) -> None:
        logger, tmpdir = self._make_logger("test-file-handler")
        try:
            file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
            assert len(file_handlers) == 1
        finally:
            self._cleanup(logger, tmpdir)

    def test_logger_has_console_handler(self) -> None:
        logger, tmpdir = self._make_logger("test-console-handler")
        try:
            stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)
                               and not isinstance(h, logging.handlers.RotatingFileHandler)]
            assert len(stream_handlers) == 1
        finally:
            self._cleanup(logger, tmpdir)

    def test_logger_caching(self) -> None:
        logger1, tmpdir1 = self._make_logger("test-cached")
        try:
            handler_count = len(logger1.handlers)
            logger2, tmpdir2 = self._make_logger("test-cached")
            try:
                assert logger1 is logger2
                assert len(logger2.handlers) == handler_count
            finally:
                self._cleanup(logger2, tmpdir2)
        finally:
            self._cleanup(logger1, tmpdir1)

    def test_logger_creates_log_file(self) -> None:
        logger, tmpdir = self._make_logger("test-file-creation")
        try:
            logger.info("Test message")
            for h in logger.handlers:
                h.flush()
            log_file = Path(tmpdir) / "test-file-creation.jsonl"
            assert log_file.exists()
        finally:
            self._cleanup(logger, tmpdir)

    def test_log_file_contains_json(self) -> None:
        logger, tmpdir = self._make_logger("test-json-output")
        try:
            logger.info("Structured log test")
            for h in logger.handlers:
                h.flush()
            log_file = Path(tmpdir) / "test-json-output.jsonl"
            data = json.loads(log_file.read_text().strip())
            assert data["message"] == "Structured log test"
            assert data["level"] == "INFO"
        finally:
            self._cleanup(logger, tmpdir)

    def test_custom_log_level(self) -> None:
        logger, tmpdir = self._make_logger("test-debug-level", level=logging.DEBUG)
        try:
            assert logger.level == logging.DEBUG
        finally:
            self._cleanup(logger, tmpdir)

    def test_custom_log_file(self) -> None:
        logger, tmpdir = self._make_logger("test-custom-file", log_file="custom.jsonl")
        try:
            logger.info("Custom file test")
            for h in logger.handlers:
                h.flush()
            log_file = Path(tmpdir) / "custom.jsonl"
            assert log_file.exists()
        finally:
            self._cleanup(logger, tmpdir)

    def test_propagate_disabled(self) -> None:
        logger, tmpdir = self._make_logger("test-no-propagate")
        try:
            assert logger.propagate is False
        finally:
            self._cleanup(logger, tmpdir)

    def test_context_fields_injected(self) -> None:
        logger, tmpdir = self._make_logger("test-context", context={"service": "api"})
        try:
            logger.info("Context test")
            for h in logger.handlers:
                h.flush()
            log_file = Path(tmpdir) / "test-context.jsonl"
            data = json.loads(log_file.read_text().strip())
            assert data["service"] == "api"
        finally:
            self._cleanup(logger, tmpdir)

    def test_multiple_loggers_independent(self) -> None:
        logger_a, tmpdir_a = self._make_logger("test-multi-a")
        logger_b, tmpdir_b = self._make_logger("test-multi-b")
        try:
            assert logger_a is not logger_b
            assert logger_a.name != logger_b.name
        finally:
            self._cleanup(logger_a, tmpdir_a)
            self._cleanup(logger_b, tmpdir_b)


# ── Request ID Tests ──────────────────────────────────────────────────────

class TestRequestID:
    def test_set_request_id_generates_uuid(self) -> None:
        rid = set_request_id()
        assert isinstance(rid, str)
        assert len(rid) == 12

    def test_set_request_id_custom_value(self) -> None:
        rid = set_request_id("custom-id-123")
        assert rid == "custom-id-123"
        assert get_request_id() == "custom-id-123"

    def test_get_request_id_returns_none_by_default(self) -> None:
        request_id_var.set(None)
        assert get_request_id() is None

    def test_request_id_context_persists(self) -> None:
        set_request_id("test-ctx")
        assert get_request_id() == "test-ctx"
        assert get_request_id() == "test-ctx"

    def test_request_id_in_log_output(self) -> None:
        tmpdir = tempfile.mkdtemp()
        logger = setup_logger("test-req-id", log_dir=tmpdir)
        try:
            set_request_id("req-abc-123")
            logger.info("Request processed")
            for h in logger.handlers:
                h.flush()
            log_file = Path(tmpdir) / "test-req-id.jsonl"
            data = json.loads(log_file.read_text().strip())
            assert data["request_id"] == "req-abc-123"
        finally:
            for h in logger.handlers[:]:
                h.close()
                logger.removeHandler(h)
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


# ── Shutdown Tests ────────────────────────────────────────────────────────

class TestShutdown:
    def test_shutdown_does_not_raise(self) -> None:
        from app.logging.structured_logging import shutdown
        shutdown()
