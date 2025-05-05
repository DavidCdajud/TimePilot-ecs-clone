# src/ecs/systems/s_enemy_rotation.py
import math
import pygame
import esper
from ecs.components.velocity import Velocity
from ecs.components.sprite import Sprite
from ecs.components.enemy_orientation import EnemyOrientation

def sistema_enemy_rotation(world: esper.World) -> None:
    """
    Ajusta el sprite de cada enemigo según su dirección de movimiento.
    """
    for ent, (vel, sp, ori) in world.get_components(Velocity, Sprite, EnemyOrientation):
        vx, vy = vel.vx, vel.vy
        if vx == 0 and vy == 0:
            idx = ori.neutral_index
        else:
            angle = math.degrees(math.atan2(-vy, vx))  # invertimos Y para Pygame
            # normalizamos a [0,360)
            angle = (angle + 360) % 360
            # dividimos el círculo en N sectores según el número de frames
            n = len(ori.frames)
            sector = int(round(angle / 360 * n)) % n
            idx = sector
        # actualizamos el surface
        new_surf = ori.frames[idx]
        sp.surface = new_surf
        # (opcional) si varía el offset:
        sp.offset = (new_surf.get_width()//2, new_surf.get_height()//2)
