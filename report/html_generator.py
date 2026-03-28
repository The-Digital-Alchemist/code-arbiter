from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import List, Optional

from metrics.engine import AggregateMetrics, TaskMetrics
from report.generator import _classify_refined, _rule_based_insights


_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #0f1117;
    color: #e2e8f0;
    padding: 40px 24px;
    min-height: 100vh;
}
.container { max-width: 900px; margin: 0 auto; }
h1 {
    font-size: 22px;
    font-weight: 600;
    color: #f8fafc;
    margin-bottom: 4px;
    letter-spacing: -0.3px;
}
.subtitle {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 32px;
}

/* Summary cards */
.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 32px;
}
.card {
    background: #1e2130;
    border: 1px solid #2d3148;
    border-radius: 10px;
    padding: 18px 20px;
}
.card-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #64748b;
    margin-bottom: 8px;
}
.card-value {
    font-size: 26px;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1;
}
.card-value.green { color: #34d399; }
.card-value.yellow { color: #fbbf24; }
.card-value.red { color: #f87171; }

/* Section headers */
.section-title {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #64748b;
    margin: 32px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2130;
}

/* Task table */
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
th {
    text-align: left;
    padding: 10px 14px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #64748b;
    border-bottom: 1px solid #2d3148;
}
td {
    padding: 10px 14px;
    border-bottom: 1px solid #1a1d2e;
    vertical-align: top;
}
tr:last-child td { border-bottom: none; }
tr:hover td { background: #1a1d2e; }

/* Status badge */
.badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
}
.badge-pass { background: #064e3b; color: #34d399; }
.badge-fail { background: #450a0a; color: #f87171; }

/* Failure type pill */
.pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    background: #1e2130;
    color: #94a3b8;
    border: 1px solid #2d3148;
}

/* Insights */
.insights-block {
    background: #1e2130;
    border: 1px solid #2d3148;
    border-radius: 10px;
    padding: 20px 24px;
    margin-top: 8px;
}
.insight-item {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #2d3148;
}
.insight-item:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}
.insight-task {
    font-size: 13px;
    font-weight: 600;
    color: #f87171;
    margin-bottom: 6px;
}
.insight-text {
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.6;
}

/* Failing tests list */
.failing-tests {
    margin-top: 4px;
    font-size: 11px;
    color: #64748b;
}
.failing-tests span {
    display: inline-block;
    margin-right: 6px;
    margin-top: 3px;
    padding: 1px 7px;
    background: #1a1d2e;
    border-radius: 3px;
    font-family: monospace;
}

.footer {
    margin-top: 48px;
    font-size: 11px;
    color: #334155;
    text-align: center;
}
"""

_INSIGHT_COPY = {
    "temporal_reasoning_error": (
        "The model identifies that a suspicious pattern exists but fails to retroactively "
        "flag earlier events that belong to the same window. This is a weakness in multi-entity "
        "temporal reasoning: the model processes events sequentially and marks only the triggering "
        "event, not all events that contributed to the trigger."
    ),
    "edge_case_error": (
        "The model's logic is correct for the happy path but breaks on edge cases (empty inputs, "
        "no valid result). A common failure mode where the model follows the 'normal' example in "
        "the prompt and does not reason about boundary conditions."
    ),
    "index_handling_error": (
        "The model confuses indices with values, or fails to enforce the i &lt; j constraint "
        "consistently. Suggests the model pattern-matched to a simpler variant of the problem."
    ),
    "performance_error": (
        "The model produced logically correct code but with the wrong time complexity. "
        "Brute-force solutions pass small inputs but fail the performance gates. "
        "The model likely recalled a naive implementation rather than deriving the optimal one."
    ),
    "attribution_error": (
        "The model identifies the pattern but attributes it to the wrong entities. "
        "A signal classification failure rather than a logic failure."
    ),
}


def _pass_rate_color(rate: float) -> str:
    if rate >= 0.9:
        return "green"
    if rate >= 0.7:
        return "yellow"
    return "red"


def generate_html_report(
    task_metrics: List[TaskMetrics],
    aggregate: AggregateMetrics,
    provider: str,
    model_name: str,
    insights_provider: Optional[str] = None,
) -> str:
    failures = [t for t in task_metrics if not t.passed]
    pass_rate_pct = f"{aggregate.pass_rate:.1%}"
    avg_latency = f"{aggregate.average_latency_ms:.0f}ms" if aggregate.average_latency_ms else "n/a"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    color = _pass_rate_color(aggregate.pass_rate)

    # --- Summary cards ---
    cards_html = f"""
    <div class="cards">
      <div class="card">
        <div class="card-label">Pass Rate</div>
        <div class="card-value {color}">{pass_rate_pct}</div>
      </div>
      <div class="card">
        <div class="card-label">Tasks Passed</div>
        <div class="card-value">{aggregate.passed_tasks} / {aggregate.total_tasks}</div>
      </div>
      <div class="card">
        <div class="card-label">Avg Latency</div>
        <div class="card-value">{avg_latency}</div>
      </div>
      <div class="card">
        <div class="card-label">Failures</div>
        <div class="card-value {"red" if failures else "green"}">{len(failures)}</div>
      </div>
    </div>
    """

    # --- Task table ---
    rows = []
    for t in task_metrics:
        badge = '<span class="badge badge-pass">PASS</span>' if t.passed else '<span class="badge badge-fail">FAIL</span>'

        if not t.passed:
            category, _ = _classify_refined(t.failed_tests, t.task_id)
            pill = f'<span class="pill">{category}</span>'
            failing = ""
            if t.failed_tests:
                spans = "".join(f"<span>{ft}</span>" for ft in t.failed_tests[:4])
                extra = f"<span>+{len(t.failed_tests) - 4} more</span>" if len(t.failed_tests) > 4 else ""
                failing = f'<div class="failing-tests">{spans}{extra}</div>'
            detail = f"{pill}{failing}"
        else:
            detail = '<span style="color:#334155;font-size:12px;">—</span>'

        rows.append(f"""
        <tr>
          <td style="font-family:monospace;font-size:12px;color:#cbd5e1;">{t.task_id}</td>
          <td>{badge}</td>
          <td style="color:#64748b;font-size:12px;">{t.tests_passed}/{t.tests_passed + t.tests_failed}</td>
          <td style="color:#94a3b8;font-size:12px;">{t.latency_ms:.0f}ms</td>
          <td>{detail}</td>
        </tr>""")

    table_html = f"""
    <div class="section-title">All Tasks</div>
    <table>
      <thead>
        <tr>
          <th>Task</th>
          <th>Status</th>
          <th>Tests</th>
          <th>Latency</th>
          <th>Failure</th>
        </tr>
      </thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    """

    # --- Insights ---
    if not failures:
        insights_html = """
    <div class="section-title">Key Insights</div>
    <div class="insights-block">
      <div class="insight-text">The model passed all tasks. Consider adding harder tasks or running
      multiple rounds to surface non-deterministic failures.</div>
    </div>
    """
    else:
        items = []
        for f in failures:
            category, _ = _classify_refined(f.failed_tests, f.task_id)
            body = _INSIGHT_COPY.get(
                category,
                f"Failure type: {category}. Failing tests: {', '.join(f.failed_tests[:3])}."
            )
            items.append(f"""
      <div class="insight-item">
        <div class="insight-task">{f.task_id}</div>
        <div class="insight-text">{body}</div>
      </div>""")

        # pattern note
        if len(failures) > 1:
            categories = {_classify_refined(f.failed_tests, f.task_id)[0] for f in failures}
            if len(categories) == 1:
                note = f"All failures share the same root category: <strong>{list(categories)[0]}</strong>. Systematic weakness, not isolated errors."
            else:
                note = "Failures span multiple categories. No single systematic weakness identified."
            items.append(f"""
      <div class="insight-item">
        <div class="insight-task" style="color:#fbbf24;">Pattern</div>
        <div class="insight-text">{note}</div>
      </div>""")

        insights_html = f"""
    <div class="section-title">Key Insights</div>
    <div class="insights-block">{"".join(items)}</div>
    """

    # --- Assemble ---
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Benchmark Report — {model_name}</title>
  <style>{_CSS}</style>
</head>
<body>
  <div class="container">
    <h1>Benchmark Report</h1>
    <div class="subtitle">{model_name} &nbsp;·&nbsp; {provider} &nbsp;·&nbsp; {now}</div>
    {cards_html}
    {table_html}
    {insights_html}
    <div class="footer">AI Code Generation Evaluation Engine</div>
  </div>
</body>
</html>
"""
