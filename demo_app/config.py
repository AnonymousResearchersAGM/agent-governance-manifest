"""Configuration for the demo task tracker."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    app_name: str
    max_open_tasks: int
    token_issuer: str


def load_settings() -> Settings:
    max_open_tasks = int(getenv("DEMO_MAX_OPEN_TASKS", "25"))
    if max_open_tasks <= 0:
        raise ValueError("DEMO_MAX_OPEN_TASKS must be positive")
    return Settings(
        app_name=getenv("DEMO_APP_NAME", "AGM Demo Task Tracker"),
        max_open_tasks=max_open_tasks,
        token_issuer=getenv("DEMO_TOKEN_ISSUER", "agm-demo"),
    )
