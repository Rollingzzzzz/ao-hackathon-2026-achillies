"""Data loading and message parsing for the S-A1 data package."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

TIMEOUT_RE = re.compile(r"(\S+) servisine yapilan cagri zaman asimina ugradi")
CONNREF_RE = re.compile(r"(\S+) baglantisi reddedildi")
EXT_RE = re.compile(r"Dis servis (\S+)")

# Alarm types considered hard structural failures ("markers"). These are the
# only types allowed to SEED events; other types attach later.
MARKER_TYPES = {
    "network_down", "pkt_loss", "disk_full", "db_write_fail", "gc_pressure",
    "oom_risk", "ext_slow", "ext_unreach", "batch_overlap", "batch_slow",
    "conn_refused", "db_conn_pool",
}
# Resource-type alarms that indicate a SLOW-BURN event when anomalous cells
# of the same (service, type) persist over a long span. Symptom types
# (timeout/http_5xx/latency) are deliberately excluded: they repeat across
# unrelated events and would bridge them.
SUSTAINABLE_TYPES = {
    "mem_high", "cpu_high", "disk_warn", "db_conn_pool",
}
NETWORK_TYPES = {"network_down", "network_flap", "pkt_loss"}


@dataclass
class Dataset:
    alarms: pd.DataFrame
    deps: pd.DataFrame
    inventory: pd.DataFrame

    def __post_init__(self) -> None:
        self.alarms["timestamp"] = pd.to_datetime(self.alarms["timestamp"])
        self.alarms = self.alarms.sort_values("timestamp").reset_index(drop=True)
        if "blame" not in self.alarms.columns:
            self.alarms["blame"] = ""

    @property
    def services(self) -> list[str]:
        return sorted(self.alarms["service"].unique().tolist())


def parse_blame(alarm_type: str, message: str) -> str:
    """Extract the blamed target service from causality-bearing messages.

    timeout / conn_refused / ext_* messages explicitly name the CALLED
    (failing) party — a direct causal edge we get for free from the data.
    """
    if alarm_type == "timeout":
        m = TIMEOUT_RE.search(message)
        return m.group(1) if m else ""
    if alarm_type == "conn_refused":
        m = CONNREF_RE.search(message)
        return m.group(1) if m else ""
    if alarm_type in ("ext_slow", "ext_unreach"):
        m = EXT_RE.search(message)
        return m.group(1) if m else ""
    return ""


def load_dataset(data_dir: Path) -> Dataset:
    data_dir = Path(data_dir)
    alarms = pd.read_csv(data_dir / "alarms.csv")
    deps = pd.read_csv(data_dir / "service_dependencies.csv")
    inv = pd.read_csv(data_dir / "host_inventory.csv")

    alarms["blame"] = [
        parse_blame(at, msg)
        for at, msg in zip(alarms["alarm_type"], alarms["message"])
    ]
    return Dataset(alarms=alarms, deps=deps, inventory=inv)
