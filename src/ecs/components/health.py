# src/ecs/components/health.py
from dataclasses import dataclass

@dataclass
class Health:
    current: int
