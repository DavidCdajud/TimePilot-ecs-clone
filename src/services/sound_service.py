# core/sound_service.py
import pygame
from pathlib import Path

class SoundService:
    """Cachea SFX y maneja BGM con pygame.mixer."""
    def __init__(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self._cache: dict[str, pygame.mixer.Sound] = {}

    # ---------- SFX ----------
    def _get(self, path: str) -> pygame.mixer.Sound:
        if path not in self._cache:
            if not Path(path).exists():
                raise FileNotFoundError(path)
            self._cache[path] = pygame.mixer.Sound(path)
        return self._cache[path]

    def play_sfx(self, path: str, volume: float = 1.0) -> None:
        snd = self._get(path)
        snd.set_volume(volume)
        snd.play()

    # ---------- BGM ----------
    def play_bgm(self, path: str, loops: int = -1, volume: float = .6) -> None:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)

    def stop_bgm(self):     pygame.mixer.music.stop()
    def pause_bgm(self):    pygame.mixer.music.pause()
    def resume_bgm(self):   pygame.mixer.music.unpause()
