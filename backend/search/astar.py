import heapq
from itertools import count

from backend.heuristics import reward_heuristic
from backend.search.common import (
    Stats,
    build_result,
    collect,
    reconstruct_path,
    remaining_rewards,
    reward_index,
    successors,
)


def astar(scenario):
    start, goal = scenario.start, scenario.goal
    index = reward_index(scenario)
    stats = Stats()

    def h(state):
        pos, mask = state
        if pos == goal:
            return 0
        return reward_heuristic(pos, goal, remaining_rewards(index, mask), scenario.reward_value)

    start_state = (start, collect(index, start, 0))
    # contador desempata prioridades iguais de forma deterministica
    tie = count()
    frontier = [(h(start_state), next(tie), 0, start_state)]
    best_g = {start_state: 0}
    parent = {start_state: None}
    stats.generated = 1
    stats.update_frontier(1)

    while frontier:
        _, _, g, state = heapq.heappop(frontier)
        # entrada antiga, ja existe caminho melhor para esse estado
        if g > best_g[state]:
            continue
        stats.expand(state[0])

        if state[0] == goal:
            path = [s[0] for s in reconstruct_path(parent, state)]
            return build_result("A*", scenario, stats, path)

        for nxt, new_g in successors(scenario, index, state, g):
            if new_g < best_g.get(nxt, float("inf")):
                best_g[nxt] = new_g
                parent[nxt] = state
                heapq.heappush(frontier, (new_g + h(nxt), next(tie), new_g, nxt))
                stats.generated += 1
        stats.update_frontier(len(frontier))

    # fronteira vazia: nao ha caminho
    return build_result("A*", scenario, stats, None)
