# src/ecs/systems/s_enemy_spawn.py

import random
import esper
from ecs.components.c_enemy_spawner import CEnemySpawner
from create.prefabs_creator import create_enemy_plane

def sistema_enemy_spawn(world: esper.World, delta: float):
    # Itera correctamente sobre cada CEnemySpawner en la world
    for _, spawner in world.get_component(CEnemySpawner):
        spawner.timer += delta
        if spawner.timer >= spawner.interval:
            spawner.timer -= spawner.interval

            # Elige y clona la configuración base
            base_cfg = random.choice(spawner.configs)
            cfg = base_cfg.copy()

            # Inyecta la posición de spawn
            cfg["spawn"] = {
                "x": random.uniform(0, spawner.screen_width),
                "y": -cfg.get("frame_h", 16) / 2
            }

            print(f"[ENEMY_SPAWN] creando enemigo en x={cfg['spawn']['x']:.1f}")
            create_enemy_plane(world, cfg)
