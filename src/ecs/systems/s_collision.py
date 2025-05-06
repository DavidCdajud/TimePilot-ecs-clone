# src/ecs/systems/s_collision.py
import json
import esper
import pygame

from ecs.components.transform import Transform
from ecs.components.sprite   import Sprite
from ecs.components.tags.c_tag_bullet import CTagBullet
from ecs.components.tags.c_tag_enemy  import CTagEnemy
from ecs.components.health  import Health

from create.prefabs_creator import create_explosion, create_score_popup
from ecs.components.score_board import ScoreBoard

# Config de la explosión, cargada una vez
with open("assets/cfg/explosion.json", encoding="utf-8") as _f:
    EXPLO_CFG = json.load(_f)


PUNTOS_POR_ENEMIGO = 400

def sistema_colisiones_balas_enemigos(world: esper.World) -> None:
    bullets  = list(world.get_components(CTagBullet, Transform, Sprite))
    enemies  = list(world.get_components(CTagEnemy,  Transform, Sprite, Health))
    tableros = list(world.get_component(ScoreBoard))
    if not bullets or not enemies or not tableros:
        return
    score_ent, sb = tableros[0]

    for b_ent, (_, b_tr, b_sp) in bullets:
        b_rect = b_sp.surface.get_rect(center=b_tr.pos)
        for e_ent, (_, e_tr, e_sp, e_hp) in enemies:
            e_rect = e_sp.surface.get_rect(center=e_tr.pos)
            if not b_rect.colliderect(e_rect):
                continue

            world.delete_entity(b_ent)          # 🔸 destruye bala
            e_hp.current -= 1
            if e_hp.current <= 0:
                world.delete_entity(e_ent)      # 🔸 destruye enemigo
                create_explosion(world, EXPLO_CFG, e_tr.pos)
                create_score_popup(world, PUNTOS_POR_ENEMIGO, e_tr.pos)
                sb.score += PUNTOS_POR_ENEMIGO  # 🔸 suma puntos
            break