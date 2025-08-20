import time
from dataclasses import dataclass


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""


@dataclass
class CircuitBreaker:
    max_failures: int
    reset_timeout: int
    failures: int = 0
    opened_at: float | None = None

    def before_call(self) -> None:
        if self.opened_at is None:
            return
        if time.time() - self.opened_at >= self.reset_timeout:
            self.failures = 0
            self.opened_at = None
        else:
            raise CircuitBreakerOpen()

    @property
    def is_open(self) -> bool:
        return self.opened_at is not None

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.max_failures:
            self.opened_at = time.time()
