# src/ecs/components/player_input.py
from dataclasses import dataclass

@dataclass
class PlayerInput:
    """Velocidad de movimiento del jugador en píxeles/segundo."""
    speed: float
