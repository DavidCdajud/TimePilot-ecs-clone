import pygame
from pathlib import Path

class ImagesService:
    def __init__(self) -> None:
        self._images: dict[str, pygame.Surface] = {}

    def get(self, path: str) -> pygame.Surface:
        """Carga y memoriza una imagen con convert_alpha()."""
        if path not in self._images:
            if not Path(path).is_file():
                raise FileNotFoundError(f"Imagen no encontrada: {path}")
            self._images[path] = pygame.image.load(path).convert_alpha()
        return self._images[path]

    