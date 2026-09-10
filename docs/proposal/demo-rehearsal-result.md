# Demo Rehearsal Result

Date: 10 September 2026

This rehearsal checked the presentation files, saved evidence, API startup, live dashboard run,
detector-fault run, and dashboard benchmark workflow. It was refreshed after the simulator was
corrected to use demand-rate arrivals and completed-vehicle waiting time.

## Files Checked

| Item | Result |
|---|---|
| Presentation deck | `docs/presentation/traffic-light-demo-corrected.pptx` exists |
| Final assembled report | `docs/final-report/final-report.md` exists |
| Live dashboard screenshot | `output/playwright/dashboard-live-simulation.png` exists |
| Detector-fault screenshot | `output/playwright/dashboard-fault-mismatch.png` exists |
| Benchmark screenshot | `output/playwright/dashboard-benchmark-results.png` exists |
| Result summary | `results/dissertation/results_summary.md` exists |

## Local Server Check

Command used:

```powershell
.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8000
```

Checks:

- `GET /health` returned `{"status":"ok"}`.
- `GET /api/scenarios` returned the configured scenarios, including `balanced`, `ns-heavy`,
  `ew-heavy`, `ns-burst`, and `alternating-peak`.
- The dashboard opened at `http://127.0.0.1:8000/` with title `Smart Traffic-Light Dashboard`.

## Short Live Simulation Rehearsal

Settings:

- Controller: adaptive
- Scenario: `ns-heavy`
- Fault profile: none
- Duration: 30 seconds
- Step: 1 second
- Seed: 42

Observed result:

- Status: complete
- Completed vehicles: 8
- Mean wait: 4.9 seconds
- Max queue: 9
- Safety violations: 0

This confirms that the live dashboard path works for a short presentation rehearsal. The final
reported results still come from the full 300-second, 10-seed experiment package.

## Detector-Fault Rehearsal

Settings:

- Controller: adaptive
- Scenario: `ns-heavy`
- Fault profile: `ns-stuck-high`
- Duration: 30 seconds
- Step: 1 second
- Seed: 42

Observed result:

- Status: complete
- Completed vehicles: 14
- Mean wait: 3.3 seconds
- Max queue: 3
- Safety violations: 0
- North queue/detector: 0 true queue, 80 detector demand
- South queue/detector: 3 true queue, 80 detector demand

This confirms that the dashboard visibly separates true queue values from faulty detector
readings.

## Dashboard Benchmark Rehearsal

Settings:

- Duration: 30 seconds
- Step: 1 second
- Benchmark seeds: 5

Observed result:

- The dashboard benchmark produced 50 rows.
- The benchmark table included fixed and adaptive rows for all five scenarios.
- Aggregate mean-wait and max-queue charts rendered.
- The displayed benchmark rows showed zero safety violations.

## Rehearsal Outcome

The demo path is ready for a short live walkthrough. For the actual presentation, use the saved
screenshots and generated result files as fallback evidence if the browser or server is slow.
