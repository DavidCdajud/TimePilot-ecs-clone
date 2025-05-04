from dataclasses import dataclass

@dataclass
class PlayerInput:
    speed: float = 140.0               # velocidad de movimiento
    shoot_cooldown: float = 0.25       # segundos entre disparos
    time_since_shot: float = 0.0       # contador interno
