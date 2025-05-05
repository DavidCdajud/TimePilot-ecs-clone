# src/ecs/systems/s_player_rotation.py

import math
import esper
from ecs.components.velocity import Velocity
from ecs.components.sprite import Sprite
from ecs.components.player_orientation import PlayerOrientation

# Ajuste en grados para corregir el desfase de tu hoja de sprites
ANGLE_OFFSET = -90  

def sistema_player_rotation(world: esper.World) -> None:
    for ent, (vel, orient, sprite) in world.get_components(
        Velocity, PlayerOrientation, Sprite
    ):
        vx, vy = vel.vx, vel.vy

        if vx == 0 and vy == 0:
            idx = orient.neutral_index
        else:
            # 1) Calcula el ángulo original
            raw_angle = math.degrees(math.atan2(-vy, vx))  # 0° = derecha, 90° = arriba

            # 2) Aplica el offset para realinear el índice con tu sheet
            angle = (raw_angle + ANGLE_OFFSET) % 360

            # 3) Mapea 0–360° a 0–n_frames
            n = len(orient.frames)
            idx = int((angle / 360) * n) % n

        # Asigna el frame correcto
        sprite.surface = orient.frames[idx]
