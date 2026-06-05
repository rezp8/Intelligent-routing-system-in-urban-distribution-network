from __future__ import annotations
from models.map_grid import MapGrid


def idastar(grid: MapGrid) -> dict | None:
    """IDA* for scenario 4: grid with bridge cells (Bk).

    State: (row, col, bridge_chain_id)
      bridge_chain_id = None   → agent is not on any bridge
      bridge_chain_id = int    → agent is on this chain (next step on same chain is free)

    Heuristic: h = 0
      Manhattan distance is NOT admissible for general bridge maps — a Bk chain of
      length L costs k total, but Manhattan counts L steps.  If k < L the heuristic
      would overestimate.  h = 0 is trivially admissible and guarantees optimality.

    Loop prevention: set of states on the current DFS path (no global visited set).
    This is correct for IDA*: a state that was visited on a different branch may be
    reachable at lower cost via the current branch, so global pruning would miss it.
    """
    starts = grid.find_starts()
    goals = grid.find_goals()

    start_pos = next(iter(starts.values()))
    goal_pos = next(iter(goals.values()))

    sr, sc = start_pos
    start_chain = grid.bridge_chain_id(sr, sc)
    initial_state = (sr, sc, start_chain)

    _found: dict = {}
    _expanded = [0]

    def _dfs(
        r: int,
        c: int,
        chain: int | None,
        g: int,
        threshold: int,
        on_path: set,
        actions: list[str],
    ) -> int | float:
        """Depth-limited DFS on cost.

        Returns:
          -1             → goal found; result stored in _found
          int / inf      → minimum f that exceeded threshold (next threshold candidate)
        """
        f = g  # h = 0

        if f > threshold:
            return f

        _expanded[0] += 1

        if (r, c) == goal_pos:
            _found['cost'] = g
            _found['actions'] = actions[:]
            return -1

        minimum: int | float = float('inf')

        for action, nr, nc in grid.neighbors(r, c):
            cost = grid.entry_cost(nr, nc, T=0, current_bridge_chain=chain)
            new_chain = grid.bridge_chain_id(nr, nc)
            new_state = (nr, nc, new_chain)

            if new_state in on_path:
                continue

            on_path.add(new_state)
            actions.append(action)

            t = _dfs(nr, nc, new_chain, g + cost, threshold, on_path, actions)

            if t == -1:
                return -1   # propagate: solution found, unwind without cleanup

            if t < minimum:
                minimum = t

            actions.pop()
            on_path.discard(new_state)

        return minimum

    threshold = 0

    while True:
        _found.clear()
        _expanded[0] = 0
        on_path = {initial_state}

        t = _dfs(sr, sc, start_chain, 0, threshold, on_path, [])

        if t == -1:
            return {
                'cost': _found['cost'],
                'actions': _found['actions'],
                'expanded': _expanded[0],
            }

        if t == float('inf'):
            return None

        threshold = t
