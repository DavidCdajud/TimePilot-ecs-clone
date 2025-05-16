# src/ecs/systems/s_input_player.py
import json, pygame, esper
from core.service_locator import ServiceLocator as SL
from ecs.components.velocity      import Velocity
from ecs.components.player_input  import PlayerInput
from ecs.components.transform     import Transform
from create.prefabs_creator       import create_bullet

with open("assets/cfg/bullet.json", encoding="utf-8") as _f:
    BULLET_CFG = json.load(_f)

def sistema_input_player(world: esper.World, dt: float) -> None:
    keys = pygame.key.get_pressed()

    for ent, (vel, pi) in world.get_components(Velocity, PlayerInput):
        # ── Movimiento ───────────────────────────────────────────
        vx = vy = 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: vx -= pi.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: vx += pi.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: vy -= pi.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: vy += pi.speed
        vel.vx, vel.vy = vx, vy

        move_vec = pygame.Vector2(vx, vy)
        if move_vec.length_squared():               # solo si se mueve
            pi.last_dir = move_vec.normalize()

        # ── Disparo con cooldown ────────────────────────────────
        pi.time_since_last_shot += dt
        shooting = keys[pygame.K_z] or keys[pygame.K_SPACE]

        if shooting and pi.time_since_last_shot >= pi.fire_cooldown:
            pi.time_since_last_shot = 0.0

            # dirección de la bala:
            fire_dir = move_vec.normalize() if move_vec.length_squared() else pi.last_dir

            tr = world.component_for_entity(ent, Transform)
            create_bullet(world, BULLET_CFG, tr.pos, fire_dir)

            # ▶ sonido de disparo
            SL.sound_service.play_sfx("assets/snd/player_shoot.ogg", volume=0.8)
