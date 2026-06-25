"""Business logic for a tiny in-memory task tracker."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Task:
    task_id: int
    title: str
    owner: str
    completed: bool = False


@dataclass
class TaskStore:
    max_open_tasks: int
    _tasks: dict[int, Task] = field(default_factory=dict)
    _next_id: int = 1

    def add_task(self, title: str, owner: str) -> Task:
        if not title.strip():
            raise ValueError("title is required")
        if not owner.strip():
            raise ValueError("owner is required")
        if len(self.open_tasks()) >= self.max_open_tasks:
            raise ValueError("too many open tasks")
        task = Task(task_id=self._next_id, title=title.strip(), owner=owner.strip())
        self._tasks[task.task_id] = task
        self._next_id += 1
        return task

    def complete_task(self, task_id: int, user_id: str) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"unknown task_id: {task_id}")
        if task.owner != user_id:
            raise PermissionError("only the owner can complete a task")
        completed = Task(task_id=task.task_id, title=task.title, owner=task.owner, completed=True)
        self._tasks[task_id] = completed
        return completed

    def open_tasks(self) -> list[Task]:
        return [task for task in self._tasks.values() if not task.completed]
