# hypothesis_probe

Focused hypothesis probes spawned by the exploration profile findings.

## Purpose
Verifies/refutes the five-event structure suspected from the profile: infra-failure
timelines by service, network-alarm rack locality, blame-target slices (who is
being called-and-failing, per 10 minutes), billing-db / subscriber-db / batch
slow-burn timelines, and per-(service,type) burstiness ranking.

## Inputs / Outputs
- Input: `data/package/katilimci_paketi/alarms.csv` (+ deps/inventory unused here)
- Output: `scripts/hypothesis_probe/probe_report.md`, `probe_stats.json`, `run_debug.log`

## CLI
- `--data-dir`, `--out-dir`, `--slice-min` (default 10), `--debug`

## Example run (full path)
```
D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\scripts\hypothesis_probe\hypothesis_probe.py --debug
```

## Key findings (2026-09-16)
- Event 1 (rack network): 01:40–01:50 dc1/rack-A has 62 network alarms vs ≤5 in every other rack; blamed targets in 01:40 slice are exactly the rack-A-hosted services.
- Event 2 (billing-db): disk_full 17× (all sev5, 100%) 02:05–02:09 → db_write_fail cascades to billing-service (20) and invoice-batch (7); billing-service blamed 43× in 02:10–02:26.
- Event 3 (session leak): mem_high sustained from 01:30 → gc_pressure 02:11–02:34 → oom_risk 02:38–02:52; session blamed by timeouts 02:30–03:03. The "hard-to-catch" slow burn.
- Event 4 (payment-provider-gw): ext_slow/ext_unreach all target ppgw 02:40–02:43; ppgw blamed 79× 02:41–03:00; overlaps event 3 in time (wrong-merge trap).
- Event 5 (subscriber-db): db_conn_pool 19× from 03:00; batch_slow/batch_overlap 03:05+; subscriber-db latency/cpu spike 03:10–03:20.

## Status
VERIFIED (agent self-run with --debug, output saved). Hypotheses were then implemented as the generic core engine (`src/alarmstorm/`).
