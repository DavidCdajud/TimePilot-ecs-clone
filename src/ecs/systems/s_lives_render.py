# ── src/ecs/systems/s_lives_render.py ─────────────────────
import pygame, esper
from typing import Optional                 #  ← ➊  NUEVO
from ecs.components.lives             import Lives
from ecs.components.tags.c_tag_player import CTagPlayer

# ------------------------------------------------------------------
#  Carga diferida (lazy-load) del icono de vida
# ------------------------------------------------------------------
_HEART: Optional[pygame.Surface] = None     #  ← ➋  usa Optional[…]

def _get_heart() -> pygame.Surface:
    """Devuelve la imagen del avión-icono; la carga la primera vez que se llama."""
    global _HEART
    if _HEART is None:
        _HEART = pygame.image.load("assets/img/plane_counter_04.png").convert_alpha()
    return _HEART
# ------------------------------------------------------------------


def sistema_lives_render(world: esper.World, screen: pygame.Surface) -> None:
    comps = world.get_components(CTagPlayer, Lives)
    if not comps:
        return

    _, (_, lives) = comps[0]
    heart = _get_heart()

    # dibuja los iconos en la esquina sup-izq, debajo del marcador SCORE
    for i in range(lives.current):
        x = 8 + i * (heart.get_width() + 4)
        screen.blit(heart, (x, 32))