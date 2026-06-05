from __future__ import annotations
import heapq
from models.map_grid import MapGrid
from models.node import Node
from utils.heuristics import manhattan


def astar(grid: MapGrid) -> dict | None:
    """A* Search for scenarios 1 (no zones) and 2 (with Z zones).

    f(n) = g(n) + h(n)
      g(n) = elapsed minutes (accumulated entry costs)
      h(n) = Manhattan distance to goal — admissible because min entry cost is 1/cell,
             and consistent because one step changes Manhattan by at most 1 while cost >= 1.

    State and STAY logic are identical to UCS; only the heap key changes.
    """
    starts = grid.find_starts()
    goals = grid.find_goals()

    start_pos = next(iter(starts.values()))
    goal_pos = next(iter(goals.values()))

    use_zones = grid.has_zones()

    def make_state(r: int, c: int, T: int) -> tuple:
        return (r, c, T % 30) if use_zones else (r, c)

    def h(r: int, c: int) -> int:
        return manhattan((r, c), goal_pos)

    root = Node(state=make_state(*start_pos, 0), g=0)
    counter = 0
    # heap entries: (f, tie_counter, node)
    frontier: list = [(h(*start_pos), counter, root)]
    visited: set[tuple] = set()
    expanded = 0

    while frontier:
        _, _, node = heapq.heappop(frontier)

        if node.state in visited:
            continue
        visited.add(node.state)
        expanded += 1

        r, c = node.state[0], node.state[1]
        T = node.g  # elapsed minutes == accumulated g

        if (r, c) == goal_pos:
            return {'cost': node.g, 'actions': node.actions(), 'expanded': expanded}

        # ── move actions ────────────────────────────────────────────────────────
        for action, nr, nc in grid.neighbors(r, c):
            cost = grid.entry_cost(nr, nc, T)
            new_g = node.g + cost
            new_state = make_state(nr, nc, new_g)
            if new_state not in visited:
                counter += 1
                child = Node(new_state, new_g, node, action)
                heapq.heappush(frontier, (new_g + h(nr, nc), counter, child))

        # ── STAY action ─────────────────────────────────────────────────────────
        if use_zones:
            new_g = node.g + 1
            new_state = make_state(r, c, new_g)
            if new_state not in visited:
                counter += 1
                child = Node(new_state, new_g, node, 'STAY')
                heapq.heappush(frontier, (new_g + h(r, c), counter, child))

    return None
