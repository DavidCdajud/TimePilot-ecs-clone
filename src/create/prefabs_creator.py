# src/create/prefabs_creator.py
import random
from typing import List, Optional, Tuple
import pygame
import esper


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
from ecs.components.orientation import Orientation
from ecs.components.enemy_orientation import EnemyOrientation
from ecs.components.health import Health
from ecs.components.duration import Duration
from ecs.components.score_popup import ScorePopup


# … resto de funciones …


def _slice_sheet(sheet: pygame.Surface, frame_w: int, frame_h: int,
                 num_frames: Optional[int] = None) -> List[pygame.Surface]:
    sw, sh = sheet.get_size()
    cols, rows = sw // frame_w, sh // frame_h
    max_frames = cols * rows
    total = min(num_frames or max_frames, max_frames)
    frames = []
    for idx in range(total):
        col, row = idx % cols, idx // cols
        rect = pygame.Rect(col*frame_w, row*frame_h, frame_w, frame_h)
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
    world.add_component(ent, Duration(0.2))

    if len(frames) > 1:
        world.add_component(ent, Animation(frames, framerate=frate))
    return ent

def create_enemy_plane(world: esper.World, cfg: dict) -> int:
    """
    Modo 'animation': ciclo normal de sprites.
    Modo 'orientation': rota sprite según dirección.
    cfg también admite 'orientation_frames'.
    """
    # 1) Carga sheet y frames base
    sheet = ServiceLocator.images_service.get(cfg["image"])
    fw = cfg.get("frame_w", sheet.get_width())
    fh = cfg.get("frame_h", sheet.get_height())
    base_frames = _slice_sheet(sheet, fw, fh, cfg.get("frames")) or [sheet]
    start = cfg.get("start_index", 0) % len(base_frames)

    # 2) Velocidad
    vmin, vmax = cfg.get("vel_min", 10), cfg.get("vel_max", 20)
    vx = random.uniform(vmin, vmax) * random.choice([-1, 1])
    vy = random.uniform(vmin, vmax) * random.choice([-1, 1])

    # 3) Spawn
    spawn = cfg.get("spawn", {"x":0,"y":0})
    sx, sy = spawn["x"], spawn["y"]

    # 4) Entidad
    ent = world.create_entity()
    world.add_component(ent, Transform((sx, sy)))
    world.add_component(ent, Velocity(vx, vy))

    # 5) Offset
    surface = base_frames[start]
    offset = (surface.get_width()//2, surface.get_height()//2)

    # 6) Sprite/animación u orientación
    mode = cfg.get("mode", "orientation")
    if mode == "animation":
        world.add_component(ent, Sprite(surface, offset, layer=2))
        if len(base_frames) > 1:
            world.add_component(ent, Animation(base_frames, cfg.get("framerate", 8)))
    else:
        nori = cfg.get("orientation_frames", len(base_frames))
        ori_frames = _slice_sheet(sheet, fw, fh, nori) or [surface]
        neutral = start % len(ori_frames)
        world.add_component(ent, Sprite(ori_frames[neutral], offset, layer=2))
        world.add_component(ent, EnemyOrientation(ori_frames, neutral_index=neutral))

    # 7) Lógica de juego
    world.add_component(ent, CTagEnemy())
    world.add_component(ent, EnemyAI(speed=cfg.get("ai_speed", 50.0)))
    world.add_component(ent, Health(cfg.get("health", 1)))

    # comps = [type(c).__name__ for c in world.components_for_entity(ent)]
    # print(f"[DEBUG create_enemy_plane] ent={ent} → {comps}")
    
    return ent

def create_explosion(world: esper.World, cfg: dict, pos: tuple[float, float]) -> int:
    sheet = ServiceLocator.images_service.get(cfg["image"])
    fw, fh   = cfg["frame_w"], cfg["frame_h"]
    num      = cfg["frames"]
    fr_rate  = cfg["framerate"]
    frames   = _slice_sheet(sheet, fw, fh, num) or [sheet]

    ent = world.create_entity()

    world.add_component(ent, Transform((pos[0], pos[1])))

    offset = (frames[0].get_width()//2, frames[0].get_height()//2)
    world.add_component(ent, Sprite(frames[0], offset))
    world.add_component(ent, Animation(frames, fr_rate))

    total_time = 1.0
    world.add_component(ent, Duration(total_time))
    return ent

def create_score_popup(world: esper.World, value: int, pos: tuple[float, float]) -> int:
    font = pygame.font.Font(None, 24)
    surf = font.render(str(value), True, (255, 255, 0))
    ent = world.create_entity()
    world.add_component(ent, Transform(pos))
    world.add_component(ent, Sprite(surf, (surf.get_width()//2, surf.get_height()//2), layer=4))
    world.add_component(ent, Velocity(0, -40))
    world.add_component(ent, Duration(1.0))
    world.add_component(ent, ScorePopup(value))
    return ent