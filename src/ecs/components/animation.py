from dataclasses import dataclass
from typing import List
import pygame

@dataclass
class Animation:
    frames: List[pygame.Surface]
    framerate: int               # FPS de la anim
    curr_time: float = 0.0
    curr_frame: int = 0
