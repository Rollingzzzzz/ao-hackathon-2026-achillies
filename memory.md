# Project Memory — achillies / AO Hackathon 2026

Professional, project-related log. Purpose: let any future session continue immediately with full context and accelerate project progress.

**Belongs here:** critical information, hints, findings, decisions, requirements, how and where a problem was solved, current progress and branch state.

**Never here:** informal conversation, brainstorming chatter, personal opinions, remarks about other teams or individuals.

Entries are dated and append-only. Anything recorded here is authoritative: the agent must not claim to be unaware of it.

---

## 2026-09-15

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
