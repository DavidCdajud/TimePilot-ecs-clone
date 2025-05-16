# ── src/ecs/systems/s_collision.py ───────────────────────────────
import json, pygame, esper

from ecs.components.transform            import Transform
from ecs.components.sprite               import Sprite
from ecs.components.health               import Health
from ecs.components.score_board          import ScoreBoard
from ecs.components.c_enemy_spawner      import CEnemySpawner      # para total_killed
from ecs.components.enemy_counter        import EnemyCounter       # ← NUEVO

from ecs.components.tags.c_tag_bullet    import CTagBullet
from ecs.components.tags.c_tag_enemy     import CTagEnemy

from create.prefabs_creator              import create_explosion, create_score_popup

# ───────────────────────── Configuración ─────────────────────────
with open("assets/cfg/explosion.json", encoding="utf-8") as _f:
    EXPLO_CFG = json.load(_f)

PUNTOS_POR_ENEMIGO = 400
# ──────────────────────────────────────────────────────────────────


def sistema_colisiones_balas_enemigos(world: esper.World) -> None:
    """
    • Detecta impactos bala–enemigo.
    • Destruye bala y enemigo in-situ.
    • Lanza explosión + popup de puntuación.
    • Actualiza ScoreBoard y contadores de bajas.
    """
    bullets  = list(world.get_components(CTagBullet, Transform, Sprite))
    enemies  = list(world.get_components(CTagEnemy,  Transform, Sprite, Health))
    tableros = list(world.get_component(ScoreBoard))
    if not bullets or not enemies or not tableros:
        return

    _, sb = tableros[0]               # único marcador

    for b_ent, (_, b_tr, b_sp) in bullets:
        b_rect = b_sp.surface.get_rect(center=b_tr.pos)

        for e_ent, (_, e_tr, e_sp, e_hp) in enemies:
            e_rect = e_sp.surface.get_rect(center=e_tr.pos)
            if not b_rect.colliderect(e_rect):
                continue

            # ── Impacto ─────────────────────────────────────────
            world.delete_entity(b_ent, immediate=True)      # bala fuera YA
            e_hp.current -= 1

            if e_hp.current <= 0:
                # ▸ efectos & puntuación
                world.delete_entity(e_ent, immediate=True)
                create_explosion(world, EXPLO_CFG, e_tr.pos)
                create_score_popup(world, PUNTOS_POR_ENEMIGO, e_tr.pos)
                sb.score += PUNTOS_POR_ENEMIGO

                # ▸ contador local del spawner (para jefe)
                for _, sp in world.get_component(CEnemySpawner):
                    sp.total_killed += 1

                # ▸ NUEVO: contador global de KILLS
                cnt = world.get_component(EnemyCounter)
                if cnt:
                    cnt[0][1].kills += 1    # solo hay uno

            break                           # siguiente bala
