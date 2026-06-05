from __future__ import annotations
from models.map_grid import MapGrid

# TODO: علیرضا نصیری
#
# State:  (row, col)              — if map has no Z tiles
#         (row, col, T mod 30)    — if map has Z tiles
#
# Frontier: min-heap on g(n) — use heapq (not a ready-made search library)
# Visited:  set of states already expanded
#
# STAY action: cost = 1, state unchanged (only (row, col) part, T still advances)
#
# Return format:
#   {'cost': int, 'actions': list[str], 'expanded': int}
#   or None if no solution


def ucs(grid: MapGrid) -> dict | None:
    raise NotImplementedError("UCS not implemented yet — assigned to علیرضا نصیری")
