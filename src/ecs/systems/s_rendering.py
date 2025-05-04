# src/ecs/systems/s_rendering.py
import esper
import pygame
from ecs.components.transform import Transform
from ecs.components.sprite import Sprite
from ecs.components.player_input import PlayerInput

def sistema_rendering(
    world: esper.World,
    pantalla: pygame.Surface,
    camera_offset: tuple[float, float],
    screen_center: tuple[int, int]
) -> None:
    # Reunir todos los (layer, ent, tr, sp)
    items = []
    for ent, (tr, sp) in world.get_components(Transform, Sprite):
        items.append((sp.layer, ent, tr, sp))

    # Ordenar ascendente por layer
    items.sort(key=lambda x: x[0])

    # Dibujar en orden
    for layer, ent, tr, sp in items:
        # calcula posición en pantalla
        x = tr.pos[0] - camera_offset[0] + screen_center[0] - sp.offset[0]
        y = tr.pos[1] - camera_offset[1] + screen_center[1] - sp.offset[1]
        pantalla.blit(sp.surface, (int(x), int(y)))