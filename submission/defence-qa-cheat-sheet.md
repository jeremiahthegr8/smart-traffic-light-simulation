# Defence Q&A Cheat Sheet

Use this as a short speaking guide during the viva. Keep the answers direct, then show the
matching code, dashboard, test, or result artifact if asked for evidence.

## Core Defence Position

This is a simulation-based engineering project, not a real-road deployment. The contribution is
the design, implementation, testing, visualisation, and evaluation of a safe adaptive
traffic-light controller against a fixed-time baseline under repeatable simulated conditions.

## Likely Questions

| Question | Short answer |
|---|---|
| Why did you move away from physical hardware? | The approved scope is simulation-only so the work can focus on controller correctness, repeatable experiments, dashboard evidence, and measurable results. Physical LEDs would show output, but they would not by themselves prove that the controller improves traffic performance. |
| How is it engineering-related? | It has explicit requirements, a safety state machine, adaptive control logic, simulation models, detector-fault handling, data logging, API endpoints, a dashboard, benchmark automation, generated evidence, and regression tests. |
| Adaptive traffic lights already exist, so what is different? | The project does not claim to invent adaptive traffic lights. Its value is a complete implemented and evaluated system: fixed/adaptive comparison on identical traffic traces, visible true queue versus detector demand, detector-fault experiments, statistical benchmark summaries, and zero-conflicting-green safety checks. |
| What exactly was improved? | Compared with a basic fixed-time controller, adaptive timing reduced mean waiting time in all five benchmark scenarios, improved maximum queue length, completed more vehicles, and still recorded zero conflicting-green violations. |
| What are the final results? | Across the 10-seed benchmark, adaptive control reduced mean completed-vehicle wait by about 8.33% to 43.11% depending on scenario, with zero safety violations. |
| How are cars detected in a simulation-only project? | The simulator maintains true queue lengths internally and exposes virtual detector readings to the controller. Those virtual readings replace physical sensors for the approved scope. |
| What about rain, darkness, glare, dirt, or poor visibility? | Those conditions are represented as detector-error causes, not weather graphics. The system tests their effect through stuck-high and stuck-low detector profiles, where the controller receives wrong demand data while the true queue remains separate. |
| Why not use camera detection in the simulation? | Camera detection would be a separate computer-vision project. This project evaluates traffic-control logic, so virtual detector values are the right abstraction for repeatable controller tests. |
| What happens when detector readings are wrong? | Performance can degrade because the adaptive controller sees inaccurate demand, but safety still holds because detector values cannot directly command green lights. The phase machine still enforces amber and all-red transitions. |
| How do you know the fixed/adaptive comparison is fair? | Each paired comparison uses the same scenario, duration, step size, and random seed, so both controllers receive the same arrival trace. |
| What prevents conflicting green lights? | Both controllers share the same base phase sequence, and every signal state passes through a safety check that rejects North/South and East/West green at the same time. |
| Did adaptive always perform better? | In the corrected final 10-seed benchmark, adaptive improved mean wait, completed vehicles, and maximum queue in all five scenarios. Under severe detector faults, performance can drop, which is why the report presents limitations clearly. |
| Is the simulator realistic enough for real roads? | It is realistic enough for controlled academic comparison of controller behaviour, but not for direct real-road prediction. It does not include turning movements, pedestrians, emergency vehicles, lane changes, calibrated field data, or certified hardware. |
| Can this be deployed on a public road? | No. It is not certified traffic-control equipment. Real deployment would require approved hardware, fail-safe design, calibration, field validation, and legal authorisation. |
| What should future work add? | SUMO-based validation, calibrated junction data, more detector-noise models, pedestrian/emergency phases, turning movements, and optional hardware adapters if the project later returns to Raspberry Pi demonstration. |

## Evidence To Show

| Claim | Evidence |
|---|---|
| Safe phase machine | `src/trafficlight/domain/controller.py`, `src/trafficlight/domain/safety.py` |
| Virtual detector model | `src/trafficlight/simulation/engine.py`, `src/trafficlight/simulation/faults.py` |
| Fair fixed/adaptive benchmark | `src/trafficlight/simulation/benchmark.py` |
| Final benchmark results | `results/dissertation/benchmark_summary.csv`, `results/dissertation/results_summary.md` |
| Detector-fault results | `results/dissertation/failure_modes.csv` |
| Live visual proof | `output/playwright/dashboard-live-simulation.png` |
| Fault visual proof | `output/playwright/dashboard-fault-mismatch.png` |
| Regression tests | `tests/`, latest result: `24 passed, 1 warning` |

## Strong Closing Statement

The project is engineering-focused because it turns a traffic-control problem into a testable
software system with safety constraints, repeatable simulation, fault modelling, measured
performance, and evidence artifacts. Its limitation is that it is not a real-road deployment, and
that limitation is stated clearly in the report.
