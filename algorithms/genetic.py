from __future__ import annotations
import random
from models.map_grid import MapGrid
from utils.heuristics import manhattan


# ── chromosome encoding ───────────────────────────────────────────────────────
#
# Chromosome = permutation of length (num_goals + num_agents - 1).
#   items  0 .. num_goals-1          → goal indices
#   items  num_goals .. chrom_len-1  → separator tokens (one per agent boundary)
#
# Reading left-to-right: goals before the first separator go to agent 0,
# between first and second separator go to agent 1, and so on.
# The relative order of goal indices within a segment defines the visit sequence.
#
# Example — 2 agents, goals [G1, G2]:
#   [0, SEP, 1]  →  S1: [G1],      S2: [G2]   makespan = max(3, 2) = 3  ✓
#   [SEP, 0, 1]  →  S1: [],        S2: [G1,G2]
#   [0, 1, SEP]  →  S1: [G1, G2],  S2: []
# ─────────────────────────────────────────────────────────────────────────────


def _route_time(start: tuple[int, int], goal_positions: list[tuple[int, int]]) -> int:
    """Sum of Manhattan distances: start → g1 → g2 → …"""
    t, pos = 0, start
    for gpos in goal_positions:
        t += manhattan(pos, gpos)
        pos = gpos
    return t


def _decode(
    chrom: list[int],
    num_agents: int,
    goal_keys: list[str],
) -> list[list[str]]:
    m = len(goal_keys)
    buckets: list[list[str]] = [[] for _ in range(num_agents)]
    agent = 0
    for item in chrom:
        if item >= m:                            # separator token
            agent = min(agent + 1, num_agents - 1)
        else:
            buckets[agent].append(goal_keys[item])
    return buckets


def _makespan(
    chrom: list[int],
    num_agents: int,
    goal_keys: list[str],
    starts: dict[str, tuple[int, int]],
    goal_coords: dict[str, tuple[int, int]],
    agent_names: list[str],
) -> int:
    buckets = _decode(chrom, num_agents, goal_keys)
    worst = 0
    for i, name in enumerate(agent_names):
        t = _route_time(starts[name], [goal_coords[g] for g in buckets[i]])
        if t > worst:
            worst = t
    return worst


# ── genetic operators ─────────────────────────────────────────────────────────

def _ox_crossover(p1: list[int], p2: list[int]) -> list[int]:
    """Order Crossover (OX1) — preserves relative order from both parents."""
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))
    child: list[int | None] = [None] * n
    child[a:b + 1] = p1[a:b + 1]
    segment = set(p1[a:b + 1])
    fill = [x for x in p2 if x not in segment]
    j = 0
    for i in range(n):
        if child[i] is None:
            child[i] = fill[j]
            j += 1
    return child  # type: ignore[return-value]


def _mutate(chrom: list[int], rate: float) -> list[int]:
    """Swap-mutation: exchange two random positions."""
    chrom = chrom[:]
    if random.random() < rate:
        i, j = random.sample(range(len(chrom)), 2)
        chrom[i], chrom[j] = chrom[j], chrom[i]
    return chrom


def _tournament(
    population: list[list[int]],
    scores: list[int],
    k: int,
) -> list[int]:
    """Return the chromosome with the lowest makespan among k random candidates."""
    candidates = random.sample(range(len(population)), k)
    best = min(candidates, key=lambda i: scores[i])
    return population[best]


# ── entry point ───────────────────────────────────────────────────────────────

def genetic(
    grid: MapGrid,
    pop_size: int = 150,
    generations: int = 400,
    mutation_rate: float = 0.15,
    tournament_k: int = 3,
    seed: int | None = None,
) -> dict | None:
    if seed is not None:
        random.seed(seed)

    starts = grid.find_starts()
    goal_coords = grid.find_goals()

    if not starts or not goal_coords:
        return None

    agent_names = sorted(starts.keys())
    goal_keys = sorted(goal_coords.keys())
    num_agents = len(agent_names)
    num_goals = len(goal_keys)

    # chromosome = goals (0..m-1) + separators (m..m+k-2)
    base = list(range(num_goals + num_agents - 1))

    def score(chrom: list[int]) -> int:
        return _makespan(chrom, num_agents, goal_keys, starts, goal_coords, agent_names)

    # ── initialise ────────────────────────────────────────────────────────────
    population = [random.sample(base, len(base)) for _ in range(pop_size)]
    scores = [score(c) for c in population]

    best_idx = min(range(pop_size), key=lambda i: scores[i])
    best_chrom = population[best_idx][:]
    best_score = scores[best_idx]

    # ── evolve ────────────────────────────────────────────────────────────────
    for _ in range(generations):
        new_pop: list[list[int]] = [best_chrom[:]]   # elitism

        while len(new_pop) < pop_size:
            p1 = _tournament(population, scores, tournament_k)
            p2 = _tournament(population, scores, tournament_k)
            child = _ox_crossover(p1, p2)
            child = _mutate(child, mutation_rate)
            new_pop.append(child)

        population = new_pop
        scores = [score(c) for c in population]

        gen_best = min(range(pop_size), key=lambda i: scores[i])
        if scores[gen_best] < best_score:
            best_score = scores[gen_best]
            best_chrom = population[gen_best][:]

    # ── build result ──────────────────────────────────────────────────────────
    best_buckets = _decode(best_chrom, num_agents, goal_keys)
    assignments: dict = {}
    for i, name in enumerate(agent_names):
        targets = best_buckets[i]
        assignments[name] = {
            'start': starts[name],
            'targets': targets,
            'coords': [goal_coords[g] for g in targets],
        }

    return {'makespan': float(best_score), 'assignments': assignments}
