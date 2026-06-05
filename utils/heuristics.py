from __future__ import annotations


def manhattan(pos: tuple[int, int], goal: tuple[int, int]) -> int:
    """Admissible heuristic: straight-line Manhattan distance."""
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
