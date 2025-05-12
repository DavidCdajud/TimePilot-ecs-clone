# src/ecs/systems/s_input_player.py
import json
import pygame
import esper
from ecs.components.velocity import Velocity
from ecs.components.player_input import PlayerInput
from ecs.components.transform import Transform
from ecs.components.last_direction import LastDirection
from create.prefabs_creator import create_bullet

# Carga la configuración de la bala
with open("assets/cfg/bullet.json", encoding="utf-8") as _f:
    BULLET_CFG = json.load(_f)

def sistema_input_player(world: esper.World, delta: float) -> None:
    keys = pygame.key.get_pressed()
    for ent, (vel, pi) in world.get_components(Velocity, PlayerInput):
        vx = vy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:   vx -= pi.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  vx += pi.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:     vy -= pi.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:   vy += pi.speed
        vel.vx, vel.vy = vx, vy

        # Registra la última dirección válida si hay movimiento
        if vx != 0 or vy != 0:
            last_vec = pygame.Vector2(vx, vy).normalize()
            if world.has_component(ent, LastDirection):
                world.component_for_entity(ent, LastDirection).vec = last_vec
            else:
                world.add_component(ent, LastDirection(last_vec))

        # Disparo con cooldown
        pi.time_since_last_shot += delta
        if (keys[pygame.K_z] or keys[pygame.K_SPACE]) and pi.time_since_last_shot >= pi.fire_cooldown:
            pi.time_since_last_shot = 0.0
            tr = world.component_for_entity(ent, Transform)
            dir_vec = pygame.Vector2(vx, vy)
            if dir_vec.length_squared() == 0:
                dir_vec = pygame.Vector2(0, -1)
            else:
                dir_vec = dir_vec.normalize()
            create_bullet(world, BULLET_CFG, tr.pos, dir_vec)
