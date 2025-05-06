# src/ecs/systems/s_animation.py
import esper
from ecs.components.sprite import Sprite
from ecs.components.animation import Animation

def sistema_animacion(world: esper.World, dt: float) -> None:
    for _, (anim, sprite) in world.get_components(Animation, Sprite):
        anim.curr_time += dt
        if anim.curr_time < 1.0 / anim.framerate:
            continue

        anim.curr_time = 0.0

        # Avanzamos frame
        if anim.curr_frame < len(anim.frames) - 1:
            anim.curr_frame += 1
        elif anim.loop:                    # ← solo reiniciamos si loop es True
            anim.curr_frame = 0

        sprite.surface = anim.frames[anim.curr_frame]
