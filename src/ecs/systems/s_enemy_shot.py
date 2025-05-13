# ── src/ecs/systems/s_enemy_shoot.py ───────────────────────────
import random, pygame, esper
from ecs.components.transform        import Transform
from ecs.components.enemy_shooter    import EnemyShooter
from ecs.components.enemy_ai         import EnemyAI          # sólo quienes persiguen
from ecs.components.tags.c_tag_enemy import CTagEnemy
from ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from create.prefabs_creator          import create_enemy_bullet
import json

# Re-usamos la misma config de bala / sonido
with open("assets/cfg/enemy_bullet.json", encoding="utf-8") as _f:
    BULLET_CFG = json.load(_f)

def sistema_enemy_shoot(world: esper.World, dt: float) -> None:
    # 1) localizar jugador
    from ecs.components.tags.c_tag_player import CTagPlayer
    player = next(iter(world.get_component(CTagPlayer)), None)
    if not player:
        return
    p_ent, _ = player
    p_tr = world.component_for_entity(p_ent, Transform)
    player_pos = pygame.Vector2(p_tr.pos)

    # 2) recorre sólo enemigos CON EnemyShooter
    for e_ent, (tr, shooter) in world.get_components(Transform, EnemyShooter):
        # opcional: sólo los que tienen EnemyAI disparan
        if not world.has_component(e_ent, EnemyAI):
            continue

        shooter.time += dt
        if shooter.time < shooter.cooldown:
            continue                      # aún no toca

        shooter.time -= shooter.cooldown  # reinicio limpio

        if random.random() > shooter.fire_prob:
            continue                      # fallo de probabilidad

        # 3) dispara
        dir_vec = player_pos - pygame.Vector2(tr.pos)
        if dir_vec.length_squared() == 0:
            dir_vec = pygame.Vector2(0, 1)  # fallback

        # salimos un poco delante del morro para que no se “tape”
        spawn = pygame.Vector2(tr.pos) + dir_vec.normalize() * 8
        create_enemy_bullet(world, BULLET_CFG, spawn, dir_vec)
