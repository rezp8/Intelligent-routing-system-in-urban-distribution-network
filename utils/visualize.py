from __future__ import annotations
from models.map_grid import MapGrid

_DELTA = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1), 'STAY': (0, 0)}
_ARROW = {'UP': '^', 'DOWN': 'v', 'LEFT': '<', 'RIGHT': '>', 'STAY': '*'}


def render_path(grid: MapGrid, actions: list[str]) -> str:
    """Return an ASCII grid with the solution path overlaid using direction arrows."""
    starts = grid.find_starts()
    sr, sc = next(iter(starts.values()))

    # Map each visited cell to the arrow of the action taken to leave it
    overlay: dict[tuple[int, int], str] = {}
    r, c = sr, sc
    overlay[(r, c)] = 'S'
    for action in actions:
        dr, dc = _DELTA[action]
        r, c = r + dr, c + dc
        overlay[(r, c)] = _ARROW.get(action, '?')
    overlay[(r, c)] = 'G'  # final cell is always the goal

    # Uniform column width
    cell_w = max(len(grid.cell(row, col)) for row in range(grid.rows) for col in range(grid.cols))
    cell_w = max(cell_w, 1) + 2  # padding

    rows_out = []
    for row in range(grid.rows):
        parts = []
        for col in range(grid.cols):
            raw = grid.cell(row, col)
            if (row, col) in overlay:
                token = f'[{overlay[(row, col)]}]'
            else:
                token = raw
            parts.append(token.center(cell_w))
        rows_out.append(' '.join(parts))

    sep = '-' * (grid.cols * (cell_w + 1) - 1)
    return sep + '\n' + '\n'.join(rows_out) + '\n' + sep
