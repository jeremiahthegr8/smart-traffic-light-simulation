# Smart Traffic-Light Simulation Submission Package

Date prepared: 10 September 2026

This folder contains the current examiner-facing package for the simulation-only adaptive
traffic-light project.

## Main Files

| File | Purpose |
|---|---|
| `final-report.md` | Final assembled report in Markdown format |
| `traffic-light-demo-v2.pptx` | Revised presentation deck |
| `demonstration-script.md` | Short viva/demo walkthrough script |
| `final-submission-checklist.md` | Final checks before submission |
| `demo-rehearsal-result.md` | Recorded result from the live dashboard rehearsal |

## Evidence Files

| Folder | Contents |
|---|---|
| `evidence/` | Result summary, benchmark CSVs, detector-fault CSV, and SVG charts |
| `screenshots/` | Saved dashboard screenshots for live simulation, detector fault, and benchmark views |

## Source Code

The source code remains in the repository on the `simulation-only` branch. The main packages are:

- `src/trafficlight/domain/`
- `src/trafficlight/simulation/`
- `src/trafficlight/api/`
- `src/trafficlight/dashboard/`
- `src/trafficlight/storage/`

## Verification

The latest test command used was:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Latest result:

```text
22 passed, 1 warning
```

## Before Final Submission

Confirm the institution's required title page, citation style, page formatting, and accepted file
types. If the school requires PDF or DOCX, convert `final-report.md` using the school-approved
template before submitting.
