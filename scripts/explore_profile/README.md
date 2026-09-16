# explore_profile

Broad one-pass exploration profiler for the S-A1 alarm data package.

## Purpose
Answers "what does this dataset look like in total?" before any scenario-specific
logic: distributions, per-minute time histogram, burst candidates, message
templates, dependency-graph summary, host-inventory cross-checks, rack/dc locality.

## Inputs / Outputs
- Input: `data/package/katilimci_paketi/alarms.csv`, `service_dependencies.csv`, `host_inventory.csv` (gitignored data dir)
- Output: `scripts/explore_profile/profile_report.md` (human-readable), `profile_stats.json` (machine), `run_debug.log`

## CLI
- `--data-dir` (default: the extracted package path), `--out-dir`, `--bucket-seconds` (default 60), `--top-bursts`, `--sample-messages`, `--debug`

## Example run (full path)
```
D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\scripts\explore_profile\explore_profile.py --debug
```

## Key findings (2026-09-16)
- 3,000 alarms, 25 types, 27 services, 56 hosts, window 01:30–03:30; no nulls/dupes; tags consistent with inventory.
- One dominant burst 01:42–01:54 (peak 79/min) localized to dc1/rack-A (132 alarms in one 5-min bucket); secondary wave 02:41–02:55 around payment-provider-gw.
- Slow-burn signals: billing-db `disk_full` cluster 02:05–02:09, session-service `mem_high` sustained from window start, subscriber-db late-window `db_conn_pool` rise.
- `timeout`/`conn_refused`/`ext_*` messages NAME their failing target — free causal edges (blame parsing).
- Noise pool candidates (low severity, time-uniform): cert_expiry, log_rotate, ntp_drift, backup_warn, disk_warn.

## Status
VERIFIED (agent self-run with --debug, output saved). Superseded for analysis by the core engine; kept as exploration evidence.
