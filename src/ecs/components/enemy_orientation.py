# src/ecs/components/enemy_orientation.py
from dataclasses import dataclass
from typing import List
import pygame

@dataclass
class EnemyOrientation:
    frames: List[pygame.Surface]
    neutral_index: int  # Índice del frame “sin giro”
