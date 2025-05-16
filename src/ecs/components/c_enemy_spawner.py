# ── src/ecs/components/c_enemy_spawner.py ─────────────
from dataclasses import dataclass, field
import random

@dataclass
class CEnemySpawner:
    configs: list[dict]               # prefabs de enemigos normales
    interval: float                   # seg entre intentos de spawn
    screen_width: int
    boss_cfg_path: str = "assets/cfg/boss.json" 

    timer:     float = 0.0            # acumulador interno
    max_alive: int   = 15             # ← nuevo  (8-10 simultáneos)
    kill_goal: int   = 5             # ← nuevo  (bajas para boss)

    total_killed: int = 0             # se incrementa desde s_collision
    boss_spawned: bool = False

    # probabilidad de que un enemigo use EnemyAI (persiga)
    chase_prob: float = 0.4           # 60 % persigue, 40 % patrulla
