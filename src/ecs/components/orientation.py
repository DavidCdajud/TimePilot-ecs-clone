# src/ecs/components/orientation.py
from dataclasses import dataclass
from typing import List
import pygame

@dataclass
class Orientation:
    frames: List[pygame.Surface]   # lista de sprites para cada dirección
    neutral_index: int             # índice cuando la velocidad es cero
