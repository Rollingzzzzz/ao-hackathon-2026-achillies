# explorer

Pipeline execution-history GUI (internal debug tool, not part of the jury
delivery). Renders every event-day step in EXECUTION ORDER with its folders,
files, README summaries, run commands and debug logs in the browser.

## Purpose
"Which script ran when, in which folder, with which outputs?" — a step-by-step
answer for team debugging. Steps mirror `docs/fazlar.md` phases 1-6:
explore_profile → hypothesis_probe → core engine (src/alarmstorm + run.py) →
dashboard/serve → delivery package → trap_audit self-audit.

## How it works
- `explorer.py` scans the repo and emits `out/explorer_manifest.json`
  (step definitions + live file metadata: size, mtime, kind). mtime evidence
  keeps "last run" honest.
- `serve.py` serves the GUI at `/explorer`, the manifest at
  `/api/explorer` (auto-generated on first request), and file contents at
  `/api/file?path=...` — strictly whitelisted to manifest-listed files,
  repo-root confined, text suffixes only, 200 KB truncation. Raw data
  (`data/`) and `.git/` are never viewable.
- `out/explorer.html` — dark UI: left step timeline (phase, time window,
  file count, last-run evidence), right step detail (README summary, note,
  copyable run command, per-folder file tables), inline file viewer
  (Esc closes, ←/→ steps, logs tagged LOG).

## Inputs / Outputs
- Input: the repository itself (scripts/, src/, out/, docs/, prompts/, demo/)
- Output: `out/explorer_manifest.json` (GUI is `out/explorer.html` via serve.py)

## CLI / example run (full path)
```
D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\scripts\explorer\explorer.py
D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\serve.py
```
Then open http://localhost:8787/explorer (manifest auto-generates if missing).

## Status
VERIFIED (agent self-run + browser E2E: 6 steps render, step-2 navigation,
run_debug.log opened in the viewer; whitelist blocks data/ and .git/).
Awaiting human confirmation.
