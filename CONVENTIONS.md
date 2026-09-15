# CONVENTIONS — achillies

**Purpose of this file:** Avoid losing hackathon-day time on design debates and guarantee that the code we write is robust. Every binding engineering decision is recorded here. During development, this file is applied as written; rules here are not re-negotiated mid-session.

## Dependency Freeze (Reproducible Environment)

- The project MUST run in a dedicated Python 3.11 virtual environment, isolated from system-wide packages.
- At every verified working state — and MANDATORY for the final working prototype before the hard deadline — the exact installed package versions MUST be recorded from that environment into `requirements.txt` (root of the repo) via `python -m pip freeze > requirements.txt`.
- The freeze file MUST be committed and pushed to GitHub, so the exact same environment can be recreated on any other machine (e.g., Selahattin's test computer) with `python -m pip install -r requirements.txt` and the prototype is guaranteed to run there.

## Language and Runtime

- All code MUST use Python **3.11** (team decision, based on the "Python 3.11+" requirement in the official announcement).

## Large-File Handling

These rules apply to EVERY job/function that processes files of unknown or large size:

- **Chunked (streamed) input:** NEVER load an entire large file into memory. Read inputs in bounded chunks or line by line, so memory usage stays roughly constant regardless of file size.
- **Non-exploding code:** Code MUST NOT crash, hang, or exhaust memory on large inputs. No unbounded lists, no full-file reads, no accumulating the whole dataset in RAM.
- **Atomic output writing:** Write outputs to a temporary file first, then rename/move it into its final path in ONE step. A partially written or corrupt output file must never exist.
- **Balance rule:** Do not over-engineer. Keep the implementation simple and fast — the only hard requirement is bounded memory and safe writes.

## CLI Parameters

- Every tunable behavior of a script MUST be exposed as a command-line argument, so behavior can be changed from outside when invoking the script, without editing the code.

## File In, File Out

- Every input is a file. Every output is a file. Scripts read from file paths and write all results to file paths — no data lives only inside the process.

## Debug Mode

- Every script MUST accept a `--debug` flag. When set, a human can easily follow what the script is doing and where (clear progress messages, intermediate states, decision points).

## Script Output Organization (Traceability)

- Every script MUST write its own outputs (results, run statistics, logs) into a folder dedicated to it: `scripts/<script-name>/` under the project folder, created automatically if missing.
- Everything a script produces MUST be traceable back to that script by name.

> Note: `scripts/` is an addition of ours on top of the mandatory skeleton from the announcement; it does not replace any required folder.

## Script Development and Verification Loop

- For every script (every problem-solving piece) developed, the agent (ZCode / GLM-5.3) first verifies it autonomously: reviews the code for internal consistency, runs its own trial executions, and inspects the produced outputs.
- Whenever the agent runs a script on its own during development (any self-trial), it MUST run it with `--debug` enabled, and MUST save the debug output (results, analytics, run statistics, timings) under that script's dedicated folder (`scripts/<script-name>/`).
- After each iteration, the agent MUST hand the exact run/test commands to the user in the chat, so the human can execute the script personally and observe its behavior directly, with their own eyes.
- After the work is committed on its branch, the agent MUST post in the chat the exact commands for running that branch's script(s) with FULL paths (absolute paths usable as-is from any terminal), so the human can personally run them and verify with their own eyes that the script works in that branch.
- The final consistency/acceptance check of every script development is ALWAYS performed by the human. A script counts as verified only after explicit user confirmation (the same confirmation that gates merging into `main`).

## Per-Script README (Context Recovery)

- Every script we develop MUST have its own README file, located in the script's dedicated folder: `scripts/<script-name>/README.md`.
- The README MUST contain summary-level information about the script: purpose (what problem it solves), inputs and outputs (file paths, formats), CLI parameters, an example run command (full path), key decisions and findings, and current status.
- The README MUST be kept up to date as the script evolves; it is updated together with the script, not after the fact.
- Rationale: chat context is finite — after a compaction (context limit reached), past details are lost. The per-script README is the durable recall point: to remember anything about a script's history, read its README first.

## Secrets and Sensitive Data

- NEVER commit or push API keys, tokens, passwords, credentials, or any real value belonging in `.env`. Only `.env.example` with EMPTY placeholder values may be committed.
- NEVER commit or push any Turkcell-related sensitive information: customer data, internal system details, internal credentials, or any non-synthetic platform content.
- Before EVERY commit, this check is MANDATORY: inspect `git status` and the staged diff (`git diff --staged`) and confirm nothing sensitive is included. If anything sensitive is found, it MUST be removed before the commit is made. A commit MUST NOT be created while this check is skipped.

## File Language

- CONVENTIONS.md and every agent-facing project document (including `memory.md`) MUST be written in **English only**. No Turkish content is allowed in these files. Proper names keep their official spelling.
- All agent-facing project documents MUST contain professional, project-related content only: facts, decisions, findings and engineering context. No informal conversation, no personal remarks.

## Git Branching Workflow

- NEVER commit directly to `main` during development.
- For every work item, open a branch FIRST, then commit to that branch.
- A big task (e.g. "TASK BIG") is split into stages; each stage gets its own branch (part 1 → branch, part 2 → branch, ...).
- Per-branch cycle: open branch → implement → run it → verify it works → the user says "this works" → ONLY THEN merge the branch into `main`.
- A branch is merged into `main` exclusively after explicit user confirmation. `main` must always stay in a verified, working state.

## Project Memory (memory.md)

- The project root MUST contain a `memory.md` file.
- The agent (ZCode) is AUTHORIZED and EXPECTED to autonomously append entries to `memory.md` whenever:
  - the user gives a command, decision, or preference, or
  - a critical development occurs (milestone, blocker, state change, important result).
- Entries MUST be dated and APPEND-only: never delete or rewrite older entries.
- Content scope: entries MUST be professional and strictly project-related — critical information, hints, findings, decisions, requirements, how and where a problem was solved, and current progress state, so that any future session can continue faster. Entries MUST NOT contain informal conversation, brainstorming chatter, personal opinions, or remarks about other teams or individuals.
- Anything recorded in `memory.md` is authoritative project context. The agent MUST read `memory.md` at session start, and MUST NOT claim to be unaware of, or to have forgotten, anything recorded there.
