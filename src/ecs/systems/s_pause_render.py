import pygame
import esper

from ecs.components.sprite import Sprite
from ecs.components.transform import Transform
from ecs.components.tags.c_tag_pause_menu import CTagPauseMenu

def sistema_pause_render(world: esper.World, screen: pygame.Surface) -> None:
    for ent, (_, spr) in world.get_components(CTagPauseMenu, Sprite):
        tr = world.component_for_entity(ent, Transform)
        screen.blit(
            spr.surface,
            (tr.pos[0] - spr.offset[0], tr.pos[1] - spr.offset[1])
        )
