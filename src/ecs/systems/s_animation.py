import esper
from ecs.components.sprite import Sprite
from ecs.components.animation import Animation

def sistema_animacion(world: esper.World, dt: float) -> None:
    for _, (anim, sprite) in world.get_components(Animation, Sprite):
        anim.curr_time += dt
        if anim.curr_time >= 1.0 / anim.framerate:
            anim.curr_time = 0.0
            anim.curr_frame = (anim.curr_frame + 1) % len(anim.frames)
            sprite.surface = anim.frames[anim.curr_frame]
