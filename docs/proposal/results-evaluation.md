# Results and Evaluation Draft

This section evaluates the simulation-only smart traffic-light controller against a fixed-time
baseline. The evaluation uses repeatable simulation runs rather than physical hardware, matching
the revised project scope.

## Experiment Setup

Each benchmark compares the fixed-time and adaptive controllers using the same scenario, seed,
duration, and simulation step. This keeps the traffic arrival trace identical for each paired
comparison, so the observed differences come from the controller logic rather than different
random traffic inputs.

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
with the fixed-time baseline. The strongest mean-wait reduction occurred in the alternating-peak
scenario, where adaptive control reduced mean wait by 7.24% +/- 0.53 percentage points. The
East/West-heavy scenario also showed a clear improvement, with mean wait reduced by 6.68% +/-
0.39 percentage points and mean maximum queue reduced by 11.26% +/- 0.31 percentage points.

| Scenario | Fixed mean wait (s) | Adaptive mean wait (s) | Wait improvement | Fixed max queue | Adaptive max queue | Queue improvement | Completed change |
|---|---:|---:|---:|---:|---:|---:|---:|
| Balanced | 265.27 +/- 6.02 | 251.50 +/- 5.42 | +5.18% +/- 0.29 pp | 99.40 +/- 2.40 | 98.20 +/- 1.89 | +1.17% +/- 0.89 pp | +8.00 +/- 0.51 |
| NS-heavy | 281.27 +/- 4.43 | 263.76 +/- 4.26 | +6.22% +/- 0.59 pp | 151.90 +/- 2.90 | 137.50 +/- 2.58 | +9.48% +/- 0.49 pp | +9.80 +/- 1.09 |
| EW-heavy | 290.81 +/- 5.30 | 271.35 +/- 4.59 | +6.68% +/- 0.39 pp | 152.90 +/- 3.45 | 135.70 +/- 3.25 | +11.26% +/- 0.31 pp | +10.60 +/- 0.67 |
| NS-burst | 287.02 +/- 6.49 | 271.31 +/- 6.20 | +5.47% +/- 0.42 pp | 131.10 +/- 3.01 | 120.90 +/- 2.90 | +7.78% +/- 0.67 pp | +8.50 +/- 0.67 |
| Alternating peak | 301.63 +/- 5.75 | 279.81 +/- 5.88 | +7.24% +/- 0.53 pp | 115.40 +/- 2.76 | 118.40 +/- 2.55 | -2.65% +/- 1.80 pp | +12.20 +/- 1.09 |

The adaptive controller also completed more vehicles in every scenario. The increase ranged from
8.00 additional vehicles in the balanced scenario to 12.20 additional vehicles in the
alternating-peak scenario. This supports the claim that demand-responsive timing can improve
throughput as well as waiting time under the tested conditions.

The maximum-queue result is more mixed. Adaptive control reduced mean maximum queue length in the
balanced, NS-heavy, EW-heavy, and NS-burst scenarios. In the alternating-peak scenario, however,
the mean maximum queue increased from 115.40 to 118.40 vehicles. This means the adaptive approach
improved average waiting time and completed vehicles in that case, but did not minimise peak
queue length. The likely reason is that the controller serves changing demand more aggressively,
which improves flow overall while allowing a short-lived peak queue to form during the demand
transition.

## Detector Fault Results

The detector fault experiments test whether the controller and safety model remain stable when
simulated demand readings are wrong. These tests used the NS-heavy scenario, the same 300-second
duration, the same 0.5-second step size, and seeds 1 to 10.

| Fault profile | Runs | Mean completed | Mean wait (s) | Mean max queue | Safety violations |
|---|---:|---:|---:|---:|---:|
| none | 10 | 225.80 | 263.76 | 137.50 | 0 |
| ns-stuck-high | 10 | 228.40 | 258.04 | 131.20 | 0 |
| ew-stuck-low | 10 | 232.00 | 253.49 | 105.40 | 0 |
| all-stuck-low-midrun | 10 | 196.60 | 314.48 | 146.90 | 0 |

The all-stuck-low-midrun profile caused the worst performance degradation. Mean completed vehicles
fell to 196.60 and mean wait increased to 314.48 seconds. This is expected because the adaptive
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
mean waiting time by about 5.18% to 7.24% and completed more vehicles than the fixed-time baseline,
while maintaining zero conflicting-green violations. Queue-length performance also improved in
four out of five scenarios, with the alternating-peak case showing a tradeoff between lower mean
wait and a slightly higher peak queue.

The main limitation is that these findings come from a simplified software simulation. The model
does not include turning movements, pedestrians, emergency vehicles, lane changes, real detector
noise, or calibrated traffic-flow data from an actual junction. The results are therefore best
presented as evidence that the controller design works inside the implemented simulation, not as a
direct prediction of road-network performance.
