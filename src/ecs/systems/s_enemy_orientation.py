# src/ecs/systems/s_enemy_orientation.py
import math
import esper
from ecs.components.velocity import Velocity
from ecs.components.sprite import Sprite
from src.ecs.components.enemy_orientation import EnemyOrientation
from ecs.components.tags.c_tag_enemy import CTagEnemy

def sistema_enemy_orientation(world: esper.World) -> None:
    """
    Para cada enemigo con Velocity + EnemyOrientation + Sprite,
    calcula el ángulo de (vx,vy) y actualiza sprite.surface al frame correspondiente.
    """
    for ent, (vel, ori, spr) in world.get_components(Velocity, EnemyOrientation, Sprite):
        if not world.has_component(ent, CTagEnemy):
            continue

        # si no se mueve, usa neutral
        if vel.vx == 0 and vel.vy == 0:
            idx = ori.neutral_index
        else:
            # ángulo en radianes: cero apuntando a la derecha, giro anti-horario
            ang = math.atan2(-vel.vy, vel.vx)  # invertimos vy para y hacia arriba
            # normalizamos a [0, 2π)
            if ang < 0:
                ang += 2*math.pi
            # dividimos círculo en N sectores
            N = len(ori.frames)
            sector = int((ang / (2*math.pi)) * N) % N
            idx = sector

        # sólo actualizamos si cambió
        new_surf = ori.frames[idx]
        if new_surf is not spr.surface:
            # preserva offset y layer
            spr.surface = new_surf
