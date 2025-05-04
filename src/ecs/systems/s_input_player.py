# src/ecs/systems/s_input_player.py
import pygame
import esper
from ecs.components.velocity import Velocity
from ecs.components.player_input import PlayerInput

def sistema_input_player(world: esper.World, delta_tiempo: float) -> None:
    """
    Lee flechas (o WASD) y ajusta Velocity en cada entidad con PlayerInput.
    """
    keys = pygame.key.get_pressed()
    for _, (vel, pi) in world.get_components(Velocity, PlayerInput):
        vx = vy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx -= pi.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx += pi.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vy -= pi.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vy += pi.speed
        vel.vx = vx
        vel.vy = vy
