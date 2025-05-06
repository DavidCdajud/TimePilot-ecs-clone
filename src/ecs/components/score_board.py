# src/ecs/components/score_board.py
from dataclasses import dataclass
@dataclass
class ScoreBoard:
    score: int = 0
