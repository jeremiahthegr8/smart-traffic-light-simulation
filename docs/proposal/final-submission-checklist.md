# Final Submission Checklist

Use this checklist before submitting or presenting the simulation-only project. It separates
items already covered by the repository from items that depend on the institution's required
format.

## Completed Project Evidence

- Final assembled report: `docs/final-report/final-report.md`
- GCTU five-chapter report source: `docs/final-report/final-report-gctu-structure.md`
- Editable Word report export: `docs/final-report/final-report-gctu-structure.docx`
- PDF report export: `docs/final-report/final-report-gctu-structure.pdf`
- Presentation deck: `docs/presentation/traffic-light-demo-corrected.pptx`
- Demonstration script: `docs/proposal/demonstration-script.md`
- Demo rehearsal result: `docs/proposal/demo-rehearsal-result.md`
- Institution format reference: `docs/proposal/institution-format-reference.md`
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

- Required title-page format, programme name, student name, supervisor name, and ID number.
- Replace the placeholders in `docs/final-report/final-report-gctu-structure.md` and regenerate `docs/final-report/final-report-gctu-structure.docx` and `docs/final-report/final-report-gctu-structure.pdf` with the exact student and supervisor details.
- Required declaration, acknowledgement, abstract, and table-of-contents wording.
- Required citation style, such as IEEE, Harvard, APA, or departmental style.
- Required page numbering, margins, line spacing, and font.
- Required figure/table caption format and numbering style.
- Required appendix format and whether source-code listings are needed.
- Required submission format, such as PDF, DOCX, printed copy, Git repository, or presentation.
- Whether the defence deck must use the old 16-slide topic order.

## Final Demo Rehearsal

- Review the latest rehearsal result in `docs/proposal/demo-rehearsal-result.md`.
- Open `docs/presentation/traffic-light-demo-corrected.pptx`.
- Start the dashboard with `.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8000`.
- Run one adaptive live simulation with `ns-heavy`.
- Show one detector-fault run using `ns-stuck-high`.
- Show the benchmark results view or saved screenshot.
- Run `.\.venv\Scripts\python.exe -m pytest` if live dashboard timing fails.
