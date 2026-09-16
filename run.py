#!/usr/bin/env python3
"""Repo-root entry point for the AlarmStorm pipeline.

Usage (from repo root, venv active):
    python run.py --debug
    python run.py --data-dir <package dir> --out-dir <out dir>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from alarmstorm.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
