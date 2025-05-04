# src/services/resource_manager.py
import pygame
from pathlib import Path

class ResourceManager:
    def __init__(self, assets_dir: Path):
        self._assets = assets_dir
        self._images: dict[str, pygame.Surface] = {}

        # --- Mapa lógico → archivo ---
        self._file_map: dict[str, str] = {
            "player_sheet":  "player_sheet.png",   # hoja 32 × 16×16
            "enemy_01":      "enemy_01.png",    # enemigo 16×16
            "player_bullet": "bullet_01_02_03.png",
        }

    # ------------------------------------------------------------------
    def image(self, key: str) -> pygame.Surface:
        """Devuelve la Surface asociada a <key>, cargándola si hace falta."""
        if key not in self._file_map:
            raise ValueError(
                f"[ResourceManager] La clave '{key}' no está registrada en _file_map"
            )

        if key not in self._images:
            file_name = self._file_map[key]
            path = self._assets / "img" / file_name
            self._images[key] = pygame.image.load(path).convert_alpha()

        return self._images[key]
