from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import docker
import docker.errors

from generation.base import GeneratedSolution
from runner.local_runner import TestRunResult, _parse_pytest_output, _classify_failure


class DockerRunner:
    """
    Runs pytest for a generated solution inside an isolated Docker container.

    The container has no network access and limited resources, making it safe
    to execute untrusted LLM-generated code. Each run gets a fresh container
    that is destroyed after the tests complete.
    """

    def __init__(self, client: docker.DockerClient | None = None) -> None:
        self._client = client or docker.from_env()

    def run(self, solution: GeneratedSolution) -> TestRunResult:
        task = solution.task
        tests_dir = Path(__file__).resolve().parents[1] / "dataset" / "tests"
        test_file_src = tests_dir / task.test_file

        with tempfile.TemporaryDirectory() as tmpdir_str:
            tmpdir = Path(tmpdir_str)

            # Write the generated solution into the workspace.
            (tmpdir / "solution.py").write_text(solution.code + "\n", encoding="utf-8")

            # Copy the test file into the same workspace so the container
            # can run it without needing access to the host filesystem.
            shutil.copy(test_file_src, tmpdir / task.test_file)

            return self._run_in_container(
                task_id=task.task_id,
                image=task.docker_image,
                workspace=tmpdir,
                test_file=task.test_file,
                timeout=task.timeout,
            )

    def _run_in_container(
        self,
        *,
        task_id: str,
        image: str,
        workspace: Path,
        test_file: str,
        timeout: int,
    ) -> TestRunResult:
        try:
            container = self._client.containers.run(
                image=image,
                command=["pytest", test_file, "-v"],
                volumes={str(workspace): {"bind": "/workspace", "mode": "rw"}},
                working_dir="/workspace",
                network_disabled=True,
                mem_limit="256m",
                cpu_period=100000,
                cpu_quota=50000,  # 50% of one CPU core
                detach=True,
                stdout=True,
                stderr=True,
            )
        except docker.errors.ImageNotFound:
            return TestRunResult(
                task_id=task_id,
                exit_code=-1,
                passed=False,
                stdout="",
                stderr=f"Docker image '{image}' not found. Run: docker build -t {image} eval_engine/sandbox/",
            )
        except docker.errors.DockerException as exc:
            return TestRunResult(
                task_id=task_id,
                exit_code=-1,
                passed=False,
                stdout="",
                stderr=f"Docker error: {exc}",
            )

        try:
            result = container.wait(timeout=timeout + 10)
            exit_code = result["StatusCode"]
            logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
            tests_passed, tests_failed, failed_tests = _parse_pytest_output(logs)
            failure_type = _classify_failure(logs, exit_code)
            return TestRunResult(
                task_id=task_id,
                exit_code=exit_code,
                passed=exit_code == 0,
                stdout=logs,
                stderr="",
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                failed_tests=failed_tests,
                failure_type=failure_type,
            )
        except Exception as exc:
            container.kill()
            return TestRunResult(
                task_id=task_id,
                exit_code=-1,
                passed=False,
                stdout="",
                stderr=f"Container timed out or failed: {exc}",
            )
        finally:
            container.remove(force=True)
