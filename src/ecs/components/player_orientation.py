# src/ecs/components/player_orientation.py
from dataclasses import dataclass
import pygame
from typing import List, Tuple

@dataclass
class PlayerOrientation:
    frames: List[pygame.Surface]   # lista completa de frames de orientación
    neutral_index: int             # índice cuando velocidad es cero
