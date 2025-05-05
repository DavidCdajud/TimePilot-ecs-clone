# src/ecs/components/player_input.py

from dataclasses import dataclass

@dataclass
class PlayerInput:
    """
    Componente de input para el jugador:
    - speed: velocidad de movimiento (px/s)
    - fire_cooldown: tiempo mínimo entre disparos (s)
    - time_since_last_shot: cronómetro interno para el cooldown
    """
    speed: float
    fire_cooldown: float = 0.2
    time_since_last_shot: float = 0.0
