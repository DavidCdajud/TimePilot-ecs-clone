# src/create/prefab_creator.py

import random
from typing import List, Optional, Tuple

import esper
import pygame

from ecs.components.transform import Transform
from ecs.components.velocity import Velocity
from ecs.components.sprite import Sprite
from ecs.components.animation import Animation
from core.service_locator import ServiceLocator
from ecs.components.player_input import PlayerInput
from ecs.components.player_orientation import PlayerOrientation
from ecs.components.tags.c_tag_cloud import CTagCloud
from src.ecs.components.bullet import Bullet
from src.ecs.components.tags.c_tag_bullet import CTagBullet


def _slice_sheet(
    sheet: pygame.Surface,
    frame_w: int,
    frame_h: int,
    num_frames: Optional[int] = None
) -> List[pygame.Surface]:
    """
    Extrae hasta num_frames frames del sheet (columnas x filas).
    """
    sw, sh = sheet.get_size()
    cols = sw // frame_w
    rows = sh // frame_h
    max_frames = cols * rows
    total = min(num_frames or max_frames, max_frames)

    frames: List[pygame.Surface] = []
    for idx in range(total):
        col = idx % cols
        row = idx // cols
        x, y = col * frame_w, row * frame_h
        rect = pygame.Rect(x, y, frame_w, frame_h)
        frames.append(sheet.subsurface(rect))
    return frames


def _center_offset(surf: pygame.Surface) -> Tuple[int, int]:
    return surf.get_width() // 2, surf.get_height() // 2


def create_player_plane(world: esper.World, cfg: dict) -> int:
    """
    Crea la nave del jugador:
      - Transform, Velocity
      - PlayerInput (define la velocidad)
      - Sprite (frame neutral)
      - PlayerOrientation (todos los frames para orientar según vx,vy)
    """
    sheet = ServiceLocator.images.get(cfg["image"])
    frames = _slice_sheet(sheet, cfg["frame_w"], cfg["frame_h"], cfg.get("frames"))
    neutral_idx = cfg.get("start_index", 0)

    ent = world.create_entity()
    world.add_component(ent, Transform((cfg["spawn"]["x"], cfg["spawn"]["y"])))
    world.add_component(ent, Velocity(0.0, 0.0))
    world.add_component(ent, PlayerInput(cfg["speed"]))

    # Frame inicial (neutral) y offset centrado
    first_frame = frames[neutral_idx]
    offset = _center_offset(first_frame)
    world.add_component(ent, Sprite(first_frame, offset, layer=3))

    # Guarda todos los frames para el sistema de orientación
    world.add_component(ent, PlayerOrientation(frames, neutral_index=neutral_idx))

    return ent


def create_cloud(world: esper.World, cfg: dict) -> int:
    """
    Crea una nube. Si lleva sheet de animación, usa Animation.
    Añade CTagCloud para que el sistema de spawn la reconozca.
    """
    sheet = ServiceLocator.images.get(cfg["image"])
    fw, fh = cfg.get("frame_w"), cfg.get("frame_h")
    num = cfg.get("frames")
    frate = cfg.get("framerate", 6)

    # Extrae frames si es un sheet, o usa la imagen completa
    if fw and fh:
        frames = _slice_sheet(sheet, fw, fh, num)
        if not frames:
            frames = [sheet]
    else:
        frames = [sheet]

    # Crea la entidad con el primer frame
    surf = frames[0]
    offset = _center_offset(surf)
    ent = world.create_entity()
    world.add_component(ent, Transform((cfg["spawn"]["x"], cfg["spawn"]["y"])))
    world.add_component(ent, Sprite(surf, offset))
    world.add_component(ent, CTagCloud())

    # Si hay varios frames, añade la animación
    if len(frames) > 1:
        world.add_component(ent, Animation(frames, framerate=frate))

    return ent


def _center_offset(surf: pygame.Surface) -> Tuple[int, int]:
    return surf.get_width() // 2, surf.get_height() // 2

def create_bullet(
    world: esper.World,
    cfg: dict,
    start_pos: Tuple[float, float],
    direction: pygame.Vector2
) -> int:
    """
    Crea una bala que se mueve en la dirección dada:
      - Transform, Velocity, Sprite
      - CTagBullet para colisiones
      - Bullet(owner, damage) para lógica de daño
      - Animation si es un sheet animado
    cfg debe contener:
      - image: ruta al sprite o spritesheet
      - speed: velocidad de la bala
      - frame_w, frame_h (opcional): tamaño de cada frame
      - frames (opcional): número de frames a extraer
      - framerate (opcional): velocidad de animación
      - damage (opcional): daño que inflige
    """
    sheet = ServiceLocator.images.get(cfg["image"])
    fw, fh = cfg.get("frame_w"), cfg.get("frame_h")
    num = cfg.get("frames")
    frate = cfg.get("framerate", 12)

    # Extraer frames de un sheet o usar imagen completa
    if fw and fh:
        frames = _slice_sheet(sheet, fw, fh, num)
        surf = frames[0] if frames else sheet
    else:
        frames = [sheet]
        surf = sheet

    ent = world.create_entity()
    # Posición y velocidad
    world.add_component(ent, Transform(start_pos))
    vel_vec = direction.normalize() * cfg["speed"]
    world.add_component(ent, Velocity(vel_vec.x, vel_vec.y))
    # Gráfico
    world.add_component(ent, Sprite(surf, _center_offset(surf)))
    # Etiqueta y datos de la bala
    world.add_component(ent, CTagBullet())
    world.add_component(ent, Bullet(owner=None, damage=cfg.get("damage", 1)))
    # Animación si procede
    if len(frames) > 1:
        world.add_component(ent, Animation(frames, framerate=frate))

    return ent


def create_enemy_plane(world: esper.World, cfg: dict) -> int:
    """
    Crea un enemigo con velocidad aleatoria y posible animación.
    """
    sheet = ServiceLocator.images.get(cfg["image"])
    frames = _slice_sheet(sheet, cfg["frame_w"], cfg["frame_h"], cfg.get("frames"))
    start = cfg.get("start_index", 0)

    vmin, vmax = cfg["vel_min"], cfg["vel_max"]
    vx = random.uniform(vmin, vmax) * random.choice([-1, 1])
    vy = random.uniform(vmin, vmax) * random.choice([-1, 1])

    ent = world.create_entity()
    world.add_component(ent, Transform((cfg["spawn"]["x"], cfg["spawn"]["y"])))
    world.add_component(ent, Velocity(vx, vy))

    first = frames[start]
    world.add_component(ent, Sprite(first, _center_offset(first)))

    if len(frames) > 1:
        fr = cfg.get("framerate", 8)
        world.add_component(ent, Animation(frames, fr))

    return ent
