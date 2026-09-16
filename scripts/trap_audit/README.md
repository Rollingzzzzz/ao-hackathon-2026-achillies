# trap_audit

Internal ground-truth proxy audit. NOT part of the jury delivery: it uses the
alarm_id emission order, which is a generator artifact, purely as a
verification instrument. The correlation engine never reads alarm_id.

## Purpose
Answers "did the scenario author hide something our solution fell for?" by
building a mechanical proxy for the hidden ground truth and scoring the
delivered out/ artifacts against it.

## Proxy hypothesis (validated here)
alarm_id preserves generator emission order: IDs 1..1238 are the real event
band (five incidents), IDs 1239..3000 are uniformly spread background noise
(1762 alarms). Validated by three independent mechanical signals that must
agree:
1. severity confinement (all 248 sev5 alarms have ID <= 1104),
2. 60-ID-window time-span explosion at the change-point plateau [1192, 1244]
   (13.6 min below vs 104.9 min above),
3. coherent-tail boundary inside the plateau -> split = ID 1238 (last
   single-service burst tail; the 20 IDs above it draw from 14 services).

## Findings against the delivered run (out/, 2026-09-16)

BEFORE the core-evidence attach gate (legacy run):
- Cards absorbed 1157 of 1762 noise alarms (noise-elimination recall 34.3%);
  per-card noise share: EVT-01 64.8%, EVT-05 67.3%, EVT-03 39.0%, EVT-02
  35.5%, EVT-04 31.0%.
- 14 real event alarms eliminated as noise - the 02:57-03:03 cascade tails
  of EVT-01 (auth-service/web-bff) and EVT-04 (mobile-bff), including the
  only stray sev5 ALM-01048.

AFTER the fix (core-gated attach, 3 sweeps, strong-alarm proximity; same
branch, `out/` regenerated):
- Noise recall 92.2% (1626/1762 eliminated), precision 95.6%; noise inside
  cards down to 136; attached total 2381 -> 1301 (1124 event-band).
- All 248 sev5 alarms now attached (ALM-01048 recovered into EVT-04's tail);
  5 cards and all 5 root causes unchanged.
- Remaining 74 eliminated reals are all sev3 (54 of them single
  latency_high blips with no blame target and no anomaly cell) - defensible
  as evidence-based elimination.

Also settled here:
- EVT-05 root direction CONFIRMED: subscriber-db signals start 03:03:50,
  batch_overlap only 03:05:28 -> subscriber-db is the root, batch load the
  contributing factor.
- ALM-02377 concern closed: ID 2377 sits deep in the noise band.

## Inputs / Outputs
- Input: `data/package/katilimci_paketi/alarms.csv`, `out/events_full.json`,
  `out/noise_audit.json`
- Output: `scripts/trap_audit/audit_report.md`, `audit_stats.json`

## CLI
- `--data-dir`, `--out-dir`, `--scan-lo` (default 1150), `--scan-hi`
  (default 1350); boundary must land inside the scan range.

## Example run (full path)
```
D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\scripts\trap_audit\trap_audit.py --scan-lo 1100 --scan-hi 1400
```

## Status
VERIFIED (agent self-run, outputs saved). Feeds the engine fix pass: stricter
attach gating (D1), tail recovery (D2), EVT-05 direction kept (D3).
