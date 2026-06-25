"""Configuration helpers used to exercise medium and critical changes."""

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class AppConfig:
    environment: str
    debug: bool
    session_timeout_minutes: int


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    environment = getenv("APP_ENV", "development")
    debug = getenv("APP_DEBUG", "false").lower() == "true"
    timeout = int(getenv("SESSION_TIMEOUT_MINUTES", "30"))
    if timeout <= 0:
        raise ValueError("SESSION_TIMEOUT_MINUTES must be positive")
    return AppConfig(
        environment=environment,
        debug=debug,
        session_timeout_minutes=timeout,
    )

