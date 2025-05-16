# ── src/ecs/systems/s_kill_render.py ────────────────────────────
import pygame, esper
from typing import Optional
from ecs.components.enemy_counter import EnemyCounter

_FONT_PATH  = "assets/fnt/PressStart2P.ttf"
_FONT_SIZE  = 6
_FONT_COLOR = (255, 0, 0)
_POS        = (160, 8)          # debajo del marcador SCORE

_font: Optional[pygame.font.Font] = None
def _get_font() -> pygame.font.Font:
    global _font
    if _font is None:
        _font = pygame.font.Font(_FONT_PATH, _FONT_SIZE)
    return _font


def sistema_kill_render(world: esper.World, screen: pygame.Surface) -> None:
    comps = world.get_component(EnemyCounter)
    if not comps:
        return
    _, cnt = comps[0]

    text = f"KILLS:  {cnt.kills}"
    surf = _get_font().render(text, True, _FONT_COLOR)
    screen.blit(surf, _POS)
