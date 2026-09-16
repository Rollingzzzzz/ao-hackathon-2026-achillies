#!/usr/bin/env python3
"""Hypothesis probes for S-A1: timing and blame-target cross-tabs.

Answers focused questions raised by the first profile:
- disk_full / db_write_fail: which service, when?
- gc_pressure / oom_risk: which service, when?
- network_down / network_flap / pkt_loss: which dc/rack, when?
- timeout / conn_refused / ext_*: blamed target service parsed from message, when?
- subscriber-db + batch types timeline; session-service early window.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

DEFAULT_DATA_DIR = Path(r"D:\projeler\ao-hackathon-2026-achillies\data\package\katilimci_paketi")

TIMEOUT_RE = re.compile(r"(\S+) servisine yapilan cagri zaman asimina ugradi")
CONNREF_RE = re.compile(r"(\S+) baglantisi reddedildi")
EXT_RE = re.compile(r"Dis servis (\S+)")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="S-A1 hypothesis probes")
    p.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    p.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
    p.add_argument("--slice-min", type=int, default=10, help="time slice length in minutes")
    p.add_argument("--debug", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    t0 = time.time()
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    def dbg(m: str) -> None:
        if args.debug:
            print(f"[debug {time.time() - t0:5.1f}s] {m}", flush=True)

    df = pd.read_csv(args.data_dir / "alarms.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["minute"] = df["timestamp"].dt.strftime("%H:%M")
    df["slice"] = df["timestamp"].dt.floor(f"{args.slice_min}min").dt.strftime("%H:%M")

    R: list[str] = ["# S-A1 Hypothesis Probes", f"_generated {datetime.now().isoformat(timespec='seconds')}_"]
    stats: dict = {}

    def h(title: str) -> None:
        R.append(f"\n## {title}\n")

    def rows_table(header, rows) -> None:
        R.append("| " + " | ".join(header) + " |")
        R.append("|" + "---|" * len(header))
        for r in rows:
            R.append("| " + " | ".join(str(x) for x in r) + " |")

    # ---------- probe 1: infra failure types by service and time ----------
    h("Infra failure types (disk_full, db_write_fail, gc_pressure, oom_risk, conn_refused, network_down, pkt_loss, ext_*) by service x time")
    infra_types = ["disk_full", "db_write_fail", "gc_pressure", "oom_risk", "network_down", "pkt_loss", "ext_slow", "ext_unreach", "batch_overlap"]
    sel = df[df["alarm_type"].isin(infra_types)]
    rows = []
    for (svc, atype), g in sel.groupby(["service", "alarm_type"]):
        rows.append((svc, atype, len(g), g["minute"].min(), g["minute"].max(), ", ".join(g["minute"].head(12))))
    rows.sort(key=lambda r: (r[1], -r[2]))
    rows_table(("service", "type", "n", "first", "last", "first 12 minutes"), rows)
    stats["infra_by_service"] = [list(r) for r in rows]
    dbg("infra types done")

    # ---------- probe 2: network alarms by dc/rack over time ----------
    h("Network alarms (network_down, network_flap, pkt_loss) by dc/rack x 5min (only cells with n>=3)")
    net = df[df["alarm_type"].isin(["network_down", "network_flap", "pkt_loss"])].copy()
    net["5min"] = net["timestamp"].dt.floor("300s").dt.strftime("%H:%M")
    cells = net.groupby(["5min", "veri_merkezi", "kabin", "alarm_type"]).size().reset_index(name="n")
    cells = cells[cells["n"] >= 3].sort_values(["5min", "n"], ascending=[True, False])
    rows_table(("5min", "dc", "rack", "type", "n"), [(r["5min"], r["veri_merkezi"], r["kabin"], r["alarm_type"], int(r["n"])) for _, r in cells.iterrows()])
    stats["net_rack_cells"] = [[r["5min"], r["veri_merkezi"], r["kabin"], r["alarm_type"], int(r["n"])] for _, r in cells.iterrows()]
    # per rack totals for network alarms
    h("Network alarms total per (dc, rack)")
    rows_table(("dc", "rack", "n"), [(f"{dc}|{rk}", "", int(n)) for (dc, rk), n in net.groupby(["veri_merkezi", "kabin"]).size().items()])
    # network alarms per rack within burst window vs outside
    h("Network alarms per (dc,rack): 01:40-01:55 vs rest")
    m = (net["timestamp"].dt.strftime("%H:%M") >= "01:40") & (net["timestamp"].dt.strftime("%H:%M") <= "01:55")
    rows = []
    for (dc, rk), g in net.groupby(["veri_merkezi", "kabin"]):
        rows.append((f"{dc}/{rk}", int((g[m]).shape[0]), int((g[~m]).shape[0])))
    rows_table(("dc/rack", "01:40-01:55", "rest"), rows)
    stats["net_rack_split"] = [list(r) for r in rows]
    dbg("network locality done")

    # ---------- probe 3: blame targets parsed from messages ----------
    h("Blame targets: timeout / conn_refused / ext_* messages name a target service")

    def blame(row):
        msg = row["message"]
        at = row["alarm_type"]
        if at == "timeout":
            mm = TIMEOUT_RE.search(msg)
            if mm:
                return mm.group(1)
        if at == "conn_refused":
            mm = CONNREF_RE.search(msg)
            if mm:
                return mm.group(1)
        if at in ("ext_slow", "ext_unreach"):
            mm = EXT_RE.search(msg)
            if mm:
                return mm.group(1)
        return None

    df["blame"] = df.apply(blame, axis=1)
    bl = df[df["blame"].notna()]
    rows = []
    for (bt, at), g in bl.groupby(["blame", "alarm_type"]):
        rows.append((bt, at, len(g), g["minute"].min(), g["minute"].max()))
    rows.sort(key=lambda r: -r[2])
    rows_table(("blamed target", "alarm_type", "n", "first", "last"), rows)
    stats["blame_totals"] = [list(r) for r in rows]

    h("Blame totals per 10-min slice (top 3 targets per slice)")
    rows = []
    for sl, g in bl.groupby("slice"):
        top = Counter(g["blame"]).most_common(3)
        rows.append((sl, len(g), ", ".join(f"{k}({v})" for k, v in top)))
    rows_table(("slice", "blame alarms", "top targets"), rows)
    stats["blame_by_slice"] = [list(r) for r in rows]
    dbg("blame parsing done")

    # ---------- probe 4: slow-burn timelines ----------
    h("billing-db and billing-service/invoice-batch infra timeline (disk_full, disk_warn, db_write_fail, db_conn_pool)")
    bsel = df[(df["service"].isin(["billing-db", "billing-service", "invoice-batch"])) & (df["alarm_type"].isin(["disk_full", "disk_warn", "db_write_fail", "db_conn_pool"]))]
    rows = []
    for (svc, at), g in bsel.groupby(["service", "alarm_type"]):
        per10 = Counter(g["slice"])
        rows.append((svc, at, len(g), g["minute"].min(), g["minute"].max(), dict(sorted(per10.items()))))
    rows_table(("service", "type", "n", "first", "last", "per-10min"), rows)
    stats["billing_timeline"] = [list(r) for r in rows]

    h("subscriber-db / batch services timeline (subscriber-db, batch-scheduler, reconciliation-batch, report-batch; all types)")
    ssel = df[df["service"].isin(["subscriber-db", "batch-scheduler", "reconciliation-batch", "report-batch"])]
    rows = []
    for (svc, at), g in ssel.groupby(["service", "alarm_type"]):
        per10 = Counter(g["slice"])
        rows.append((svc, at, len(g), dict(sorted(per10.items()))))
    rows.sort(key=lambda r: (r[0], -r[2]))
    rows_table(("service", "type", "n", "per-10min"), rows)
    stats["subscriber_timeline"] = [list(r) for r in rows]

    h("session-service early window (01:30-01:45) types")
    esel = df[(df["service"] == "session-service") & (df["timestamp"].dt.strftime("%H:%M") <= "01:45")]
    rows_table(("type", "n", "first", "last"), [(at, len(g), g["minute"].min(), g["minute"].max()) for at, g in esel.groupby("alarm_type")])
    stats["session_early"] = [[at, len(g)] for at, g in esel.groupby("alarm_type")]
    dbg("slow-burn timelines done")

    # ---------- probe 5: severity-5 alarms timeline ----------
    h("Severity-5 alarms per 10-min slice x top services")
    s5 = df[df["severity"] == 5]
    rows = []
    for sl, g in s5.groupby("slice"):
        top = Counter(g["service"]).most_common(3)
        rows.append((sl, len(g), ", ".join(f"{k}({v})" for k, v in top)))
    rows_table(("slice", "sev5 n", "top services"), rows)
    stats["sev5_by_slice"] = [list(r) for r in rows]

    # ---------- probe 6: per-service-per-type baseline burstiness ----------
    h("Most anomalous (service, type) cells: max per-minute count vs overall per-minute mean")
    rows = []
    df["min"] = df["timestamp"].dt.floor("60s")
    for (svc, at), g in df.groupby(["service", "alarm_type"]):
        pm = g.groupby("min").size()
        if len(g) < 5:
            continue
        ratio = pm.max() / (len(g) / 120.0)  # mean per active minute approx window 120 min
        rows.append((svc, at, len(g), int(pm.max()), pm.idxmax().strftime("%H:%M"), round(ratio, 1)))
    rows.sort(key=lambda r: -r[3])
    rows_table(("service", "type", "n", "max/min", "peak", "peak/mean"), rows[:40])
    stats["burstiest_cells"] = [list(r) for r in rows[:40]]
    dbg("burstiness done")

    # ---------- write ----------
    rp, sp = out_dir / "probe_report.md", out_dir / "probe_stats.json"
    tmp = rp.with_suffix(".tmp"); tmp.write_text("\n".join(R), encoding="utf-8"); tmp.replace(rp)
    tmp = sp.with_suffix(".tmp"); tmp.write_text(json.dumps(stats, ensure_ascii=False, indent=2, default=str), encoding="utf-8"); tmp.replace(sp)
    print(f"OK: {rp} elapsed={time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
