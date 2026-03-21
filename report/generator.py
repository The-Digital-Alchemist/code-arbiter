from __future__ import annotations

import textwrap
from collections import defaultdict
from datetime import datetime
from typing import List, Optional

from metrics.engine import AggregateMetrics, TaskMetrics


# ---------------------------------------------------------------------------
# Refined failure taxonomy
# Maps test name patterns to human-readable failure categories.
# ---------------------------------------------------------------------------

_REFINED_FAILURE_PATTERNS: list[tuple[list[str], str, str]] = [
    # (keywords in failing test names, category, description)
    (
        ["window", "sliding", "timestamp", "60", "time"],
        "temporal_reasoning_error",
        "Fails to reason correctly across time windows",
    ),
    (
        ["empty", "no_pairs", "no_solution", "no_suspicious", "not_found"],
        "edge_case_error",
        "Incorrect handling of empty or no-result cases",
    ),
    (
        ["index", "indices", "self", "same_index"],
        "index_handling_error",
        "Confuses indices with values or uses same index twice",
    ),
    (
        ["performance", "large", "10m", "1m", "100k"],
        "performance_error",
        "Correct logic but too slow - likely O(n^2) or O(n) where O(log n) required",
    ),
    (
        ["sorted", "sort", "order"],
        "output_ordering_error",
        "Returns correct values but in wrong order",
    ),
    (
        ["sender", "flagged", "suspicious"],
        "attribution_error",
        "Identifies the pattern but attributes it to wrong entities",
    ),
]


def _classify_refined(failing_tests: List[str], task_id: str) -> tuple[str, str]:
    """
    Map a list of failing test names to a refined failure category.
    Returns (category, description).
    """
    combined = " ".join(failing_tests).lower() + " " + task_id.lower()

    for keywords, category, description in _REFINED_FAILURE_PATTERNS:
        if any(kw in combined for kw in keywords):
            return category, description

    return "logic_error", "Incorrect logic - assertions failed"


def _divider(char: str = "-", width: int = 60) -> str:
    return char * width


def _section_summary(
    aggregate: AggregateMetrics,
    model_name: str,
    provider: str,
) -> str:
    pass_rate_pct = f"{aggregate.pass_rate:.1%}"
    avg_latency = f"{aggregate.average_latency_ms:.0f}ms" if aggregate.average_latency_ms else "n/a"

    lines = [
        _divider("="),
        "  BENCHMARK REPORT",
        _divider("="),
        "",
        "  SECTION 1 - SUMMARY",
        _divider(),
        "",
        f"  Model:        {model_name}",
        f"  Provider:     {provider}",
        f"  Tasks run:    {aggregate.total_tasks}",
        f"  Passed:       {aggregate.passed_tasks}/{aggregate.total_tasks}",
        f"  Pass rate:    {pass_rate_pct}",
        f"  Avg latency:  {avg_latency}",
        f"  Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]
    return "\n".join(lines)


def _section_failure_breakdown(task_metrics: List[TaskMetrics]) -> str:
    failures = [t for t in task_metrics if not t.passed]

    lines = [
        "",
        "  SECTION 2 - FAILURE BREAKDOWN",
        _divider(),
        "",
    ]

    if not failures:
        lines.append("  No failures. All tasks passed.")
        return "\n".join(lines)

    lines.append(f"  Failures ({len(failures)}):")

    # Raw failure types
    raw_counts: dict[str, int] = defaultdict(int)
    for f in failures:
        raw_counts[f.failure_type] += 1

    for ftype, count in sorted(raw_counts.items()):
        lines.append(f"    {ftype}: {count}")

    # Refined failure types
    lines.append("")
    lines.append("  Refined:")

    refined_counts: dict[str, int] = defaultdict(int)
    for f in failures:
        category, _ = _classify_refined(f.failed_tests, f.task_id)
        refined_counts[category] += 1

    for category, count in sorted(refined_counts.items()):
        lines.append(f"    {category}: {count}")

    return "\n".join(lines)


def _section_task_failures(task_metrics: List[TaskMetrics]) -> str:
    failures = [t for t in task_metrics if not t.passed]

    lines = [
        "",
        "  SECTION 3 - TASK-LEVEL FAILURES",
        _divider(),
        "",
    ]

    if not failures:
        lines.append("  No failures to report.")
        return "\n".join(lines)

    for f in failures:
        category, description = _classify_refined(f.failed_tests, f.task_id)

        lines.append(f"  {f.task_id}:")
        lines.append(f"    failure_type:   {category}")
        lines.append(f"    raw_type:       {f.failure_type}")
        lines.append(f"    tests_passed:   {f.tests_passed}")
        lines.append(f"    tests_failed:   {f.tests_failed}")
        lines.append(f"    pattern:        {description}")

        if f.failed_tests:
            lines.append(f"    failing_tests:")
            for t in f.failed_tests[:5]:  # cap at 5 to keep report readable
                lines.append(f"      - {t}")
            if len(f.failed_tests) > 5:
                lines.append(f"      ... and {len(f.failed_tests) - 5} more")

        lines.append("")

    return "\n".join(lines)


def _section_insights(
    task_metrics: List[TaskMetrics],
    aggregate: AggregateMetrics,
    insights_provider: Optional[str] = None,
) -> str:
    failures = [t for t in task_metrics if not t.passed]

    lines = [
        "  SECTION 4 - KEY INSIGHTS",
        _divider(),
        "",
    ]

    if not failures:
        lines += [
            "  The model passed all tasks.",
            "",
            "  This may indicate the task set is too easy to discriminate",
            "  between models. Consider adding harder tasks or running",
            "  multiple rounds to surface non-deterministic failures.",
        ]
        return "\n".join(lines)

    if insights_provider:
        # LLM-generated insights
        insight_text = _generate_llm_insights(task_metrics, failures, insights_provider)
        lines.append(textwrap.indent(insight_text, "  "))
    else:
        # Rule-based insights
        lines += _rule_based_insights(failures, aggregate)

    return "\n".join(lines)


def _rule_based_insights(
    failures: List[TaskMetrics],
    aggregate: AggregateMetrics,
) -> List[str]:
    lines = []

    for f in failures:
        category, _ = _classify_refined(f.failed_tests, f.task_id)

        if category == "temporal_reasoning_error":
            lines += [
                f"  [{f.task_id}]",
                "  The model identifies that a suspicious pattern exists but fails",
                "  to retroactively flag earlier events that belong to the same",
                "  window. This is a weakness in multi-entity temporal reasoning:",
                "  the model processes events sequentially and marks only the",
                "  triggering event, not all events that contributed to the trigger.",
                "",
            ]

        elif category == "edge_case_error":
            lines += [
                f"  [{f.task_id}]",
                "  The model's logic is correct for the happy path but breaks on",
                "  edge cases (empty inputs, no valid result). This is a common",
                "  failure mode where the model follows the 'normal' example in",
                "  the prompt and does not reason about boundary conditions.",
                "",
            ]

        elif category == "index_handling_error":
            lines += [
                f"  [{f.task_id}]",
                "  The model confuses indices with values, or fails to enforce",
                "  the i < j constraint consistently. This suggests the model",
                "  pattern-matched to a simpler variant of the problem.",
                "",
            ]

        elif category == "performance_error":
            lines += [
                f"  [{f.task_id}]",
                "  The model produced logically correct code but with the wrong",
                "  time complexity. Brute-force solutions pass small inputs",
                "  but fail the performance gates. The model likely recalled",
                "  a naive implementation rather than deriving the optimal one.",
                "",
            ]

        else:
            lines += [
                f"  [{f.task_id}]",
                f"  Failure type: {category}.",
                f"  Failing tests: {', '.join(f.failed_tests[:3])}",
                "",
            ]

    # Overall pattern note
    if len(failures) > 1:
        categories = {_classify_refined(f.failed_tests, f.task_id)[0] for f in failures}
        if len(categories) == 1:
            lines += [
                "  Pattern: All failures share the same root category.",
                f"  This points to a systematic weakness in {list(categories)[0]}",
                "  rather than isolated task-specific errors.",
            ]
        else:
            lines += [
                "  Pattern: Failures span multiple categories.",
                "  No single systematic weakness identified - failures are task-specific.",
            ]

    return lines


def _generate_llm_insights(
    task_metrics: List[TaskMetrics],
    failures: List[TaskMetrics],
    provider: str,
) -> str:
    from generation.factory import get_generator
    from generation.base import GeneratedSolution, GenerationMetadata
    from dataset.manager import Task

    failure_summary = "\n".join(
        f"- Task: {f.task_id}\n"
        f"  Failing tests: {', '.join(f.failed_tests)}\n"
        f"  Failure type: {f.failure_type}\n"
        f"  Passed {f.tests_passed} of {f.tests_passed + f.tests_failed} tests"
        for f in failures
    )

    prompt = (
        f"You are analyzing the results of an AI coding benchmark.\n\n"
        f"The model failed the following tasks:\n\n{failure_summary}\n\n"
        f"In 3-5 sentences, explain:\n"
        f"1. What specific reasoning failure caused each error\n"
        f"2. Whether this is a systematic weakness or isolated failure\n"
        f"3. What this reveals about the model's capabilities\n\n"
        f"Be specific and technical. Do not repeat the test names verbatim."
    )

    try:
        # Use a synthetic task to drive the generator
        dummy_task = Task(
            task_id="insight",
            description=prompt,
            language="python",
            test_file="",
            timeout=30,
        )
        gen = get_generator(provider)
        solution = gen.generate(dummy_task)
        return solution.code  # the "code" is actually the insight text here
    except Exception as exc:
        return f"(LLM insight generation failed: {exc})\n" + "\n".join(
            _rule_based_insights(failures, None)  # type: ignore
        )


def generate_report(
    task_metrics: List[TaskMetrics],
    aggregate: AggregateMetrics,
    provider: str,
    model_name: str,
    insights_provider: Optional[str] = None,
) -> str:
    """
    Generate a full text benchmark report with 4 sections:
      1. Summary
      2. Failure Breakdown
      3. Task-Level Failures
      4. Key Insights
    """
    sections = [
        _section_summary(aggregate, model_name, provider),
        _section_failure_breakdown(task_metrics),
        _section_task_failures(task_metrics),
        _section_insights(task_metrics, aggregate, insights_provider),
        "\n" + _divider("=") + "\n",
    ]
    return "\n".join(sections)
