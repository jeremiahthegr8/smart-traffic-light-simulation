# Experiment Results Summary

## Experiment Configuration

- Duration per run: 300 seconds
- Simulation step: 0.5 seconds
- Random seeds: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
- Controllers compared: fixed-time baseline and adaptive demand controller

## Fixed-Time vs Adaptive Control

| Scenario | Fixed mean wait (s) | Adaptive mean wait (s) | Wait change | Fixed max queue | Adaptive max queue | Queue change | Completed change | Safety violations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| alternating-peak | 301.63 +/- 5.75 | 279.81 +/- 5.88 | +7.24% +/- 0.53 pp | 115.40 +/- 2.76 | 118.40 +/- 2.55 | -2.65% +/- 1.80 pp | 12.20 +/- 1.09 | 0 |
| balanced | 265.27 +/- 6.02 | 251.50 +/- 5.42 | +5.18% +/- 0.29 pp | 99.40 +/- 2.40 | 98.20 +/- 1.89 | +1.17% +/- 0.89 pp | 8.00 +/- 0.51 | 0 |
| ew-heavy | 290.81 +/- 5.30 | 271.35 +/- 4.59 | +6.68% +/- 0.39 pp | 152.90 +/- 3.45 | 135.70 +/- 3.25 | +11.26% +/- 0.31 pp | 10.60 +/- 0.67 | 0 |
| ns-burst | 287.02 +/- 6.49 | 271.31 +/- 6.20 | +5.47% +/- 0.42 pp | 131.10 +/- 3.01 | 120.90 +/- 2.90 | +7.78% +/- 0.67 pp | 8.50 +/- 0.67 | 0 |
| ns-heavy | 281.27 +/- 4.43 | 263.76 +/- 4.26 | +6.22% +/- 0.59 pp | 151.90 +/- 2.90 | 137.50 +/- 2.58 | +9.48% +/- 0.49 pp | 9.80 +/- 1.09 | 0 |

## Detector Fault Simulation

| Fault profile | Runs | Mean completed | Mean wait (s) | Mean max queue | Safety violations |
|---|---:|---:|---:|---:|---:|
| all-stuck-low-midrun | 10 | 196.60 | 314.48 | 146.90 | 0 |
| ew-stuck-low | 10 | 232.00 | 253.49 | 105.40 | 0 |
| none | 10 | 225.80 | 263.76 | 137.50 | 0 |
| ns-stuck-high | 10 | 228.40 | 258.04 | 131.20 | 0 |

## Safety Result

Across the benchmark and detector-fault experiments, the controller recorded 0 conflicting-green violations.

## Generated Assets

- `benchmark_rows.csv`: row-level fixed/adaptive runs
- `benchmark_summary.csv`: aggregate fixed/adaptive results
- `failure_modes.csv`: detector fault results
- `mean_wait.svg`: mean waiting-time chart
- `max_queue.svg`: mean maximum-queue chart
- `completed.svg`: mean completed-vehicles chart
