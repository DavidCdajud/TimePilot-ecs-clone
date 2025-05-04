# src/ecs/components/cloud_spawner.py
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class CloudSpawner:
    configs: List[Dict]
    screen_width: float
    screen_height: float
    min_y: float
    max_y: float
    # distancia en px que la cámara debe moverse para spawnear
    move_threshold: float = 50.0
    # posición de cámara en el último spawn
    last_cam_pos: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
