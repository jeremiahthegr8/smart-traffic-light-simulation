# Smart Traffic-Light Simulation Submission Package

Date prepared: 10 September 2026

This folder contains the current examiner-facing package for the simulation-only adaptive
traffic-light project.

## Main Files

| File | Purpose |
|---|---|
| `complete-prep-guide.md` | Single-file overview for someone preparing to understand or defend the project |
| `final-report.md` | Final assembled report in Markdown format |
| `final-report-gctu-structure.md` | Five-chapter report source following the previous GCTU pattern |
| `final-report-gctu-structure.docx` | Editable Word version of the five-chapter report |
| `final-report-gctu-structure.pdf` | PDF export of the five-chapter report |
| `traffic-light-demo-corrected.pptx` | Corrected presentation deck |
| `demonstration-script.md` | Short viva/demo walkthrough script |
| `final-submission-checklist.md` | Final checks before submission |
| `final-details-needed.md` | Exact personal/institution details still needing confirmation |
| `defence-qa-cheat-sheet.md` | Short answers for likely examiner questions |
| `demo-rehearsal-result.md` | Recorded result from the live dashboard rehearsal |
| `institution-format-reference.md` | Format notes extracted from the previous project files |
| `methodology-implementation.md` | Methodology and implementation chapter draft |

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
24 passed, 1 warning
```

## Before Final Submission

Confirm the institution's required title page, citation style, page formatting, and accepted file
types. Replace the student and supervisor placeholders before final submission; if those details
are changed in the Markdown source, regenerate the DOCX and PDF exports.
