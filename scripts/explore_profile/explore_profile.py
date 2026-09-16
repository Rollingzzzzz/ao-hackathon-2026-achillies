#!/usr/bin/env python3
"""Exploration profiler for the S-A1 alarm dataset.

Reads the full data package (alarms.csv, service_dependencies.csv,
host_inventory.csv) and produces a broad one-pass profile:
distributions, time histogram, burst candidates, message templates,
dependency-graph summary. Output goes to this script's folder.

File in, file out; every tunable is a CLI argument; --debug prints
progress and intermediate stats to console.
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="S-A1 alarm dataset exploration profiler")
    p.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Directory containing the data package files")
    p.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent, help="Output directory")
    p.add_argument("--bucket-seconds", type=int, default=60, help="Time-bucket size for histograms (seconds)")
    p.add_argument("--top-bursts", type=int, default=25, help="How many top burst buckets to list")
    p.add_argument("--sample-messages", type=int, default=3, help="Sample messages per alarm type")
    p.add_argument("--debug", action="store_true", help="Verbose console output")
    return p.parse_args()


def normalize_message(msg: str) -> str:
    """Collapse variable tokens (numbers, hosts, durations) into placeholders."""
    s = str(msg)
    s = re.sub(r"\b\d[\d.,:]*\b", "<N>", s)
    s = re.sub(r"\bao-\d+-[a-z0-9-]+\b", "<HOST>", s)
    s = re.sub(r"\b\d+(?:\.\d+){3}\b", "<IP>", s)
    return s


def main() -> int:
    args = parse_args()
    t0 = time.time()
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    def dbg(msg: str) -> None:
        if args.debug:
            print(f"[debug {time.time() - t0:6.1f}s] {msg}", flush=True)

    # ---------- load ----------
    alarms_path = args.data_dir / "alarms.csv"
    deps_path = args.data_dir / "service_dependencies.csv"
    inv_path = args.data_dir / "host_inventory.csv"
    for p in (alarms_path, deps_path, inv_path):
        if not p.exists():
            print(f"ERROR: missing input {p}", file=sys.stderr)
            return 2

    df = pd.read_csv(alarms_path)
    deps = pd.read_csv(deps_path)
    inv = pd.read_csv(inv_path)
    dbg(f"loaded alarms={len(df)} deps={len(deps)} inventory={len(inv)}")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    report: list[str] = []
    stats: dict = {}

    def section(title: str) -> None:
        report.append(f"\n## {title}\n")

    def table(rows: list[tuple], header: tuple) -> None:
        report.append("| " + " | ".join(header) + " |")
        report.append("|" + "---|" * len(header))
        for r in rows:
            report.append("| " + " | ".join(str(x) for x in r) + " |")

    report.append("# S-A1 Exploration Profile")
    report.append(f"_generated {datetime.now().isoformat(timespec='seconds')} · bucket={args.bucket_seconds}s · alarms={len(df)}_")

    # ---------- basic sanity ----------
    section("Basic counts")
    rows = [
        ("alarm rows", len(df)),
        ("columns", list(df.columns)),
        ("null cells per column", {c: int(df[c].isna().sum()) for c in df.columns}),
        ("duplicate full rows", int(df.duplicated().sum())),
        ("unique alarm_id", int(df["alarm_id"].nunique())),
        ("time span", f'{df["timestamp"].min()} .. {df["timestamp"].max()}'),
    ]
    for k, v in rows:
        report.append(f"- **{k}**: {v}")
    stats["basic"] = {k: str(v) for k, v in rows}
    dbg("basic sanity done")

    # ---------- distributions ----------
    section("Distributions")
    for col in ("alarm_type", "severity", "source_system", "service", "host", "veri_merkezi", "kabin", "ortam"):
        if col not in df.columns:
            continue
        vc = df[col].value_counts()
        report.append(f"\n### {col} ({vc.size} distinct)\n")
        table([(k, int(v)) for k, v in vc.items()], (col, "count"))
        stats[f"dist_{col}"] = {str(k): int(v) for k, v in vc.items()}
    dbg("distributions done")

    # ---------- time histogram ----------
    section("Time histogram")
    bucket = df["timestamp"].dt.floor(f"{args.bucket_seconds}s")
    bc = bucket.value_counts().sort_index()
    mean_rate = float(bc.mean())
    report.append(f"- bucket mean={mean_rate:.1f}, median={bc.median():.0f}, max={bc.max()} at {bc.idxmax()}, min={bc.min()}")
    # ASCII sparkline
    mx = int(bc.max())
    lines = []
    for ts, c in bc.items():
        bar = "#" * max(1, int(round(60 * c / mx)))
        lines.append(f"{ts.strftime('%H:%M:%S')} {int(c):4d} {bar}")
    report.append("```\n" + "\n".join(lines) + "\n```")
    stats["time_histogram"] = {ts.isoformat(): int(c) for ts, c in bc.items()}

    section(f"Top {args.top_bursts} burst buckets")
    top = bc.sort_values(ascending=False).head(args.top_bursts)
    # what is inside each burst bucket
    burst_rows = []
    for ts, c in top.items():
        sel = df[bucket == ts]
        services = sel["service"].value_counts().head(4)
        types = sel["alarm_type"].value_counts().head(4)
        burst_rows.append((
            ts.strftime("%H:%M:%S"), int(c),
            ", ".join(f"{k}({v})" for k, v in services.items()),
            ", ".join(f"{k}({v})" for k, v in types.items()),
        ))
    table(burst_rows, ("bucket", "count", "top services", "top types"))
    stats["top_bursts"] = [{"ts": r[0], "count": r[1], "services": r[2], "types": r[3]} for r in burst_rows]
    dbg("time histogram done")

    # ---------- per-service burstiness ----------
    section("Per-service burst profile")
    svc_rows = []
    for svc, g in df.groupby("service"):
        b = g["timestamp"].dt.floor(f"{args.bucket_seconds}s").value_counts()
        span = g["timestamp"].max() - g["timestamp"].min()
        svc_rows.append((
            svc, len(g), int(g["severity"].max()), int(b.max()), b.idxmax().strftime("%H:%M:%S"),
            str(span).split(".")[0],
            ", ".join(g["alarm_type"].value_counts().head(3).index),
        ))
    svc_rows.sort(key=lambda r: r[3], reverse=True)
    table(svc_rows, ("service", "alarms", "max_sev", "max/bucket", "peak_at", "span", "top types"))
    stats["per_service"] = [dict(zip(("service", "alarms", "max_sev", "max_bucket", "peak_at", "span", "top_types"), r)) for r in svc_rows]
    dbg("per-service done")

    # ---------- message templates ----------
    section("Message templates per alarm_type")
    df["msg_template"] = df["message"].map(normalize_message)
    tmpl_rows = []
    for atype, g in df.groupby("alarm_type"):
        tc = g["msg_template"].value_counts()
        samples = list(g["message"].head(args.sample_messages))
        tmpl_rows.append((atype, len(g), tc.size, tc.index[0], " || ".join(samples[:2])))
    tmpl_rows.sort(key=lambda r: r[1], reverse=True)
    table(tmpl_rows, ("alarm_type", "count", "distinct_templates", "dominant_template", "sample messages"))
    stats["message_templates"] = [list(r) for r in tmpl_rows]
    dbg("message templates done")

    # ---------- severity cross ----------
    section("alarm_type x severity")
    ct = pd.crosstab(df["alarm_type"], df["severity"])
    table([(i, *row) for i, row in zip(ct.index, ct.values.tolist())], ("alarm_type", *[f"sev{s}" for s in ct.columns]))
    stats["type_x_severity"] = {str(i): row for i, row in zip(ct.index, ct.values.tolist())}

    # ---------- dependencies ----------
    section("Dependency graph summary")
    all_svc = set(df["service"].unique())
    dep_src = set(deps["kaynak_servis"].unique())
    dep_dst = set(deps["hedef_servis"].unique())
    report.append(f"- edges: {len(deps)}; kaynak services: {len(dep_src)}; hedef services: {len(dep_dst)}")
    report.append(f"- services with alarms but absent from dep graph as kaynak: {sorted(all_svc - dep_src)}")
    report.append(f"- services with alarms but absent as hedef: {sorted(all_svc - dep_dst)}")
    out_deg = Counter(deps["kaynak_servis"])
    in_deg = Counter(deps["hedef_servis"])
    table(
        [(s, in_deg.get(s, 0), out_deg.get(s, 0)) for s in sorted(all_svc)],
        ("service", "depended_on_by (in-deg)", "depends_on (out-deg)"),
    )
    stats["dep_graph"] = {"edges": len(deps), "in_deg": dict(in_deg), "out_deg": dict(out_deg)}
    report.append("\n```\n" + deps.to_string(index=False) + "\n```")
    dbg("dependency summary done")

    # ---------- inventory ----------
    section("Host inventory summary")
    inv_rows = []
    for dc, g in inv.groupby("veri_merkezi"):
        for rack, g2 in g.groupby("kabin"):
            inv_rows.append((dc, rack, len(g2), ", ".join(g2["servis"].value_counts().head(5).index.astype(str))))
    table(inv_rows, ("dc", "rack", "hosts", "top services on hosts"))
    report.append("\n```\n" + inv.to_string(index=False) + "\n```")
    stats["inventory"] = [list(r) for r in inv_rows]

    # host in alarms but not inventory / vice versa
    section("Host coverage cross-check")
    alarm_hosts = set(df["host"].unique())
    inv_hosts = set(inv["host"].unique())
    report.append(f"- hosts in alarms: {len(alarm_hosts)}; in inventory: {len(inv_hosts)}")
    report.append(f"- alarms hosts missing from inventory: {sorted(alarm_hosts - inv_hosts)}")
    report.append(f"- inventory hosts with zero alarms: {sorted(inv_hosts - alarm_hosts)}")
    # tags vs inventory consistency
    merged = df.merge(inv[["host", "veri_merkezi", "kabin"]], on="host", how="left", suffixes=("", "_inv"))
    mism = merged[merged["veri_merkezi"] != merged["veri_merkezi_inv"]]
    report.append(f"- alarm-tag vs inventory dc mismatches: {len(mism)}")
    dbg("inventory done")

    # ---------- rack/dc time locality ----------
    section("Rack x 5-minute locality")
    b5 = df["timestamp"].dt.floor("300s")
    loc = df.groupby([b5, "veri_merkezi", "kabin"]).size().reset_index(name="n").sort_values("n", ascending=False)
    table([(r["timestamp"].strftime("%H:%M"), r["veri_merkezi"], r["kabin"], int(r["n"])) for _, r in loc.head(20).iterrows()],
          ("5min", "dc", "rack", "alarms"))
    stats["rack_time"] = [[r["timestamp"].strftime("%H:%M"), r["veri_merkezi"], r["kabin"], int(r["n"])] for _, r in loc.head(20).iterrows()]
    dbg("locality done")

    # ---------- write outputs ----------
    report_path = out_dir / "profile_report.md"
    stats_path = out_dir / "profile_stats.json"
    tmp = report_path.with_suffix(".md.tmp")
    tmp.write_text("\n".join(report), encoding="utf-8")
    tmp.replace(report_path)
    tmp = stats_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(stats, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp.replace(stats_path)

    dbg(f"outputs written: {report_path}, {stats_path}")
    print(f"OK: report={report_path} stats={stats_path} elapsed={time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
