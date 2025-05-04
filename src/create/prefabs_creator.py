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

def _slice_sheet(
    sheet: pygame.Surface,
    frame_w: int,
    frame_h: int,
    num_frames: Optional[int] = None
) -> List[pygame.Surface]:
    """
    Rota por columnas y filas, extrayendo como máximo num_frames
    o (cols * rows) si num_frames es None.
    Imprime un DEBUG con tamaños para ayudarte a ajustar el JSON.
    """
    sw, sh = sheet.get_size()
    print(f"[DEBUG] sheet_size=({sw},{sh}), frame=({frame_w},{frame_h}), num_frames={num_frames}")

    cols = sw // frame_w
    rows = sh // frame_h
    max_frames = cols * rows
    total = min(num_frames or max_frames, max_frames)

    frames: List[pygame.Surface] = []
    for idx in range(total):
        col = idx % cols
        row = idx // cols
        x, y = col * frame_w, row * frame_h

        # Verifica que el rect cabe dentro de la hoja
        if x + frame_w <= sw and y + frame_h <= sh:
            rect = pygame.Rect(x, y, frame_w, frame_h)
            frames.append(sheet.subsurface(rect))
        else:
            print(f"[WARNING] Frame {idx} fuera de límites: rect=({x},{y},{frame_w},{frame_h}), sheet_size=({sw},{sh})")
    return frames


def _center_offset(surf: pygame.Surface) -> Tuple[int, int]:
    return surf.get_width() // 2, surf.get_height() // 2


def create_player_plane(world: esper.World, cfg: dict) -> int:
    """
    cfg debe tener:
      - image: ruta al sheet
      - frame_w, frame_h
      - frames (opcional)
      - start_index (opcional)
      - framerate (opcional)
      - spawn: {x, y}
    """
    sheet = ServiceLocator.images.get(cfg["image"])
    frames = _slice_sheet(
        sheet,
        cfg["frame_w"],
        cfg["frame_h"],
        cfg.get("frames")
    )
    start = cfg.get("start_index", 0)
    fr = cfg.get("framerate", 12)

    ent = world.create_entity()
    world.add_component(ent, Transform((cfg["spawn"]["x"], cfg["spawn"]["y"])))
    world.add_component(ent, Velocity(0.0, 0.0))
    first = frames[start]
    world.add_component(ent, Sprite(first, _center_offset(first)))
    if len(frames) > 1:
        world.add_component(ent, Animation(frames, framerate=fr))
    return ent

def create_cloud(
    world: esper.World,
    cfg: dict
) -> int:
    """
    cfg debe tener:
      - image: ruta al sheet o PNG
      - speed: velocidad vertical
      - spawn: {x, y}
    Opcionalmente (para animar hoja):
      - frame_w, frame_h, frames, framerate
    """
    sheet = ServiceLocator.images.get(cfg["image"])
    fw = cfg.get("frame_w")
    fh = cfg.get("frame_h")
    num = cfg.get("frames")
    frate = cfg.get("framerate", 6)

    # Intenta cortar hoja si frame_w/frame_h están presentes
    if fw and fh:
        frames = _slice_sheet(sheet, fw, fh, num)
        if not frames:
            print(f"⚠️  No se extrajeron frames de {cfg['image']} (fw={fw},fh={fh}). Usando imagen completa.")
            frames = [sheet]
    else:
        frames = [sheet]

    # Selecciona el primer surf para empezar
    surf = frames[0]
    offset = _center_offset(surf)

    ent = world.create_entity()
    world.add_component(ent, Transform((cfg["spawn"]["x"], cfg["spawn"]["y"])))
    world.add_component(ent, Velocity(0.0, cfg["speed"]))
    world.add_component(ent, Sprite(surf, offset))

    # Solo si hay más de un frame, añade animación
    if len(frames) > 1:
        world.add_component(ent, Animation(frames, framerate=frate))

    return ent


def create_bullet(
    world: esper.World,
    cfg: dict,
    start_pos: Tuple[float, float],
    direction: pygame.Vector2
) -> int:
    """
    cfg: { image, speed, spawn_offset: {x,y}, ... }
    """
    sheet = ServiceLocator.images.get(cfg["image"])
    fw = cfg.get("frame_w")
    fh = cfg.get("frame_h")
    if fw and fh:
        frames = _slice_sheet(sheet, fw, fh, cfg.get("frames"))
        surf = frames[0]
    else:
        surf = sheet
        frames = [sheet]

    ent = world.create_entity()
    world.add_component(ent, Transform(start_pos))
    vel = direction.normalize() * cfg["speed"]
    world.add_component(ent, Velocity(vel.x, vel.y))
    world.add_component(ent, Sprite(surf, _center_offset(surf)))
    if len(frames) > 1:
        fr = cfg.get("framerate", 12)
        world.add_component(ent, Animation(frames, fr))
    return ent


def create_enemy_plane(world: esper.World, cfg: dict) -> int:
    """
    Similar a create_player_plane pero añade velocidad aleatoria,
    tags, sonido, etc.
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
