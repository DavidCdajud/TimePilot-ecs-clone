# src/ecs/systems/s_cloud_spawner.py
import random
import esper
import pygame
from ecs.components.cloud_spawner import CloudSpawner
from ecs.components.transform import Transform
from ecs.components.sprite import Sprite
from create.prefabs_creator import create_cloud
from core.service_locator import ServiceLocator
from src.ecs.components.tags.c_tag_cloud import CTagCloud

def sistema_spawner_nubes(world: esper.World, delta: float) -> None:
    # 1) Construyo una lista de (Transform, Sprite) de todas las nubes actuales
    existing = [
        (tr, sp)
        for _, (tag, tr, sp) in world.get_components(CTagCloud, Transform, Sprite)
    ]

    # 2) Para cada spawner
    for _, spawner in world.get_component(CloudSpawner):
        # lógica de initial_count (semilla inicial)
        if spawner.initial_count > 0:
            for _ in range(spawner.initial_count):
                cfg = random.choice(spawner.configs)
                spawn_cfg = cfg.copy()
                spawn_cfg["spawn"] = {
                    "x": random.uniform(0, spawner.screen_width),
                    "y": random.uniform(spawner.min_y, spawner.max_y)
                }
                create_cloud(world, spawn_cfg)
            spawner.initial_count = 0

        # llegadas aleatorias
        spawner.timer += delta
        if spawner.timer >= spawner.next_spawn:
            spawner.timer -= spawner.next_spawn
            spawner.next_spawn = random.uniform(spawner.min_interval, spawner.max_interval)

            # genero de 1 a 3 nubes
            for _ in range(random.randint(1, 3)):
                cfg = random.choice(spawner.configs)

                # dimensiones del frame
                sheet = ServiceLocator.images.get(cfg["image"])
                fw = cfg.get("frame_w", sheet.get_width())
                fh = cfg.get("frame_h", sheet.get_height())

                # intento hasta 5 posiciones no superpuestas
                for _ in range(5):
                    x = random.uniform(0, spawner.screen_width)
                    y = random.uniform(spawner.min_y, spawner.max_y)

                    # compruebo solapamiento AABB
                    overlap = False
                    for tr, sp in existing:
                        ex, ey = tr.pos
                        sw, sh = sp.surface.get_size()
                        if abs(x - ex) < (fw/2 + sw/2) and abs(y - ey) < (fh/2 + sh/2):
                            overlap = True
                            break

                    if not overlap:
                        spawn_cfg = cfg.copy()
                        spawn_cfg["spawn"] = {"x": x, "y": y}
                        create_cloud(world, spawn_cfg)
                        # agrego la nube recién creada a existing para no solapar
                        new_tr = Transform((x, y))
                        new_sp = Sprite(sheet.subsurface(pygame.Rect(0, 0, fw, fh)))
                        existing.append((new_tr, new_sp))
                        break
            # fin de generación de nubes