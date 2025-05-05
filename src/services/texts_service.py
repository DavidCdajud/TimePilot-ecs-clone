# src/engine/services/texts_service.py

import pygame

class TextService:
    def __init__(self):
        self._fonts = {}

    def get(self, path: str, size: int) -> pygame.font.Font:
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.Font(path, size)
        return self._fonts[key]
