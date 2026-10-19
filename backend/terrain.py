from enum import Enum


class Terrain(Enum):
    # valor: (caractere no json, custo para entrar, nome, cor rgb)
    WALL = ("#", None, "Parede", (40, 40, 40))
    PLAIN = (".", 1, "Solido e plano", (200, 230, 160))
    SAND = ("a", 4, "Arenoso", (240, 220, 140))
    ROCK = ("r", 10, "Rochoso", (150, 140, 130))
    SWAMP = ("p", 20, "Pantano", (90, 130, 90))

    def __init__(self, char, cost, label, color):
        self.char = char
        self.cost = cost
        self.label = label
        self.color = color

    @property
    def walkable(self):
        return self is not Terrain.WALL


# mapa caractere -> terreno
TERRAIN_BY_CHAR = {t.char: t for t in Terrain}

# itens da camada 'items', podem ficar sobre qualquer terreno
START_CHAR = "S"
GOAL_CHAR = "G"
REWARD_CHAR = "$"
EMPTY_CHAR = " "
ITEM_CHARS = {START_CHAR, GOAL_CHAR, REWARD_CHAR, EMPTY_CHAR}
