# Final Submission Checklist

Use this checklist before submitting or presenting the simulation-only project. It separates
items already covered by the repository from items that depend on the institution's required
format.

## Completed Project Evidence

- Final report source: `02-final-report-gctu-structure.md`
- Editable Word report export: `02-final-report-gctu-structure.docx`
- PDF report export: `02-final-report-gctu-structure.pdf`
- Presentation deck: `01-presentation-deck.pptx`
- Demonstration script: `03-demonstration-script.md`
- Demo rehearsal result: `04-demo-rehearsal-result.md`
- Institution format reference: `06-institution-format-reference.md`
- Final run manual: `10-simulation-run-manual.md`
- Separate Chapter One document: `11-chapter-one-introduction.docx`
- Separate Chapter Two document: `12-chapter-two-literature-review.docx`
- Dashboard screenshots: `screenshots/`
- CSV/chart evidence: `evidence/`
- Requirements specification: `docs/proposal/requirements-specification.md`
- Implementation plan: `docs/proposal/implementation-plan.md`
- Generated result package command: `scripts/dissertation_results.py`
- Automated verification command: `.\.venv\Scripts\python.exe -m pytest`

## Examiner Questions Covered

- Why the project moved from Raspberry Pi hardware to simulation-only.
- How cars are detected in the simulation using virtual detector readings.
- How rain, darkness, glare, dirt, and poor visibility are handled as detector-error causes.
- What makes the work engineering-related even though adaptive traffic lights already exist.
- What changed or improved compared with a basic traffic-light demonstration.
- Why the fixed-time and adaptive comparison is fair.
- Why detector faults affect performance but not phase safety.

## Institution-Specific Items To Confirm

These depend on the school template or supervisor instructions and cannot be fully verified from
the repository alone.

- Required title-page format and programme name.
- Student names, student IDs, and supervisor name have been added to `02-final-report-gctu-structure.md`.
- If title-page details change, regenerate `02-final-report-gctu-structure.docx` and `02-final-report-gctu-structure.pdf`.
- If title-page details change, regenerate `11-chapter-one-introduction.docx` and `12-chapter-two-literature-review.docx`.
- Required declaration, acknowledgement, abstract, and table-of-contents wording.
- Required citation style, such as IEEE, Harvard, APA, or departmental style.
- Required page numbering, margins, line spacing, and font.
- Required figure/table caption format and numbering style.
- Required appendix format and whether source-code listings are needed.
- Required submission format, such as PDF, DOCX, printed copy, Git repository, or presentation.
- Whether the defence deck must use the old 16-slide topic order.

## Final Demo Rehearsal

- Review the latest rehearsal result in `04-demo-rehearsal-result.md`.
- Open `01-presentation-deck.pptx`.
- Start the dashboard with `.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8000`.
- Run one adaptive live simulation with `ns-heavy`.
- Show one detector-fault run using `ns-stuck-high`.
- Show the benchmark results view or saved screenshot.
- Run `.\.venv\Scripts\python.exe -m pytest` if live dashboard timing fails.
