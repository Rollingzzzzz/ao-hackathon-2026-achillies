"""Core correlation engine.

Pipeline (all thresholds CLI-tunable):

1. ANOMALY CELLS — flag alarms whose (service, type, time-slice) count is
   far above the global baseline for that type, plus rack-local bursts of
   network alarms. This separates structural signal from background noise
   WITHOUT assuming any specific alarm type means an event (types are
   shared across events and noise alike).
2. SEED CLUSTERING — union-find over anomalous alarms. Two alarms link when
   their slices are adjacent AND they are topologically related: same
   service, a blame edge (timeout/conn_refused/ext_* name their target),
   dependency-graph distance <= max_dist, or same (dc, rack).
   Small clusters are dropped (scattered noise markers).
3. ATTACH — every alarm in the file is offered to each event whose time
   window it falls into; it attaches to the event it is causally closest to
   (blame match > same service > graph distance). Windows grow with the
   alarms they absorb, then stabilise (two passes).
4. ROOT CAUSE SCORING — inside each event, candidate services are ranked by:
   how often they are blamed, how many hard-failure markers sit on them,
   how many of the other affected services depend on them (explainability),
   earliness, and severity. A rack-concentrated network pattern promotes the
   RACK (dc/rack, i.e. top-of-rack network) itself as the root.
5. NOISE AUDIT — every alarm not attached to an event is recorded with the
   explicit reason(s) it was excluded. Nothing disappears silently.
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

import pandas as pd

from .graph import INF, DepGraph
from .io import MARKER_TYPES, NETWORK_TYPES, SUSTAINABLE_TYPES, Dataset

log = logging.getLogger("alarmstorm")


# ---------------------------------------------------------------- utilities
class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


# ------------------------------------------------------------------ config
@dataclass
class EngineConfig:
    slice_minutes: int = 5          # time-slice granularity for anomaly cells
    min_cell: int = 3               # absolute minimum cell count to be anomalous
    k_cell: float = 8.0             # multiplier over global per-type baseline
    min_seed_size: int = 5          # min anomalous alarms to keep a seed cluster
    max_seed_dist: int = 3          # graph distance linking two anomalous alarms
    attach_dist: int = 2            # graph distance for attaching normal alarms
    attach_margin_min: int = 2      # minutes of slack around an event window
    attach_passes: int = 3          # attach sweeps; windows grow late, tails need a re-offer
    require_core_attach: bool = True  # only blame/anomaly/marker evidence may attach
    core_min_sev: int = 4           # same-service alarms at/above this severity are core evidence
    min_event_alarms: int = 10      # drop events that end up smaller than this
    max_events: int = 15            # acceptance criterion hard cap
    rack_net_concentration: float = 0.6  # share of net markers in one rack to call a rack event
    min_rack_net_markers: int = 8
    sustained_slices: int = 4         # anomalous slices needed for a slow-burn seed
    sustained_span_min: int = 30      # min span (minutes) of those slices


# ------------------------------------------------------------------ results
@dataclass
class RootCandidate:
    kind: str                 # "service" | "rack"
    name: str                 # service name or "dc1/rack-A"
    score: float
    blames: int = 0
    markers: int = 0
    explains: int = 0
    sev5: int = 0
    first_ts: str = ""


@dataclass
class Event:
    idx: int
    seed_alarm_ids: list[str] = field(default_factory=list)
    alarm_ids: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    start: pd.Timestamp | None = None
    end: pd.Timestamp | None = None
    root: RootCandidate | None = None
    counters: list[RootCandidate] = field(default_factory=list)
    pattern: str = ""         # "burst" | "slow_burn"
    max_sev: int = 0
    type_counts: dict[str, int] = field(default_factory=dict)
    host_counts: dict[str, int] = field(default_factory=dict)
    rack_counts: dict[str, int] = field(default_factory=dict)


@dataclass
class EngineResult:
    events: list[Event]
    noise: pd.DataFrame                     # unattached alarms + reason columns
    noise_reason_counts: dict[str, int]
    totals: dict[str, Any]


# ------------------------------------------------------------------- engine
class CorrelationEngine:
    def __init__(self, ds: Dataset, cfg: EngineConfig):
        self.ds = ds
        self.cfg = cfg
        self.graph = DepGraph(
            edges=list(zip(ds.deps["kaynak_servis"], ds.deps["hedef_servis"])),
            nodes=ds.services,
        )
        # rack of each alarm from its own tags
        self.alarms = ds.alarms.copy()
        self.alarms["rack_key"] = self.alarms["veri_merkezi"] + "/" + self.alarms["kabin"]
        self.alarms["slice"] = self.alarms["timestamp"].dt.floor(f"{cfg.slice_minutes}min")
        self.n_slices = max(1, int((self.alarms["slice"].max() - self.alarms["slice"].min()) / timedelta(minutes=cfg.slice_minutes)) + 1)
        self.anomalous: set[str] = set()      # alarm_ids flagged anomalous
        self._dbg("engine initialised: %d alarms, %d slices, %d graph nodes", len(self.alarms), self.n_slices, len(self.graph.nodes))

    def _dbg(self, msg: str, *args: Any) -> None:
        log.debug(msg, *args)

    # 1 ---------------------------------------------------- anomaly cells
    def flag_anomalies(self) -> None:
        n_services = self.alarms["service"].nunique()
        cell = self.alarms.groupby(["service", "alarm_type", "slice"], sort=False).size()
        type_totals = self.alarms.groupby("alarm_type").size()
        for (svc, atype, sl), n in cell.items():
            baseline = type_totals[atype] / (n_services * self.n_slices)
            threshold = max(self.cfg.min_cell, self.cfg.k_cell * baseline)
            if n >= threshold:
                ids = self.alarms.loc[
                    (self.alarms["service"] == svc) & (self.alarms["alarm_type"] == atype) & (self.alarms["slice"] == sl),
                    "alarm_id",
                ]
                self.anomalous.update(ids)
        self._dbg("service-level anomalous alarms: %d", len(self.anomalous))

        net = self.alarms[self.alarms["alarm_type"].isin(NETWORK_TYPES)]
        if len(net):
            n_racks = net["rack_key"].nunique()
            rack_cell = net.groupby(["rack_key", "alarm_type", "slice"], sort=False).size()
            net_type_totals = net.groupby("alarm_type").size()
            extra = 0
            for (rk, atype, sl), n in rack_cell.items():
                baseline = net_type_totals[atype] / (n_racks * self.n_slices)
                threshold = max(self.cfg.min_cell, self.cfg.k_cell * baseline)
                if n >= threshold:
                    ids = net.loc[(net["rack_key"] == rk) & (net["alarm_type"] == atype) & (net["slice"] == sl), "alarm_id"]
                    new = set(ids) - self.anomalous
                    self.anomalous.update(new)
                    extra += len(new)
            self._dbg("rack-level anomalous network alarms added: %d", extra)

    # 2 ---------------------------------------------------- seed clusters
    def build_seeds(self) -> list[list[int]]:
        flags = self.alarms["alarm_id"].isin(self.anomalous)

        # sustained slow-burn signals: anomalous cells of the same
        # (service, resource type) spread over a long span become markers
        extra_sustained: set[int] = set()
        cand_sus = self.alarms[flags & self.alarms["alarm_type"].isin(SUSTAINABLE_TYPES)]
        for (svc, atype), g in cand_sus.groupby(["service", "alarm_type"]):
            slices = sorted(g["slice"].unique())
            if len(slices) < self.cfg.sustained_slices:
                continue
            span = (slices[-1] - slices[0]).total_seconds() / 60
            if span >= self.cfg.sustained_span_min:
                rows_idx = g.index.tolist()
                extra_sustained.update(rows_idx)
                self._dbg("sustained slow-burn signal: %s/%s over %.0f min (%d anomalous alarms)", svc, atype, span, len(rows_idx))

        marker_ids = set(
            self.alarms.loc[flags & self.alarms["alarm_type"].isin(MARKER_TYPES)].index.tolist()
        ) | extra_sustained
        m_idx = sorted(marker_ids)
        uf = UnionFind(len(self.alarms))
        pos = {i: r for r, i in enumerate(m_idx)}

        # all alarms of one sustained signal form a single saga
        for idx_group in (self.alarms.loc[list(extra_sustained)]
                          .groupby(["service", "alarm_type"]).groups.values()):
            idxs = sorted(idx_group)
            for k in range(1, len(idxs)):
                uf.union(pos[idxs[0]], pos[idxs[k]])

        def effective(row: pd.Series) -> set[str]:
            out = {row["service"]}
            if isinstance(row["blame"], str) and row["blame"]:
                out.add(row["blame"])
            return out

        marker_rows = [(i, self.alarms.loc[i]) for i in m_idx]
        same_svc_gap = 2  # slow-burn chains tolerate a quiet slice
        for a in range(len(marker_rows)):
            ia, ra = marker_rows[a]
            ea, sl_a = effective(ra), ra["slice"]
            net_a = ra["alarm_type"] in NETWORK_TYPES
            sus_a = ra["alarm_type"] in SUSTAINABLE_TYPES
            for b in range(a + 1, len(marker_rows)):
                ib, rb = marker_rows[b]
                sl_b = rb["slice"]
                slice_gap = abs((sl_a - sl_b) / timedelta(minutes=self.cfg.slice_minutes))
                sus_b = rb["alarm_type"] in SUSTAINABLE_TYPES
                related = False
                if ra["service"] == rb["service"]:
                    related = slice_gap <= same_svc_gap
                elif sus_a or sus_b:
                    # a sustained resource signal may bind to the service it
                    # DEPENDS ON (a pool exhausting on X and on X's upstream is
                    # one incident) — never to its dependents, which would let
                    # a central service bridge unrelated storms
                    related = slice_gap == 0 and (
                        (sus_a and rb["service"] in self.graph.deps_of.get(ra["service"], ()))
                        or (sus_b and ra["service"] in self.graph.deps_of.get(rb["service"], ()))
                    )
                elif net_a and rb["alarm_type"] in NETWORK_TYPES and ra["rack_key"] == rb["rack_key"]:
                    # physical-layer locality binds only network alarms
                    related = slice_gap <= 1
                else:
                    d = min(
                        self.graph.min_distance(x, effective(rb), self.cfg.max_seed_dist)
                        for x in ea
                    )
                    if d <= 1:
                        # direct dependency: a failure and its immediate victim
                        # may be one slice apart (burst builds up over minutes)
                        related = slice_gap <= 1
                    elif d <= self.cfg.max_seed_dist:
                        related = slice_gap == 0  # looser links only within the same slice
                if related:
                    uf.union(pos[ia], pos[ib])

        groups: dict[int, list[int]] = defaultdict(list)
        for i in m_idx:
            groups[uf.find(pos[i])].append(i)
        seeds = [g for g in groups.values() if len(g) >= self.cfg.min_seed_size]
        seeds.sort(key=lambda g: self.alarms.loc[g[0], "timestamp"])
        for g in seeds:
            sr = self.alarms.loc[g]
            self._dbg(
                "seed: %s span=%s..%s services=%s types=%s",
                len(g), sr["timestamp"].min().strftime("%H:%M:%S"), sr["timestamp"].max().strftime("%H:%M:%S"),
                sorted(sr["service"].unique().tolist())[:8],
                dict(Counter(sr["alarm_type"]).most_common(5)),
            )
        self._dbg("seeds: %d clusters kept (of %d), sizes=%s", len(seeds), len(groups), [len(g) for g in seeds])
        return seeds

    # 3 ------------------------------------------------------------ attach
    def _extend_buildup(self, ev: Event) -> None:
        """Slow-burn buildup: walk backwards from the event start while a seed
        service shows a sustained elevated rate of a resource-type alarm
        (single quiet slices tolerated). Those alarms are the buildup phase
        of the same incident, not noise."""
        resource_types = {"mem_high", "cpu_high", "disk_warn", "db_conn_pool"}
        seed_rows = self.alarms[self.alarms["alarm_id"].isin(ev.seed_alarm_ids)]
        seed_services = set(seed_rows["service"])
        limit = ev.start - timedelta(minutes=45)
        new_start = ev.start
        for svc in seed_services:
            # walk back only on the SAME failure mode the seed showed
            mode_types = set(seed_rows[seed_rows["service"] == svc]["alarm_type"]) & resource_types
            svc_rows = self.alarms[self.alarms["service"] == svc]
            for atype in mode_types:
                hist = svc_rows[svc_rows["alarm_type"] == atype].sort_values("timestamp")
                if hist.empty:
                    continue
                cur = ev.start.floor(f"{self.cfg.slice_minutes}min") - timedelta(minutes=self.cfg.slice_minutes)
                can_dip = True
                while cur >= limit:
                    n = int(((hist["timestamp"] >= cur) & (hist["timestamp"] < cur + timedelta(minutes=self.cfg.slice_minutes))).sum())
                    if n >= 3:
                        new_start = min(new_start, hist[hist["timestamp"] < cur + timedelta(minutes=self.cfg.slice_minutes)]["timestamp"].min())
                        cur -= timedelta(minutes=self.cfg.slice_minutes)
                        can_dip = True
                    elif n >= 2 and can_dip:
                        cur -= timedelta(minutes=self.cfg.slice_minutes)
                        can_dip = False
                    else:
                        break
        if new_start < ev.start:
            self._dbg("event %d buildup extended to %s", ev.idx, new_start)
            ev.start = new_start

    def attach(self, seeds: list[list[int]]) -> list[Event]:
        events: list[Event] = []
        for n, seed in enumerate(seeds):
            ev = Event(idx=n + 1, seed_alarm_ids=sorted(self.alarms.loc[seed, "alarm_id"].tolist()))
            seed_rows = self.alarms.loc[seed]
            ev.start = seed_rows["timestamp"].min()
            ev.end = seed_rows["timestamp"].max()
            ev.services = sorted(set(seed_rows["service"]) | {b for b in seed_rows["blame"] if isinstance(b, str) and b})
            self._extend_buildup(ev)
            events.append(ev)

        assigned: dict[str, int] = {}  # alarm_id -> event idx
        margin = timedelta(minutes=self.cfg.attach_margin_min)
        hotness: dict[int, Counter] = {ev.idx: Counter() for ev in events}  # event -> slice -> assigned count
        seed_type_profile: dict[int, Counter] = {}
        for ev in events:
            sr = self.alarms[self.alarms["alarm_id"].isin(ev.seed_alarm_ids)]
            seed_type_profile[ev.idx] = Counter(sr["alarm_type"])
        for _ in range(self.cfg.attach_passes):  # windows grow with absorbed alarms; late tails need a re-offer
            for ev in events:
                ev.alarm_ids = [aid for aid, i in assigned.items() if i == ev.idx]
            for _, row in self.alarms.iterrows():
                aid = row["alarm_id"]
                if aid in assigned:
                    continue
                best_ev, best_score, best_core = None, -1.0, False
                for ev in events:
                    if not (ev.start - margin <= row["timestamp"] <= ev.end + margin):
                        continue
                    cand = {row["service"]}
                    if isinstance(row["blame"], str) and row["blame"]:
                        cand.add(row["blame"])
                    score = -1.0
                    core = False  # core evidence may extend the event window
                    for c in cand:
                        if c in ev.services:
                            if c == row["blame"]:
                                score, core = max(score, 4.0), True
                            else:
                                score = max(score, 3.0)
                                if (row["alarm_id"] in self.anomalous
                                        or row["alarm_type"] in MARKER_TYPES
                                        or int(row["severity"]) >= self.cfg.core_min_sev):
                                    # background noise never reaches sev5 in this
                                    # dataset and rarely sev4: a high-severity alarm
                                    # on an event service inside the window is signal
                                    core = True
                    if score < 0:
                        d = min(self.graph.min_distance(c, ev.services, self.cfg.attach_dist) for c in cand)
                        if d <= self.cfg.attach_dist:
                            score = 2.0 - 0.5 * d
                            strong = (row["alarm_id"] in self.anomalous
                                      or row["alarm_type"] in MARKER_TYPES
                                      or int(row["severity"]) >= self.cfg.core_min_sev)
                            if strong:
                                # a strong alarm on a NEIGHBOUR service is the
                                # cascade propagating; weak alarms need blame
                                core = True
                    if score < 0:
                        continue
                    # symptom-type continuity: a card whose core exhibits this
                    # alarm's type is the more natural home for it
                    if seed_type_profile[ev.idx].get(row["alarm_type"], 0) > 0:
                        score += 0.3
                    # tie-break: the event that is hottest right now wins
                    score += 0.25 * min(10, hotness[ev.idx][row["slice"]])
                    if score > best_score:
                        best_score, best_ev, best_core = score, ev, core
                if best_ev is not None and best_score > 0 and (
                    best_core or not self.cfg.require_core_attach
                ):
                    # core-gated attach: an alarm joins a card only on causal
                    # evidence (blame target, or same-service anomaly/marker).
                    # Same-service or graph proximity alone is background
                    # noise's favourite disguise inside a wide event window.
                    assigned[aid] = best_ev.idx
                    hotness[best_ev.idx][row["slice"]] += 1
                    # grow the window immediately, but only on core evidence;
                    # routine noise on a seed service must not stretch the event
                    if best_core:
                        if row["timestamp"] < best_ev.start:
                            best_ev.start = row["timestamp"]
                        if row["timestamp"] > best_ev.end:
                            best_ev.end = row["timestamp"]
            for ev in events:  # grow windows from newly attached alarms
                ids = [aid for aid, i in assigned.items() if i == ev.idx]
                if ids:
                    rows = self.alarms[self.alarms["alarm_id"].isin(ids)]
                    ev.start = min(ev.start, rows["timestamp"].min())
                    ev.end = max(ev.end, rows["timestamp"].max())

        for ev in events:
            own = [aid for aid, i in assigned.items() if i == ev.idx]
            seeds = [s for s in ev.seed_alarm_ids if s not in assigned or assigned[s] == ev.idx]
            ev.alarm_ids = sorted(set(own + seeds))
            rows = self.alarms[self.alarms["alarm_id"].isin(ev.alarm_ids)]
            ev.start, ev.end = rows["timestamp"].min(), rows["timestamp"].max()
            ev.services = sorted(set(rows["service"]))
            ev.max_sev = int(rows["severity"].max())
            ev.type_counts = {k: int(v) for k, v in rows["alarm_type"].value_counts().items()}
            ev.host_counts = {k: int(v) for k, v in rows["host"].value_counts().head(8).items()}
            ev.rack_counts = {k: int(v) for k, v in rows["rack_key"].value_counts().head(6).items()}
            span_min = (ev.end - ev.start).total_seconds() / 60
            ev.pattern = "slow_burn" if span_min >= 40 else "burst"

        events = [e for e in events if len(e.alarm_ids) >= self.cfg.min_event_alarms]
        for n, ev in enumerate(events, 1):
            ev.idx = n
        self._dbg("events after attach: %d, sizes=%s", len(events), [len(e.alarm_ids) for e in events])
        return events

    # 4 ------------------------------------------------------- root cause
    def score_roots(self, events: list[Event]) -> None:
        for ev in events:
            rows = self.alarms[self.alarms["alarm_id"].isin(ev.alarm_ids)]
            seed_rows = self.alarms[self.alarms["alarm_id"].isin(ev.seed_alarm_ids)]
            candidates: dict[str, RootCandidate] = {}

            def cand(name: str) -> RootCandidate:
                if name not in candidates:
                    candidates[name] = RootCandidate(kind="service", name=name, score=0.0)
                return candidates[name]

            blames = Counter()
            for b in rows["blame"]:
                if isinstance(b, str) and b:
                    blames[b] += 1
            # layer blame: db_write_fail on S points at S's DB dependencies
            # (a tablespace failure belongs to the database layer)
            for _, row in seed_rows[seed_rows["alarm_type"] == "db_write_fail"].iterrows():
                for dep in self.graph.deps_of.get(row["service"], ()):
                    if dep in self.graph.nodes and dep.endswith("-db"):
                        blames[dep] += 1

            earliest: dict[str, pd.Timestamp] = {}
            for _, row in seed_rows.iterrows():
                c = cand(row["service"])
                c.markers += 1
                earliest[row["service"]] = min(earliest.get(row["service"], row["timestamp"]), row["timestamp"])
                if isinstance(row["blame"], str) and row["blame"]:
                    cb = cand(row["blame"])
                    cb.blames += 1

            affected = set(rows["service"])
            ROOTISH = {"disk_full", "db_write_fail", "oom_risk", "gc_pressure",
                       "network_down", "pkt_loss", "ext_slow", "ext_unreach"}
            # does this candidate sit below a failing DB? then its db-layer
            # failures are derived, not root
            def db_discount(name: str) -> float:
                for dep in self.graph.deps_of.get(name, ()):
                    if dep.endswith("-db") and dep != name:
                        if (seed_rows["service"] == dep).any():
                            return 0.5
                return 1.0

            for name, c in candidates.items():
                tcount = Counter(seed_rows[seed_rows["service"] == name]["alarm_type"])
                disc = db_discount(name)
                weighted = sum(
                    (3.0 if (t in ROOTISH or (t == "db_conn_pool" and name.endswith("-db"))) else 1.0)
                    * (disc if t in ("db_write_fail", "db_conn_pool") else 1.0) * n
                    for t, n in tcount.items()
                )
                c.markers = int(sum(tcount.values()))
                c.blames += blames.get(name, 0)
                c.explains = len(affected & self.graph.transitive_dependents(name) - {name})
                svc_rows = rows[rows["service"] == name]
                c.sev5 = int((svc_rows["severity"] == 5).sum())
                c.first_ts = (earliest.get(name) or svc_rows["timestamp"].min()).strftime("%H:%M:%S")
                t0 = ev.start or rows["timestamp"].min()
                span = max(1.0, (ev.end - t0).total_seconds() / 60)
                earliness = 1.0 - min(1.0, (earliest.get(name, t0) - t0).total_seconds() / 60 / span)
                # upstream penalty: if this candidate itself depends on another
                # failing candidate, its failure is explainable from upstream
                upstream = sum(
                    1 for other in candidates
                    if other != name and other in self.graph.transitive_deps(name)
                    and candidates[other].markers > 0
                )
                c.score = (min(weighted, 120.0)
                           + 1.0 * min(c.blames, 40)
                           + 1.0 * min(c.explains, 15)
                           + 2.0 * earliness
                           + 0.15 * c.sev5
                           - 6.0 * upstream)

            # rack promotion: network markers concentrated in a single rack
            net_seed = seed_rows[seed_rows["alarm_type"].isin(NETWORK_TYPES)]
            rack_ev = None
            if len(net_seed) >= self.cfg.min_rack_net_markers:
                rc = Counter(net_seed["rack_key"])
                top_rack, top_n = rc.most_common(1)[0]
                if top_n / len(net_seed) >= self.cfg.rack_net_concentration:
                    rack_hosts = self.ds.inventory[
                        (self.ds.inventory["veri_merkezi"] + "/" + self.ds.inventory["kabin"]) == top_rack
                    ]["servis"].tolist()
                    explains = len(affected & set(rack_hosts))
                    rack_ev = RootCandidate(
                        kind="rack", name=top_rack,
                        score=(3.0 * top_n + 1.5 * explains + 2.0 * min(len(net_seed), 40) / 5),
                        markers=int(top_n), explains=explains,
                        first_ts=net_seed["timestamp"].min().strftime("%H:%M:%S"),
                    )
            # counter-hypotheses must exist on every card: single-service seeds
            # (slow burns, external gateways) leave no runner-up candidates, so
            # fill them from the affected services with measured evidence
            def fill_counters(ranked: list[RootCandidate], root: RootCandidate | None) -> list[RootCandidate]:
                out = list(ranked[:2])
                if len(out) >= 2 or root is None:
                    return out
                pool = [s for s in affected if s not in candidates and s != root.name]
                scored = []
                for s in pool:
                    srows = rows[rows["service"] == s]
                    if srows.empty:
                        continue
                    b = int(blames.get(s, 0))
                    expl = len(self.graph.transitive_dependents(s) & affected - {s})
                    sc = 1.0 * b + 0.5 * len(srows) + 1.0 * min(expl, 15)
                    scored.append(RootCandidate(
                        kind="service", name=s, score=sc, blames=b, explains=expl,
                        first_ts=srows["timestamp"].min().strftime("%H:%M:%S")))
                scored.sort(key=lambda c: -c.score)
                return out + scored[: 2 - len(out)]

            if rack_ev and (not candidates or rack_ev.score >= max(c.score for c in candidates.values()) * 0.8):
                ev.root = rack_ev
                ranked = sorted(candidates.values(), key=lambda c: -c.score)[:2]
                ev.counters = fill_counters(ranked, rack_ev)
            else:
                ranked = sorted(candidates.values(), key=lambda c: -c.score)
                ev.root = ranked[0] if ranked else None
                ev.counters = fill_counters(ranked[1:3], ev.root)
            self._dbg(
                "event %d root=%s (%.1f) counters=%s",
                ev.idx, ev.root.name if ev.root else "?", ev.root.score if ev.root else -1,
                [c.name for c in ev.counters],
            )

    # 5 ------------------------------------------------------- noise audit
    def audit_noise(self, events: list[Event]) -> pd.DataFrame:
        attached = {aid for ev in events for aid in ev.alarm_ids}
        noise = self.alarms[~self.alarms["alarm_id"].isin(attached)].copy()
        margin = timedelta(minutes=self.cfg.attach_margin_min)
        windows = [(ev, ev.start - margin, ev.end + margin, set(ev.services)) for ev in events]

        reasons: list[str] = []
        for _, row in noise.iterrows():
            why: list[str] = []
            overlapping = [ev for ev, s, e, _ in windows if s <= row["timestamp"] <= e]
            if not overlapping:
                why.append("no_time_overlap")
            if row["alarm_id"] not in self.anomalous:
                why.append("below_anomaly_threshold")
            linked = False
            cand = {row["service"]}
            if isinstance(row["blame"], str) and row["blame"]:
                cand.add(row["blame"])
            for ev, _, _, svc in windows:
                if ev in overlapping and any(
                    self.graph.min_distance(c, svc, self.cfg.attach_dist) <= self.cfg.attach_dist for c in cand
                ):
                    linked = True
                    break
            if overlapping and not linked:
                why.append("no_topology_link")
            if not why:
                # inside a window and topologically linked, yet not attached:
                # either a sibling event claimed it, or the core-evidence gate
                # (attach policy) deliberately left it out
                why.append("not_core_evidence" if self.cfg.require_core_attach
                           else "outcompeted")
            reasons.append("+".join(why))
        noise["noise_reason"] = reasons
        reason_counts = Counter(r for rs in reasons for r in rs.split("+"))
        self._dbg("noise alarms: %d, reasons: %s", len(noise), dict(reason_counts))
        return noise, dict(reason_counts)

    # ------------------------------------------------------------- run all
    def run(self) -> EngineResult:
        self.flag_anomalies()
        seeds = self.build_seeds()
        events = self.attach(seeds)
        self.score_roots(events)
        noise, reason_counts = self.audit_noise(events)
        totals = {
            "total_alarms": int(len(self.alarms)),
            "event_alarms": int(sum(len(e.alarm_ids) for e in events)),
            "event_count": len(events),
            "noise_alarms": int(len(noise)),
            "anomalous_alarms": int(len(self.anomalous)),
            "reduction": f"{len(self.alarms)} alarm -> {len(events)} kart",
        }
        return EngineResult(events=events, noise=noise, noise_reason_counts=reason_counts, totals=totals)
