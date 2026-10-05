"""Directed-graph helpers the rules share."""

from collections import defaultdict
from collections.abc import Iterable, Iterator


def cycles(edges: Iterable[tuple[str, str]]) -> tuple[tuple[str, ...], ...]:
    """Every strongly connected component of two or more nodes, each sorted, in sorted order.

    Tarjan's algorithm, iterative: an import chain thousands of files deep must
    not hit the recursion limit.
    """
    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in edges:
        adjacency[source].append(target)
        adjacency.setdefault(target, [])
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    found: list[tuple[str, ...]] = []

    def visit(node: str) -> None:
        index[node] = low[node] = len(index)
        stack.append(node)
        on_stack.add(node)

    for start in list(adjacency):
        if start in index:
            continue
        visit(start)
        work: list[tuple[str, Iterator[str]]] = [(start, iter(adjacency[start]))]
        while work:
            node, children = work[-1]
            child = next((c for c in children if c not in index or c in on_stack), None)
            if child is not None and child not in index:
                visit(child)
                work.append((child, iter(adjacency[child])))
                continue
            if child is not None:
                low[node] = min(low[node], index[child])
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                component = [stack.pop()]
                while component[-1] != node:
                    component.append(stack.pop())
                on_stack.difference_update(component)
                if len(component) > 1:
                    found.append(tuple(sorted(component)))
    return tuple(sorted(found))
