import time
import pytest

from bot.circuit_breaker import CircuitBreaker, CircuitBreakerOpen


def test_circuit_breaker_opens_and_resets():
    cb = CircuitBreaker(max_failures=2, reset_timeout=1)
    cb.record_failure()
    assert not cb.is_open
    cb.record_failure()
    assert cb.is_open
    with pytest.raises(CircuitBreakerOpen):
        cb.before_call()
    time.sleep(1.1)
    cb.before_call()
    assert not cb.is_open
