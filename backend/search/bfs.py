from collections import deque

from backend.search.common import Stats, build_result, reconstruct_path


def bfs(scenario):
    grid, start, goal = scenario.grid, scenario.start, scenario.goal
    stats = Stats()

    # fila fifo, parent tambem serve como conjunto de visitados
    frontier = deque([start])
    parent = {start: None}
    stats.generated = 1
    stats.update_frontier(1)

    while frontier:
        current = frontier.popleft()
        stats.expand(current)

        if current == goal:
            return build_result("BFS", scenario, stats, reconstruct_path(parent, current))

        for nxt in grid.neighbors(current):
            if nxt not in parent:
                parent[nxt] = current
                frontier.append(nxt)
                stats.generated += 1
        stats.update_frontier(len(frontier))

    # fronteira vazia: nao ha caminho
    return build_result("BFS", scenario, stats, None)
