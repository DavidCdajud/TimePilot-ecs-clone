# ── src/ecs/systems/s_enemy_bullet_collision.py ────────────────
import json, random
import esper, pygame
from ecs.components.transform           import Transform
from ecs.components.sprite              import Sprite
from ecs.components.bullet              import Bullet
from ecs.components.lives               import Lives
from ecs.components.tags.c_tag_player   import CTagPlayer
from ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from create.prefabs_creator             import create_explosion
from core.service_locator               import ServiceLocator as SL 

# usamos MISMA explosión pequeña que el jugador
with open("assets/cfg/explosion.json", encoding="utf-8") as _f:
    _EXPLO_CFG = json.load(_f)

def sistema_enemy_bullet_collision(world: esper.World, engine) -> None:
    # — jugador (único) —
    players = list(world.get_components(CTagPlayer, Transform, Sprite, Lives))
    if not players:
        return
    p_ent, (_, p_tr, p_sp, p_lv) = players[0]
    p_rect = p_sp.surface.get_rect(center=p_tr.pos)

    # — balas enemigas —
    for b_ent, (_, b_tr, b_sp, b_data) in \
            world.get_components(CTagEnemyBullet, Transform, Sprite, Bullet):

        b_rect = b_sp.surface.get_rect(center=b_tr.pos)
        if not b_rect.colliderect(p_rect):
            continue

        # ▸ destruir bala
        world.delete_entity(b_ent, immediate=True)

        SL.sound_service.play_sfx("assets/snd/player_hit.wav")

        # ▸ restar vida según daño
        p_lv.current -= b_data.damage
        if p_lv.current <= 0:
            # explosión del jugador + Game Over
            create_explosion(world, _EXPLO_CFG, p_tr.pos)
            world.delete_entity(p_ent)
            engine.pop_state()             # cierra Play
            from core.states.game_over_state import GameOverState
            engine.push_state(GameOverState(engine))
        break
