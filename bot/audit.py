"""Audit logging utilities."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, Protocol

from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import AuditLog


class InteractionLike(Protocol):
    user: Any


def log_action(
    action: str, target_param: str | None = None
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator to log a management action to the audit log."""

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(
            interaction: InteractionLike, *args: Any, **kwargs: Any
        ) -> Any:
            result = await func(interaction, *args, **kwargs)
            session: Session = SessionLocal()
            try:
                target = None
                if target_param and target_param in kwargs:
                    target = kwargs[target_param]
                else:
                    target = kwargs.get("target") or (args[0] if args else None)
                entry = AuditLog(
                    user_id=getattr(getattr(interaction, "user", None), "id", None),
                    action=action,
                    target=str(target) if target is not None else None,
                    details={"args": args, "kwargs": kwargs},
                )
                session.add(entry)
                session.commit()
            finally:
                session.close()
            return result

        return wrapper

    return decorator
