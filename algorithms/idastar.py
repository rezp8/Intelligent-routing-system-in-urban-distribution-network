from __future__ import annotations
from models.map_grid import MapGrid

# TODO: رضا پیردیر
#
# IDA* — iterative-deepening A* (memory = O(depth), no global visited set)
#
# State: (row, col, bridge_chain_id)
#   bridge_chain_id = None   → agent is NOT on any bridge
#   bridge_chain_id = int    → agent is on this bridge chain (so next step is free if same chain)
#
# Cost threshold: start with h(start, goal); each iteration raises threshold to
#   the minimum f(n) that exceeded the previous threshold.
#
# Loop prevention: track the current DFS path (not a global visited set).
#   Do not revisit a state that already appears in the current path.
#
# No Z tiles in scenario 4 — T is not needed in the state.
#
# Return format:
#   {'cost': int, 'actions': list[str], 'expanded': int}
#   or None if no solution


def idastar(grid: MapGrid) -> dict | None:
    raise NotImplementedError("IDA* not implemented yet — assigned to رضا پیردیر")
