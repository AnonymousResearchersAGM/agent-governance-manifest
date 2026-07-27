"""Runtime services for record identity, clocks, and selector signing.

Normal AGM execution uses random identifiers, the real UTC clock, and a
process-local random selector secret.  Research fixtures may temporarily
install :class:`DemoExecutionContext` so their source records are deterministic
before any presentation is rendered.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Iterator, Protocol


DEMO_UUID_NAMESPACE = uuid.UUID("0db5132d-ec92-5ce9-9358-359b1bdc6f83")


class ExecutionContext(Protocol):
    """Minimal runtime boundary used by the governance domain."""

    def new_id(self, prefix: str) -> str:
        """Return a new record identifier."""

    def now(self) -> str:
        """Return a timezone-explicit UTC timestamp."""

    def selector_secret(self) -> bytes:
        """Return secret key material for selector-token authentication."""


@dataclass
class RuntimeExecutionContext:
    """Production/default execution services.

    The selector key is intentionally random per process unless an embedding
    application supplies its own execution context.  It is never the fixed
    research-demo key.
    """

    _selector_secret: bytes = field(
        default_factory=lambda: secrets.token_bytes(32),
        repr=False,
    )

    def new_id(self, prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex}"

    def now(self) -> str:
        return (
            datetime.now(UTC)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

    def selector_secret(self) -> bytes:
        return self._selector_secret


@dataclass
class DemoExecutionContext:
    """Deterministic services scoped to one named research scenario.

    IDs use ``scenario namespace + object type + stable ordinal`` through
    UUID5.  The demo selector key is derived again with the scenario namespace,
    preventing otherwise-identical objects in different scenarios from sharing
    tokens.
    """

    scenario_namespace: str
    fixed_timestamp: str
    token_secret: bytes
    _ordinals: dict[str, int] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        if not self.scenario_namespace.strip():
            raise ValueError("Demo scenario namespace is required")
        if not self.fixed_timestamp.strip():
            raise ValueError("Demo fixed timestamp is required")
        if not self.token_secret:
            raise ValueError("Demo token secret is required")

    def new_id(self, prefix: str) -> str:
        ordinal = self._ordinals.get(prefix, 0) + 1
        self._ordinals[prefix] = ordinal
        value = uuid.uuid5(
            DEMO_UUID_NAMESPACE,
            f"{self.scenario_namespace}:{prefix}:{ordinal}",
        )
        return f"{prefix}-{value.hex}"

    def now(self) -> str:
        return self.fixed_timestamp

    def selector_secret(self) -> bytes:
        return hashlib.sha256(
            self.token_secret
            + b"\0"
            + self.scenario_namespace.encode("utf-8")
        ).digest()


_RUNTIME_CONTEXT = RuntimeExecutionContext()
_ACTIVE_CONTEXT: ContextVar[ExecutionContext | None] = ContextVar(
    "agm_execution_context",
    default=None,
)


def current_execution_context() -> ExecutionContext:
    return _ACTIVE_CONTEXT.get() or _RUNTIME_CONTEXT


def new_record_id(prefix: str) -> str:
    return current_execution_context().new_id(prefix)


def current_timestamp() -> str:
    return current_execution_context().now()


def selector_token_secret() -> bytes:
    return current_execution_context().selector_secret()


@contextmanager
def use_execution_context(context: ExecutionContext) -> Iterator[ExecutionContext]:
    """Install an execution context for the current task and restore it safely."""

    token = _ACTIVE_CONTEXT.set(context)
    try:
        yield context
    finally:
        _ACTIVE_CONTEXT.reset(token)
