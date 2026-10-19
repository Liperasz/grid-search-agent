def manhattan(a, b):
    # custo minimo de terreno e 1, entao manhattan nunca superestima
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reward_heuristic(pos, goal, remaining, reward_value):
    # remaining: posicoes das recompensas ainda nao coletadas
    # para cada recompensa: ou vai buscar (passa por ela e depois vai ao premio)
    # ou desiste dela e paga a penalidade, o que for mais barato
    to_goal = manhattan(pos, goal)
    best = to_goal
    for r in remaining:
        fetch = manhattan(pos, r) + manhattan(r, goal)
        skip = to_goal + reward_value
        best = max(best, min(fetch, skip))
    return best
