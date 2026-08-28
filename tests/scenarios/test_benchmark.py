import csv

from trafficlight.simulation.benchmark import run_benchmark, write_benchmark_csv


def test_benchmark_runs_fixed_and_adaptive_on_same_trace(tmp_path) -> None:
    rows = run_benchmark(scenarios=["ns-heavy"], seeds=[7], duration_s=60, step_s=1)

    assert [row.controller for row in rows] == ["fixed", "adaptive"]
    assert rows[0].arrivals == rows[1].arrivals
    assert rows[0].conflicting_green_violations == 0
    assert rows[1].conflicting_green_violations == 0
    assert rows[1].completed_delta_vs_fixed is not None

    csv_path = write_benchmark_csv(rows, tmp_path / "benchmark.csv")
    with csv_path.open(newline="", encoding="utf-8") as handle:
        csv_rows = list(csv.DictReader(handle))

    assert len(csv_rows) == 2
    assert csv_rows[0]["controller"] == "fixed"
    assert csv_rows[1]["controller"] == "adaptive"
