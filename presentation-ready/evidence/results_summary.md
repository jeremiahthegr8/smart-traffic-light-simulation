# Experiment Results Summary

## Experiment Configuration

- Duration per run: 300 seconds
- Simulation step: 0.5 seconds
- Random seeds: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
- Controllers compared: fixed-time baseline and adaptive demand controller

## Fixed-Time vs Adaptive Control

| Scenario | Fixed mean wait (s) | Adaptive mean wait (s) | Wait change | Fixed max queue | Adaptive max queue | Queue change | Completed change | Safety violations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| alternating-peak | 54.58 +/- 3.50 | 38.09 +/- 5.24 | +30.76% +/- 6.20 pp | 38.90 +/- 3.80 | 30.70 +/- 4.79 | +21.81% +/- 6.93 pp | 23.50 +/- 2.98 | 0 |
| balanced | 23.91 +/- 1.25 | 21.89 +/- 1.25 | +8.33% +/- 3.90 pp | 13.00 +/- 1.31 | 11.70 +/- 0.93 | +9.18% +/- 5.82 pp | 1.90 +/- 1.90 | 0 |
| ew-heavy | 50.15 +/- 2.77 | 28.48 +/- 2.15 | +43.11% +/- 3.57 pp | 40.90 +/- 3.71 | 20.20 +/- 2.86 | +50.84% +/- 4.11 pp | 42.70 +/- 3.33 | 0 |
| ns-burst | 44.10 +/- 1.71 | 37.82 +/- 3.21 | +14.46% +/- 5.07 pp | 39.90 +/- 3.97 | 28.40 +/- 4.08 | +29.54% +/- 3.87 pp | 36.50 +/- 3.18 | 0 |
| ns-heavy | 43.93 +/- 3.38 | 29.51 +/- 2.37 | +32.54% +/- 4.23 pp | 44.00 +/- 5.99 | 22.90 +/- 4.83 | +48.77% +/- 4.75 pp | 41.60 +/- 3.67 | 0 |

## Detector Fault Simulation

| Fault profile | Runs | Mean completed | Mean wait (s) | Mean max queue | Safety violations |
|---|---:|---:|---:|---:|---:|
| all-stuck-low-midrun | 10 | 160.60 | 34.18 | 41.00 | 0 |
| ew-stuck-low | 10 | 197.50 | 24.29 | 17.30 | 0 |
| none | 10 | 196.50 | 29.51 | 22.90 | 0 |
| ns-stuck-high | 10 | 198.40 | 26.52 | 17.40 | 0 |

## Safety Result

Across the benchmark and detector-fault experiments, the controller recorded 0 conflicting-green violations.

## Generated Assets

- `benchmark_rows.csv`: row-level fixed/adaptive runs
- `benchmark_summary.csv`: aggregate fixed/adaptive results
- `failure_modes.csv`: detector fault results
- `mean_wait.svg`: mean waiting-time chart
- `max_queue.svg`: mean maximum-queue chart
- `completed.svg`: mean completed-vehicles chart
