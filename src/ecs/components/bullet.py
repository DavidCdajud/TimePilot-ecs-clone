# src/ecs/components/bullet.py
from dataclasses import dataclass

@dataclass
class Bullet:
    """Marca a la entidad como proyectil."""
    owner: str              # "player" o "enemy"
    damage: int = 1
