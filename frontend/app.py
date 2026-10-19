import io
import json

import pygame

from backend.runner import ALGORITHMS, COLORS, run, run_all
from backend.scenario import load_scenario
from frontend import renderer
from frontend.panel import draw_panel, draw_table
from tools.compare import SURFACE, plt, scenario_figure

MAP_W, MAP_H = 900, 680
PANEL_W = 340
STATUS_H = 30
FPS = 60
BG = (30, 30, 32)
STATUS_TEXT = (220, 220, 215)
SPEEDS = [0.25, 0.5, 1, 2, 4, 8]
# tempo base de um passo em segundos, multiplicado conforme o custo do terreno
STEP_TIME = 0.08
# a exploracao inteira leva por volta desse tempo em velocidade x1
EXPLORE_SECONDS = 3.0
TABLE_REPEATS = 10
# deslocamento de cada rota no modo todas as rotas, para nao ficarem sobrepostas
ROUTE_OFFSETS = {"BFS": -6, "DFS": -2, "Gulosa": 2, "A*": 6}


class App:
    def __init__(self, files, index):
        pygame.init()
        pygame.display.set_caption("Trabalho 1 - Busca")
        self.screen = pygame.display.set_mode((MAP_W + PANEL_W, MAP_H + STATUS_H))
        self.clock = pygame.time.Clock()
        self.fonts = {
            "title": pygame.font.SysFont("dejavusans,arial", 19, bold=True),
            "body": pygame.font.SysFont("dejavusans,arial", 15),
            "bold": pygame.font.SysFont("dejavusans,arial", 15, bold=True),
            "small": pygame.font.SysFont("dejavusans,arial", 13),
            "banner": pygame.font.SysFont("dejavusans,arial", 24, bold=True),
        }
        self.map_area = pygame.Rect(0, 0, MAP_W, MAP_H)
        self.panel_area = pygame.Rect(MAP_W, 0, PANEL_W, MAP_H + STATUS_H)
        self.files = files
        self.index = index
        self.speed_i = SPEEDS.index(1)
        self.buttons = {}
        self.load()

    def load(self):
        self.error = None
        self.scenario = None
        self.view = None
        try:
            self.scenario = load_scenario(self.files[self.index])
            # coin_font depende do tamanho da celula do cenario
            self.view = renderer.MapView(self.scenario.grid, self.map_area.inflate(-20, -20))
            self.coin_font = pygame.font.SysFont("dejavusans,arial", max(self.view.cell // 2, 8), bold=True)
        except (ValueError, json.JSONDecodeError) as e:
            self.error = str(e)
        self.all_results = None
        self.chart = None
        self.show_all = False
        self.reset()

    def reset(self):
        self.state = "idle"
        self.result = None
        self.explore_pos = 0.0
        self.step_i = 0
        self.step_timer = 0.0
        self.paused = False
        self.show_table = False
        self.show_chart = False

    def speed(self):
        return SPEEDS[self.speed_i]

    def start(self, name):
        if self.scenario is None:
            return
        self.reset()
        self.result = run(name, self.scenario)
        self.state = "exploring"

    def results_for_all(self):
        # roda os 4 so uma vez por cenario, usado na tabela e no modo todas as rotas
        if self.all_results is None:
            self.all_results = run_all(self.scenario, TABLE_REPEATS)
        return self.all_results

    def chart_image(self):
        # matplotlib desenha a figura em memoria e o pygame carrega como imagem
        if self.chart is None:
            area = self.map_area
            fig = scenario_figure(self.scenario, self.results_for_all(), (area.w / 100, area.h / 100))
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=100, facecolor=SURFACE)
            plt.close(fig)
            buffer.seek(0)
            self.chart = pygame.image.load(buffer, "chart.png")
        return self.chart

    def explored_count(self):
        return min(int(self.explore_pos), len(self.result.explored_order))

    def finish_exploring(self):
        self.explore_pos = len(self.result.explored_order)
        self.state = "walking" if self.result.found else "no_path"

    # loop principal

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and not self.on_key(event):
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.on_click(event.pos)
            self.update(dt)
            self.draw()

    def on_key(self, event):
        # devolve false quando o programa deve fechar
        key = event.key
        if key == pygame.K_ESCAPE:
            return False
        if key in (pygame.K_n, pygame.K_p):
            step = 1 if key == pygame.K_n else -1
            self.index = (self.index + step) % len(self.files)
            self.load()
            return True
        if self.scenario is None:
            return True

        names = list(ALGORITHMS)
        numbers = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
        if key in numbers:
            self.start(names[numbers.index(key)])
        elif key == pygame.K_SPACE:
            if self.state == "exploring":
                self.finish_exploring()
            elif self.state == "walking":
                self.paused = not self.paused
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.speed_i = min(self.speed_i + 1, len(SPEEDS) - 1)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.speed_i = max(self.speed_i - 1, 0)
        elif key == pygame.K_r:
            self.reset()
        elif key == pygame.K_c:
            self.results_for_all()
            self.show_table = not self.show_table
            self.show_chart = False
        elif key == pygame.K_t:
            self.results_for_all()
            self.show_all = not self.show_all
        elif key == pygame.K_g:
            self.show_chart = not self.show_chart
            self.show_table = False
        return True

    def on_click(self, point):
        for name, rect in self.buttons.items():
            if rect.collidepoint(point):
                self.start(name)

    def update(self, dt):
        if self.result is None or self.paused:
            return
        dt *= self.speed()

        if self.state == "exploring":
            total = len(self.result.explored_order)
            self.explore_pos += max(total / EXPLORE_SECONDS, 30) * dt
            if self.explore_pos >= total:
                self.finish_exploring()

        elif self.state == "walking":
            path = self.result.path
            if self.step_i >= len(path) - 1:
                self.state = "done"
                return
            # terreno mais caro faz o agente demorar mais naquela casa
            cost = self.scenario.grid.cost(path[self.step_i + 1])
            self.step_timer += dt
            if self.step_timer >= STEP_TIME * (1 + cost / 4):
                self.step_timer = 0.0
                self.step_i += 1

    # desenho

    def draw(self):
        self.screen.fill(BG)
        if self.scenario is None:
            renderer.draw_banner(self.screen, self.map_area, "erro ao carregar o cenario", self.fonts["banner"])
        else:
            self.draw_map()
        self.buttons = draw_panel(self.screen, self.panel_area, self, self.fonts)
        if self.show_table and self.scenario is not None:
            draw_table(self.screen, self.map_area, self.results_for_all(), self.scenario, self.fonts)
        if self.show_chart and self.scenario is not None:
            self.screen.blit(self.chart_image(), self.map_area.topleft)
        self.draw_status()
        pygame.display.flip()

    def draw_map(self):
        scenario, view = self.scenario, self.view
        renderer.draw_map(self.screen, view)

        rewards = set(scenario.rewards)
        agent = scenario.start
        result = self.result
        if result is not None:
            # sombra forte durante a exploracao, fraca depois para o terreno continuar visivel
            alpha = 90 if self.state == "exploring" else 40
            renderer.draw_explored(self.screen, view, set(result.explored_order[: self.explored_count()]), alpha)
            if result.found and self.state in ("walking", "done"):
                renderer.draw_path(self.screen, view, result.path, COLORS[result.algorithm])
                walked = result.path[: self.step_i + 1]
                rewards -= set(walked)
                agent = walked[-1]

        if self.show_all:
            for r in self.results_for_all():
                if r.found:
                    renderer.draw_path(self.screen, view, r.path, COLORS[r.algorithm], 3, ROUTE_OFFSETS[r.algorithm])

        renderer.draw_rewards(self.screen, view, rewards, self.coin_font)
        renderer.draw_goal(self.screen, view, scenario.goal)
        renderer.draw_agent(self.screen, view, agent)

        if self.state == "no_path":
            renderer.draw_banner(self.screen, self.map_area, "Nao existe caminho ate o premio", self.fonts["banner"])

    def draw_status(self):
        # mostra a celula embaixo do mouse
        text = "passe o mouse sobre o mapa para ver o terreno"
        if self.view is not None:
            pos = self.view.cell_at(pygame.mouse.get_pos())
            if pos is not None:
                terrain = self.scenario.grid.terrain(pos)
                cost = "intransponivel" if terrain.cost is None else f"custo {terrain.cost}"
                extras = []
                if pos in self.scenario.rewards:
                    extras.append("recompensa")
                if pos == self.scenario.start:
                    extras.append("inicio")
                if pos == self.scenario.goal:
                    extras.append("premio")
                text = f"celula {pos}   {terrain.label}   {cost}   {'  '.join(extras)}"
        label = self.fonts["small"].render(text, True, STATUS_TEXT)
        self.screen.blit(label, (12, MAP_H + (STATUS_H - label.get_height()) // 2))


def run_app(files, index=0):
    App(files, index).run()
    pygame.quit()
