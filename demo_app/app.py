"""Small command-line entry point for the demo task tracker."""

from __future__ import annotations

from demo_app.auth import authenticate_token
from demo_app.config import load_settings
from demo_app.tasks import TaskStore


def create_demo_task(token: str, title: str) -> str:
    user = authenticate_token(token)
    if user is None:
        return "authentication failed"
    settings = load_settings()
    store = TaskStore(max_open_tasks=settings.max_open_tasks)
    task = store.add_task(title=title, owner=user.user_id)
    return f"{task.task_id}:{task.title}:{task.owner}"


if __name__ == "__main__":
    print(create_demo_task("alice-token", "Prepare AGM evidence package"))
