from dataclasses import dataclass

@dataclass
class Velocity:
    """Velocidad linear en píxeles/segundo para X e Y."""
    vx: float = 0.0
    vy: float = 0.0
