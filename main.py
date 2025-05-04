import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "src"
sys.path.append(str(ROOT))   # ahora 'ecs', 'core', etc. son visibles

from core.game_engine import GameEngine

if __name__ == "__main__":
    GameEngine().run()
