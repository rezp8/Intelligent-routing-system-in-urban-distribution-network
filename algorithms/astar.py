from __future__ import annotations
from models.map_grid import MapGrid

# TODO: علیرضا نصیری
#
# Same structure as UCS but f(n) = g(n) + h(n).
# Use manhattan() from utils.heuristics as the admissible heuristic.
#
# State:  (row, col)              — if map has no Z tiles
#         (row, col, T mod 30)    — if map has Z tiles
#
# STAY action: cost = 1 (allows waiting in front of Z to avoid the 15-min penalty)
#
# Return format:
#   {'cost': int, 'actions': list[str], 'expanded': int}
#   or None if no solution


def astar(grid: MapGrid) -> dict | None:
    raise NotImplementedError("A* not implemented yet — assigned to علیرضا نصیری")
