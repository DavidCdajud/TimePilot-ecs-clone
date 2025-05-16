# ── src/ecs/systems/s_boss_shoot.py ─────────────────────────────
import random, math, json, pygame, esper

from ecs.components.transform        import Transform
from ecs.components.velocity         import Velocity
from ecs.components.boss_shooter     import BossShooter
from create.prefabs_creator          import create_enemy_bullet
from core.service_locator            import ServiceLocator as SL

# ── Configuración de la bala (re-usamos la del enemigo común) ──
with open("assets/cfg/enemy_bullet.json", encoding="utf-8") as _f:
    BULLET_CFG = json.load(_f)


def sistema_boss_shoot(world: esper.World, dt: float) -> None:
    # ────────────────────── Localizar jugador ───────────────────
    from ecs.components.tags.c_tag_player import CTagPlayer
    p_lookup = next(iter(world.get_component(CTagPlayer)), None)
    if not p_lookup:
        return

    p_ent, _ = p_lookup
    p_tr     = world.component_for_entity(p_ent, Transform)
    player_pos = pygame.Vector2(p_tr.pos)

    # ─────────────────── Recorrer jefes con BossShooter ─────────
    for b_ent, (tr, shooter) in world.get_components(Transform, BossShooter):

        # 1)  Cool-down individual
        shooter.time += dt
        if shooter.time < shooter.cooldown:
            continue
        shooter.time -= shooter.cooldown        # reinicio limpio

        # 2)  Probabilidad de disparar
        if random.random() > shooter.fire_prob:
            continue

        # ─────────── Par á m e t r o s   d e   s p r e a d ──────────
        spread_cnt   = getattr(shooter, "spread_count", 5)    # impar
        spread_ang   = getattr(shooter, "spread_angle", 35)   # ° totales
        speed_override = getattr(shooter, "bullet_speed", None)

        # Vector base hacia el jugador
        base_dir = pygame.Vector2(player_pos - pygame.Vector2(tr.pos))
        if base_dir.length_squared() == 0:
            base_dir = pygame.Vector2(0, 1)
        base_dir = base_dir.normalize()

        step_deg   = spread_ang / (spread_cnt - 1)
        start_deg  = -spread_ang / 2

        # ────────────────── Crear balas en rocío ─────────────────
        for i in range(spread_cnt):
            ang_deg   = start_deg + i * step_deg
            dir_vec   = base_dir.rotate(ang_deg)
            spawn_pos = pygame.Vector2(tr.pos) + dir_vec * 12

            bullet_ent = create_enemy_bullet(world, BULLET_CFG, spawn_pos, dir_vec)

            # ¿Velocidad especial para el jefe?
            if speed_override is not None:
                vel      = world.component_for_entity(bullet_ent, Velocity)
                vel.vx   = dir_vec.x * speed_override
                vel.vy   = dir_vec.y * speed_override

        # SFX
        SL.sound_service.play_sfx("assets/snd/enemy_shoot.wav", 0.7)
