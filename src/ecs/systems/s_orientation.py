# src/ecs/systems/s_orientation.py
import math
import esper
from ecs.components.velocity import Velocity
from ecs.components.orientation import Orientation
from ecs.components.sprite import Sprite

def sistema_orientacion(world: esper.World) -> None:
    for ent, (vel, ori, spr) in world.get_components(Velocity, Orientation, Sprite):
        vx, vy = vel.vx, vel.vy
        if vx == 0 and vy == 0:
            idx = ori.neutral_index
        else:
            ang = math.degrees(math.atan2(vy, vx))
            if ang < 0: ang += 360
            n = len(ori.frames)
            sector = 360 / n
            idx = int((ang + sector/2) // sector) % n

        frame = ori.frames[idx]
        spr.surface = frame
        spr.offset = (frame.get_width()//2, frame.get_height()//2)
