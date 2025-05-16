# ── src/ecs/systems/s_collision.py ─────────────────────────────
import json, pygame, esper

from ecs.components.transform            import Transform
from ecs.components.sprite               import Sprite
from ecs.components.health               import Health
from ecs.components.score_board          import ScoreBoard
from ecs.components.c_enemy_spawner      import CEnemySpawner
from ecs.components.enemy_counter        import EnemyCounter

from ecs.components.tags.c_tag_bullet    import CTagBullet
from ecs.components.tags.c_tag_enemy     import CTagEnemy
from ecs.components.tags.c_tag_boss      import CTagBoss

from core.states.win_state               import WinState
from core.service_locator                import ServiceLocator as SL

from create.prefabs_creator              import create_explosion, create_score_popup


# ───────────── Configuración ──────────────────────────────────
with open("assets/cfg/explosion.json", encoding="utf-8") as _f:
    EXPLO_CFG = json.load(_f)

PUNTOS_POR_ENEMIGO = 400
# ───────────────────────────────────────────────────────────────


def sistema_colisiones_balas_enemigos(world: esper.World, engine) -> None:
    """Gestión del impacto bala ⇄ enemigo (+ jefe)."""
    bullets  = world.get_components(CTagBullet, Transform, Sprite)
    enemies  = world.get_components(CTagEnemy,  Transform, Sprite, Health)
    marcador = next(iter(world.get_component(ScoreBoard)), None)
    if not bullets or not enemies or not marcador:
        return

    _, sb = marcador  # único tablero

    for b_ent, (_, b_tr, b_sp) in bullets:
        b_rect = b_sp.surface.get_rect(center=b_tr.pos)

        for e_ent, (_, e_tr, e_sp, e_hp) in enemies:
            if not b_rect.colliderect(e_sp.surface.get_rect(center=e_tr.pos)):
                continue

            # ---------- impacto ----------
            world.delete_entity(b_ent, immediate=True)       # bala fuera
            e_hp.current -= 1

            if e_hp.current <= 0:
                # ☑︎ ¿era el jefe? –- lo averiguamos **antes** de borrarlo
                is_boss = world.has_component(e_ent, CTagBoss)

                # efectos, score, sonido
                create_explosion(world, EXPLO_CFG, e_tr.pos)
                create_score_popup(world, PUNTOS_POR_ENEMIGO, e_tr.pos)
                sb.score += PUNTOS_POR_ENEMIGO
                SL.sound_service.play_sfx("assets/snd/enemy_die.ogg", 0.7)

                # contadores de bajas
                for _, sp in world.get_component(CEnemySpawner):
                    sp.total_killed += 1
                cnt = world.get_component(EnemyCounter)
                if cnt:
                    cnt[0][1].kills += 1

                # eliminamos definitivamente al enemigo
                world.delete_entity(e_ent, immediate=True)

                # si era el jefe ⇒ victoria
                if is_boss:
                    world.clear_database()
                    return                         
