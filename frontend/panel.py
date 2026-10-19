import pygame

from backend.runner import ALGORITHMS, COLORS
from backend.terrain import Terrain

BG = (245, 244, 240)
INK = (25, 25, 25)
MUTED = (100, 100, 95)
LINE = (210, 208, 200)
BUTTON = (225, 223, 215)
BEST = (20, 130, 60)
ERROR = (190, 40, 40)
PAD = 16

CONTROLS = [
    "1-4  rodar algoritmo",
    "ESPACO  pular exploracao / pausar",
    "+ -  velocidade      R  reiniciar",
    "N P  trocar cenario  T  todas as rotas",
    "C  comparativo       G  graficos",
    "ESC  sair do programa",
]


STATE_LABELS = {
    "idle": "parado",
    "exploring": "explorando",
    "walking": "andando",
    "done": "chegou ao premio",
    "no_path": "sem caminho",
}


class Writer:
    # escreve linhas de cima para baixo dentro do painel
    def __init__(self, surface, rect, fonts):
        self.surface = surface
        self.rect = rect
        self.fonts = fonts
        self.y = rect.y + PAD

    def text(self, value, font="body", color=INK, x=0):
        label = self.fonts[font].render(value, True, color)
        self.surface.blit(label, (self.rect.x + PAD + x, self.y))
        return label.get_height()

    def line(self, value, font="body", color=INK, gap=4):
        self.y += self.text(value, font, color) + gap

    def pair(self, key, value):
        self.text(key, color=MUTED)
        self.text(str(value), x=140)
        self.y += self.fonts["body"].get_height() + 3

    def section(self, title):
        self.y += 6
        pygame.draw.line(self.surface, LINE, (self.rect.x + PAD, self.y), (self.rect.right - PAD, self.y))
        self.y += 8
        self.line(title, "small", MUTED)


def draw_panel(surface, rect, app, fonts):
    pygame.draw.rect(surface, BG, rect)
    w = Writer(surface, rect, fonts)

    name = app.scenario.name if app.scenario else app.files[app.index].name
    w.line(f"{name}  ({app.index + 1}/{len(app.files)})", "title")
    if app.error:
        for part in wrap(app.error, fonts["small"], rect.w - 2 * PAD):
            w.line(part, "small", ERROR, 2)
        return {}
    for part in wrap(app.scenario.description, fonts["small"], rect.w - 2 * PAD):
        w.line(part, "small", MUTED, 2)

    # botoes dos algoritmos em duas colunas
    w.section("ALGORITMO")
    buttons = {}
    bw, bh = (rect.w - 2 * PAD - 10) // 2, 30
    for i, alg in enumerate(ALGORITHMS):
        x = rect.x + PAD + (i % 2) * (bw + 10)
        y = w.y + (i // 2) * (bh + 8)
        button = pygame.Rect(x, y, bw, bh)
        selected = app.result is not None and app.result.algorithm == alg
        pygame.draw.rect(surface, COLORS[alg] if selected else BUTTON, button, border_radius=6)
        pygame.draw.rect(surface, COLORS[alg], button, 2, border_radius=6)
        label = fonts["body"].render(f"[{i + 1}] {alg}", True, INK)
        surface.blit(label, label.get_rect(center=button.center))
        buttons[alg] = button
    w.y += 2 * (bh + 8)

    result = app.result
    if result is not None and app.state in ("exploring", "walking"):
        # acompanhamento ao vivo enquanto anima
        w.section(f"EXECUCAO  ({result.algorithm})")
        walked = result.path[: app.step_i + 1] if result.found else []
        w.pair("estado", STATE_LABELS[app.state] + ("  (pausado)" if app.paused else ""))
        w.pair("expandidos", f"{app.explored_count()} / {result.expanded}")
        if result.found:
            w.pair("passo", f"{app.step_i} / {result.steps}")
            w.pair("custo", app.scenario.grid.path_cost(walked))
            got = len({p for p in walked if p in app.scenario.rewards})
            w.pair("recompensas", f"{got} / {len(app.scenario.rewards)}")
    elif result is not None:
        w.section(f"RESULTADO  ({result.algorithm})")
        w.line(result.message, color=BEST if result.found else ERROR)
        if result.found:
            w.pair("passos", result.steps)
            w.pair("custo total", result.cost)
            w.pair("recompensas", f"{len(result.collected)} / {len(app.scenario.rewards)}")
        w.pair("nos expandidos", result.expanded)
        w.pair("nos gerados", result.generated)
        w.pair("fronteira max", result.max_frontier)
        w.pair("tempo", f"{result.time_ms:.3f} ms")

    # legenda em duas colunas para caber no painel
    w.section("LEGENDA")
    col_w = (rect.w - 2 * PAD) // 2
    for i, terrain in enumerate(Terrain):
        x = (i % 2) * col_w
        y = w.y + (i // 2) * (fonts["small"].get_height() + 4)
        pygame.draw.rect(surface, terrain.color, (rect.x + PAD + x, y + 2, 12, 12))
        cost = terrain.label if terrain.cost is None else f"{terrain.label} {terrain.cost}"
        label = fonts["small"].render(cost, True, INK)
        surface.blit(label, (rect.x + PAD + x + 18, y))
    w.y += 3 * (fonts["small"].get_height() + 4)
    w.line("carinha = agente    moeda = recompensa", "small", MUTED, 2)
    w.line("estrela = premio", "small", MUTED, 2)
    w.line(f"valor de cada recompensa: {app.scenario.reward_value}", "small", MUTED)

    # controles presos no rodape
    w.y = rect.bottom - PAD - len(CONTROLS) * (fonts["small"].get_height() + 2) - 18
    w.section(f"CONTROLES   velocidade x{app.speed()}")
    for item in CONTROLS:
        w.line(item, "small", MUTED, 2)
    return buttons


def wrap(text, font, width):
    lines, current = [], ""
    for word in text.split():
        test = f"{current} {word}".strip()
        if font.size(test)[0] > width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


# colunas da tabela: titulo, funcao que extrai o valor, se menor e melhor, se precisa de caminho
TABLE_COLUMNS = [
    ("Passos", lambda r: r.steps, True, True),
    ("Custo", lambda r: r.cost, True, True),
    ("Recomp.", lambda r: len(r.collected), False, True),
    ("Expandidos", lambda r: r.expanded, True, False),
    ("Gerados", lambda r: r.generated, True, False),
    ("Fronteira", lambda r: r.max_frontier, True, False),
    ("Tempo (ms)", lambda r: r.time_ms, True, False),
]


def draw_table(surface, area, results, scenario, fonts):
    # escurece o mapa e desenha a tabela por cima
    shade = pygame.Surface(area.size, pygame.SRCALPHA)
    shade.fill((0, 0, 0, 140))
    surface.blit(shade, area.topleft)

    col_w, first_w, row_h = 92, 110, 34
    width = first_w + 90 + col_w * len(TABLE_COLUMNS)
    box = pygame.Rect(0, 0, width + 2 * PAD, row_h * (len(results) + 1) + 90)
    box.center = area.center
    pygame.draw.rect(surface, BG, box, border_radius=10)

    x0, y = box.x + PAD, box.y + PAD
    surface.blit(fonts["title"].render(f"Comparativo: {scenario.name}", True, INK), (x0, y))
    y += 36

    headers = ["Algoritmo", "Achou"] + [c[0] for c in TABLE_COLUMNS]
    xs = [x0, x0 + first_w] + [x0 + first_w + 90 + i * col_w for i in range(len(TABLE_COLUMNS))]
    for x, title in zip(xs, headers):
        surface.blit(fonts["small"].render(title, True, MUTED), (x, y))
    y += row_h - 8
    pygame.draw.line(surface, LINE, (x0, y), (box.right - PAD, y))

    # melhor valor de cada coluna, considerando so quem achou caminho quando precisa
    best = []
    for _, get, lower, needs_path in TABLE_COLUMNS:
        valid = [get(r) for r in results if r.found or not needs_path]
        best.append((min(valid) if lower else max(valid)) if valid else None)

    for r in results:
        y += 8
        pygame.draw.rect(surface, COLORS[r.algorithm], (x0, y + 3, 12, 12))
        surface.blit(fonts["body"].render(r.algorithm, True, INK), (x0 + 18, y))
        surface.blit(fonts["body"].render("sim" if r.found else "nao", True, INK if r.found else ERROR), (xs[1], y))
        for i, (_, get, _, needs_path) in enumerate(TABLE_COLUMNS):
            if needs_path and not r.found:
                value, color, font = "-", MUTED, "body"
            else:
                v = get(r)
                value = f"{v:.3f}" if isinstance(v, float) else str(v)
                is_best = v == best[i]
                color, font = (BEST, "bold") if is_best else (INK, "body")
            surface.blit(fonts[font].render(value, True, color), (xs[i + 2], y))
        y += row_h - 8

    note = "verde = melhor valor da coluna    C fecha    G abre os graficos"
    surface.blit(fonts["small"].render(note, True, MUTED), (x0, box.bottom - PAD - 14))
