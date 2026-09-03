from __future__ import annotations

import csv
import html
from pathlib import Path

from trafficlight.simulation.benchmark import BenchmarkRow, aggregate_benchmark, write_benchmark_csv
from trafficlight.simulation.failure_modes import aggregate_failure_modes, write_failure_modes_csv


SUMMARY_FIELDS = (
    "scenario",
    "controller",
    "runs",
    "mean_completed",
    "std_completed",
    "ci95_completed",
    "mean_wait_s",
    "std_wait_s",
    "ci95_wait_s",
    "mean_max_queue",
    "std_max_queue",
    "ci95_max_queue",
    "total_conflicting_green_violations",
    "mean_completed_delta_vs_fixed",
    "std_completed_delta_vs_fixed",
    "ci95_completed_delta_vs_fixed",
    "mean_wait_improvement_pct",
    "std_wait_improvement_pct",
    "ci95_wait_improvement_pct",
    "mean_max_queue_improvement_pct",
    "std_max_queue_improvement_pct",
    "ci95_max_queue_improvement_pct",
)


def write_report_assets(rows: list[BenchmarkRow], output_dir: str | Path) -> dict[str, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    aggregates = aggregate_benchmark(rows)

    outputs = {
        "rows_csv": write_benchmark_csv(rows, directory / "benchmark_rows.csv"),
        "summary_csv": write_summary_csv(aggregates, directory / "benchmark_summary.csv"),
        "mean_wait_chart": write_grouped_bar_chart_svg(
            aggregates,
            directory / "mean_wait.svg",
            metric="mean_wait_s",
            title="Mean Waiting Time by Scenario",
            y_label="Seconds",
        ),
        "max_queue_chart": write_grouped_bar_chart_svg(
            aggregates,
            directory / "max_queue.svg",
            metric="mean_max_queue",
            title="Mean Maximum Queue by Scenario",
            y_label="Vehicles",
        ),
        "completed_chart": write_grouped_bar_chart_svg(
            aggregates,
            directory / "completed.svg",
            metric="mean_completed",
            title="Mean Completed Vehicles by Scenario",
            y_label="Vehicles",
        ),
    }
    return outputs


def write_dissertation_report(
    *,
    benchmark_rows: list[BenchmarkRow],
    failure_rows: list[dict],
    output_dir: str | Path,
    duration_s: float,
    step_s: float,
    seeds: tuple[int, ...],
) -> dict[str, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    benchmark_outputs = write_report_assets(benchmark_rows, directory)
    failure_csv = write_failure_modes_csv(failure_rows, directory / "failure_modes.csv")
    report_path = directory / "results_summary.md"
    report_path.write_text(
        build_results_markdown(
            benchmark_aggregates=aggregate_benchmark(benchmark_rows),
            failure_aggregates=aggregate_failure_modes(failure_rows),
            duration_s=duration_s,
            step_s=step_s,
            seeds=seeds,
        ),
        encoding="utf-8",
    )

    return {
        **benchmark_outputs,
        "failure_csv": failure_csv,
        "markdown_report": report_path,
    }


def build_results_markdown(
    *,
    benchmark_aggregates: list[dict],
    failure_aggregates: list[dict],
    duration_s: float,
    step_s: float,
    seeds: tuple[int, ...],
) -> str:
    seed_text = ", ".join(str(seed) for seed in seeds)
    lines = [
        "# Experiment Results Summary",
        "",
        "## Experiment Configuration",
        "",
        f"- Duration per run: {duration_s:g} seconds",
        f"- Simulation step: {step_s:g} seconds",
        f"- Random seeds: {seed_text}",
        "- Controllers compared: fixed-time baseline and adaptive demand controller",
        "",
        "## Fixed-Time vs Adaptive Control",
        "",
        _benchmark_markdown_table(benchmark_aggregates),
        "",
        "## Detector Fault Simulation",
        "",
        _failure_markdown_table(failure_aggregates),
        "",
        "## Safety Result",
        "",
        (
            "Across the benchmark and detector-fault experiments, the controller recorded "
            f"{_total_violations(benchmark_aggregates, failure_aggregates)} conflicting-green "
            "violations."
        ),
        "",
        "## Generated Assets",
        "",
        "- `benchmark_rows.csv`: row-level fixed/adaptive runs",
        "- `benchmark_summary.csv`: aggregate fixed/adaptive results",
        "- `failure_modes.csv`: detector fault results",
        "- `mean_wait.svg`: mean waiting-time chart",
        "- `max_queue.svg`: mean maximum-queue chart",
        "- `completed.svg`: mean completed-vehicles chart",
        "",
    ]
    return "\n".join(lines)


def write_summary_csv(aggregates: list[dict], path: str | Path) -> Path:
    output_path = Path(path)
    if output_path.parent != Path("."):
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in aggregates:
            writer.writerow(row)
    return output_path


def _benchmark_markdown_table(aggregates: list[dict]) -> str:
    by_key = {(row["scenario"], row["controller"]): row for row in aggregates}
    scenarios = sorted({row["scenario"] for row in aggregates})
    rows = [
        "| Scenario | Fixed mean wait (s) | Adaptive mean wait (s) | Wait change | "
        "Fixed max queue | Adaptive max queue | Queue change | Completed change | Safety violations |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in scenarios:
        fixed = by_key.get((scenario, "fixed"))
        adaptive = by_key.get((scenario, "adaptive"))
        if fixed is None or adaptive is None:
            continue
        rows.append(
            "| "
            + " | ".join(
                [
                    scenario,
                    _fmt_ci(fixed["mean_wait_s"], fixed["ci95_wait_s"]),
                    _fmt_ci(adaptive["mean_wait_s"], adaptive["ci95_wait_s"]),
                    _fmt_pct_ci(
                        adaptive["mean_wait_improvement_pct"],
                        adaptive["ci95_wait_improvement_pct"],
                    ),
                    _fmt_ci(fixed["mean_max_queue"], fixed["ci95_max_queue"]),
                    _fmt_ci(adaptive["mean_max_queue"], adaptive["ci95_max_queue"]),
                    _fmt_pct_ci(
                        adaptive["mean_max_queue_improvement_pct"],
                        adaptive["ci95_max_queue_improvement_pct"],
                    ),
                    _fmt_ci(
                        adaptive["mean_completed_delta_vs_fixed"],
                        adaptive["ci95_completed_delta_vs_fixed"],
                    ),
                    str(
                        fixed["total_conflicting_green_violations"]
                        + adaptive["total_conflicting_green_violations"]
                    ),
                ]
            )
            + " |"
        )
    return "\n".join(rows)


def _failure_markdown_table(aggregates: list[dict]) -> str:
    rows = [
        "| Fault profile | Runs | Mean completed | Mean wait (s) | Mean max queue | "
        "Safety violations |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in aggregates:
        rows.append(
            "| "
            + " | ".join(
                [
                    row["fault"],
                    str(row["runs"]),
                    _fmt(row["mean_completed"]),
                    _fmt(row["mean_wait_s"]),
                    _fmt(row["mean_max_queue"]),
                    str(row["total_conflicting_green_violations"]),
                ]
            )
            + " |"
        )
    return "\n".join(rows)


def _fmt(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"{float(value):.2f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{float(value):+.2f}%"


def _fmt_ci(value: float | int | None, ci95: float | int | None) -> str:
    if value is None:
        return "-"
    if ci95 is None or float(ci95) == 0.0:
        return _fmt(value)
    return f"{_fmt(value)} +/- {_fmt(ci95)}"


def _fmt_pct_ci(value: float | None, ci95: float | None) -> str:
    if value is None:
        return "-"
    if ci95 is None or float(ci95) == 0.0:
        return _fmt_pct(value)
    return f"{_fmt_pct(value)} +/- {_fmt(ci95)} pp"


def _total_violations(benchmark_aggregates: list[dict], failure_aggregates: list[dict]) -> int:
    return sum(row["total_conflicting_green_violations"] for row in benchmark_aggregates) + sum(
        row["total_conflicting_green_violations"] for row in failure_aggregates
    )


def write_grouped_bar_chart_svg(
    aggregates: list[dict],
    path: str | Path,
    *,
    metric: str,
    title: str,
    y_label: str,
) -> Path:
    output_path = Path(path)
    if output_path.parent != Path("."):
        output_path.parent.mkdir(parents=True, exist_ok=True)

    scenarios = sorted({row["scenario"] for row in aggregates})
    by_key = {(row["scenario"], row["controller"]): row for row in aggregates}
    values = [
        float(by_key[(scenario, controller)][metric])
        for scenario in scenarios
        for controller in ("fixed", "adaptive")
        if (scenario, controller) in by_key
    ]
    max_value = max(values) if values else 1.0

    width = 1040
    height = 460
    margin_left = 72
    margin_right = 30
    margin_top = 54
    margin_bottom = 96
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    group_width = chart_width / max(len(scenarios), 1)
    bar_width = min(42, group_width * 0.28)
    fixed_colour = "#637083"
    adaptive_colour = "#1f6feb"

    parts = [
        _svg_header(width, height),
        f'<text x="{width / 2}" y="30" text-anchor="middle" class="title">{html.escape(title)}</text>',
        f'<text x="18" y="{height / 2}" transform="rotate(-90 18 {height / 2})" '
        f'text-anchor="middle" class="axis-label">{html.escape(y_label)}</text>',
        _line(margin_left, margin_top, margin_left, margin_top + chart_height, "axis"),
        _line(margin_left, margin_top + chart_height, width - margin_right, margin_top + chart_height, "axis"),
        _legend(width - 220, 24, fixed_colour, adaptive_colour),
    ]

    for tick in range(0, 6):
        value = (max_value / 5) * tick
        y = margin_top + chart_height - (value / max_value) * chart_height
        parts.append(_line(margin_left - 5, y, width - margin_right, y, "grid" if tick else "axis"))
        parts.append(
            f'<text x="{margin_left - 10}" y="{y + 4:.1f}" text-anchor="end" '
            f'class="tick">{value:.0f}</text>'
        )

    for index, scenario in enumerate(scenarios):
        group_x = margin_left + index * group_width
        center_x = group_x + group_width / 2
        label = html.escape(scenario.replace("-", " "))
        parts.append(
            f'<text x="{center_x:.1f}" y="{height - 52}" text-anchor="middle" '
            f'class="scenario">{label}</text>'
        )
        for offset, controller, colour in (
            (-bar_width * 0.62, "fixed", fixed_colour),
            (bar_width * 0.62, "adaptive", adaptive_colour),
        ):
            row = by_key.get((scenario, controller))
            if row is None:
                continue
            value = float(row[metric])
            bar_height = (value / max_value) * chart_height if max_value else 0
            x = center_x + offset - bar_width / 2
            y = margin_top + chart_height - bar_height
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" '
                f'height="{bar_height:.1f}" fill="{colour}" rx="4" />'
            )
            parts.append(
                f'<text x="{x + bar_width / 2:.1f}" y="{y - 6:.1f}" '
                f'text-anchor="middle" class="value">{value:.1f}</text>'
            )

    parts.append("</svg>\n")
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path


def _svg_header(width: int, height: int) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  .title {{ font: 700 20px Arial, sans-serif; fill: #17202a; }}
  .axis-label, .scenario, .tick, .value {{ font: 12px Arial, sans-serif; fill: #334155; }}
  .scenario {{ font-weight: 700; text-transform: capitalize; }}
  .axis {{ stroke: #475569; stroke-width: 1.4; }}
  .grid {{ stroke: #d8dee6; stroke-width: 1; }}
</style>
<rect width="{width}" height="{height}" fill="#ffffff" />"""


def _line(x1: float, y1: float, x2: float, y2: float, class_name: str) -> str:
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
        f'y2="{y2:.1f}" class="{class_name}" />'
    )


def _legend(x: float, y: float, fixed_colour: str, adaptive_colour: str) -> str:
    return f"""<g>
  <rect x="{x}" y="{y}" width="14" height="14" fill="{fixed_colour}" rx="3" />
  <text x="{x + 22}" y="{y + 12}" class="tick">Fixed</text>
  <rect x="{x + 86}" y="{y}" width="14" height="14" fill="{adaptive_colour}" rx="3" />
  <text x="{x + 108}" y="{y + 12}" class="tick">Adaptive</text>
</g>"""
