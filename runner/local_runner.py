from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from generation.base import GeneratedSolution


@dataclass(frozen=True)
class TestRunResult:
    task_id: str
    exit_code: int
    passed: bool
    stdout: str
    stderr: str
    tests_passed: int = 0
    tests_failed: int = 0
    failed_tests: List[str] = field(default_factory=list)


def _parse_pytest_output(output: str) -> tuple[int, int, List[str]]:
    """
    Extract passed count, failed count, and failing test names from pytest output.

    Example pytest summary line:
      '3 failed, 7 passed in 0.42s'
      '10 passed in 0.12s'
    """
    passed = 0
    failed = 0
    failed_tests: List[str] = []

    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)

    if passed_match:
        passed = int(passed_match.group(1))
    if failed_match:
        failed = int(failed_match.group(1))

    # Extract individual failing test names: "FAILED test_foo.py::test_bar_baz"
    failed_tests = re.findall(r"FAILED [^:]+::(\w+)", output)

    return passed, failed, failed_tests


def run_tests_for_solution(solution: GeneratedSolution) -> TestRunResult:
    """
    Write the generated code into a temp directory and run pytest against
    the corresponding test module from the dataset.

    This is the local (non-sandboxed) runner for development use.
    """
    task = solution.task
    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        # Write the generated solution as solution.py
        (tmpdir / "solution.py").write_text(solution.code + "\n", encoding="utf-8")

        eval_engine_root = Path(__file__).resolve().parents[1]
        tests_dir = eval_engine_root / "dataset" / "tests"
        test_module = tests_dir / task.test_file

        cmd: List[str] = [
            sys.executable,
            "-m",
            "pytest",
            str(test_module),
            f"--rootdir={tmpdir}",
            "-v",
        ]

        # Pass eval_engine root AND tmpdir via PYTHONPATH so tests can import
        # both `generation.*` (eval_engine root) and `solution` (tmpdir).
        env = os.environ.copy()
        extra_paths = os.pathsep.join([str(tmpdir), str(eval_engine_root)])
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            extra_paths + os.pathsep + existing_pythonpath
            if existing_pythonpath
            else extra_paths
        )

        completed = subprocess.run(
            cmd,
            cwd=tmpdir,
            capture_output=True,
            text=True,
            env=env,
        )

        output = completed.stdout + completed.stderr
        tests_passed, tests_failed, failed_tests = _parse_pytest_output(output)

        return TestRunResult(
            task_id=task.task_id,
            exit_code=completed.returncode,
            passed=completed.returncode == 0,
            stdout=completed.stdout,
            stderr=completed.stderr,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            failed_tests=failed_tests,
        )