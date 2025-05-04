from dataclasses import dataclass
import pygame

@dataclass
class Sprite:
    sheet_id: str              # clave del ResourceManager
    frame_w: int               # ancho de cada frame
    frame_h: int               # alto de cada frame
