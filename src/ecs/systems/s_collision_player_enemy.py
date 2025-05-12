# ── src/ecs/systems/s_collision_player_enemy.py ───────────
import json, esper, pygame
from ecs.components.transform   import Transform
from ecs.components.sprite      import Sprite
from ecs.components.lives       import Lives
from ecs.components.tags.c_tag_player import CTagPlayer
from ecs.components.tags.c_tag_enemy  import CTagEnemy
from create.prefabs_creator import create_explosion

_EXPLO_CFG = json.load(open("assets/cfg/explosion.json", encoding="utf-8"))


def sistema_colision_player_enemy(world: esper.World) -> None:
    players  = list(world.get_components(CTagPlayer, Transform, Sprite, Lives))
    enemies  = list(world.get_components(CTagEnemy,  Transform, Sprite))
    if not players or not enemies:
        return

    for p_ent, (_, p_tr, p_sp, p_lv) in players:
        p_rect = p_sp.surface.get_rect(center=p_tr.pos)
        for e_ent, (_, e_tr, e_sp) in enemies:
            e_rect = e_sp.surface.get_rect(center=e_tr.pos)
            if p_rect.colliderect(e_rect):
                # explosión compartida
                create_explosion(world, _EXPLO_CFG, p_tr.pos)

                # restar vida y eliminar enemigo
                p_lv.current -= 1
                world.delete_entity(e_ent)

                # sin vidas -> eliminar jugador (o lanzar Game-Over)
                if p_lv.current <= 0:
                    world.delete_entity(p_ent)
                break
