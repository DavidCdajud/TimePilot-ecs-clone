# src/ecs/systems/s_pause_setup.py
import pygame, esper
from ecs.components.tags.c_tag_pause_menu import CTagPauseMenu
from ecs.components.transform import Transform
from ecs.components.sprite    import Sprite
from ecs.components.orientation import Orientation  # si necesitas manejar selección
from ecs.components.animation  import Animation    # opcional, si animas el texto

# ── Configuración visual ─────────────────────────────────────────
_FONT_PATH   = "assets/fnt/PressStart2P.ttf"
_FONT_SIZE   = 32
_FONT_COLOR  = (255, 255, 255)
_LINE_SPACING = 48    # píxeles entre cada opción

def sistema_pause_setup(world: esper.World) -> None:
    """
    Crea las opciones 'Resume' y 'Quit' centrales en pantalla,
    etiquetadas con CTagPauseMenu para render/input.
    """
    screen = pygame.display.get_surface()
    w, h   = screen.get_size()

    # fuente única
    font = pygame.font.Font(_FONT_PATH, _FONT_SIZE)

    options = ["RESUME", "QUIT"]
    start_y = h / 2 - (_LINE_SPACING * (len(options) - 1) / 2)

    for idx, text in enumerate(options):
        surf = font.render(text, True, _FONT_COLOR)
        # calculamos el centro de este texto
        x = w / 2
        y = start_y + idx * _LINE_SPACING
        # el componente Transform guardará el centro
        ent = world.create_entity()
        world.add_component(ent, CTagPauseMenu())
        world.add_component(ent, Transform((x, y)))
        # Sprite offset centrado
        offset = (surf.get_width()//2, surf.get_height()//2)
        world.add_component(ent, Sprite(surf, offset))

        # (Opcional) podrías añadir un componente de selección,
        # por ejemplo Orientation o un CTagSelected para un cursor.
