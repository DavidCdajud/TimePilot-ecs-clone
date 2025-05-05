# src/ecs/components/bullet.py
from dataclasses import dataclass

@dataclass
class Bullet:
    owner: int
    damage: int
