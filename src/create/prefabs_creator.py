# src/create/prefabs_creator.py
import random
from typing import List, Optional, Tuple
import pygame
import esper
from typing import Optional


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
from ecs.components.lives import Lives
from ecs.components.enemy_ai import EnemyAI
from core.service_locator import ServiceLocator as SL
from ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from ecs.components.enemy_shooter import EnemyShooter
from ecs.components.boss_shooter import BossShooter
from ecs.components.tags.c_tag_boss import CTagBoss

_POPUP_FONT_PATH = "assets/fnt/PressStart2P.ttf"
_POPUP_FONT_SIZE = 6
_popup_font: Optional[pygame.font.Font] = None

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
    sheet  = ServiceLocator.images_service.get(cfg["image"])
    frames = _slice_sheet(sheet, cfg["frame_w"], cfg["frame_h"], cfg.get("frames"))
    neutral_idx = cfg.get("start_index", 0)

    ent = world.create_entity()
    world.add_component(ent, Transform((cfg["spawn"]["x"], cfg["spawn"]["y"])))
    world.add_component(ent, Velocity(0.0, 0.0))
    world.add_component(ent, PlayerInput(cfg["speed"]))

    surf   = frames[neutral_idx]
    offset = _center_offset(surf)
    world.add_component(ent, Sprite(surf, offset, layer=3))

    world.add_component(ent, CTagPlayer())
    world.add_component(ent, PlayerOrientation(frames, neutral_index=neutral_idx))
    world.add_component(ent, Lives(cfg.get("lives", 3)))   # ← vidas

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
    world.add_component(ent, Duration(1.0))
    if len(frames) > 1:
        world.add_component(ent, Animation(frames, framerate=frate))
    return ent

def create_enemy_plane(world: esper.World, cfg: dict) -> int:
    sheet = SL.images_service.get(cfg["image"])
    fw, fh = cfg.get("frame_w"), cfg.get("frame_h")
    base   = _slice_sheet(sheet, fw, fh, cfg.get("frames"))
    start  = cfg.get("start_index", 0) % len(base)

    vx = random.uniform(cfg.get("vel_min", 10), cfg.get("vel_max", 20)) \
         * random.choice([-1, 1])
    vy = random.uniform(cfg.get("vel_min", 10), cfg.get("vel_max", 20)) \
         * random.choice([-1, 1])

    ent = world.create_entity()
    sx, sy = cfg.get("spawn", {"x": 0, "y": 0}).values()
    world.add_component(ent, Transform((sx, sy)))
    world.add_component(ent, Velocity(vx, vy))

    mode = cfg.get("mode", "orientation")
    if mode == "animation":
        world.add_component(ent,
            Sprite(base[start], _center_offset(base[start]), layer=2)
        )
        if len(base) > 1:
            world.add_component(ent, Animation(base, cfg.get("framerate", 8)))
    else:
        nori = cfg.get("orientation_frames", len(base))
        ori  = _slice_sheet(sheet, fw, fh, nori)
        neutral = start % len(ori)
        world.add_component(ent,
            Sprite(ori[neutral], _center_offset(ori[neutral]), layer=2)
        )
        world.add_component(ent, EnemyOrientation(ori, neutral_index=neutral))

    world.add_component(ent, CTagEnemy())
    world.add_component(ent, Health(cfg.get("health", 1)))
    world.add_component(ent, EnemyAI(speed=cfg.get("ai_speed", 50.0)))

    shoot_cfg = cfg.get("shooter", {})
    world.add_component(ent,
        EnemyShooter(cooldown=shoot_cfg.get("cooldown", 1.2),
                     fire_prob=shoot_cfg.get("fire_prob", .30))
    )
    return ent

def create_explosion(world: esper.World, cfg: dict, pos: tuple[float, float]) -> int:
    SL.sound_service.play_sfx("assets/snd/player_die.ogg")
    sheet  = ServiceLocator.images_service.get(cfg["image"])
    fw, fh = cfg["frame_w"], cfg["frame_h"]
    frames = _slice_sheet(sheet, fw, fh, cfg["frames"]) or [sheet]
    fr     = cfg["framerate"]

    ent = world.create_entity()
    world.add_component(ent, Transform(pos))

    offset = (frames[0].get_width() // 2, frames[0].get_height() // 2)
    world.add_component(ent, Sprite(frames[0], offset))
    world.add_component(ent, Animation(frames, fr, loop=False))   # ← NO se repite

    # la animación dura len(frames)/fr segundos
    world.add_component(ent, Duration(len(frames) / fr))
    return ent

def _get_popup_font() -> pygame.font.Font:
    global _popup_font
    if _popup_font is None:
        _popup_font = pygame.font.Font(_POPUP_FONT_PATH, _POPUP_FONT_SIZE)
    return _popup_font

def create_score_popup(world: esper.World, value: int, pos: tuple[float, float]) -> int:
    font = _get_popup_font()                                       # ← usa la fuente deseada
    surf = font.render(str(value), True, (255, 255, 255))
    ent  = world.create_entity()

    world.add_component(ent, Transform(pos))
    world.add_component(ent, Sprite(
        surf,
        (surf.get_width() // 2, surf.get_height() // 2),
        layer=4
    ))
    world.add_component(ent, Velocity(0, -40))
    world.add_component(ent, Duration(1.0))
    world.add_component(ent, ScorePopup(value))

    return ent


# ------------------------------------------------------------------
def create_boss_plane(world: esper.World, cfg: dict, spawn_pos: tuple[float, float]) -> int:
    """
    Crea el jefe final:
      • Sprite/animación a partir de un spritesheet
      • Más vida que un enemigo normal
      • Opcionalmente con EnemyAI para que persiga
    """
    # 1) Carga sheet y trocea
    sheet = ServiceLocator.images_service.get(cfg["image"])
    fw, fh   = cfg["frame_w"], cfg["frame_h"]
    frames   = _slice_sheet(sheet, fw, fh, cfg.get("frames")) or [sheet]
    fr_rate  = cfg.get("framerate", 6)

    # 2) Entidad básica
    ent = world.create_entity()
    world.add_component(ent, Transform(spawn_pos))
    world.add_component(ent, Velocity(0, 0))          # de entrada quieto

    # 3) Sprite (primer frame) y animación
    offset = (frames[0].get_width()//2, frames[0].get_height()//2)
    world.add_component(ent, Sprite(frames[0], offset, layer=2))
    if len(frames) > 1:
        world.add_component(ent, Animation(frames, fr_rate))

    # 4) Lógica de juego
    world.add_component(ent, CTagEnemy())
    world.add_component(ent, CTagBoss())        
    world.add_component(ent, Health(cfg.get("health", 20)))
    # si quieres que persiga, añade EnemyAI

    if cfg.get("ai_speed"):                            # opcional
        world.add_component(ent, EnemyAI(speed=cfg["ai_speed"]))



    cd   = cfg.get("shoot_cooldown", 1.0)   # 1 s por defecto
    p    = cfg.get("shoot_prob",    0.40)   # 40 %
    world.add_component(ent, BossShooter(cooldown=cd, fire_prob=p))
    return ent
# ------------------------------------------------------------------

# ── src/create/prefabs_creator.py  (añade al final del archivo)


def create_enemy_bullet(world, cfg, start_pos, direction):
    ent = create_bullet(world, cfg, start_pos, direction)
    world.remove_component(ent, CTagBullet)
    world.add_component(ent, CTagEnemyBullet())
    # sonido SÓLO cuando se crea la bala
    SL.sound_service.play_sfx("assets/snd/enemy_shoot.wav", volume=.7)
    return ent

