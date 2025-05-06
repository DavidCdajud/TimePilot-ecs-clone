# src/ecs/components/duration.py
from dataclasses import dataclass

@dataclass
class Duration:
    time_left: float
