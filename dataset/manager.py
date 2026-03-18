from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import json


@dataclass(frozen=True)
class Task:
    task_id: str
    description: str
    language: str
    test_file: str
    timeout: int
    docker_image: str = "eval-engine-python:latest"


class DatasetError(Exception):
    """Raised when the dataset configuration is invalid."""


def _dataset_root() -> Path:
    return Path(__file__).resolve().parent


def _tasks_dir() -> Path:
    return _dataset_root() / "tasks"


def load_tasks(dataset_name: Optional[str] = None) -> List[Task]:
    """
    Load and validate all tasks from the tasks directory.

    For now `dataset_name` is unused but reserved so we can later
    support multiple named datasets without breaking the API.
    """
    tasks_path = _tasks_dir()
    if not tasks_path.exists():
        raise DatasetError(f"Tasks directory does not exist: {tasks_path}")

    tasks: List[Task] = []
    for entry in sorted(tasks_path.glob("*.json")):
        with entry.open("r", encoding="utf-8") as f:
            try:
                raw = json.load(f)
            except json.JSONDecodeError as exc:
                raise DatasetError(f"Invalid JSON in {entry.name}: {exc}") from exc

        task = _parse_task(raw, source=entry.name)
        tasks.append(task)

    if not tasks:
        raise DatasetError(f"No task files found in {tasks_path}")

    return tasks


REQUIRED_FIELDS = ("task_id", "description", "language", "test_file", "timeout")


def _parse_task(raw: dict, *, source: str) -> Task:
    missing = [field for field in REQUIRED_FIELDS if field not in raw]
    if missing:
        raise DatasetError(f"Task in {source} is missing fields: {', '.join(missing)}")

    if raw["language"] != "python":
        # MVP is python-only; we keep the error explicit.
        raise DatasetError(
            f"Task {raw.get('task_id', '<unknown>')} in {source} has unsupported "
            f"language={raw['language']!r} (only 'python' is supported in the MVP)"
        )

    timeout = raw["timeout"]
    if not isinstance(timeout, int) or timeout <= 0:
        raise DatasetError(
            f"Task {raw['task_id']} in {source} has invalid timeout={timeout!r}; "
            "expected positive integer seconds"
        )

    return Task(
        task_id=str(raw["task_id"]),
        description=str(raw["description"]),
        language=str(raw["language"]),
        test_file=str(raw["test_file"]),
        timeout=timeout,
        docker_image=str(raw.get("docker_image", "eval-engine-python:latest")),
    )

