# src/ecs/systems/input_system.py
import pygame
from esper import Processor

from ecs.components.player_input import PlayerInput
from ecs.components.velocity     import Velocity
from ecs.components.transform    import Transform
from create.prefabs_create       import create_bullet   # ← nombre real

class InputSystem(Processor):
    def process(self, dt: float) -> None:
        # 1) Eventos capturados por el GameEngine
        events = getattr(self.world, "_events", [])
        shoot_pressed = any(
            ev.type == pygame.KEYDOWN and ev.key == pygame.K_z for ev in events
        )

        # 2) Estado de teclas para movimiento continuo
        keys = pygame.key.get_pressed()

        # 3) Recorremos entidades controlables
        for _, (inp, vel, tr) in self.world.get_components(
                PlayerInput, Velocity, Transform):

            # ── Movimiento ──────────────────────────────────────────
            vel.vx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * inp.speed
            vel.vy = (keys[pygame.K_DOWN]  - keys[pygame.K_UP])   * inp.speed

            # ── Cool-down del disparo ──────────────────────────────
            inp.time_since_shot = max(0, inp.time_since_shot - dt)

            # ── Disparo ────────────────────────────────────────────
            if shoot_pressed and inp.time_since_shot == 0:
                bullet_pos = (tr.pos[0], tr.pos[1] - 8)
                print(f"[INFO] Disparo en {bullet_pos}")
                create_bullet(self.world, bullet_pos)            # ← dispara
                inp.time_since_shot = inp.shoot_cooldown
