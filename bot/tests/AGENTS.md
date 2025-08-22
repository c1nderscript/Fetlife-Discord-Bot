# AGENTS: bot/tests

**Scope**: bot/tests

**Purpose**: Pytest suite covering the Discord bot.

---

## File Context Map
- `conftest.py`: shared fixtures.
- `fixtures/`: reusable test data.
- `test_web_interface.py`: management web interface tests.
- `test_*.py`: feature-specific tests for bot components.

## Rules
- Use `pytest` for all tests.
- Mock external network calls or run through the adapter test harness.
- Keep tests hermetic and idempotent.
- Update or add tests when modifying bot behavior.
