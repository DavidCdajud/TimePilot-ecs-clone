# src/ecs/systems/s_movement.py
from ecs.components.transform import Transform
from ecs.components.velocity  import Velocity

def sistema_movimiento(world, dt):
    for ent, (tr, vel) in world.get_components(Transform, Velocity):
        x, y = tr.pos
        world.component_for_entity(ent, Transform).pos = (x + vel.vx*dt,
                                                          y + vel.vy*dt)
