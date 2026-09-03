from trafficlight.simulation.benchmark import run_benchmark
from trafficlight.simulation.failure_modes import run_failure_modes
from trafficlight.simulation.reporting import build_results_markdown, write_dissertation_report


def test_dissertation_report_writes_tables_and_assets(tmp_path) -> None:
    benchmark_rows = run_benchmark(scenarios=["balanced"], seeds=[1], duration_s=30, step_s=1)
    failure_rows = run_failure_modes(scenario="balanced", seeds=(1,), duration_s=30, step_s=1)

    outputs = write_dissertation_report(
        benchmark_rows=benchmark_rows,
        failure_rows=failure_rows,
        output_dir=tmp_path,
        duration_s=30,
        step_s=1,
        seeds=(1,),
    )

    report = outputs["markdown_report"].read_text(encoding="utf-8")
    assert "| Scenario | Fixed mean wait" in report
    assert "| Fault profile | Runs |" in report
    assert "conflicting-green violations" in report
    assert outputs["failure_csv"].exists()
    assert outputs["mean_wait_chart"].exists()


def test_build_results_markdown_handles_empty_tables() -> None:
    markdown = build_results_markdown(
        benchmark_aggregates=[],
        failure_aggregates=[],
        duration_s=10,
        step_s=1,
        seeds=(1,),
    )

    assert "# Experiment Results Summary" in markdown
    assert "Duration per run: 10 seconds" in markdown
