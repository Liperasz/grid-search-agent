import time

from backend.result import SearchResult

FOUND_MESSAGE = "caminho encontrado"
NOT_FOUND_MESSAGE = "nao existe caminho ate o premio"


class Stats:
    # contadores e cronometro compartilhados por todos os algoritmos
    def __init__(self):
        self.expanded = 0
        self.generated = 0
        self.max_frontier = 0
        self.explored_order = []
        self.start_time = time.perf_counter()

    def expand(self, pos):
        self.expanded += 1
        self.explored_order.append(pos)

    def update_frontier(self, size):
        self.max_frontier = max(self.max_frontier, size)

    def elapsed_ms(self):
        return (time.perf_counter() - self.start_time) * 1000


def reconstruct_path(parent, end):
    # parent mapeia estado -> estado anterior, o inicial aponta para None
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def build_result(name, scenario, stats, path):
    # path ja deve estar em posicoes (linha, coluna), ou None se nao achou
    elapsed = stats.elapsed_ms()
    result = SearchResult(
        algorithm=name,
        found=path is not None,
        message=FOUND_MESSAGE if path is not None else NOT_FOUND_MESSAGE,
        expanded=stats.expanded,
        generated=stats.generated,
        max_frontier=stats.max_frontier,
        time_ms=elapsed,
        explored_order=stats.explored_order,
    )
    if path is not None:
        result.path = path
        result.cost = scenario.grid.path_cost(path)
        # recompensas coletadas sao as que estao na rota final, sem repetir
        result.collected = list(dict.fromkeys(p for p in path if p in scenario.rewards))
    return result


# funcoes usadas pela gulosa e pelo a*, onde o estado e (posicao, mascara de recompensas)

def reward_index(scenario):
    # cada recompensa recebe um bit na mascara
    return {pos: i for i, pos in enumerate(sorted(scenario.rewards))}


def collect(index, pos, mask):
    if pos in index:
        return mask | (1 << index[pos])
    return mask


def remaining_rewards(index, mask):
    return [pos for pos, i in index.items() if not mask & (1 << i)]


def successors(scenario, index, state, g):
    # gera (proximo estado, novo g); ao chegar no premio soma a penalidade das recompensas que faltaram
    pos, mask = state
    for nxt in scenario.grid.neighbors(pos):
        new_mask = collect(index, nxt, mask)
        new_g = g + scenario.grid.cost(nxt)
        if nxt == scenario.goal:
            missed = len(index) - bin(new_mask).count("1")
            new_g += missed * scenario.reward_value
        yield (nxt, new_mask), new_g
