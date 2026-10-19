import math

import pygame

MAX_CELL = 48
GRID_LINE = (60, 60, 60)
WALL_EDGE = (75, 75, 75)
EXPLORED = (60, 120, 220)
COIN = (240, 190, 40)
COIN_EDGE = (150, 110, 10)
STAR = (230, 60, 60)
AGENT = (255, 215, 0)
INK = (20, 20, 20)
BANNER = (190, 40, 40)
WHITE = (255, 255, 255)


class MapView:
    # converte posicoes do grid em pixels dentro da area do mapa
    def __init__(self, grid, area):
        self.grid = grid
        self.cell = min(area.w // grid.cols, area.h // grid.rows, MAX_CELL)
        width, height = self.cell * grid.cols, self.cell * grid.rows
        self.origin = (area.x + (area.w - width) // 2, area.y + (area.h - height) // 2)
        self.rect = pygame.Rect(self.origin, (width, height))

    def cell_rect(self, pos):
        r, c = pos
        return pygame.Rect(self.origin[0] + c * self.cell, self.origin[1] + r * self.cell, self.cell, self.cell)

    def center(self, pos):
        return self.cell_rect(pos).center

    def cell_at(self, point):
        if not self.rect.collidepoint(point):
            return None
        return ((point[1] - self.origin[1]) // self.cell, (point[0] - self.origin[0]) // self.cell)


def draw_map(surface, view):
    grid = view.grid
    for r in range(grid.rows):
        for c in range(grid.cols):
            rect = view.cell_rect((r, c))
            terrain = grid.terrain((r, c))
            pygame.draw.rect(surface, terrain.color, rect)
            if terrain.walkable:
                pygame.draw.rect(surface, GRID_LINE, rect, 1)
            else:
                # parede com borda interna, lembrando o simbolo de bloco
                pygame.draw.rect(surface, WALL_EDGE, rect.inflate(-4, -4), 2)


def draw_explored(surface, view, cells, alpha=90):
    shade = pygame.Surface((view.cell, view.cell), pygame.SRCALPHA)
    shade.fill((*EXPLORED, alpha))
    for pos in cells:
        surface.blit(shade, view.cell_rect(pos))


def draw_path(surface, view, path, color, width=4, offset=0):
    if len(path) < 2:
        return
    points = [(x + offset, y + offset) for x, y in (view.center(p) for p in path)]
    pygame.draw.lines(surface, color, False, points, width)


def draw_rewards(surface, view, rewards, font):
    radius = max(view.cell // 3, 4)
    for pos in rewards:
        center = view.center(pos)
        pygame.draw.circle(surface, COIN, center, radius)
        pygame.draw.circle(surface, COIN_EDGE, center, radius, 2)
        text = font.render("$", True, COIN_EDGE)
        surface.blit(text, text.get_rect(center=center))


def draw_goal(surface, view, pos):
    cx, cy = view.center(pos)
    outer, inner = view.cell * 0.42, view.cell * 0.18
    points = []
    for i in range(10):
        radius = outer if i % 2 == 0 else inner
        angle = -math.pi / 2 + i * math.pi / 5
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    pygame.draw.polygon(surface, STAR, points)
    pygame.draw.polygon(surface, INK, points, 1)


def draw_agent(surface, view, pos):
    # carinha desenhada com formas, nem toda fonte tem o caractere do rosto
    cx, cy = view.center(pos)
    radius = max(int(view.cell * 0.4), 5)
    pygame.draw.circle(surface, AGENT, (cx, cy), radius)
    pygame.draw.circle(surface, INK, (cx, cy), radius, 2)
    eye = max(radius // 6, 1)
    pygame.draw.circle(surface, INK, (cx - radius // 3, cy - radius // 4), eye)
    pygame.draw.circle(surface, INK, (cx + radius // 3, cy - radius // 4), eye)
    mouth = pygame.Rect(0, 0, radius, int(radius / 1.6))
    mouth.center = (cx, cy + radius // 5)
    pygame.draw.arc(surface, INK, mouth, math.pi, 2 * math.pi, 2)


def draw_banner(surface, area, text, font):
    label = font.render(text, True, WHITE)
    box = label.get_rect(center=area.center).inflate(40, 24)
    pygame.draw.rect(surface, BANNER, box, border_radius=8)
    surface.blit(label, label.get_rect(center=box.center))
