# trap_audit report (INTERNAL - not for jury)

## Stage A - proxy validation (three independent signals)

1. Severity confinement: max sev5 ID = **1104** of 248 sev5 alarms, all below the split: True.
2. Span explosion: 60-ID window spans 13.6 min below vs 104.9 min above at the change-point plateau [1192, 1244].
3. Coherent tail inside the plateau -> boundary = **ID 1238** (trailing 10 IDs: single-service burst; the 20 IDs above it draw from 14 distinct services).

Boundary evidence (last event-band rows vs first noise-band rows):

| alarm | timestamp | service | type | sev |
|-------|-----------|---------|------|-----|
| ALM-01237 (EVENT) | 03:26:46 | subscriber-service | db_conn_pool | 4 |
| ALM-01238 (EVENT) | 03:27:01 | subscriber-service | db_conn_pool | 4 |
| ALM-01239 (NOISE) | 02:19:03 | payment-provider-gw | network_flap | 2 |

- Verdict: **PROXY_SUPPORTED** (split = ID 1238; event band 1-1238, noise band 1239-3000)

## Stage B - delivery scored against proxy

| card | root | alarms | event-band | noise-band | noise share |
|------|------|--------|------------|------------|-------------|
| EVT-01 | session-service | 234 | 185 | 49 | 20.9% |
| EVT-02 | dc1/rack-A | 459 | 433 | 26 | 5.7% |
| EVT-03 | billing-db | 276 | 255 | 21 | 7.6% |
| EVT-04 | payment-provider-gw | 168 | 165 | 3 | 1.8% |
| EVT-05 | subscriber-db | 164 | 126 | 38 | 23.2% |

- Noise band total: **1762**; attached into cards: **137**; eliminated: 1625 -> **noise recall 92.2%**, **precision 95.6%**.
- Real event-band alarms eliminated as noise: **74**
  - ALM-00135 dns-resolver http_5xx sev3 @ 2026-09-10T01:43:08 (below_anomaly_threshold)
  - ALM-00137 dns-resolver latency_high sev3 @ 2026-09-10T01:44:34 (below_anomaly_threshold)
  - ALM-00316 notification-service http_5xx sev3 @ 2026-09-10T01:45:46 (below_anomaly_threshold)
  - ALM-00328 order-service latency_high sev3 @ 2026-09-10T01:45:55 (below_anomaly_threshold)
  - ALM-00199 web-bff http_5xx sev3 @ 2026-09-10T01:46:59 (below_anomaly_threshold)
  - ALM-00427 charging-service latency_high sev3 @ 2026-09-10T01:47:27 (below_anomaly_threshold)
  - ALM-00156 report-batch latency_high sev3 @ 2026-09-10T01:47:32 (below_anomaly_threshold)
  - ALM-00319 notification-service latency_high sev3 @ 2026-09-10T01:47:58 (below_anomaly_threshold)
  - ALM-00208 web-bff latency_high sev3 @ 2026-09-10T01:48:20 (below_anomaly_threshold)
  - ALM-00397 reconciliation-batch http_5xx sev3 @ 2026-09-10T01:48:21 (below_anomaly_threshold)
  - ALM-00406 report-batch latency_high sev3 @ 2026-09-10T01:49:04 (below_anomaly_threshold)
  - ALM-00210 web-bff latency_high sev3 @ 2026-09-10T01:49:41 (below_anomaly_threshold)
  - ALM-00437 charging-service latency_high sev3 @ 2026-09-10T01:49:55 (below_anomaly_threshold)
  - ALM-00254 billing-service latency_high sev3 @ 2026-09-10T01:50:09 (below_anomaly_threshold)
  - ALM-00305 subscriber-service latency_high sev3 @ 2026-09-10T01:50:17 (below_anomaly_threshold)
  - ALM-00400 reconciliation-batch latency_high sev3 @ 2026-09-10T01:50:33 (below_anomaly_threshold)
  - ALM-00323 notification-service latency_high sev3 @ 2026-09-10T01:50:52 (below_anomaly_threshold)
  - ALM-00408 report-batch thread_pool sev3 @ 2026-09-10T01:50:52 (below_anomaly_threshold)
  - ALM-00212 web-bff thread_pool sev3 @ 2026-09-10T01:50:53 (below_anomaly_threshold)
  - ALM-00342 order-service http_5xx sev3 @ 2026-09-10T01:51:55 (below_anomaly_threshold)
  - ALM-00264 billing-service http_5xx sev3 @ 2026-09-10T01:52:07 (below_anomaly_threshold)
  - ALM-00315 subscriber-service latency_high sev3 @ 2026-09-10T01:52:16 (below_anomaly_threshold)
  - ALM-00393 subscriber-service latency_high sev3 @ 2026-09-10T01:52:34 (below_anomaly_threshold)
  - ALM-00325 notification-service latency_high sev3 @ 2026-09-10T01:52:50 (below_anomaly_threshold)
  - ALM-00343 order-service thread_pool sev3 @ 2026-09-10T01:53:11 (below_anomaly_threshold)
  - ALM-00423 charging-service thread_pool sev3 @ 2026-09-10T01:53:25 (below_anomaly_threshold)
  - ALM-00411 report-batch latency_high sev3 @ 2026-09-10T01:53:52 (below_anomaly_threshold)
  - ALM-00173 mobile-bff latency_high sev3 @ 2026-09-10T01:53:53 (below_anomaly_threshold)
  - ALM-00327 notification-service thread_pool sev3 @ 2026-09-10T01:54:11 (below_anomaly_threshold)
  - ALM-00457 order-service latency_high sev3 @ 2026-09-10T01:54:24 (below_anomaly_threshold)
  - ALM-00638 order-service latency_high sev3 @ 2026-09-10T02:12:43 (below_anomaly_threshold)
  - ALM-00632 payment-service txn_fail sev3 @ 2026-09-10T02:22:33 (below_anomaly_threshold)
  - ALM-00698 charging-service txn_fail sev3 @ 2026-09-10T02:23:18 (below_anomaly_threshold)
  - ALM-00718 charging-service txn_fail sev3 @ 2026-09-10T02:24:55 (below_anomaly_threshold)
  - ALM-00605 payment-service latency_high sev3 @ 2026-09-10T02:25:09 (below_anomaly_threshold)
  - ALM-00830 web-bff latency_high sev3 @ 2026-09-10T02:30:00 (below_anomaly_threshold)
  - ALM-00812 mobile-bff latency_high sev3 @ 2026-09-10T02:30:04 (below_anomaly_threshold)
  - ALM-00785 auth-service latency_high sev3 @ 2026-09-10T02:30:05 (below_anomaly_threshold)
  - ALM-00821 mobile-bff latency_high sev3 @ 2026-09-10T02:30:15 (below_anomaly_threshold)
  - ALM-00805 mobile-bff latency_high sev3 @ 2026-09-10T02:30:41 (below_anomaly_threshold)
  - ALM-00793 auth-service latency_high sev3 @ 2026-09-10T02:30:49 (below_anomaly_threshold)
  - ALM-00774 auth-service latency_high sev3 @ 2026-09-10T02:33:01 (below_anomaly_threshold)
  - ALM-00831 web-bff latency_high sev3 @ 2026-09-10T02:33:15 (below_anomaly_threshold)
  - ALM-00794 auth-service latency_high sev3 @ 2026-09-10T02:33:51 (below_anomaly_threshold)
  - ALM-00832 web-bff latency_high sev3 @ 2026-09-10T02:36:58 (below_anomaly_threshold)
  - ALM-00814 mobile-bff latency_high sev3 @ 2026-09-10T02:36:59 (below_anomaly_threshold)
  - ALM-00788 auth-service latency_high sev3 @ 2026-09-10T02:39:11 (below_anomaly_threshold)
  - ALM-00796 auth-service latency_high sev3 @ 2026-09-10T02:39:16 (below_anomaly_threshold)
  - ALM-00815 mobile-bff latency_high sev3 @ 2026-09-10T02:39:35 (below_anomaly_threshold)
  - ALM-00841 web-bff latency_high sev3 @ 2026-09-10T02:39:45 (below_anomaly_threshold)
  - ALM-00808 mobile-bff latency_high sev3 @ 2026-09-10T02:39:58 (below_anomaly_threshold)
  - ALM-00824 mobile-bff latency_high sev3 @ 2026-09-10T02:39:59 (below_anomaly_threshold)
  - ALM-00797 auth-service latency_high sev3 @ 2026-09-10T02:42:12 (below_anomaly_threshold)
  - ALM-00789 auth-service latency_high sev3 @ 2026-09-10T02:42:24 (below_anomaly_threshold)
  - ALM-00834 web-bff latency_high sev3 @ 2026-09-10T02:42:40 (below_anomaly_threshold)
  - ALM-00777 auth-service latency_high sev3 @ 2026-09-10T02:42:42 (below_anomaly_threshold)
  - ALM-00835 web-bff latency_high sev3 @ 2026-09-10T02:45:10 (below_anomaly_threshold)
  - ALM-00810 mobile-bff latency_high sev3 @ 2026-09-10T02:45:29 (below_anomaly_threshold)
  - ALM-00827 mobile-bff latency_high sev3 @ 2026-09-10T02:48:01 (below_anomaly_threshold)
  - ALM-00800 auth-service latency_high sev3 @ 2026-09-10T02:51:31 (below_anomaly_threshold)
  - ALM-00819 mobile-bff latency_high sev3 @ 2026-09-10T02:51:46 (below_anomaly_threshold)
  - ALM-00845 web-bff latency_high sev3 @ 2026-09-10T02:51:50 (below_anomaly_threshold)
  - ALM-00846 web-bff latency_high sev3 @ 2026-09-10T02:54:09 (below_anomaly_threshold)
  - ALM-00847 web-bff latency_high sev3 @ 2026-09-10T02:57:02 (below_anomaly_threshold)
  - ALM-00802 auth-service latency_high sev3 @ 2026-09-10T02:57:37 (below_anomaly_threshold)
  - ALM-00783 auth-service latency_high sev3 @ 2026-09-10T03:00:29 (below_anomaly_threshold)
  - ALM-00784 auth-service latency_high sev3 @ 2026-09-10T03:03:22 (below_anomaly_threshold)
  - ALM-00849 web-bff latency_high sev3 @ 2026-09-10T03:03:30 (below_anomaly_threshold)
  - ALM-01178 subscriber-db cpu_high sev3 @ 2026-09-10T03:11:10 (below_anomaly_threshold)
  - ALM-01132 report-batch cpu_high sev3 @ 2026-09-10T03:11:45 (below_anomaly_threshold)
  - ALM-01166 subscriber-db cpu_high sev3 @ 2026-09-10T03:16:42 (below_anomaly_threshold)
  - ALM-01122 reconciliation-batch cpu_high sev3 @ 2026-09-10T03:19:18 (below_anomaly_threshold)
  - ALM-01169 subscriber-db latency_high sev3 @ 2026-09-10T03:20:39 (below_anomaly_threshold)
  - ALM-01171 subscriber-db latency_high sev3 @ 2026-09-10T03:22:23 (below_anomaly_threshold)
- sev5 alarms NOT in any card: none

## EVT-05 root-direction evidence

- Window 2026-09-10 03:04:41 - 2026-09-10 03:30:19.
- subscriber-db first alarm in window: 03:04:43; by type: {"db_conn_pool": {"n": 19, "first": "03:09:19", "last": "03:27:14"}, "latency_high": {"n": 13, "first": "03:10:22", "last": "03:22:23"}, "cpu_high": {"n": 17, "first": "03:06:10", "last": "03:28:28"}, "disk_warn": {"n": 6, "first": "03:04:43", "last": "03:29:19"}}
- batch-scheduler first alarm in window: 03:05:28; by type: {"batch_overlap": {"n": 4, "first": "03:05:28", "last": "03:06:50"}}
- Alarms blaming subscriber-db from other services: 0 {}
