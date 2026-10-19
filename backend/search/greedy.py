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


def greedy(scenario):
    start, goal = scenario.start, scenario.goal
    index = reward_index(scenario)
    stats = Stats()

    def h(state):
        pos, mask = state
        if pos == goal:
            return 0
        return reward_heuristic(pos, goal, remaining_rewards(index, mask), scenario.reward_value)

    start_state = (start, collect(index, start, 0))
    # prioridade so pela heuristica, sem considerar o custo ja gasto
    tie = count()
    frontier = [(h(start_state), next(tie), start_state)]
    parent = {start_state: None}
    stats.generated = 1
    stats.update_frontier(1)

    while frontier:
        _, _, state = heapq.heappop(frontier)
        stats.expand(state[0])

        if state[0] == goal:
            path = [s[0] for s in reconstruct_path(parent, state)]
            return build_result("Gulosa", scenario, stats, path)

        # g nao importa aqui, so os estados vizinhos
        for nxt, _ in successors(scenario, index, state, 0):
            if nxt not in parent:
                parent[nxt] = state
                heapq.heappush(frontier, (h(nxt), next(tie), nxt))
                stats.generated += 1
        stats.update_frontier(len(frontier))

    # fronteira vazia: nao ha caminho
    return build_result("Gulosa", scenario, stats, None)
