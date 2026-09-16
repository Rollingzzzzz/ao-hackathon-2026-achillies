#!/usr/bin/env python3
"""Zero-dependency demo server (stdlib http.server).

Serves the generated dashboard and out/ artifacts, and exposes a tiny
action-lifecycle API so the on-stage demo can open / progress / close
actions live:

    GET  /api/actions        -> current actions map (JSON)
    POST /api/actions        -> body {"id": "EVT-01", "status": "işlemde"|"kapalı"|"açık"}
    GET  /explorer           -> pipeline execution-history GUI (debug)
    GET  /api/explorer       -> execution-history manifest (auto-generated)
    GET  /api/file?path=rel  -> whitelisted file content for the explorer

Actions persist to out/actions.json (survive restarts; regenerated cards
keep existing statuses).

Usage:  python serve.py [--port 8787] [--out-dir out]
Then open http://localhost:8787
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent
VALID = {"açık", "işlemde", "kapalı"}
ALIASES = {"acik": "açık", "islemde": "işlemde", "kapali": "kapalı",
           "open": "açık", "in_progress": "işlemde", "closed": "kapalı"}
lock = threading.Lock()

FILE_TEXT_SUFFIXES = {".md", ".py", ".json", ".log", ".txt", ".html", ".example", ""}
MAX_FILE_BYTES = 200_000  # larger files are truncated for the viewer


def actions_path(out_dir: Path) -> Path:
    return out_dir / "actions.json"


def load_actions(out_dir: Path) -> dict:
    p = actions_path(out_dir)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def save_action(out_dir: Path, card_id: str, status: str) -> dict:
    with lock:
        data = load_actions(out_dir)
        cur = data.get(card_id, {"status": "açık", "history": []})
        if cur["status"] != status:
            cur["history"].append({
                "at": datetime.now().isoformat(timespec="seconds"),
                "from": cur["status"], "to": status, "by": "demo",
            })
        cur["status"] = status
        data[card_id] = cur
        tmp = actions_path(out_dir).with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(actions_path(out_dir))
        return data


def explorer_manifest(out_dir: Path) -> dict:
    """Load out/explorer_manifest.json, generating it on first use."""
    p = out_dir / "explorer_manifest.json"
    if not p.exists():
        subprocess.run([sys.executable, str(REPO / "scripts" / "explorer" / "explorer.py")],
                       check=False, capture_output=True)
    return json.loads(p.read_text(encoding="utf-8"))


def whitelisted_paths(manifest: dict) -> set[str]:
    return {f["path"] for step in manifest["steps"] for g in step["groups"] for f in g["files"]}


class Handler(BaseHTTPRequestHandler):
    out_dir: Path = REPO / "out"

    def log_message(self, fmt: str, *args) -> None:  # quieter console
        print(f"[serve] {self.address_string()} {fmt % args}")

    def _json(self, obj: dict, code: int = 200) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.startswith("/api/actions"):
            return self._json(load_actions(self.out_dir))
        if self.path.startswith("/explorer"):
            rel = "explorer.html"
        elif self.path.startswith("/api/explorer"):
            return self._json(explorer_manifest(self.out_dir))
        elif self.path.startswith("/api/file"):
            from urllib.parse import parse_qs, urlparse
            q = parse_qs(urlparse(self.path).query)
            rel_path = (q.get("path", [""])[0]).replace("\\", "/").lstrip("/")
            manifest = explorer_manifest(self.out_dir)
            f = (REPO / rel_path).resolve()
            inside = str(f).lower().startswith(str(REPO.resolve()).lower())
            viewable = f.suffix.lower() in FILE_TEXT_SUFFIXES or f.name.startswith(".env")
            if (not rel_path or rel_path not in whitelisted_paths(manifest)
                    or not inside or not f.is_file() or not viewable):
                return self._json({"error": "dosya manifest beyaz listesinde değil"}, 404)
            raw = f.read_bytes()
            truncated = len(raw) > MAX_FILE_BYTES
            return self._json({
                "path": rel_path, "truncated": truncated,
                "content": raw[:MAX_FILE_BYTES].decode("utf-8", errors="replace"),
            })
        else:
            rel = "dashboard.html" if self.path in ("/", "/index.html") else self.path.lstrip("/")
        f = (self.out_dir / rel).resolve()
        if not str(f).startswith(str(self.out_dir.resolve())) or not f.is_file():
            self.send_error(404)
            return
        ctype = "text/html" if f.suffix == ".html" else (
            "image/png" if f.suffix == ".png" else (
                "application/json" if f.suffix == ".json" else "text/plain"))
        body = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text") else ""))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if not self.path.startswith("/api/actions"):
            self.send_error(404)
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n).decode("utf-8"))
            card_id, status = payload["id"], payload["status"]
            status = ALIASES.get(str(status).lower().strip(), status)  # curl/console-safe
        except Exception:
            return self._json({"error": "geçersiz istek"}, 400)
        if status not in VALID:
            return self._json({"error": f"status {VALID} olmalı"}, 400)
        cards = json.loads((self.out_dir / "cards.json").read_text(encoding="utf-8"))
        if card_id not in {c["id"] for c in cards}:
            return self._json({"error": "bilinmeyen kart"}, 404)
        data = save_action(self.out_dir, card_id, status)
        print(f"[serve] aksiyon güncellendi: {card_id} -> {status}")
        return self._json(data)


def main() -> int:
    ap = argparse.ArgumentParser(description="AlarmStorm demo sunucusu")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--out-dir", type=Path, default=REPO / "out")
    args = ap.parse_args()
    Handler.out_dir = args.out_dir
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"AlarmStorm demo sunucusu: http://localhost:{args.port}  (durdurmak: Ctrl+C)")
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
