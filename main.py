from __future__ import annotations

import json
import sys

import click
from dotenv import load_dotenv

load_dotenv()


@click.group()
def cli():
    """AI Code Generation Evaluation Engine."""
    pass


@cli.command()
@click.argument("task_id")
@click.option("--provider", "-p", default=None, help="Generator provider: openai, claude, local, stub")
@click.option("--docker/--no-docker", default=True, help="Run tests inside Docker sandbox (default: on)")
def inspect(task_id, provider, docker):
    """Generate and run a single task — show generated code and full pytest output."""
    from dataset.manager import load_tasks
    from generation.factory import get_generator
    from runner.local_runner import run_tests_for_solution
    from runner.docker_runner import DockerRunner

    tasks = {t.task_id: t for t in load_tasks()}
    if task_id not in tasks:
        click.echo(f"Unknown task '{task_id}'. Available: {', '.join(sorted(tasks))}")
        return

    task = tasks[task_id]
    generator = get_generator(provider)

    click.echo(f"\n{'='*60}")
    click.echo(f"TASK:     {task.task_id}")
    click.echo(f"PROMPT:   {task.description}")
    click.echo(f"{'='*60}\n")

    click.echo("Generating code...")
    solution = generator.generate(task)

    click.echo(f"\n--- GENERATED CODE ({solution.metadata.model_name}, {solution.metadata.latency_ms:.0f}ms) ---\n")
    click.echo(solution.code)

    click.echo(f"\n--- RUNNING TESTS ({'Docker' if docker else 'Local'}) ---\n")
    runner = DockerRunner() if docker else None
    result = runner.run(solution) if runner else run_tests_for_solution(solution)

    click.echo(result.stdout)
    if result.stderr:
        click.echo("STDERR:")
        click.echo(result.stderr)

    verdict = "PASS" if result.passed else f"FAIL [{result.failure_type}]"
    click.echo(f"\n--- VERDICT: {verdict} | passed={result.tests_passed} failed={result.tests_failed} ---")


@cli.command()
@click.option("--provider", "-p", default=None, help="Generator provider: openai, claude, stub")
@click.option("--docker/--no-docker", default=True, help="Run tests inside Docker sandbox (default: on)")
@click.option("--json-output", "json_output", is_flag=True, default=False, help="Output raw JSON")
def run(provider, docker, json_output):
    """Run all tasks once and report PASS/FAIL per task."""
    from orchestrator import run_provider_with_metrics

    click.echo(f"Running with provider={provider or 'stub'} docker={docker} ...")
    task_metrics, aggregate = run_provider_with_metrics(provider, use_docker=docker)

    if json_output:
        output = {
            "provider": provider or "stub",
            "tasks": [
                {
                    "task_id": t.task_id,
                    "status": t.status,
                    "tests_passed": t.tests_passed,
                    "tests_failed": t.tests_failed,
                    "failed_tests": t.failed_tests,
                    "failure_type": t.failure_type,
                    "latency_ms": round(t.latency_ms, 2),
                }
                for t in task_metrics
            ],
            "aggregate": {
                "total_tasks": aggregate.total_tasks,
                "passed_tasks": aggregate.passed_tasks,
                "pass_rate": round(aggregate.pass_rate, 4),
                "average_latency_ms": round(aggregate.average_latency_ms or 0, 2),
            },
        }
        click.echo(json.dumps(output, indent=2))
        return

    click.echo("")
    for t in task_metrics:
        icon = "PASS" if t.status == "PASS" else "FAIL"
        failure_info = f"  [{t.failure_type}] failing: {t.failed_tests}" if t.status == "FAIL" else ""
        click.echo(
            f"[{icon}] {t.task_id:<30} "
            f"passed={t.tests_passed} failed={t.tests_failed} "
            f"latency={t.latency_ms:.0f}ms"
            f"{failure_info}"
        )

    click.echo("")
    click.echo(
        f"Result: {aggregate.passed_tasks}/{aggregate.total_tasks} passed "
        f"({aggregate.pass_rate:.0%}) | avg {aggregate.average_latency_ms:.0f}ms"
    )


@cli.command()
@click.option("--provider", "-p", default=None, help="Generator provider: openai, claude, stub")
@click.option("--runs", "-n", default=5, show_default=True, help="Number of runs per task")
@click.option("--docker/--no-docker", default=True, help="Run tests inside Docker sandbox (default: on)")
@click.option("--json-output", "json_output", is_flag=True, default=False, help="Output raw JSON")
def multi(provider, runs, docker, json_output):
    """Run each task N times and report pass rates."""
    from orchestrator import run_multi

    click.echo(f"Running {runs}x per task with provider={provider or 'stub'} docker={docker} ...")
    report = run_multi(provider, runs=runs, use_docker=docker)

    if json_output:
        output = {
            "provider": report.provider,
            "runs_per_task": report.runs_per_task,
            "overall_pass_rate": round(report.overall_pass_rate, 4),
            "tasks": [
                {
                    "task_id": t.task_id,
                    "pass_rate": round(t.pass_rate, 4),
                    "passes": t.passes,
                    "runs": t.runs,
                    "failure_types": t.failure_types,
                }
                for t in report.task_pass_rates
            ],
        }
        click.echo(json.dumps(output, indent=2))
        return

    click.echo("")
    for t in report.task_pass_rates:
        bar = "#" * t.passes + "-" * (t.runs - t.passes)
        failures = {k: v for k, v in t.failure_types.items() if k != "none"}
        failure_str = f"  failures: {failures}" if failures else ""
        click.echo(
            f"{t.task_id:<30} [{bar}] {t.passes}/{t.runs} "
            f"({t.pass_rate:.0%}){failure_str}"
        )

    click.echo("")
    click.echo(f"Overall pass rate: {report.overall_pass_rate:.0%} across {report.runs_per_task} runs per task")


@cli.command()
@click.option("--provider", "-p", default=None, help="Generator provider: openai, claude, local, stub")
@click.option("--docker/--no-docker", default=True, help="Run tests inside Docker sandbox (default: on)")
@click.option("--insights", default=None, help="Provider to use for LLM-generated insights (optional)")
@click.option("--output", "-o", default=None, help="Write report to file instead of stdout")
def report(provider, docker, insights, output):
    """Run all tasks and generate a full benchmark report."""
    from orchestrator import run_provider_with_metrics
    from report.generator import generate_report

    click.echo(f"Running benchmark with provider={provider or 'stub'} docker={docker} ...")
    task_metrics, aggregate = run_provider_with_metrics(provider, use_docker=docker)

    # Derive model name from env vars matching the provider, fall back to provider label
    import os
    _model_env = {"openai": "OPENAI_MODEL", "claude": "CLAUDE_MODEL", "local": "LOCAL_MODEL_NAME"}
    model_name = os.environ.get(_model_env.get(provider or "", ""), provider or "stub")

    click.echo("Generating report...")
    text = generate_report(
        task_metrics=task_metrics,
        aggregate=aggregate,
        provider=provider or "stub",
        model_name=model_name,
        insights_provider=insights,
    )

    import os
    from pathlib import Path
    from datetime import datetime

    if not output:
        reports_dir = Path(__file__).parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model = model_name.replace("/", "-").replace(":", "-")
        output = str(reports_dir / f"report_{provider or 'stub'}_{safe_model}_{timestamp}.txt")

    with open(output, "w", encoding="utf-8") as f:
        f.write(text)
    click.echo(f"\nReport saved to: {output}")
    click.echo("\n" + text)


if __name__ == "__main__":
    cli()
