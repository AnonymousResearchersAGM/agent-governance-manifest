import pytest

from demo_app.tasks import TaskStore


def test_add_and_complete_task():
    store = TaskStore(max_open_tasks=3)
    task = store.add_task("Review evidence", owner="alice")

    assert task.task_id == 1
    assert store.open_tasks() == [task]

    completed = store.complete_task(task.task_id, user_id="alice")
    assert completed.completed
    assert store.open_tasks() == []


def test_task_limit_is_enforced():
    store = TaskStore(max_open_tasks=1)
    store.add_task("First", owner="alice")

    with pytest.raises(ValueError, match="too many open tasks"):
        store.add_task("Second", owner="alice")


def test_only_owner_can_complete_task():
    store = TaskStore(max_open_tasks=3)
    task = store.add_task("Owner-only", owner="alice")

    with pytest.raises(PermissionError):
        store.complete_task(task.task_id, user_id="bob")
