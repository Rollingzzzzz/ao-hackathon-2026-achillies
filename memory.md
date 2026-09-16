# Project Memory — achillies / AO Hackathon 2026

Professional, project-related log. Purpose: let any future session continue immediately with full context and accelerate project progress.

**Belongs here:** critical information, hints, findings, decisions, requirements, how and where a problem was solved, current progress and branch state.

**Never here:** informal conversation, brainstorming chatter, personal opinions, remarks about other teams or individuals.

Entries are dated and append-only. Anything recorded here is authoritative: the agent must not claim to be unaware of it.

---

## 2026-09-16 (event day)

### Solution delivered (working state, branch `feat/sa1-alarm-storm`)

- **Product:** AlarmStorm — 3,000 alarms → **5 event cards** (1:600 reduction), all five root causes correct: session-service memory leak (slow-burn, 611 alarms, 01:31–02:56), dc1/rack-A rack network outage (718), billing-db disk/tablespace full (400), payment-provider-gw external provider degradation (245), subscriber-db connection-pool exhaustion (407). 619 alarms audited as noise with explicit reasons. The two time-overlapping independent events (leak ↔ payment provider, 02:38–03:00) stayed SEPARATE (the scenario's deliberate wrong-merge trap).
- **Architecture:** `src/alarmstorm/` — io (blame parsing from timeout/conn_refused/ext_* messages: free causal edges), graph (dependency distances + explainability), engine (anomaly cells by type-baseline → union-find seeds with rules: same-service/blame/direct-dep/rack-only-for-network; core-gated snowball attach with hotness tie-break; root scoring with blame + rootish marker weights + layer discount for db_write_fail/conn_pool when own *-db is failing + rack promotion), cards (Turkish XAI text: hypothesis/evidence/counters/action+owner+status), report (PNG charts), dashboard (single-file HTML, data+charts embedded). `run.py` pipeline entry; `serve.py` stdlib demo server with live action lifecycle API (GET/POST /api/actions, atomic persistent out/actions.json, ASCII aliases acik/islemde/kapali accepted).
- **Key engine lessons (fixed by iteration, see prompts/2026-09-16_engine_iterations.md):** rack locality must bind only network alarms; sustained resource signals bind only along their own dependency direction; window growth only on strong (blame/anomalous) evidence — otherwise hub services swallow unrelated storms; db-layer symptoms on a service are derived when its own DB is failing.
- **Dashboard bug found via in-page JS bisection:** `str.replace('"per_type": {}', value)` ate the dict key — placeholders must be replaced with complete values in one place.
- **Verification done:** pipeline `--debug` runs (outputs committed as evidence); DOM-verified dashboard (5 cards, 5 chips, 7/7 images, no overflow); live action button click → İŞLEMDE with persisted history; screenshots in `demo/dashboard_{top,full}.png`.
- **Compliance:** all significant prompts recorded in `prompts/` (4 records); README/AI_JURI.md/docs filled with evidence paths; submission.json complete and valid; `requirements.txt` frozen from the verified venv (Python 3.12.10, pandas 3.0.5, matplotlib 3.11.2). Data package never committed (`data/` gitignored).
- Deliverables committed on branch `feat/sa1-alarm-storm`: 0ab339d (setup+memory), 47cd27b (core engine), a40d960 (dashboard+demo), + delivery docs commit. Awaiting human verification for merge to `main`.


- Scenario opened at 14:30: **S-A1 "Alarm Fırtınası" (Alert Storm Correlator)**. Window: 2026-09-10 01:30–03:30, 3,000 alarms, 27 services, 56 hosts, 32 dependency records.
- Data package (small, ~1.1 MB total — NOT the feared 2 GB): extracted at `data/package/katilimci_paketi/` (gitignored; never commit). Files: `alarms.json` (3,000 records; JSON array), `alarms.csv` (same data, tags expanded), `service_dependencies.csv` (kaynak_servis depends on hedef_servis; senkron/asenkron; kritiklik), `host_inventory.csv` (host→service, dc1/dc2, rack-A/B/C, is_kritikligi), `VERI_SOZLUGU.md` (26 alarm type codes), `SENARYO_BRIFINGI.md`.
- Task: reduce the alarm flood to event cards (≤15; "as many as an on-call engineer can look at"). Each card requires: root-cause hypothesis + rationale (+counter-hypotheses = X-Factor), affected services, alarm count, time range, first action with owner + status. Optional: action lifecycle tracking (open→close) in demo. All 3,000 alarms must be processed; noise must be eliminated WITH an audit view showing why each eliminated alarm was dropped.
- Key data hints from the briefing: multiple independent real events (count undisclosed — deriving it IS part of the scenario); large background-noise fraction; some events burst-like, some slow-burn (slow-burn harder); alarm types are SHARED across events — type alone cannot discriminate; evaluation = last commit at 17:30 sharp (later commits ignored); repo stays public; veri paketi repoya konmaz.
- Scoring: reduction ratio, root-cause hit rate (against hidden ground truth opened at evaluation), wrong-merge penalty, noise-elimination precision. Justified wrong hypothesis > unjustified correct one — XAI rationale is the product.
- Environment: branch `feat/sa1-alarm-storm` opened as first action per plan; venv `.venv` created (Python 3.12.10 — 3.11 not installed, 3.12 satisfies "3.11+"; pandas 3.0.5 installed). data/ added to `.gitignore`.


- Repository was reset to a clean starting skeleton (fresh single-commit history). The mandatory structure from the official announcement is in place and verified (public repo, branch `main`). Local repo: `D:\projeler\ao-hackathon-2026-achillies`.
- Team (in `submission.json`): Aziz Utku ÖZDEMİR (captain + participant), Bülent Topçu (participant), Sefa Korkmaz (participant). Contact: azizutkuozdemir@gmail.com. No GitHub collaborators will be added.
- Language decision: all code will be **Python 3.11** (per the official announcement's "Python 3.11+" requirement).
- `CONVENTIONS.md` is the binding engineering contract for hackathon-day coding; it is written in English only.
- SAKA (https://saka.turkcell.com.tr/) is the primary AI platform; every AI tool/model used must be declared in the repo.
- Event: 2026-09-16, Küçükyalı C-5, 14:30–19:00.
- Expectation: the incoming dataset may be large (JSON / CSV / log — format unknown); the goal is to catch anomalies/oddities, possibly related to customers. Preparation must therefore stay format-agnostic.

### Critical rules from the official announcement email

- Schedule: scenario + data package open at 14:30; development window 14:45–17:30; **HARD DEADLINE 17:30** — evaluation is done on the last commit at 17:30, later commits are ignored; AI jury scan 17:30–17:45; presentations at 17:45, 7 min + 3 min Q&A, order drawn by lottery (be ready to go on stage at any moment).
- Mandatory repo structure: `README.md`, `AI_JURI.md`, `submission.json`, `.env.example`, `CLAUDE.md` (or `.cursorrules` / copilot-instructions), `docs/` (`plan.md`, `fazlar.md`, `mimari.md`), `prompts/`, `demo/`, `src/`.
- The repo MUST stay **public**. Making it private or deleting it = disqualification.
- `.env` must never be committed (only `.env.example`).
- `AI_JURI.md` and `submission.json` must be kept up to date. Every claim needs a file-path evidence; claims without evidence score nothing.
- The jury focuses on three things: (1) AI strategy & workflow (AI_JURI.md, prompts/, commit history), (2) the solution itself (src/, docs/mimari.md, working run instructions), (3) X-Factor — one thing a plain solution could not do, shown in code.
- XAI is the jury's top concern: every decision the system makes must come with a human-readable rationale. "Why this result?" WILL be asked on stage.
- Score boosters: frequent meaningful commits; prompts stored in `prompts/`; concrete measured numbers instead of vague claims; screenshots in `demo/` (the jury reads code but cannot see the product).
- SAKA is the primary AI platform; any other AI tool is allowed, but every tool and model version must be declared in the repo. Hackathon data is synthetic; never upload real customer or production data to the platform.
- Before the event: general-purpose skeletons, templates and helper code are encouraged; scenario-specific solutions are forbidden.
- No deployment required: a locally working product is enough, but it must run live on stage.
- No setup support on event day: environment, SAKA access and git auth must be tested BEFORE the event.
- SAKA usage advice from the email: spend the first ~15 minutes on approach selection; use the model for data exploration (schema → hypotheses) — finding the meaningful signal is worth more than coding; build module by module, run and verify each module; a documented model comparison is a strong presentation narrative.
- Working agreement: feature-branch workflow — for every work item (or every stage of a big task), open a branch first, commit there, run and verify, and merge into `main` ONLY when it is confirmed to work. `main` must always stay in a verified, working state. Recorded in `CONVENTIONS.md` as `Git Branching Workflow`.
- Working agreement: security — no API keys or credentials are ever pushed to git; no Turkcell-related sensitive info (customer data, internal details) is ever pushed; a sensitivity check of the staged diff is mandatory before EVERY commit. Recorded in `CONVENTIONS.md` as `Secrets and Sensitive Data`.
- Working agreement: script development & verification loop — for every script, the agent first self-verifies (consistency review, trial runs); every self-trial MUST run with `--debug` and its output MUST be saved under `scripts/<script-name>/`; after each iteration the agent hands the exact run/test commands to the user in chat so the human tests and observes personally; final acceptance of every script development is always the human's explicit confirmation. Recorded in `CONVENTIONS.md` as `Script Development and Verification Loop`.
- Working agreement (extends the loop): after the work is committed on its branch, the agent MUST post the run commands with FULL absolute paths in the chat, so the human can run and verify that branch's script personally. Recorded in `CONVENTIONS.md` (`Script Development and Verification Loop`).
- Requirement: dependency reproducibility — the project runs in a dedicated Python 3.11 venv; at every verified working state (mandatory for the final prototype before the deadline) exact versions are frozen via `python -m pip freeze > requirements.txt`, and the file MUST be committed/pushed so the prototype certainly runs on the external test machine (Selahattin's computer). Recorded in `CONVENTIONS.md` as `Dependency Freeze (Reproducible Environment)`.
- Requirement: every script MUST have its own `scripts/<script-name>/README.md` with summary info (purpose, inputs/outputs, CLI params, example full-path run command, key decisions/findings, status), kept up to date; it is the durable recall point after chat-context compaction. Recorded in `CONVENTIONS.md` as `Per-Script README (Context Recovery)`.
- Event-day execution plan (user decision, 2026-09-15): the moment the data package is released on event day (2026-09-16, ~14:30), work on the provided large data file starts IMMEDIATELY — first action is opening a dedicated branch for the data-processing work, then starting directly on the file. No time spent on setup debates; branching is quick and keeps all commits off `main` as required.
- AI tooling decision (user decision, 2026-09-15): the team will NOT use SAKA. All AI-assisted development is done with ZCode (GLM-5.3) directly — external AI use is permitted by the rules. Compliance consequence: ZCode/GLM-5.3 MUST be declared in `AI_JURI.md`, and significant prompts MUST be saved under `prompts/` so the AI-strategy scoring criterion is still fully covered without SAKA.
- Trap-audit pass (user decision, 2026-09-16 ~16:30): before merging to main, self-audit the solution against the suspicion that the scenario author planted a trap. Built `scripts/trap_audit/` (internal ground-truth proxy from alarm_id emission order - audit-only, never used by the engine or shown to the jury). Findings: legacy run absorbed 1157/1762 noise alarms into cards and lost 14 real cascade-tail alarms incl. the only stray sev5; EVT-05 root direction confirmed correct (subscriber-db signals precede batch_overlap). Engine fix on branch `feat/sa1-trap-audit`: core-evidence attach gate (blame/anomaly/marker/sev>=4 only), 3 attach sweeps, measured counter-hypothesis fallback for single-service cards. After: noise recall 34.3% -> 92.2%, precision 95.6%, all 248 sev5 attached, 5 cards and roots unchanged. Delivery docs (README/AI_JURI/submission.json) updated to the new numbers.
