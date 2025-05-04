# ecs/systems/bullet_system.py
import pygame
from esper import Processor
from ecs.components.bullet import Bullet
from ecs.components.transform import Transform
from ecs.components.velocity import Velocity

class BulletSystem(Processor):
    def process(self, dt: float):
        screen_h = pygame.display.get_surface().get_height()

        for ent, (tr, vel) in self.world.get_components(Transform, Velocity):
            if not self.world.has_component(ent, Bullet):
                continue

            # actualizar posición (MovementSystem lo haría, pero así evitamos orden)
            tr.pos = (tr.pos[0] + vel.vx * dt,
                      tr.pos[1] + vel.vy * dt)

            # destruir bala fuera de pantalla
            if tr.pos[1] < -10 or tr.pos[1] > screen_h + 10:
                self.world.delete_entity(ent)
