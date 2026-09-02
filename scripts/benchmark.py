from __future__ import annotations

import argparse
import json
from pathlib import Path

from trafficlight.simulation.benchmark import (
    aggregate_benchmark,
    benchmark_rows_to_dicts,
    run_benchmark,
    write_benchmark_csv,
)
from trafficlight.simulation.reporting import write_grouped_bar_chart_svg, write_summary_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare fixed-time and adaptive controllers.")
    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenarios",
        default=[],
        help="Scenario to run. Repeat for multiple scenarios. Defaults to all core scenarios.",
    )
    parser.add_argument("--seed", action="append", dest="seed_values", type=int, default=[])
    parser.add_argument(
        "--seeds",
        dest="seed_count",
        type=int,
        default=1,
        help="Run seeds 1..N if --seed is omitted.",
    )
    parser.add_argument("--duration", type=float, default=300.0)
    parser.add_argument("--step", type=float, default=0.5)
    parser.add_argument("--csv", type=Path, default=Path("results/benchmark.csv"))
    parser.add_argument("--summary-csv", type=Path, default=Path("results/benchmark_summary.csv"))
    parser.add_argument("--charts", type=Path, default=Path("results/charts"))
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    rows = run_benchmark(
        scenarios=args.scenarios or ("balanced", "ns-heavy", "ew-heavy", "ns-burst", "alternating-peak"),
        seeds=args.seed_values or tuple(range(1, args.seed_count + 1)),
        duration_s=args.duration,
        step_s=args.step,
    )
    csv_path = write_benchmark_csv(rows, args.csv)
    aggregates = aggregate_benchmark(rows)
    summary_path = write_summary_csv(aggregates, args.summary_csv)
    args.charts.mkdir(parents=True, exist_ok=True)
    chart_outputs = {
        "mean_wait_chart": write_grouped_bar_chart_svg(
            aggregates,
            args.charts / "mean_wait.svg",
            metric="mean_wait_s",
            title="Mean Waiting Time by Scenario",
            y_label="Seconds",
        ),
        "max_queue_chart": write_grouped_bar_chart_svg(
            aggregates,
            args.charts / "max_queue.svg",
            metric="mean_max_queue",
            title="Mean Maximum Queue by Scenario",
            y_label="Vehicles",
        ),
        "completed_chart": write_grouped_bar_chart_svg(
            aggregates,
            args.charts / "completed.svg",
            metric="mean_completed",
            title="Mean Completed Vehicles by Scenario",
            y_label="Vehicles",
        ),
    }
    print(
        json.dumps(
            {
                "csv": str(csv_path),
                "summary_csv": str(summary_path),
                "charts": {name: str(path) for name, path in chart_outputs.items()},
                "rows": benchmark_rows_to_dicts(rows),
                "aggregates": aggregates,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
