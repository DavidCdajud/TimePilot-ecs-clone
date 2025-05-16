# ── src/ecs/components/enemy_counter.py
from dataclasses import dataclass

@dataclass
class EnemyCounter:
    kills: int = 0          # bajas acumuladas
