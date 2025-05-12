# ── src/ecs/systems/s_enemy_spawn.py ─────────────────────────────
import random, math, esper, pygame
from ecs.components.transform        import Transform
from ecs.components.c_enemy_spawner  import CEnemySpawner
from ecs.components.tags.c_tag_enemy import CTagEnemy          # ← import único
from ecs.components.enemy_ai         import EnemyAI            # ← import único
from ecs.components.tags.c_tag_player import CTagPlayer
from create.prefabs_creator          import (
    create_enemy_plane,
    create_boss_plane,               # ← nuevo prefab para el jefe
)

_MIN_DISTANCE  = 180    # px mínimos al jugador
_MAX_DISTANCE  = 260    # px máximos al jugador

def _random_point_around(center: pygame.Vector2) -> tuple[float, float]:
    ang  = random.uniform(0, math.tau)
    dist = random.uniform(_MIN_DISTANCE, _MAX_DISTANCE)
    off  = pygame.Vector2(math.cos(ang), math.sin(ang)) * dist
    pt   = center + off
    return pt.x, pt.y

# -----------------------------------------------------------------
def sistema_enemy_spawn(world: esper.World, dt: float) -> None:
    # 1) localizar jugador -------------------------------------------------
    player = next(iter(world.get_component(CTagPlayer)), None)
    if not player:
        return
    p_ent, _ = player
    p_tr = world.component_for_entity(p_ent, Transform)
    player_pos = pygame.Vector2(p_tr.pos)

    # 2) único spawner en escena ------------------------------------------
    for sp_ent, sp in world.get_component(CEnemySpawner):
        if sp.boss_spawned:          # jefe ya creado → nada más
            continue

        # enemigos vivos actualmente
        alive = len(world.get_component(CTagEnemy))
        if alive >= sp.max_alive:    # tope simultáneo (8-10)
            sp.timer = 0
            continue

        # temporizador
        sp.timer += dt
        if sp.timer < sp.interval:
            continue
        sp.timer = 0.0

        # ¿invocar jefe?
        if sp.total_killed >= sp.kill_goal:
            create_boss_plane(world, player_pos)
            sp.boss_spawned = True
            continue

        # 3) crear enemigo normal ----------------------------------------
        cfg = random.choice(sp.configs).copy()
        cfg["spawn"] = {"x": 0, "y": 0}
        cfg["spawn"]["x"], cfg["spawn"]["y"] = _random_point_around(player_pos)
        ent = create_enemy_plane(world, cfg)

        # ¿persigue o no al jugador?
        if random.random() > sp.chase_prob:
            # NO persigue → quitar EnemyAI
            if world.has_component(ent, EnemyAI):
                world.remove_component(ent, EnemyAI)
        # (si persigue, EnemyAI ya viene en el prefab)
