# src/ecs/systems/s_player_shoot.py
import pygame
import esper
from ecs.components.transform import Transform
from ecs.components.player_input import PlayerInput
from create.prefabs_creator import create_bullet

def sistema_player_shoot(
    world: esper.World,
    bullet_cfg: dict,
    camera_pos: tuple[float,float],
    screen_center: tuple[int,int]
) -> None:
    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    for ent, (tr, pi) in world.get_components(Transform, PlayerInput):
        # detectamos si Z o clic izquierdo están recién pulsados
        pressed = keys[pygame.K_z] or mouse_buttons[0]
        if pressed and not pi.last_shot_pressed:
            pi.last_shot_pressed = True

            # calculamos posición del cursor en coordenadas del mundo
            mx, my = pygame.mouse.get_pos()
            world_x = camera_pos[0] - screen_center[0] + mx
            world_y = camera_pos[1] - screen_center[1] + my

            dir_vec = pygame.Vector2(world_x - tr.pos[0], world_y - tr.pos[1])
            if dir_vec.length() != 0:
                dir_vec = dir_vec.normalize()
            else:
                dir_vec = pygame.Vector2(0, -1)

            create_bullet(world, bullet_cfg, (tr.pos[0], tr.pos[1]), dir_vec)

        elif not pressed:
            pi.last_shot_pressed = False
