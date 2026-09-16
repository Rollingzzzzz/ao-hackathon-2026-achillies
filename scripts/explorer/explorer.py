#!/usr/bin/env python3
"""explorer - build the pipeline execution-history manifest for the web GUI.

Scans the repository and emits out/explorer_manifest.json describing every
analysis/production step of event day in EXECUTION ORDER (per docs/fazlar.md
phases): for each step, the folders involved, every file with size/mtime,
the README summary, the exact run command, and the freshest output timestamp
as "last run" evidence. The manifest is served by serve.py at /api/explorer
and rendered step-by-step by out/explorer.html.

Read-only: never modifies scripts or outputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Execution order mirrors docs/fazlar.md (phases 1-6). Each step lists the
# folders whose contents belong to that step; file metadata is read live
# from disk so mtimes stay honest evidence of when things last ran.
STEPS = [
    {
        "id": "s1", "order": 1,
        "phase": "Faz 1 · Keşif", "time_hint": "14:35–14:45",
        "title": "explore_profile — ham verinin keşif profili",
        "summary_from": "scripts/explore_profile/README.md",
        "run_cmd": r"D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\scripts\explore_profile\explore_profile.py --debug",
        "dirs": ["scripts/explore_profile"],
        "note": "Paket iner inmez: dağılımlar, dakikalık histogram, burst adayları, mesaj şablonları. Buradan rack patlaması, slow-burn'ler ve blame madeni bulundu.",
    },
    {
        "id": "s2", "order": 2,
        "phase": "Faz 2 · Hipotez", "time_hint": "14:45–14:50",
        "title": "hypothesis_probe — 5 olay hipotezinin odaklı doğrulaması",
        "summary_from": "scripts/hypothesis_probe/README.md",
        "run_cmd": r"D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\scripts\hypothesis_probe\hypothesis_probe.py --debug",
        "dirs": ["scripts/hypothesis_probe"],
        "note": "Profile dayalı 5 hipotez odaklı sorgularla doğrulandı. 'Yakalaması zor' olan slow-burn (session leak) burada netleşti.",
    },
    {
        "id": "s3", "order": 3,
        "phase": "Faz 3 · Çekirdek motor", "time_hint": "14:50–15:05",
        "title": "src/alarmstorm — genel korelasyon motoru (5 aşama) + run.py",
        "summary_from": None,
        "run_cmd": r"D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\run.py --debug",
        "dirs": ["src/alarmstorm", "out", "out/charts"],
        "extra_files": ["run.py"],
        "note": "Hipotezler elle kodlanmadı; anomali hücre → tohum → attach → kök skorlama → gürültü denetimi boru hattı aynı 5 olaya kendi başına ulaştı. Iterasyon geçmişi: prompts/2026-09-16_engine_iterations.md.",
    },
    {
        "id": "s4", "order": 4,
        "phase": "Faz 4 · Ürünleştirme", "time_hint": "15:05–15:15",
        "title": "Nöbetçi konsolu — dashboard + canlı aksiyon sunucusu",
        "summary_from": "demo/README.md",
        "run_cmd": r"D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\serve.py",
        "dirs": ["demo"],
        "extra_files": ["serve.py", "out/dashboard.html", "out/actions.json"],
        "note": "Tek dosya dashboard (out/dashboard.html), aksiyon yaşam döngüsü API'si (açık→işlemde→kapalı, kalıcı), ekran görüntüleri demo/ altında.",
    },
    {
        "id": "s5", "order": 5,
        "phase": "Faz 5 · Teslim", "time_hint": "15:15–16:30",
        "title": "Teslim paketi — README, AI_JURI, submission, docs üçlüsü",
        "summary_from": None,
        "run_cmd": None,
        "dirs": ["docs", "prompts"],
        "extra_files": ["README.md", "AI_JURI.md", "submission.json", "CLAUDE.md",
                        "CONVENTIONS.md", ".env.example", "requirements.txt", "memory.md"],
        "note": "Her iddia dosya yoluyla kanıtlı; pip freeze requirements.txt'de; istem kayıtları prompts/ altında.",
    },
    {
        "id": "s6", "order": 6,
        "phase": "Faz 6 · Öz-denetim", "time_hint": "16:30–17:15",
        "title": "trap_audit — 'gol var mı?' denetimi + çekirdek-kanıt kapısı düzeltmesi",
        "summary_from": "scripts/trap_audit/README.md",
        "run_cmd": r"D:\projeler\ao-hackathon-2026-achillies\.venv\Scripts\python.exe D:\projeler\ao-hackathon-2026-achillies\scripts\trap_audit\trap_audit.py --scan-lo 1100 --scan-hi 1400",
        "dirs": ["scripts/trap_audit"],
        "extra_files": ["src/alarmstorm/engine.py", "docs/fazlar.md",
                        "prompts/2026-09-16_engine_iterations.md"],
        "note": "İç proxy alarm_id emisyon sırasından üretildi (yalnız denetimde). Bulgular: 1.157 gürültü kartlara emilmişti, 14 gerçek kuyruk alarmı elenmişti. Düzeltme: attach'e çekirdek-kanıt kapısı → gürültü eleme %34→%92, tüm sev5 kartlarda, 5 kart/kök değişmedi.",
    },
]


def kind_of(p: Path) -> str:
    n = p.name.lower()
    if n.endswith(".log"):
        return "log"
    if n == "readme.md":
        return "doc"
    if p.suffix == ".py":
        return "code"
    if p.suffix == ".md":
        return "report"
    if p.suffix == ".json":
        return "data"
    if p.suffix in {".png", ".jpg"}:
        return "image"
    if p.suffix in {".txt", ".example", ""} or n.startswith(".env"):
        return "doc"
    return "other"


def file_entry(p: Path) -> dict:
    st = p.stat()
    return {
        "path": p.relative_to(ROOT).as_posix(),
        "name": p.name,
        "size": st.st_size,
        "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        "kind": kind_of(p),
    }


def read_summary(rel: str | None) -> str:
    if not rel:
        return ""
    p = ROOT / rel
    if not p.exists():
        return ""
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("```"):
            return s
    return ""


def build_manifest() -> dict:
    steps = []
    for spec in STEPS:
        groups, all_files = [], []
        for d in spec["dirs"]:
            dp = ROOT / d
            if not dp.is_dir():
                continue
            files = [file_entry(p) for p in sorted(dp.iterdir())
                     if p.is_file() and p.name != "__pycache__"]
            groups.append({"label": d, "dir": d, "files": files})
            all_files.extend(files)
        for rel in spec.get("extra_files", []):
            p = ROOT / rel
            if p.is_file():
                fe = file_entry(p)
                groups.append({"label": rel, "dir": str(p.parent.relative_to(ROOT)), "files": [fe]})
                all_files.append(fe)
        last_run = max((f["mtime"] for f in all_files), default="")
        steps.append({
            "id": spec["id"], "order": spec["order"],
            "phase": spec["phase"], "time_hint": spec["time_hint"],
            "title": spec["title"],
            "summary": read_summary(spec["summary_from"]),
            "run_cmd": spec["run_cmd"],
            "note": spec["note"],
            "last_run": last_run,
            "file_count": len(all_files),
            "groups": groups,
        })
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(ROOT),
        "steps": steps,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "out" / "explorer_manifest.json"))
    args = ap.parse_args()
    manifest = build_manifest()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {len(manifest['steps'])} step -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
