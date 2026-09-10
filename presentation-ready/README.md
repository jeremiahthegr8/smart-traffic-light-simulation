# Presentation Ready Folder

Use this folder for the project defence or viva.

## Open First

1. `01-presentation-deck.pptx`
2. `03-demonstration-script.md`
3. `02-final-report-gctu-structure.md`

## Supporting Files

- `04-demo-rehearsal-result.md`: confirms the dashboard, fault run, and benchmark run worked.
- `05-final-submission-checklist.md`: final checks before submission.
- `06-institution-format-reference.md`: notes taken from the previous project format.
- `screenshots/`: fallback dashboard screenshots.
- `evidence/`: CSV summaries, SVG charts, and final result summary.

## Live Demo Command

```powershell
.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`.
