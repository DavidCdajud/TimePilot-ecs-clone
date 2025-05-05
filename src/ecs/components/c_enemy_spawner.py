# src/ecs/components/c_enemy_spawner.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class CEnemySpawner:
    """
    Spawner periódico de enemigos:
      - configs: lista de dicts (de enemies.json)
      - interval: cada cuántos segundos spawnear
      - screen_width: ancho de la ventana para posicionar x aleatorio
      - timer: cronómetro interno
    """
    configs: List[Dict]
    interval: float
    screen_width: float
    timer: float = 0.0