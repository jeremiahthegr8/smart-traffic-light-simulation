# Results and Evaluation Draft

This section evaluates the simulation-only smart traffic-light controller against a fixed-time
baseline. The evaluation uses repeatable simulation runs rather than physical hardware, matching
the revised project scope.

## Experiment Setup

Each benchmark compares the fixed-time and adaptive controllers using the same scenario, seed,
duration, and simulation step. This keeps the traffic arrival trace identical for each paired
comparison, so the observed differences come from the controller logic rather than different
random traffic inputs.

The final experiment package was regenerated after correcting the simulator's arrival and waiting
time accounting. Arrivals are now sampled from the configured per-minute demand rate, and mean
wait is calculated from completed vehicles using each vehicle's recorded arrival and departure
time.

- Duration per run: 300 seconds
- Simulation step: 0.5 seconds
- Seeds: 1 to 10
- Scenarios: balanced, North/South heavy, East/West heavy, North/South burst, alternating peak
- Main metrics: mean waiting time, maximum queue length, completed vehicles, safety violations
- Source artifacts: `results/dissertation/benchmark_rows.csv`,
  `results/dissertation/benchmark_summary.csv`, and
  `results/dissertation/results_summary.md`

## Fixed-Time vs Adaptive Results

Across all five benchmark scenarios, the adaptive controller reduced mean waiting time compared
with the fixed-time baseline. The strongest mean-wait reduction occurred in the East/West-heavy
scenario, where adaptive control reduced mean completed-vehicle wait by 43.11% +/- 3.57
percentage points. The North/South-heavy scenario also showed a clear improvement, with mean wait
reduced by 32.54% +/- 4.23 percentage points and mean maximum queue reduced by 48.77% +/- 4.75
percentage points.

| Scenario | Fixed mean wait (s) | Adaptive mean wait (s) | Wait improvement | Fixed max queue | Adaptive max queue | Queue improvement | Completed change |
|---|---:|---:|---:|---:|---:|---:|---:|
| Balanced | 23.91 +/- 1.25 | 21.89 +/- 1.25 | +8.33% +/- 3.90 pp | 13.00 +/- 1.31 | 11.70 +/- 0.93 | +9.18% +/- 5.82 pp | +1.90 +/- 1.90 |
| NS-heavy | 43.93 +/- 3.38 | 29.51 +/- 2.37 | +32.54% +/- 4.23 pp | 44.00 +/- 5.99 | 22.90 +/- 4.83 | +48.77% +/- 4.75 pp | +41.60 +/- 3.67 |
| EW-heavy | 50.15 +/- 2.77 | 28.48 +/- 2.15 | +43.11% +/- 3.57 pp | 40.90 +/- 3.71 | 20.20 +/- 2.86 | +50.84% +/- 4.11 pp | +42.70 +/- 3.33 |
| NS-burst | 44.10 +/- 1.71 | 37.82 +/- 3.21 | +14.46% +/- 5.07 pp | 39.90 +/- 3.97 | 28.40 +/- 4.08 | +29.54% +/- 3.87 pp | +36.50 +/- 3.18 |
| Alternating peak | 54.58 +/- 3.50 | 38.09 +/- 5.24 | +30.76% +/- 6.20 pp | 38.90 +/- 3.80 | 30.70 +/- 4.79 | +21.81% +/- 6.93 pp | +23.50 +/- 2.98 |

The adaptive controller also completed more vehicles in every scenario. The increase ranged from
1.90 additional vehicles in the balanced scenario to 42.70 additional vehicles in the
East/West-heavy scenario. This supports the claim that demand-responsive timing can improve
throughput as well as waiting time under the tested conditions.

Adaptive control also reduced mean maximum queue length in all five scenarios. The largest
queue improvement occurred in the East/West-heavy scenario, where mean maximum queue fell from
40.90 to 20.20 vehicles. This supports the argument that the adaptive controller responds most
strongly when demand is uneven.

## Detector Fault Results

The detector fault experiments test whether the controller and safety model remain stable when
simulated demand readings are wrong. These tests used the NS-heavy scenario, the same 300-second
duration, the same 0.5-second step size, and seeds 1 to 10.

| Fault profile | Runs | Mean completed | Mean wait (s) | Mean max queue | Safety violations |
|---|---:|---:|---:|---:|---:|
| none | 10 | 196.50 | 29.51 | 22.90 | 0 |
| ns-stuck-high | 10 | 198.40 | 26.52 | 17.40 | 0 |
| ew-stuck-low | 10 | 197.50 | 24.29 | 17.30 | 0 |
| all-stuck-low-midrun | 10 | 160.60 | 34.18 | 41.00 | 0 |

The all-stuck-low-midrun profile caused the worst performance degradation. Mean completed vehicles
fell to 160.60 and mean max queue increased to 41.00 vehicles. This is expected because the adaptive
controller receives no demand signal after the fault begins, so it cannot respond accurately to
real queues. Even so, the system still recorded zero conflicting-green violations.

The stuck-high and East/West stuck-low profiles did not create safety violations either. Their
performance results should be interpreted as simulation outcomes under the current demand model,
not as a guarantee that detector faults are harmless in real traffic. They show that the phase
state machine continues to enforce safe signal transitions even when demand inputs are faulty.

## Safety Evaluation

The central safety rule is that North/South green and East/West green must never be active at the
same time. Across the benchmark and detector-fault experiments, the simulation recorded zero
conflicting-green violations.

This result supports the safety part of the project claim. The adaptive controller is only allowed
to influence green duration decisions; it does not bypass amber or all-red clearance states. Safety
is therefore enforced by the shared phase state machine rather than by the adaptive timing
heuristic alone.

## Dashboard Evidence

The dashboard screenshots provide implementation evidence for the final report:

- `output/playwright/dashboard-live-simulation.png`: live simulation with visible queued and moving
  vehicles.
- `output/playwright/dashboard-fault-mismatch.png`: detector-fault view showing North/South
  detector readings stuck at 80 while real queues remain lower.
- `output/playwright/dashboard-benchmark-results.png`: fixed-vs-adaptive benchmark table and
  aggregate charts from a 10-seed run.

The chart assets generated for report figures are:

- `results/dissertation/mean_wait.svg`
- `results/dissertation/max_queue.svg`
- `results/dissertation/completed.svg`

## Conclusion

The results support the project claim. Under the tested scenarios, the adaptive controller reduced
mean completed-vehicle waiting time by about 8.33% to 43.11% and completed more vehicles than the
fixed-time baseline, while maintaining zero conflicting-green violations. Queue-length performance
also improved in all five benchmark scenarios.

The main limitation is that these findings come from a simplified software simulation. The model
does not include turning movements, pedestrians, emergency vehicles, lane changes, real detector
noise, or calibrated traffic-flow data from an actual junction. The results are therefore best
presented as evidence that the controller design works inside the implemented simulation, not as a
direct prediction of road-network performance.
