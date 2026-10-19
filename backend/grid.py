from backend.terrain import Terrain

# ordem fixa: cima, direita, baixo, esquerda
DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class Grid:
    def __init__(self, cells):
        # cells e uma matriz de Terrain, acessada por (linha, coluna)
        self.cells = cells
        self.rows = len(cells)
        self.cols = len(cells[0])

    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def terrain(self, pos):
        r, c = pos
        return self.cells[r][c]

    def is_wall(self, pos):
        return not self.terrain(pos).walkable

    def cost(self, pos):
        # custo de entrar na celula
        return self.terrain(pos).cost

    def neighbors(self, pos):
        r, c = pos
        result = []
        for dr, dc in DIRECTIONS:
            nxt = (r + dr, c + dc)
            if self.in_bounds(nxt) and not self.is_wall(nxt):
                result.append(nxt)
        return result

    def path_cost(self, path):
        # soma o custo de cada passo, sem contar a celula inicial
        return sum(self.cost(p) for p in path[1:])

    def free_cells(self):
        return sum(1 for row in self.cells for t in row if t.walkable)
