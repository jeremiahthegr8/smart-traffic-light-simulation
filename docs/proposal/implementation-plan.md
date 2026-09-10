# Smart Traffic-Light Simulation Implementation Plan

This branch changes the project direction from Raspberry Pi hardware to a total software
simulation.

## Project Goal

Build and evaluate an adaptive four-way smart traffic-light controller using repeatable
simulation, live visualisation, database logging, and fixed-vs-adaptive benchmarks.

The core claim to prove is:

> The adaptive controller reduces waiting time and/or queue length compared with a fixed-time
> baseline under unequal or changing traffic demand, while maintaining zero conflicting-green
> violations.

## Engineering Contribution

The project does not claim that adaptive traffic-light control is new. Its engineering
contribution is a complete, simulation-only implementation that can be tested and evaluated with
repeatable evidence:

- a fixed-time baseline and adaptive controller sharing the same safe phase machine;
- deterministic scenarios and seeds for fair controller comparison;
- visible dashboard simulation with true queues and controller-visible detector values;
- detector-fault profiles for incorrect high and low demand readings;
- SQLite logging, CSV export, charts, and automated tests.

## Scope

- North/South and East/West phase groups.
- Explicit green, amber, and all-red clearance states.
- Fixed-time baseline controller.
- Adaptive controller based on detected queue demand.
- Simulation-only signal and detector abstractions.
- Time-varying traffic scenarios with repeatable seeds.
- SQLite run/event/metric logging.
- Browser dashboard with live vehicle visualisation.
- Fixed-vs-adaptive benchmark runner.
- CSV export for dissertation results.
- Detector fault simulation for stuck-high and stuck-low readings.
- Dashboard fault-profile controls showing queue counts versus detector readings.
- Statistical spread measures for repeatable multi-seed benchmarks.
- Dashboard aggregate charts comparing fixed-time and adaptive control.
- Automated safety, scenario, storage, benchmark, and API tests.

## Not In Scope

- Raspberry Pi deployment.
- GPIO wiring.
- Physical LEDs.
- Camera hardware.
- Public-road use.

The previous hardware-capable version is preserved on `master`. This branch is for the
simulation-only project direction.

## Operational Factors and Detector Assumptions

Vehicle detection is modelled as a virtual detector reading. The simulator keeps the real queue
for each approach, then sends a controller-visible demand value to the adaptive controller.

Rain, darkness, glare, dirt, poor calibration, and damaged sensors are treated as reasons why a
detector reading could become inaccurate. The current implementation represents this through
stuck-high and stuck-low detector fault profiles. It does not physically model camera images,
lighting, road-surface conditions, or sensor electronics.

Future simulation factors to add after the current MVP:

- intermittent noisy detector readings;
- delayed detector updates;
- pedestrian call buttons and crossing phases;
- emergency-vehicle priority;
- turning movements and blocked lanes;
- weather-dependent discharge rate or arrival behaviour.

## Implementation Order

1. Core domain model and phase state machine.
2. Safety interlock and unit tests.
3. Fixed-time controller baseline.
4. Adaptive green-time controller.
5. Simulation engine and scenario tests.
6. SQLite run/event/metric logging.
7. FastAPI status API and WebSocket stream.
8. Browser dashboard with visible vehicles.
9. Fixed-vs-adaptive benchmark and CSV export.
10. Aggregate benchmark statistics.
11. Report-ready charts and experiment tables.
12. Failure-mode simulation.
13. Dissertation results package script.
14. Multi-seed spread measures and dashboard aggregate charts.

## Experiment Scenarios

- `balanced`: similar demand on all approaches.
- `ns-heavy`: higher North/South demand than East/West.
- `ew-heavy`: higher East/West demand than North/South.
- `ns-burst`: a short North/South demand surge.
- `alternating-peak`: demand shifts from North/South to East/West.

Each fixed/adaptive comparison must use the same scenario, duration, step size, and seed.
For final reporting, run multiple seeds and report average, spread, and safety violations.

## Safety Rules

- Startup begins with all-red.
- North/South green and East/West green must never be active at the same time.
- Every green phase must pass through amber before all-red clearance.
- All-red clearance must occur before the opposing movement receives green.
- Adaptive logic may change green duration, but it may not bypass safety states.
- Maximum green prevents heavy demand from starving the opposing group.

## Current Status

- Repository skeleton: complete.
- Fixed-time controller: complete for MVP.
- Adaptive controller: complete for MVP.
- Time-varying simulator: complete for MVP.
- SQLite logging: complete for MVP.
- FastAPI status endpoints and WebSocket stream: complete for MVP.
- Browser dashboard with visible vehicle queues: complete for MVP.
- Fixed-vs-adaptive benchmark and CSV export: complete for MVP.
- Aggregate benchmark statistics: complete for MVP.
- Report-ready chart and summary export: complete for MVP.
- Failure-mode simulation: complete for MVP.
- Dissertation results package script: complete for MVP.
- Dashboard fault-profile visualisation: complete for MVP.
- Statistical spread measures and benchmark aggregate dashboard charts: complete for MVP.
- Requirements specification draft: complete.
- Background and literature review draft: complete.
- Methodology and implementation draft: complete.
- Results and evaluation draft: complete.
- Final report draft assembly: complete.
- Final report formatting draft: complete.
- Demonstration script draft: complete.
- Presentation deck draft: complete.
- Final submission checklist: complete.
- Demo rehearsal result: complete.
- Submission package folder: complete.
- Tests: initial safety, scenario, storage, benchmark, and API coverage complete.
