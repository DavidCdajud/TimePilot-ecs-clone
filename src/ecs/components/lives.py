# ── src/ecs/components/lives.py ────────────────────────────
from dataclasses import dataclass

@dataclass
class Lives:
    current: int
