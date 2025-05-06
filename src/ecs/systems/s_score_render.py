# src/ecs/systems/s_score_render.py
import pygame, esper

from typing import Optional               #  ←  NUEVO
from ecs.components.score_board import ScoreBoard

# ── Config visual ──────────────────────────────────────────────
_FONT_PATH  = "assets/fnt/PressStart2P.ttf"
_FONT_SIZE  = 6
_FONT_COLOR = (255, 0, 0)
_POS        = (8, 8)

# ── Carga única de la fuente ───────────────────────────────────
_font: Optional[pygame.font.Font] = None   #  ←  CAMBIADO
def _get_font() -> pygame.font.Font:
    global _font
    if _font is None:
        _font = pygame.font.Font(_FONT_PATH, _FONT_SIZE)
    return _font

# ── Sistema ────────────────────────────────────────────────────
def sistema_score_render(world: esper.World, screen: pygame.Surface) -> None:
    comps = world.get_component(ScoreBoard)
    if not comps:
        return

    _, sb = comps[0]
    font = _get_font()

    text = f"SCORE  {sb.score:,}".replace(",", ".")
    surf = font.render(text, True, _FONT_COLOR)
    screen.blit(surf, _POS)

