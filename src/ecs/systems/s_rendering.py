import esper
import pygame
from ecs.components.transform import Transform
from ecs.components.sprite import Sprite

def sistema_rendering(world: esper.World, pantalla: pygame.Surface) -> None:
    componentes = world.get_components(Transform, Sprite)
    for _, (transform, sprite) in componentes:
        x = int(transform.pos[0] - sprite.offset[0])
        y = int(transform.pos[1] - sprite.offset[1])
        pantalla.blit(sprite.surface, (x, y))
