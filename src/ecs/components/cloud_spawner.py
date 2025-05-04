# src/ecs/components/cloud_spawner.py
from dataclasses import dataclass
from typing import List, Dict, Tuple
import random

@dataclass
class CloudSpawner:
    configs: List[Dict]        # tu clouds.json
    screen_width: float
    min_y: float
    max_y: float
    min_interval: float        # intervalo mínimo entre nubes
    max_interval: float        # intervalo máximo entre nubes
    timer: float = 0.0         # tiempo acumulado
    next_spawn: float = 0.0    # tiempo programado para el siguiente spawn
    initial_count: int = 5     # cuántas nubes aparecerán al inicio

    def __post_init__(self):
        # programa el primer spawn
        self.next_spawn = random.uniform(self.min_interval, self.max_interval)
