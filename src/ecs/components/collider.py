# src/ecs/components/collider.py
from dataclasses import dataclass

@dataclass
class Collider:
    """Colisión circular sencilla."""
    radius: int = 4          # radio de la “esfera” de colisión (px)
