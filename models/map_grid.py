from __future__ import annotations
import re
from collections import deque


class MapGrid:
    DIRECTIONS = {
        'UP':    (-1,  0),
        'DOWN':  ( 1,  0),
        'LEFT':  ( 0, -1),
        'RIGHT': ( 0,  1),
    }

    def __init__(self, rows: int, cols: int, grid: list[list[str]]):
        self.rows = rows
        self.cols = cols
        self.grid = grid
        self._bridge_chains: dict[tuple[int, int], int] = {}
        self._bridge_costs: dict[tuple[int, int], int] = {}
        self._compute_bridge_chains()

    # ── construction ────────────────────────────────────────────────────────

    @classmethod
    def from_file(cls, filepath: str) -> MapGrid:
        with open(filepath, encoding='utf-8') as f:
            return cls._parse(f.read())

    @classmethod
    def from_string(cls, text: str) -> MapGrid:
        return cls._parse(text)

    @classmethod
    def _parse(cls, text: str) -> MapGrid:
        lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
        rows, cols = map(int, lines[0].split())
        grid = [lines[i + 1].split() for i in range(rows)]
        return cls(rows, cols, grid)

    # ── bounds & cell type ───────────────────────────────────────────────────

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def cell(self, r: int, c: int) -> str:
        return self.grid[r][c]

    def is_start(self, r: int, c: int) -> bool:
        v = self.grid[r][c]
        return v == 'S' or (len(v) > 1 and v[0] == 'S' and v[1:].isdigit())

    def is_goal(self, r: int, c: int) -> bool:
        v = self.grid[r][c]
        return v == 'G' or (len(v) > 1 and v[0] == 'G' and v[1:].isdigit())

    def is_bridge(self, r: int, c: int) -> bool:
        return (r, c) in self._bridge_costs

    def is_zone(self, r: int, c: int) -> bool:
        return self.grid[r][c] == 'Z'

    def has_zones(self) -> bool:
        return any(
            self.grid[r][c] == 'Z'
            for r in range(self.rows)
            for c in range(self.cols)
        )

    def has_bridges(self) -> bool:
        return bool(self._bridge_costs)

    # ── bridge info ──────────────────────────────────────────────────────────

    def bridge_chain_id(self, r: int, c: int) -> int | None:
        return self._bridge_chains.get((r, c))

    def bridge_k(self, r: int, c: int) -> int:
        return self._bridge_costs.get((r, c), 0)

    # ── cost ─────────────────────────────────────────────────────────────────
    #
    # current_bridge_chain: the chain id the agent is currently ON (None if not on a bridge).
    # Passing it lets entry_cost return 0 when the agent stays within the same bridge chain.

    def entry_cost(
        self,
        r: int,
        c: int,
        T: int = 0,
        current_bridge_chain: int | None = None,
    ) -> int:
        if self.is_start(r, c) or self.is_goal(r, c):
            return 1
        if self.is_zone(r, c):
            return 1 if (T % 30) < 15 else 15
        if self.is_bridge(r, c):
            chain = self._bridge_chains[(r, c)]
            return 0 if chain == current_bridge_chain else self._bridge_costs[(r, c)]
        return int(self.grid[r][c])

    # ── navigation ───────────────────────────────────────────────────────────

    def neighbors(self, r: int, c: int) -> list[tuple[str, int, int]]:
        """Returns [(action, nr, nc), ...] for all in-bounds moves (no STAY)."""
        result = []
        for action, (dr, dc) in self.DIRECTIONS.items():
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc):
                result.append((action, nr, nc))
        return result

    # ── entity lookup ────────────────────────────────────────────────────────

    def find_starts(self) -> dict[str, tuple[int, int]]:
        """Returns {'S': (r,c)} or {'S1': (r,c), 'S2': (r,c), ...}."""
        return {
            self.grid[r][c]: (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.is_start(r, c)
        }

    def find_goals(self) -> dict[str, tuple[int, int]]:
        """Returns {'G': (r,c)} or {'G1': (r,c), 'G2': (r,c), ...}."""
        return {
            self.grid[r][c]: (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.is_goal(r, c)
        }

    # ── bridge preprocessing ─────────────────────────────────────────────────
    #
    # Connected components of same-k bridge cells get the same chain_id.
    # Entering a chain costs k; staying on the same chain costs 0.

    def _compute_bridge_chains(self):
        chain_id = 0
        visited: set[tuple[int, int]] = set()
        for r in range(self.rows):
            for c in range(self.cols):
                m = re.match(r'^B(\d+)$', self.grid[r][c])
                if m and (r, c) not in visited:
                    k = int(m.group(1))
                    queue: deque[tuple[int, int]] = deque([(r, c)])
                    visited.add((r, c))
                    while queue:
                        cr, cc = queue.popleft()
                        self._bridge_chains[(cr, cc)] = chain_id
                        self._bridge_costs[(cr, cc)] = k
                        for _, nr, nc in self.neighbors(cr, cc):
                            nv = self.grid[nr][nc]
                            nm = re.match(r'^B(\d+)$', nv)
                            if nm and int(nm.group(1)) == k and (nr, nc) not in visited:
                                visited.add((nr, nc))
                                queue.append((nr, nc))
                    chain_id += 1

    def __str__(self) -> str:
        lines = [f"{self.rows} {self.cols}"]
        for row in self.grid:
            lines.append(' '.join(row))
        return '\n'.join(lines)

    def __repr__(self) -> str:
        return f"MapGrid({self.rows}x{self.cols})"
