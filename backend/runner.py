from backend.search.astar import astar
from backend.search.bfs import bfs
from backend.search.dfs import dfs
from backend.search.greedy import greedy

ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "Gulosa": greedy,
    "A*": astar,
}

# uma cor fixa por algoritmo, usada nos graficos e na interface
COLORS = {"BFS": "#2a78d6", "DFS": "#eb6834", "Gulosa": "#1baf7a", "A*": "#eda100"}


def run(name, scenario, repeats=1):
    # repete a busca e usa a media do tempo, pois um mapa pequeno roda em fracoes de ms
    search = ALGORITHMS[name]
    total_ms = 0.0
    for _ in range(repeats):
        result = search(scenario)
        total_ms += result.time_ms
    result.time_ms = total_ms / repeats
    return result


def run_all(scenario, repeats=1):
    return [run(name, scenario, repeats) for name in ALGORITHMS]
