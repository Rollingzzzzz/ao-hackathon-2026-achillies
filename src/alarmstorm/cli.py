"""AlarmStorm CLI orchestrator: load → correlate → score → cards → outputs."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from .cards import attach_similar_events, build_card, classify_root
from .dashboard import generate_dashboard
from .engine import CorrelationEngine, EngineConfig, EngineResult
from .io import Dataset, load_dataset
from .report import (event_chart, global_chart, noise_chart, terminal_summary,
                     write_json, write_summary_md)

DEFAULT_DATA_DIR = Path(r"D:\projeler\ao-hackathon-2026-achillies\data\package\katilimci_paketi")
DEFAULT_OUT_DIR = Path(r"D:\projeler\ao-hackathon-2026-achillies\out")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="alarmstorm",
        description="S-A1 Alert Storm Correlator — alarm selini olay kartlarına indirger.",
    )
    p.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--slice-min", type=int, default=EngineConfig.slice_minutes)
    p.add_argument("--min-cell", type=int, default=EngineConfig.min_cell)
    p.add_argument("--k-cell", type=float, default=EngineConfig.k_cell)
    p.add_argument("--min-seed-size", type=int, default=EngineConfig.min_seed_size)
    p.add_argument("--max-seed-dist", type=int, default=EngineConfig.max_seed_dist)
    p.add_argument("--attach-dist", type=int, default=EngineConfig.attach_dist)
    p.add_argument("--attach-margin-min", type=int, default=EngineConfig.attach_margin_min)
    p.add_argument("--min-event-alarms", type=int, default=EngineConfig.min_event_alarms)
    p.add_argument("--max-events", type=int, default=EngineConfig.max_events)
    p.add_argument("--debug", action="store_true", help="verbose progress logging to console")
    return p


def run_pipeline(ds: Dataset, cfg: EngineConfig) -> tuple[EngineResult, list[dict]]:
    engine = CorrelationEngine(ds, cfg)
    result = engine.run()

    cards = []
    for ev in sorted(result.events, key=lambda e: -len(e.alarm_ids))[: cfg.max_events]:
        seed_rows = ds.alarms[ds.alarms["alarm_id"].isin(ev.seed_alarm_ids)]
        kind = classify_root(ev, ev.root, seed_rows)
        cards.append(build_card(ev, ds.alarms, kind))
    cards.sort(key=lambda c: c["start"])
    for i, c in enumerate(cards, 1):
        c["id"] = f"EVT-{i:02d}"
    attach_similar_events(cards)
    return result, cards


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format="[%(levelname).1s %(asctime)s %(name)s] %(message)s", datefmt="%H:%M:%S")
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
    t0 = time.time()
    ds = load_dataset(args.data_dir)
    cfg = EngineConfig(
        slice_minutes=args.slice_min, min_cell=args.min_cell, k_cell=args.k_cell,
        min_seed_size=args.min_seed_size, max_seed_dist=args.max_seed_dist,
        attach_dist=args.attach_dist, attach_margin_min=args.attach_margin_min,
        min_event_alarms=args.min_event_alarms, max_events=args.max_events,
    )
    result, cards = run_pipeline(ds, cfg)

    out: Path = args.out_dir
    (out / "charts").mkdir(parents=True, exist_ok=True)
    write_json(out / "cards.json", cards)
    write_json(out / "noise_audit.json", {
        "totals": result.totals,
        "reason_counts": result.noise_reason_counts,
        "per_type": result.noise["alarm_type"].value_counts().to_dict(),
        "alarms": result.noise[["alarm_id", "timestamp", "service", "alarm_type",
                                "severity", "noise_reason"]].to_dict(orient="records"),
    })
    write_json(out / "events_full.json", [
        {
            "id": f"EVT-{e.idx:02d}", "start": str(e.start), "end": str(e.end),
            "alarm_ids": e.alarm_ids, "seed_alarm_ids": e.seed_alarm_ids,
            "root": e.root.__dict__ if e.root else None,
            "counters": [c.__dict__ for c in e.counters],
        }
        for e in result.events
    ])
    for c in cards:
        event_chart(c, out / "charts")
    global_chart(cards, ds.alarms, out / "charts")
    noise_chart(result.noise, ds.alarms, out / "charts")
    write_summary_md(cards, result.totals, result.noise_reason_counts, out)

    # action registry: keep human/demo decisions across regenerations
    actions_file = out / "actions.json"
    actions: dict = {}
    if actions_file.exists():
        actions = json.loads(actions_file.read_text(encoding="utf-8"))
    actions = {c["id"]: actions.get(c["id"], {"status": "açık", "history": []}) for c in cards}
    write_json(actions_file, actions)

    generate_dashboard(out, cards, result.noise_reason_counts, result.totals)
    terminal_summary(cards, result.totals)

    dbg_log = out / "run_debug.log"
    dbg_log.write_text(
        f"elapsed={time.time() - t0:.2f}s\ncfg={cfg}\ntotals={result.totals}\n"
        f"noise_reasons={result.noise_reason_counts}\n", encoding="utf-8")
    print(f"OK: outputs in {out} (elapsed {time.time() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
