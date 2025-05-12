# src/ecs/systems/s_collision_player_enemy.py

import esper
import pygame
import json

from ecs.components.transform import Transform
from ecs.components.sprite import Sprite
from ecs.components.lives import Lives
from ecs.components.tags.c_tag_player import CTagPlayer
from ecs.components.tags.c_tag_enemy import CTagEnemy
from create.prefabs_creator import create_explosion
from core.states.game_over_state import GameOverState

# Configuración de explosión
with open("assets/cfg/explosion.json", encoding="utf-8") as _f:
    _EXPLO_CFG = json.load(_f)

def sistema_colision_player_enemy(world: esper.World, engine) -> None:
    players = list(world.get_components(CTagPlayer, Transform, Sprite, Lives))
    enemies = list(world.get_components(CTagEnemy, Transform, Sprite))

    if not players or not enemies:
        return

    p_ent, (_, p_tr, p_sp, p_lv) = players[0]
    p_rect = p_sp.surface.get_rect(center=p_tr.pos)

    for e_ent, (_, e_tr, e_sp) in enemies:
        e_rect = e_sp.surface.get_rect(center=e_tr.pos)

        if p_rect.colliderect(e_rect):
            # 1) Explosión del enemigo
            create_explosion(world, _EXPLO_CFG, e_tr.pos)
            world.delete_entity(e_ent, immediate=True)  # eliminar enemigo YA

            # 2) Perder una vida
            p_lv.current -= 1

            # 3) ¿Game Over?
            if p_lv.current <= 0:
                world.delete_entity(p_ent, immediate=True)
                engine.pop_state()                      # sale de PlayState
                engine.push_state(GameOverState(engine))

            break  # evitar múltiples colisiones en un solo frame
