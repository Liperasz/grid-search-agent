from dataclasses import dataclass, field


@dataclass
class SearchResult:
    algorithm: str
    found: bool
    message: str
    path: list = field(default_factory=list)
    cost: int = 0
    collected: list = field(default_factory=list)
    expanded: int = 0
    generated: int = 0
    max_frontier: int = 0
    time_ms: float = 0.0
    # ordem em que as posicoes foram expandidas, usada para animar a exploracao
    explored_order: list = field(default_factory=list)

    @property
    def steps(self):
        return max(len(self.path) - 1, 0)
