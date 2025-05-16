# ── src/ecs/components/enemy_shooter.py ─────────────────────────
from dataclasses import dataclass

@dataclass
class EnemyShooter:
    cooldown:   float          # segundos entre intentos de disparo
    fire_prob:  float          # probabilidad [0–1] de que dispare cuando toca
    time:       float = 0.0    # ➜ temporizador interno (se rellena a 0)
