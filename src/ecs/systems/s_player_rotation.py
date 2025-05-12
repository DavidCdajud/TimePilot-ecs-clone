# src/ecs/systems/s_player_rotation.py
import math
import pygame
import esper
from ecs.components.velocity import Velocity
from ecs.components.sprite import Sprite
from ecs.components.player_orientation import PlayerOrientation
from ecs.components.last_direction import LastDirection

ANGLE_OFFSET = -90  # Corrección para alinear el sprite hacia arriba

def sistema_player_rotation(world: esper.World) -> None:
    for ent, (vel, orient, sprite) in world.get_components(
        Velocity, PlayerOrientation, Sprite
    ):
        vx, vy = vel.vx, vel.vy

        if vx == 0 and vy == 0:
            # Si está quieto, toma la última dirección si existe
            if world.has_component(ent, LastDirection):
                last_vec = world.component_for_entity(ent, LastDirection).vec
            else:
                last_vec = pygame.Vector2(0, -1)  # Por defecto: arriba
        else:
            # Movimiento actual
            last_vec = pygame.Vector2(vx, vy).normalize()
            if world.has_component(ent, LastDirection):
                world.component_for_entity(ent, LastDirection).vec = last_vec
            else:
                world.add_component(ent, LastDirection(last_vec))

        # Calcula el ángulo con offset
        raw_angle = math.degrees(math.atan2(-last_vec.y, last_vec.x))
        angle = (raw_angle + ANGLE_OFFSET) % 360
        idx = int((angle / 360) * len(orient.frames)) % len(orient.frames)
        sprite.surface = orient.frames[idx]
