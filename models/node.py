from __future__ import annotations


class Node:
    """A search node holding state, path cost, parent link, and the action that produced it."""

    def __init__(
        self,
        state: tuple,
        g: int | float = 0,
        parent: Node | None = None,
        action: str | None = None,
    ):
        self.state = state
        self.g = g
        self.parent = parent
        self.action = action

    # ── path reconstruction ──────────────────────────────────────────────────

    def path(self) -> list[Node]:
        """Returns the list of nodes from root to self."""
        nodes: list[Node] = []
        cur: Node | None = self
        while cur is not None:
            nodes.append(cur)
            cur = cur.parent
        return list(reversed(nodes))

    def actions(self) -> list[str]:
        """Returns the sequence of actions from root to self (excludes None for root)."""
        return [n.action for n in self.path() if n.action is not None]

    # ── heap support ─────────────────────────────────────────────────────────

    def __lt__(self, other: Node) -> bool:
        return self.g < other.g

    def __repr__(self) -> str:
        return f"Node(state={self.state}, g={self.g}, action={self.action!r})"
