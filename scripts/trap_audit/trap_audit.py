#!/usr/bin/env python3
"""trap_audit - internal ground-truth proxy audit (NOT part of jury delivery).

Hypothesis under test (the "planted trap" check): alarm_id preserves the
generator's emission order. If true, IDs form contiguous bands:
  - an EVENT band: a handful of time-coherent blocks that correspond to the
    real incidents, occupying IDs up to some split point
  - a NOISE band: uniformly spread background alarms above the split

This script never feeds alarm_id into any pipeline decision; it only audits.
Stage A validates the proxy mechanically (severity confinement, per-minute
rate uniformity, block coherence). Stage B scores the delivered out/
artifacts against the proxy: noise absorbed into cards, real alarms
eliminated as noise, sev5 coverage, card<->block correspondence, and the
EVT-05 root-direction evidence (subscriber-db pool vs batch-scheduler).
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def parse_ts(s: str) -> datetime:
    return datetime.fromisoformat(s.strip())


def load_alarms(data_dir: Path) -> list[dict]:
    path = data_dir / "alarms.csv"
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["id_num"] = int(r["alarm_id"].split("-")[1])
        r["ts"] = parse_ts(r["timestamp"])
        r["severity"] = int(r["severity"])
    rows.sort(key=lambda r: r["id_num"])
    return rows


# ---------------------------------------------------------------- stage A

def validate_proxy(alarms: list[dict], scan_lo: int, scan_hi: int) -> dict:
    """Mechanically test the event/noise band split on the ID axis.

    Discriminating signals (three independent, must agree):
      1. severity confinement: all sev5 alarms live below the split;
      2. span explosion: a 60-ID window below the split spans minutes
         (time-coherent blocks), above it ~the whole 2-hour window (uniform
         scatter). The change point lands somewhere on a plateau;
      3. coherent tail: inside the plateau, the event band ends with a burst
         tail (>=10 consecutive IDs from <=2 services within a quarter hour)
         while noise windows are service- and time-scattered. The boundary is
         the largest plateau ID whose trailing 10 IDs still form such a tail.
    """
    sev5 = [r for r in alarms if r["severity"] == 5]
    max_sev5_id = max(r["id_num"] for r in sev5)

    ids = [r["id_num"] for r in alarms]
    ts = [r["ts"].timestamp() for r in alarms]
    svc = [r["service"] for r in alarms]
    W = 60  # change-point comparison window (IDs)

    def span_min(lo: int, hi: int) -> float:
        xs = sorted(ts[lo:hi])
        n = len(xs)
        return (xs[int(0.9 * (n - 1))] - xs[int(0.1 * (n - 1))]) / 60.0

    scan = []
    idx_of = {v: i for i, v in enumerate(ids)}
    for split in range(scan_lo, scan_hi + 1):
        c = idx_of.get(split)
        if c is None or c - W < 0 or c + W > len(alarms):
            continue
        left = span_min(c - W, c)
        right = span_min(c, c + W)
        scan.append(dict(split=split, left_span_min=round(left, 1),
                         right_span_min=round(right, 1),
                         score=round(right - left, 1)))
    scan.sort(key=lambda s: -s["score"])
    best = scan[0]

    plateau = [s["split"] for s in scan if s["score"] >= 0.85 * best["score"]]
    plateau_lo, plateau_hi = min(plateau), max(plateau)

    def coherent_tail(c: int, k: int = 10) -> bool:
        i = idx_of[c]
        if i - k + 1 < 0:
            return False
        win = range(i - k + 1, i + 1)
        share = Counter(svc[j] for j in win).most_common(1)[0][1] / k
        span_min = (max(ts[j] for j in win) - min(ts[j] for j in win)) / 60.0
        return share >= 0.7 and span_min <= 15

    tails = [c for c in range(plateau_lo, plateau_hi + 1)
             if c in idx_of and coherent_tail(c)]
    boundary = max(tails) if tails else None
    split = boundary if boundary is not None else best["split"]
    sev_confined = max_sev5_id <= split

    def uniq_ahead(split_id: int, k: int = 20) -> int:
        i = idx_of[split_id]
        return len({svc[j] for j in range(i + 1, min(len(alarms), i + 1 + k))})

    near = [s for s in scan if abs(s["split"] - best["split"]) <= 10]
    stable = len(near) >= 8 and all(s["score"] > 0.5 * best["score"] for s in near)

    return dict(
        max_sev5_id=max_sev5_id,
        sev5_total=len(sev5),
        sev_confined=sev_confined,
        best_split=best,
        plateau=[plateau_lo, plateau_hi],
        split=split,
        split_stable=stable,
        uniq_services_after_boundary=uniq_ahead(split),
        boundary_rows=[
            dict(alarm_id=f"ALM-{r['id_num']:05d}", ts=r["timestamp"],
                 service=r["service"], alarm_type=r["alarm_type"], severity=r["severity"])
            for r in alarms if split - 1 <= r["id_num"] <= split + 1
        ],
        scan_top=scan[:8],
        verdict="PROXY_SUPPORTED" if sev_confined and stable and boundary is not None
        and plateau_hi - plateau_lo < 60
        else "PROXY_WEAK",
    )


# ---------------------------------------------------------------- stage B

def score_delivery(alarms: list[dict], split: int, out_dir: Path) -> dict:
    events = json.loads((out_dir / "events_full.json").read_text(encoding="utf-8"))
    audit = json.loads((out_dir / "noise_audit.json").read_text(encoding="utf-8"))

    def band(i: str) -> str:
        return "event" if int(i.split("-")[1]) <= split else "noise"

    cards = []
    for ev in events:
        ids = ev["alarm_ids"]
        nb = sum(1 for i in ids if band(i) == "noise")
        cards.append(dict(id=ev["id"], root=ev["root"]["name"], alarms=len(ids),
                          event_band=len(ids) - nb, noise_band=nb,
                          noise_share=round(nb / len(ids), 3)))

    noise_ids = [a["alarm_id"] for a in audit["alarms"]]
    correct = [i for i in noise_ids if band(i) == "noise"]
    wrong = [i for i in noise_ids if band(i) == "event"]
    wrong_rows = {r["alarm_id"]: r for r in alarms}
    wrong_detail = [
        dict(alarm_id=i, service=wrong_rows[i]["service"],
             alarm_type=wrong_rows[i]["alarm_type"], severity=wrong_rows[i]["severity"],
             timestamp=wrong_rows[i]["timestamp"],
             noise_reason=next(a["noise_reason"] for a in audit["alarms"]
                               if a["alarm_id"] == i))
        for i in wrong
    ]
    noise_total = sum(1 for r in alarms if r["id_num"] > split)
    attached = [i for ev in events for i in ev["alarm_ids"]]
    attached_noise = sum(1 for i in attached if band(i) == "noise")
    sev5_ids = {r["alarm_id"] for r in alarms if r["severity"] == 5}
    sev5_lost = sorted(sev5_ids - set(attached))

    return dict(
        split=split,
        cards=cards,
        totals=dict(
            noise_band_total=noise_total,
            attached=len(attached),
            attached_noise_band=attached_noise,
            eliminated=len(noise_ids),
            eliminated_true_noise=len(correct),
            eliminated_real_events=len(wrong),
            noise_recall=round(len(correct) / noise_total, 3),
            noise_precision=round(len(correct) / len(noise_ids), 3),
        ),
        real_alarms_eliminated=wrong_detail,
        sev5_not_in_cards=sev5_lost,
    )


# ------------------------------------------------------- EVT-05 direction

def evt05_direction(alarms: list[dict], out_dir: Path) -> dict:
    events = json.loads((out_dir / "events_full.json").read_text(encoding="utf-8"))
    evt05 = next(e for e in events if e["id"] == "EVT-05")
    lo, hi = parse_ts(evt05["start"]), parse_ts(evt05["end"])

    def first_last(service: str, atype: str | None = None):
        rows = [r for r in alarms if r["service"] == service and lo <= r["ts"] <= hi
                and (atype is None or r["alarm_type"] == atype)]
        if not rows:
            return None
        return dict(n=len(rows), first=min(r["ts"] for r in rows).strftime("%H:%M:%S"),
                    last=max(r["ts"] for r in rows).strftime("%H:%M:%S"))

    sub = {t: first_last("subscriber-db", t) for t in
           ("db_conn_pool", "latency_high", "cpu_high", "disk_warn", "db_write_fail")}
    batch = {t: first_last("batch-scheduler", t) for t in
             ("batch_overlap", "batch_slow")}
    sub_all = first_last("subscriber-db")
    batch_all = first_last("batch-scheduler")

    # who blames subscriber-db in the window (message text)?
    blame_sub = [r for r in alarms if lo <= r["ts"] <= hi
                 and "subscriber-db" in r["message"] and r["service"] != "subscriber-db"]
    blame_by_svc = Counter(r["service"] for r in blame_sub)

    return dict(window=[evt05["start"], evt05["end"]],
                subscriber_db_by_type={k: v for k, v in sub.items() if v},
                batch_scheduler_by_type={k: v for k, v in batch.items() if v},
                subscriber_db_first=(sub_all or {}).get("first"),
                batch_first=(batch_all or {}).get("first"),
                blame_subscriber_db_from=dict(blame_by_svc.most_common(6)),
                blame_subscriber_db_total=len(blame_sub))


# ---------------------------------------------------------------- report

def write_report(res: dict, audit_dir: Path) -> None:
    (audit_dir / "audit_stats.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    v, d, e5 = res["proxy"], res["delivery"], res["evt05"]
    L = []
    L.append("# trap_audit report (INTERNAL - not for jury)")
    L.append("")
    L.append("## Stage A - proxy validation (three independent signals)")
    L.append("")
    L.append(f"1. Severity confinement: max sev5 ID = **{v['max_sev5_id']}** of "
             f"{v['sev5_total']} sev5 alarms, all below the split: {v['sev_confined']}.")
    L.append(f"2. Span explosion: 60-ID window spans {v['best_split']['left_span_min']} min "
             f"below vs {v['best_split']['right_span_min']} min above at the change-point "
             f"plateau [{v['plateau'][0]}, {v['plateau'][1]}].")
    L.append(f"3. Coherent tail inside the plateau -> boundary = **ID {v['split']}** "
             f"(trailing 10 IDs: single-service burst; the 20 IDs above it draw from "
             f"{v['uniq_services_after_boundary']} distinct services).")
    L.append("")
    L.append("Boundary evidence (last event-band rows vs first noise-band rows):")
    L.append("")
    L.append("| alarm | timestamp | service | type | sev |")
    L.append("|-------|-----------|---------|------|-----|")
    for r in v["boundary_rows"]:
        band = "EVENT" if int(r["alarm_id"].split("-")[1]) <= v["split"] else "NOISE"
        L.append(f"| {r['alarm_id']} ({band}) | {r['ts'][11:]} | {r['service']} | "
                 f"{r['alarm_type']} | {r['severity']} |")
    L.append("")
    L.append(f"- Verdict: **{v['verdict']}** (split = ID {v['split']}; "
             f"event band 1-{v['split']}, noise band {v['split'] + 1}-3000)")
    L.append("")
    L.append("## Stage B - delivery scored against proxy")
    L.append("")
    L.append("| card | root | alarms | event-band | noise-band | noise share |")
    L.append("|------|------|--------|------------|------------|-------------|")
    for c in d["cards"]:
        L.append(f"| {c['id']} | {c['root']} | {c['alarms']} | {c['event_band']} | "
                 f"{c['noise_band']} | {c['noise_share']:.1%} |")
    t = d["totals"]
    L.append("")
    L.append(f"- Noise band total: **{t['noise_band_total']}**; attached into cards: "
             f"**{t['attached_noise_band']}**; eliminated: {t['eliminated_true_noise']} "
             f"-> **noise recall {t['noise_recall']:.1%}**, "
             f"**precision {t['noise_precision']:.1%}**.")
    L.append(f"- Real event-band alarms eliminated as noise: **{t['eliminated_real_events']}**")
    for w in d["real_alarms_eliminated"]:
        L.append(f"  - {w['alarm_id']} {w['service']} {w['alarm_type']} "
                 f"sev{w['severity']} @ {w['timestamp']} ({w['noise_reason']})")
    L.append(f"- sev5 alarms NOT in any card: {d['sev5_not_in_cards'] or 'none'}")
    L.append("")
    L.append("## EVT-05 root-direction evidence")
    L.append("")
    L.append(f"- Window {e5['window'][0]} - {e5['window'][1]}.")
    L.append(f"- subscriber-db first alarm in window: {e5['subscriber_db_first']}; "
             f"by type: {json.dumps(e5['subscriber_db_by_type'])}")
    L.append(f"- batch-scheduler first alarm in window: {e5['batch_first']}; "
             f"by type: {json.dumps(e5['batch_scheduler_by_type'])}")
    L.append(f"- Alarms blaming subscriber-db from other services: "
             f"{e5['blame_subscriber_db_total']} {dict(e5['blame_subscriber_db_from'])}")
    (audit_dir / "audit_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", default=str(ROOT / "data/package/katilimci_paketi"))
    ap.add_argument("--out-dir", default=str(ROOT / "out"))
    ap.add_argument("--scan-lo", type=int, default=1150)
    ap.add_argument("--scan-hi", type=int, default=1350)
    args = ap.parse_args()

    data_dir, out_dir = Path(args.data_dir), Path(args.out_dir)
    alarms = load_alarms(data_dir)
    proxy = validate_proxy(alarms, args.scan_lo, args.scan_hi)
    split = proxy["split"]
    res = dict(proxy=proxy, delivery=score_delivery(alarms, split, out_dir),
               evt05=evt05_direction(alarms, out_dir))
    audit_dir = Path(__file__).resolve().parent
    write_report(res, audit_dir)
    print(f"verdict={proxy['verdict']} split={split} "
          f"plateau={proxy['plateau']} sev_confined={proxy['sev_confined']}")
    print(f"noise recall={res['delivery']['totals']['noise_recall']} "
          f"precision={res['delivery']['totals']['noise_precision']}")
    print(f"real eliminated={res['delivery']['totals']['eliminated_real_events']} "
          f"sev5 lost={res['delivery']['sev5_not_in_cards']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
