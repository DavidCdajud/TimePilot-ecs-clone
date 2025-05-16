# src/ecs/components/player_input.py
from dataclasses import dataclass, field
import pygame

@dataclass
class PlayerInput:
    speed: float
    fire_cooldown : float = 0.2
    time_since_last_shot : float = 0.0
    last_shot_pressed   : bool  = False
    last_dir : pygame.Vector2 = field(
        default_factory=lambda: pygame.Vector2(0, -1)   # recuerda el último “apunte”
    )
