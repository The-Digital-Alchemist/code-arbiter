from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import List

from eval_engine.generation.base import GeneratedSolution


@dataclass(frozen=True)
class TestRunResult:
    task_id: str
    exit_code: int
    passed: bool
    stdout: str
    stderr: str


def run_tests_for_solution(solution: GeneratedSolution) -> TestRunResult:
    """
    Write the generated code and a small test harness into a temp directory
    and run pytest for the corresponding test module.

    This is a simple local runner for development prior to introducing a
    proper sandbox.
    """
    task = solution.task
    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        # Write the generated solution as solution.py
        (tmpdir / "solution.py").write_text(solution.code + "\n", encoding="utf-8")

        # Create a small conftest that adds project root to sys.path so that
        # the task's test module can import shared utilities if needed.
        conftest = textwrap.dedent(
            """
            import sys
            from pathlib import Path


            # Ensure the project root is importable in case tests need it.
            root = Path(__file__).resolve().parents[3]
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            """
        ).strip()
        (tmpdir / "conftest.py").write_text(conftest + "\n", encoding="utf-8")

        # Copy or reference the appropriate test module from the dataset tests
        # directory by running pytest with -m path.
        tests_dir = Path(__file__).resolve().parents[1] / "dataset" / "tests"
        test_module = tests_dir / task.test_file

        cmd: List[str] = [
            sys.executable,
            "-m",
            "pytest",
            str(test_module),
            f"--rootdir={tmpdir}",
        ]

        completed = subprocess.run(
            cmd,
            cwd=tmpdir,
            capture_output=True,
            text=True,
        )

        return TestRunResult(
            task_id=task.task_id,
            exit_code=completed.returncode,
            passed=completed.returncode == 0,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

