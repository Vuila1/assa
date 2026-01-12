"""Target model describing entities to aim at."""
from dataclasses import dataclass

@dataclass
class Target:
    x: float
    y: float
    z: float = 0.0
    id: int | None = None

    def to_tuple(self):
        return (self.x, self.y, self.z)
