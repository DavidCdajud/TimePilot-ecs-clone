# src/ecs/components/enemy_ai.py
from dataclasses import dataclass

@dataclass
class EnemyAI:
    """
    Componente de estado de IA básico:
      - state: 'spawn', 'chase', 'retreat'
      - timer: auxiliar para cronómetros internos
    """
    state: str = "spawn"
    timer: float = 0.0
    speed: float = 100.0    # píxeles/segundo
