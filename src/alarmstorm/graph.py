"""Service dependency graph utilities.

Direction convention (from VERI_SOZLUGU.md): edge kaynak_servis -> hedef_servis
means "kaynak depends on hedef". If hedef breaks, kaynak is affected.
All distance queries run on the UNDIRECTED projection for correlation,
while explainability (who is affected when X breaks) uses the directed view.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable

INF = 10**9


class DepGraph:
    def __init__(self, edges: Iterable[tuple[str, str]], nodes: Iterable[str] | None = None):
        self.adj: dict[str, set[str]] = defaultdict(set)      # undirected
        self.deps_of: dict[str, set[str]] = defaultdict(set)  # svc -> services it depends on
        self.dependents_of: dict[str, set[str]] = defaultdict(set)  # svc -> services depending on it
        self.nodes: set[str] = set(nodes or [])
        for src, dst in edges:
            self.nodes.update((src, dst))
            self.adj[src].add(dst)
            self.adj[dst].add(src)
            self.deps_of[src].add(dst)
            self.dependents_of[dst].add(src)

    def distance(self, a: str, b: str, max_dist: int = 4) -> int:
        """Undirected hop distance, capped; returns INF when beyond cap."""
        if a == b:
            return 0
        seen = {a}
        q: deque[tuple[str, int]] = deque([(a, 0)])
        while q:
            cur, d = q.popleft()
            if d >= max_dist:
                continue
            for nxt in self.adj.get(cur, ()):
                if nxt == b:
                    return d + 1
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, d + 1))
        return INF

    def min_distance(self, a: str, others: Iterable[str], max_dist: int = 4) -> int:
        best = INF
        for o in others:
            d = self.distance(a, o, max_dist)
            if d < best:
                best = d
            if best == 0:
                break
        return best

    def transitive_dependents(self, svc: str) -> set[str]:
        """All services (transitively) affected if `svc` breaks."""
        out: set[str] = set()
        q: deque[str] = deque([svc])
        while q:
            cur = q.popleft()
            for dep in self.dependents_of.get(cur, ()):  # src depends on cur
                if dep not in out:
                    out.add(dep)
                    q.append(dep)
        return out

    def transitive_deps(self, svc: str) -> set[str]:
        """All services `svc` transitively depends on."""
        out: set[str] = set()
        q: deque[str] = deque([svc])
        while q:
            cur = q.popleft()
            for dep in self.deps_of.get(cur, ()):
                if dep not in out:
                    out.add(dep)
                    q.append(dep)
        return out
