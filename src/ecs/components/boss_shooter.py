# src/ecs/components/boss_shooter.py
from dataclasses import dataclass

@dataclass
class BossShooter:
    cooldown: float       # segundos entre chequeos de disparo
    fire_prob: float      # probabilidad de disparar cada chequeo
    time: float = 0.0     # acumulador interno
