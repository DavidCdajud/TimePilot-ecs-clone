# src/ecs/systems/s_cloud_spawner.py
import random
import esper
import pygame
from typing import Tuple

from ecs.components.cloud_spawner import CloudSpawner
from ecs.components.transform import Transform
from ecs.components.sprite import Sprite
from create.prefabs_creator import create_cloud
from core.service_locator import ServiceLocator
from ecs.components.tags.c_tag_cloud import CTagCloud


def sistema_spawner_nubes(
    world: esper.World,
    camera_pos: Tuple[float, float]
) -> None:
    """
    Spawnea nubes cuando la cámara (jugador) se ha movido lo suficiente.
    """
    # 1) Recolecta posición y sprite de todas las nubes existentes
    existing = [
        (tr, sp)
        for _, (tag, tr, sp) in world.get_components(CTagCloud, Transform, Sprite)
    ]

    # 2) Itera sobre cada spawner configurado
    for _, spawner in world.get_component(CloudSpawner):
        last_x, last_y = spawner.last_cam_pos
        cam_x, cam_y = camera_pos

        dx = cam_x - last_x
        dy = cam_y - last_y

        # Sólo spawn si te mueves más que el umbral
        if abs(dx) >= spawner.move_threshold or abs(dy) >= spawner.move_threshold:
            # Genera entre 1 y 3 nubes por movimiento significativo
            for _ in range(random.randint(1, 3)):
                cfg = random.choice(spawner.configs)
                spawn_cfg = cfg.copy()

                # Decide spawn fuera de vista según dirección dominante
                if abs(dy) >= abs(dx):
                    # Vertical
                    if dy < 0:
                        # Movimiento hacia arriba → spawnear arriba
                        y = cam_y + spawner.screen_height/2 + cfg["frame_h"]/2
                    else:
                        # Movimiento hacia abajo → spawnear abajo
                        y = cam_y - spawner.screen_height/2 - cfg["frame_h"]/2
                    x = random.uniform(
                        cam_x - spawner.screen_width/2,
                        cam_x + spawner.screen_width/2
                    )
                else:
                    # Horizontal
                    if dx > 0:
                        # Movimiento derecha → spawnear a la izquierda
                        x = cam_x - spawner.screen_width/2 - cfg["frame_w"]/2
                    else:
                        # Movimiento izquierda → spawnear a la derecha
                        x = cam_x + spawner.screen_width/2 + cfg["frame_w"]/2
                    y = random.uniform(spawner.min_y, spawner.max_y)

                spawn_cfg["spawn"] = {"x": x, "y": y}
                create_cloud(world, spawn_cfg)

            # Actualiza la última posición de cámara para el spawner
            spawner.last_cam_pos = camera_pos