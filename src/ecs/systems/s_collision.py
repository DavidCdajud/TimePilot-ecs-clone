# src/ecs/systems/s_collision.py
import json
import esper
import pygame

from ecs.components.transform import Transform
from ecs.components.sprite   import Sprite
from ecs.components.tags.c_tag_bullet import CTagBullet
from ecs.components.tags.c_tag_enemy  import CTagEnemy
from ecs.components.health  import Health

from create.prefabs_creator import create_explosion

# Config de la explosión, cargada una vez
with open("assets/cfg/explosion.json", encoding="utf-8") as _f:
    EXPLO_CFG = json.load(_f)


def sistema_colisiones_balas_enemigos(world: esper.World) -> None:
    bullets = list(world.get_components(CTagBullet, Transform, Sprite))
    enemies = list(world.get_components(CTagEnemy,  Transform, Sprite, Health))
    if not bullets or not enemies:
        return

    for b_ent, (_, b_tr, b_sp) in bullets:
        b_rect = b_sp.surface.get_rect(center=b_tr.pos)

        for e_ent, (_, e_tr, e_sp, e_hp) in enemies:
            e_rect = e_sp.surface.get_rect(center=e_tr.pos)

            if b_rect.colliderect(e_rect):
                # ── impacto ───────────────────────────────
                world.delete_entity(b_ent)          # destruye bala
                e_hp.current -= 1                   # resta vida
                if e_hp.current <= 0:               # sin vida → explosión
                    create_explosion(world, EXPLO_CFG, e_tr.pos)
                    world.delete_entity(e_ent)
                break   # pasa a la siguiente bala
