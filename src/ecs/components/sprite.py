from dataclasses import dataclass
import pygame
from typing import Tuple

@dataclass
class Sprite:
    surface: pygame.Surface
    offset: Tuple[int, int] = (0, 0)  # por si queremos centrar
    layer: int = 0 
    
    @property
    def size(self) -> Tuple[int, int]:
        return self.surface.get_size()
