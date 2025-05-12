# ── src/ecs/systems/s_enemy_spawn.py ─────────────────────────────
"""
Genera enemigos normales (máx. 8-10 simultáneos) alrededor del jugador y,
después de alcanzar el objetivo de bajas, invoca al jefe final.

• La distancia de aparición es aleatoria dentro de un anillo definido por
  _MIN_DISTANCE y _MAX_DISTANCE.
• Cada enemigo recién creado puede (o no) llevar EnemyAI, dependiendo de
  «chase_prob» en el componente CEnemySpawner.
• Cuando el spawner registra 40 enemigos destruidos (kill_goal) deja de
  crear enemigos normales, aparece el boss y se marca «boss_spawned».
"""

import json
import math
import random

import esper
import pygame

from ecs.components.transform import Transform
from ecs.components.c_enemy_spawner import CEnemySpawner
from ecs.components.tags.c_tag_enemy import CTagEnemy
from ecs.components.enemy_ai import EnemyAI
from ecs.components.tags.c_tag_player import CTagPlayer

from create.prefabs_creator import (
    create_enemy_plane,
    create_boss_plane,
)

# ─────────────────── Configuración del jefe ─────────────────────
with open("assets/cfg/boss.json", encoding="utf-8") as _f:
    BOSS_CFG = json.load(_f)

# ───────────── Parámetros de spawn alrededor del jugador ────────
_MIN_DISTANCE = 180       # px mínimos al jugador
_MAX_DISTANCE = 260       # px máximos al jugador
# ----------------------------------------------------------------


def _random_point_around(center: pygame.Vector2) -> tuple[float, float]:
    """Devuelve una posición aleatoria dentro del anillo [_MIN, _MAX] px."""
    ang = random.uniform(0, math.tau)
    dist = random.uniform(_MIN_DISTANCE, _MAX_DISTANCE)
    offset = pygame.Vector2(math.cos(ang), math.sin(ang)) * dist
    pt = center + offset
    return pt.x, pt.y


# ───────────────────────── Sistema ECS ──────────────────────────
def sistema_enemy_spawn(world: esper.World, dt: float) -> None:
    # 1) Localizar al jugador ------------------------------------------------
    player_entry = next(iter(world.get_component(CTagPlayer)), None)
    if not player_entry:
        return

    p_ent, _ = player_entry
    p_tr = world.component_for_entity(p_ent, Transform)
    player_pos = pygame.Vector2(p_tr.pos)

    # 2) Gestionar el único CEnemySpawner -----------------------------------
    for sp_ent, sp in world.get_component(CEnemySpawner):
        # Si el jefe ya fue creado, no hacemos nada más
        if sp.boss_spawned:
            continue

        # Nº de enemigos simultáneos en pantalla
        alive = len(world.get_component(CTagEnemy))
        if alive >= sp.max_alive:
            sp.timer = 0.0        # resetea para evitar ráfagas brutales
            continue

        # Temporizador de aparición
        sp.timer += dt
        if sp.timer < sp.interval:
            continue
        sp.timer = 0.0

        # ── Invocar jefe final ───────────────────────────────────────────
        if sp.total_killed >= sp.kill_goal:
            # Posicionamos al boss cerca, pero dentro del rango configurable
            boss_x, boss_y = _random_point_around(player_pos)
            create_boss_plane(world, BOSS_CFG, (boss_x, boss_y))
            sp.boss_spawned = True
            continue

        # ── Crear enemigo normal ────────────────────────────────────────
        cfg = random.choice(sp.configs).copy()
        spawn_x, spawn_y = _random_point_around(player_pos)
        cfg["spawn"] = {"x": spawn_x, "y": spawn_y}
        ent = create_enemy_plane(world, cfg)

        # Decidir si el enemigo persigue al jugador
        if random.random() > sp.chase_prob:
            # NO persigue → se le quita el componente EnemyAI
            if world.has_component(ent, EnemyAI):
                world.remove_component(ent, EnemyAI)
        # Si persigue, EnemyAI ya viene en el prefab; no hay que hacer nada
