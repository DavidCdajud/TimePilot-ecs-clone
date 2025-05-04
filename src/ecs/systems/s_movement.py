import esper
from ecs.components.transform import Transform
from ecs.components.velocity import Velocity

def sistema_movimiento(world: esper.World, delta_tiempo: float) -> None:
    """Actualiza la posición según la velocidad."""
    componentes = world.get_components(Transform, Velocity)

    for _, (transform, velocity) in componentes:
        transform.pos = (
            transform.pos[0] + velocity.vx * delta_tiempo,
            transform.pos[1] + velocity.vy * delta_tiempo
        )
