# CONVENTIONS — achillies

**Purpose of this file:** Avoid losing hackathon-day time on design debates and guarantee that the code we write is robust. Every binding engineering decision is recorded here. During development, this file is applied as written; rules here are not re-negotiated mid-session.

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

## File Language

- CONVENTIONS.md and every agent-facing project document (including `memory.md`) MUST be written in **English only**. No Turkish content is allowed in these files. Proper names keep their official spelling.

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
- Anything recorded in `memory.md` is authoritative project context. The agent MUST read `memory.md` at session start, and MUST NOT claim to be unaware of, or to have forgotten, anything recorded there.
