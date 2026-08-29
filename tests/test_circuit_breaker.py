"""Tests for Price-My-Car circuit breaker module.

Tests state transitions, threshold behavior, and recovery.
"""

import time

from app.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError, CircuitState


class TestCircuitState:
    """Test circuit state enum."""

    def test_values(self) -> None:
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


class TestCircuitBreaker:
    """Test circuit breaker behavior."""

    def test_initial_state(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0, name="test")
        assert cb.state == CircuitState.CLOSED
        assert cb.is_open() is False

    def test_record_success(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0, name="test")
        cb.record_success()
        assert cb._failure_count == 0
        assert cb._success_count == 1

    def test_record_failure_count(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0, name="test")
        cb.record_failure()
        assert cb._failure_count == 1
        assert cb.state == CircuitState.CLOSED

    def test_opens_after_threshold(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0, name="test")
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.is_open() is True

    def test_stays_open_before_recovery(self) -> None:
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=10.0, name="test")
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        # Still open immediately
        assert cb.is_open() is True

    def test_recovers_after_timeout(self) -> None:
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01, name="test")
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        time.sleep(0.02)
        # Should transition to HALF_OPEN on next check
        assert cb.state == CircuitState.HALF_OPEN
        assert cb.is_open() is False

    def test_half_open_to_closed_on_success(self) -> None:
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01, name="test")
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_half_open_to_open_on_failure(self) -> None:
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01, name="test")
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_success_resets_failure_count(self) -> None:
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=1.0, name="test")
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb._failure_count == 0
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerOpenError:
    """Test circuit breaker open error."""

    def test_error_message(self) -> None:
        exc = CircuitBreakerOpenError("test breaker is OPEN")
        assert "test breaker is OPEN" in str(exc)
        assert issubclass(exc, Exception)
