# src/ecs/systems/s_expiration.py
import esper
from ecs.components.duration import Duration

def sistema_expiracion(world: esper.World, delta: float) -> None:
    for ent, dur in list(world.get_component(Duration)):
        dur.time_left -= delta
        if dur.time_left <= 0:
          
            world.delete_entity(ent, immediate=True)   # ← borra YA

