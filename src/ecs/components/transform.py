from dataclasses import dataclass
from typing import Tuple

@dataclass
class Transform:
    """Posición (x, y) y rotación en grados del sprite."""
    pos: Tuple[float, float] = (0.0, 0.0)
    rot: float = 0.0
