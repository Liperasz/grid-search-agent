import json
from dataclasses import dataclass
from pathlib import Path

from backend.grid import Grid
from backend.terrain import (
    EMPTY_CHAR,
    GOAL_CHAR,
    ITEM_CHARS,
    REWARD_CHAR,
    START_CHAR,
    TERRAIN_BY_CHAR,
)

MIN_FREE_CELLS = 30
MIN_REWARDS = 5
DEFAULT_REWARD_VALUE = 15


@dataclass
class Scenario:
    name: str
    description: str
    grid: Grid
    start: tuple
    goal: tuple
    rewards: frozenset
    reward_value: int
    path: str = ""


def _parse_terrain(name, lines):
    width = len(lines[0])
    cells = []
    for r, line in enumerate(lines):
        if len(line) != width:
            raise ValueError(f"{name}: linha {r} do terrain tem tamanho {len(line)}, esperado {width}")
        row = []
        for c, ch in enumerate(line):
            if ch not in TERRAIN_BY_CHAR:
                raise ValueError(f"{name}: terreno invalido '{ch}' em ({r}, {c})")
            row.append(TERRAIN_BY_CHAR[ch])
        cells.append(row)
    return Grid(cells)


def _parse_items(name, lines, grid):
    if len(lines) != grid.rows:
        raise ValueError(f"{name}: items tem {len(lines)} linhas, terrain tem {grid.rows}")

    start = goal = None
    rewards = set()
    for r, line in enumerate(lines):
        if len(line) != grid.cols:
            raise ValueError(f"{name}: linha {r} de items tem tamanho {len(line)}, esperado {grid.cols}")
        for c, ch in enumerate(line):
            if ch not in ITEM_CHARS:
                raise ValueError(f"{name}: item invalido '{ch}' em ({r}, {c})")
            if ch == EMPTY_CHAR:
                continue
            if grid.is_wall((r, c)):
                raise ValueError(f"{name}: item '{ch}' em cima de parede em ({r}, {c})")
            if ch == START_CHAR:
                if start is not None:
                    raise ValueError(f"{name}: mais de um '{START_CHAR}'")
                start = (r, c)
            elif ch == GOAL_CHAR:
                if goal is not None:
                    raise ValueError(f"{name}: mais de um '{GOAL_CHAR}'")
                goal = (r, c)
            elif ch == REWARD_CHAR:
                rewards.add((r, c))

    if start is None or goal is None:
        raise ValueError(f"{name}: items precisa de um '{START_CHAR}' e um '{GOAL_CHAR}'")
    return start, goal, rewards


def load_scenario(path):
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for key in ("terrain", "items"):
        if not data.get(key):
            raise ValueError(f"{path.name}: campo '{key}' ausente ou vazio")

    grid = _parse_terrain(path.name, data["terrain"])
    start, goal, rewards = _parse_items(path.name, data["items"], grid)

    # requisitos do enunciado viram apenas aviso, para permitir mapas de teste
    if grid.free_cells() < MIN_FREE_CELLS:
        print(f"aviso: {path.name} tem menos de {MIN_FREE_CELLS} vertices livres")
    if len(rewards) < MIN_REWARDS:
        print(f"aviso: {path.name} tem menos de {MIN_REWARDS} recompensas")

    return Scenario(
        name=data.get("name", path.stem),
        description=data.get("description", ""),
        grid=grid,
        start=start,
        goal=goal,
        rewards=frozenset(rewards),
        reward_value=data.get("reward_value", DEFAULT_REWARD_VALUE),
        path=str(path),
    )


def list_scenarios(folder="scenarios"):
    return sorted(Path(folder).glob("*.json"))
