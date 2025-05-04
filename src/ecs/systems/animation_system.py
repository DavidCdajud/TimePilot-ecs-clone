from esper import Processor
from ecs.components.sprite import Sprite
from ecs.components.animation import Animation

class AnimationSystem(Processor):
    """Actualiza el índice de cuadro para cada entidad animada."""
    def process(self, dt: float) -> None:
        for _, (anim, sp) in self.world.get_components(Animation, Sprite):
            anim.timer += dt
            if anim.timer >= anim.frame_duration:
                anim.timer -= anim.frame_duration
                anim.index = (anim.index + 1) % anim.frames
