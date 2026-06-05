from __future__ import annotations
from models.map_grid import MapGrid

# TODO: رضا پیردیر
#
# Chromosome: assignment of goals to agents + visitation order per agent
#   e.g. for agents [S1, S2] and goals [G1, G2, G3]:
#   chromosome = [[G2, G1], [G3]]  (S1 visits G2 then G1; S2 visits G3)
#
# Fitness: -Makespan  (maximise → minimise the max route time)
#   Route time per agent = sum of Manhattan distances along their assigned path
#   Makespan = max(route_time_S1, route_time_S2, ...)
#
# Required operators (implement from scratch — no ready-made GA library):
#   - Crossover  (e.g. order crossover / PMX)
#   - Mutation   (e.g. swap two goals in an agent's list, or move a goal to another agent)
#   - Selection  (e.g. tournament selection)
#
# Return format:
#   {
#     'makespan': float,
#     'assignments': {
#       'S1': {'start': (r, c), 'targets': ['G2', 'G1'], 'coords': [(r2,c2), (r1,c1)]},
#       ...
#     }
#   }


def genetic(grid: MapGrid) -> dict | None:
    raise NotImplementedError("Genetic Algorithm not implemented yet — assigned to رضا پیردیر")
