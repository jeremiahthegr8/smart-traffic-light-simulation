import csv

from trafficlight.simulation.benchmark import run_benchmark
from trafficlight.simulation.reporting import write_report_assets, write_summary_csv


def test_report_assets_write_summary_csv_and_svg_charts(tmp_path) -> None:
    rows = run_benchmark(scenarios=["balanced"], seeds=[1], duration_s=30, step_s=1)
    outputs = write_report_assets(rows, tmp_path)

    assert outputs["rows_csv"].exists()
    assert outputs["summary_csv"].exists()
    assert outputs["mean_wait_chart"].read_text(encoding="utf-8").startswith("<svg")
    assert outputs["max_queue_chart"].exists()
    assert outputs["completed_chart"].exists()

    with outputs["summary_csv"].open(newline="", encoding="utf-8") as handle:
        summary_rows = list(csv.DictReader(handle))

    assert len(summary_rows) == 2
    assert {row["controller"] for row in summary_rows} == {"fixed", "adaptive"}


def test_write_summary_csv(tmp_path) -> None:
    path = write_summary_csv(
        [
            {
                "scenario": "balanced",
                "controller": "fixed",
                "runs": 1,
                "mean_completed": 10,
                "mean_wait_s": 12.5,
                "mean_max_queue": 4,
                "total_conflicting_green_violations": 0,
                "mean_completed_delta_vs_fixed": None,
                "mean_wait_improvement_pct": None,
                "mean_max_queue_improvement_pct": None,
            }
        ],
        tmp_path / "summary.csv",
    )

    assert path.read_text(encoding="utf-8").splitlines()[0].startswith("scenario,controller")
