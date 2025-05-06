# src/ecs/components/animation.py
from dataclasses import dataclass
import pygame

@dataclass
class Animation:
    frames: list[pygame.Surface]
    framerate: int          # imágenes por segundo
    loop: bool = True       # ← NOVEDAD
    curr_frame: int = 0
    curr_time: float = 0.0
