# src/create/prefabs_creator.py
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
from ecs.components.bullet import Bullet
from ecs.components.enemy_ai import EnemyAI
from ecs.components.tags.c_tag_bullet import CTagBullet
from ecs.components.tags.c_tag_enemy import CTagEnemy
from ecs.components.tags.c_tag_player import CTagPlayer

# … resto de funciones …

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
    # después
    sheet = ServiceLocator.images_service.get(cfg["image"])
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
    
    # Marca esta entidad como “jugador”
    world.add_component(ent, CTagPlayer())


    # Guarda todos los frames para el sistema de orientación
    world.add_component(ent, PlayerOrientation(frames, neutral_index=neutral_idx))

    return ent


def create_cloud(world: esper.World, cfg: dict) -> int:
    """
    Crea una nube. Si lleva sheet de animación, usa Animation.
    Añade CTagCloud para que el sistema de spawn la reconozca.
    """
    sheet = ServiceLocator.images_service.get(cfg["image"])
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
    sheet = ServiceLocator.images_service.get(cfg["image"])
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

    print(f"[DEBUG create_enemy] cfg spawn=({cfg.get('spawn')})")
    """
    Crea un enemigo con:
      - Transform, Velocity
      - Sprite (+ Animation)
      - CTagEnemy, EnemyAI (opcional Health)
    cfg viene de enemies.json y debe incluir:
      - image, frame_w, frame_h, vel_min, vel_max
      - spawn: {x, y} (inyectado por el spawner)
    """
    # Carga de la hoja de sprites
    sheet = ServiceLocator.images_service.get(cfg["image"])

    # 1) Extraer frames o fallback
    fw = cfg.get("frame_w", sheet.get_width())
    fh = cfg.get("frame_h", sheet.get_height())
    frames = _slice_sheet(sheet, fw, fh, cfg.get("frames"))
    if not frames:
        frames = [sheet]

    # 2) Validar índice de inicio
    start = cfg.get("start_index", 0)
    if start < 0 or start >= len(frames):
        start = 0

    # 3) Velocidad aleatoria
    vmin, vmax = cfg.get("vel_min", 10), cfg.get("vel_max", 20)
    vx = random.uniform(vmin, vmax) * random.choice([-1, 1])
    vy = random.uniform(vmin, vmax) * random.choice([-1, 1])

    # 4) Leer posición de spawn
    spawn = cfg.get("spawn", {"x": 0, "y": 0})
    x0, y0 = spawn["x"], spawn["y"]

    # 5) Crear entidad y componentes básicos
    ent = world.create_entity()
    world.add_component(ent, Transform((x0, y0)))
    world.add_component(ent, Velocity(vx, vy))

    # 6) Sprite y animación
    frame = frames[start]
    offset = _center_offset(frame)
    world.add_component(ent, Sprite(frame, offset, layer=2))
    if len(frames) > 1:
        fr_rate = cfg.get("framerate", 8)
        world.add_component(ent, Animation(frames, fr_rate))

    # 7) Lógica de enemigo
    world.add_component(ent, CTagEnemy())
    world.add_component(ent, EnemyAI(speed=cfg.get("ai_speed", 50.0)))
    components = [type(comp).__name__ for comp in world.components_for_entity(ent)]
    print(f"[DEBUG create_enemy] entidad={ent} components={components}")
    # (Opcional) Salud
    # from src.ecs.components.health import Health
    # world.add_component(ent, Health(cfg.get("health", 1)))

    return ent