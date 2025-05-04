# ecs/systems/collision_system.py
from esper import Processor
from math import hypot
from ecs.components.transform import Transform
from ecs.components.collider import Collider
from ecs.components.bullet import Bullet
from ecs.components.health import Health


class CollisionSystem(Processor):
    def process(self, _):
        entities = list(self.world.get_components(Transform, Collider))
        for i, (e1, (t1, c1)) in enumerate(entities):
            for e2, (t2, c2) in entities[i + 1:]:
                if hypot(t1.pos[0] - t2.pos[0], t1.pos[1] - t2.pos[1]) < (c1.radius + c2.radius):
                    self._handle_collision(e1, e2)

    # ------------------------------------------------------------
    def _handle_collision(self, a, b):
        a_bullet = self.world.component_for_entity(a, Bullet) if self.world.has_component(a, Bullet) else None
        b_bullet = self.world.component_for_entity(b, Bullet) if self.world.has_component(b, Bullet) else None

        # bala jugador vs enemigo
        if a_bullet and a_bullet.owner == "player" and self.world.has_component(b, Health):
            self.world.delete_entity(a)
            self._damage(b, a_bullet.damage)
        elif b_bullet and b_bullet.owner == "player" and self.world.has_component(a, Health):
            self.world.delete_entity(b)
            self._damage(a, b_bullet.damage)

    def _damage(self, ent, dmg):
        hp = self.world.component_for_entity(ent, Health)
        hp.hp -= dmg
        if hp.hp <= 0:
            self.world.delete_entity(ent)
