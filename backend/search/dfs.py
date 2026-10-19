from backend.search.common import Stats, build_result, reconstruct_path


def dfs(scenario):
    grid, start, goal = scenario.grid, scenario.start, scenario.goal
    stats = Stats()

    # pilha explicita com (posicao, pai), evita limite de recursao
    frontier = [(start, None)]
    parent = {}
    stats.generated = 1
    stats.update_frontier(1)

    while frontier:
        current, prev = frontier.pop()
        if current in parent:
            continue
        parent[current] = prev
        stats.expand(current)

        if current == goal:
            return build_result("DFS", scenario, stats, reconstruct_path(parent, current))

        # empilha invertido para explorar na ordem cima, direita, baixo, esquerda
        for nxt in reversed(grid.neighbors(current)):
            if nxt not in parent:
                frontier.append((nxt, current))
                stats.generated += 1
        stats.update_frontier(len(frontier))

    # fronteira vazia: nao ha caminho
    return build_result("DFS", scenario, stats, None)
