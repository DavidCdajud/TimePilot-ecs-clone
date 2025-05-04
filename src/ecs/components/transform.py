from dataclasses import dataclass
from typing import Tuple

@dataclass
class Transform:
    """Posición y rotación (en grados) de la entidad."""
    pos: Tuple[float, float] = (0.0, 0.0)
    rot: float = 0.0
