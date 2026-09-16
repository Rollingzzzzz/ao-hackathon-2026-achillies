"""Output rendering: markdown summary, per-event timeline charts (PNG),
global timeline with event bands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from .io import NETWORK_TYPES  # noqa: E402

ACCENT = "#00e5a0"
RED = "#ff5470"
AMBER = "#ffb454"
BLUE = "#59c2ff"
BG = "#0f1117"
FG = "#d6deeb"


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def write_json(path: Path, obj: Any) -> None:
    atomic_write(path, json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def event_chart(card: dict[str, Any], out_dir: Path) -> Path:
    tl = card["timeline"]
    ts = pd.to_datetime(["2026-09-10 " + t for t, _ in tl])
    n = [c for _, c in tl]
    fig, ax = plt.subplots(figsize=(9, 2.6), dpi=130)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.fill_between(ts, n, color=ACCENT if card["severity"] < 5 else RED, alpha=0.25)
    ax.plot(ts, n, color=ACCENT if card["severity"] < 5 else RED, lw=1.6)
    ax.set_title(f'{card["id"]} · {card["title"]}', color=FG, fontsize=9)
    ax.tick_params(colors=FG, labelsize=7)
    for spine in ax.spines.values():
        spine.set_color("#2a2f3a")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.grid(color="#2a2f3a", lw=0.4, alpha=0.6)
    fig.tight_layout()
    p = out_dir / f'{card["id"]}_timeline.png'
    fig.savefig(p, facecolor=BG)
    plt.close(fig)
    return p


def global_chart(cards: list[dict[str, Any]], alarms: pd.DataFrame, out_dir: Path) -> Path:
    per_min = alarms.groupby(alarms["timestamp"].dt.floor("min")).size().sort_index()
    ts = per_min.index
    fig, ax = plt.subplots(figsize=(11, 3.2), dpi=130)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.plot(ts, per_min.values, color=FG, lw=1.2, label="alarm/dk (toplam)")
    colors = [ACCENT, BLUE, AMBER, RED, "#c792ea", "#89ddff"]
    for i, card in enumerate(cards):
        ev_ts = pd.to_datetime(["2026-09-10 " + t for t, _ in card["timeline"]])
        ev_n = [c for _, c in card["timeline"]]
        ax.plot(ev_ts, ev_n, color=colors[i % len(colors)], lw=1.6, alpha=0.9, label=f'{card["id"]} {card["root_kind_label"]}')
        ax.axvspan(ev_ts.min(), ev_ts.max(), color=colors[i % len(colors)], alpha=0.07)
    ax.set_title("Alarm akışı ve ayrıştırılan olaylar (10 Eylül 2026, 01:30–03:30)", color=FG, fontsize=10)
    ax.tick_params(colors=FG, labelsize=7)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    for spine in ax.spines.values():
        spine.set_color("#2a2f3a")
    ax.grid(color="#2a2f3a", lw=0.4, alpha=0.5)
    leg = ax.legend(fontsize=7, facecolor=BG, labelcolor=FG, loc="upper right")
    for t in leg.get_texts():
        t.set_color(FG)
    fig.tight_layout()
    p = out_dir / "global_timeline.png"
    fig.savefig(p, facecolor=BG)
    plt.close(fig)
    return p


def noise_chart(noise: pd.DataFrame, alarms: pd.DataFrame, out_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9, 2.6), dpi=130)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    all_min = alarms.groupby(alarms["timestamp"].dt.floor("min")).size().sort_index()
    noise_min = noise.groupby(noise["timestamp"].dt.floor("min")).size().sort_index().reindex(all_min.index, fill_value=0)
    ax.fill_between(all_min.index, noise_min.values, color=AMBER, alpha=0.3, label="gürültü olarak elendi")
    ax.fill_between(all_min.index, (all_min - noise_min).values, color=ACCENT, alpha=0.3, label="olay kartlarına bağlandı")
    ax.plot(all_min.index, all_min.values, color=FG, lw=0.9)
    ax.set_title("Gürültü denetimi: her alarm ya bir olay kartına bağlandı ya da gerekçesiyle elendi", color=FG, fontsize=9)
    ax.tick_params(colors=FG, labelsize=7)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    for spine in ax.spines.values():
        spine.set_color("#2a2f3a")
    ax.grid(color="#2a2f3a", lw=0.4, alpha=0.5)
    leg = ax.legend(fontsize=7, facecolor=BG, labelcolor=FG)
    fig.tight_layout()
    p = out_dir / "noise_audit.png"
    fig.savefig(p, facecolor=BG)
    plt.close(fig)
    return p


def write_summary_md(cards: list[dict[str, Any]], totals: dict[str, Any],
                     noise_reason_counts: dict[str, int], out_dir: Path) -> Path:
    L: list[str] = ["# AlarmStorm — Özet Rapor", ""]
    L.append(f'- Toplam alarm: **{totals["total_alarms"]}** → olay kartı: **{totals["event_count"]}** '
             f'(indirgeme oranı 1:{totals["total_alarms"] // max(1, totals["event_count"])})')
    L.append(f'- Olaylara bağlanan alarm: **{totals["event_alarms"]}** · gürültü olarak elenen: **{totals["noise_alarms"]}**')
    L.append("")
    L.append("| Kart | Kök neden | Örüntü | Aralık | Alarm | Kritik | Aksiyon sahibi | Durum |")
    L.append("|---|---|---|---|---|---|---|---|")
    for c in cards:
        L.append(f'| {c["id"]} | {c["title"]} | {c["pattern"]} | {c["start"]}–{c["end"]} | {c["alarm_count"]} | '
                 f'{"🔴" if c["severity"] == 5 else "🟠" if c["severity"] >= 4 else "🟡"} | '
                 f'{c["first_action"]["owner"]} | {c["first_action"]["status"]} |')
    L.append("")
    L.append("## Gürültü denetimi")
    L.append("")
    L.append("| Eleme gerekçesi | Alarm sayısı |")
    L.append("|---|---|")
    for k, v in sorted(noise_reason_counts.items(), key=lambda kv: -kv[1]):
        L.append(f"| {k} | {v} |")
    p = out_dir / "summary.md"
    atomic_write(p, "\n".join(L) + "\n")
    return p


def terminal_summary(cards: list[dict[str, Any]], totals: dict[str, Any]) -> None:
    print("=" * 78)
    print(f'  ALARMSTORM — {totals["total_alarms"]} alarm → {totals["event_count"]} olay kartı '
          f'(gürültü: {totals["noise_alarms"]})')
    print("=" * 78)
    for c in cards:
        print(f'  {c["id"]}  sev{c["severity"]}  {c["start"]}–{c["end"]}  {c["alarm_count"]:4d} alarm  '
              f'{c["pattern"]:<14} {c["title"]}')
        print(f'        └─ {c["root_cause"]["hypothesis"][:100]}')
    print("=" * 78)
