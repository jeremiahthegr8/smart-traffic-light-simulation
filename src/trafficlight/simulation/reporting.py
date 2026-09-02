from __future__ import annotations

import csv
import html
from pathlib import Path

from trafficlight.simulation.benchmark import BenchmarkRow, aggregate_benchmark, write_benchmark_csv


SUMMARY_FIELDS = (
    "scenario",
    "controller",
    "runs",
    "mean_completed",
    "mean_wait_s",
    "mean_max_queue",
    "total_conflicting_green_violations",
    "mean_completed_delta_vs_fixed",
    "mean_wait_improvement_pct",
    "mean_max_queue_improvement_pct",
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

