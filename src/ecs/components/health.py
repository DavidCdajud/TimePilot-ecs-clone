# src/ecs/components/health.py
from dataclasses import dataclass

@dataclass
class Health:
    """Puntos de vida simples para una entidad dañable."""
    hp: int = 1
