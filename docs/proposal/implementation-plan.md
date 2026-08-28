# Smart Traffic-Light Implementation Plan

This plan distills the research brief into the work that belongs in this repository.

## Project Goal

Build a simulation-first adaptive four-way traffic-light controller that can later run on a
Raspberry Pi through a replaceable GPIO adapter.

The core claim to prove is:

> The adaptive controller reduces waiting time or queue length compared with a fixed-time
> baseline under unequal traffic demand, while maintaining zero conflicting-green violations.

## MVP Scope

- North/South and East/West phase groups.
- Explicit green, amber, and all-red clearance states.
- Fixed-time baseline controller.
- Adaptive controller based on detected demand.
- Hardware-independent signal and detector interfaces.
- Lightweight simulator with repeatable random seeds.
- SQLite run/event/metric logging.
- Safety tests for conflicting greens and max-green enforcement.
- CLI command for fixed-vs-adaptive experiment runs.

## Implementation Order

1. Core domain model and phase state machine.
2. Safety interlock and unit tests.
3. Fixed-time controller baseline.
4. Adaptive green-time controller.
5. Simulation engine and scenario tests.
6. SQLite run/event/metric logging.
7. FastAPI status API and WebSocket stream.
8. Browser dashboard.
9. Fixed-vs-adaptive benchmark and CSV export.
10. GPIO Zero signal adapter.
11. Raspberry Pi deployment service.

## Experiment Scenarios

- `balanced`: similar demand on all approaches.
- `ns-heavy`: higher North/South demand than East/West.
- `ew-heavy`: higher East/West demand than North/South.

Each fixed/adaptive comparison must use the same scenario, duration, step size, and seed.

## Safety Rules

- Startup begins with all-red.
- North/South green and East/West green must never be active at the same time.
- Every green phase must pass through amber before all-red clearance.
- All-red clearance must occur before the opposing movement receives green.
- Adaptive logic may change green duration, but it may not bypass safety states.
- Maximum green prevents sensor faults or heavy demand from starving the opposing group.

## Current Status

- Repository skeleton: complete.
- Fixed-time controller: complete for MVP.
- Adaptive controller: complete for MVP.
- Simulator: complete for MVP.
- SQLite logging: complete for MVP.
- FastAPI status endpoints and WebSocket stream: complete for MVP.
- Browser dashboard with visible vehicle queues: complete for MVP.
- Fixed-vs-adaptive benchmark and CSV export: complete for MVP.
- Tests: initial safety, scenario, storage, and API coverage complete.
- GPIO/deployment: pending.
