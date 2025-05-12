# src/ecs/components/last_direction.py
import pygame

class LastDirection:
    def __init__(self, direction: pygame.Vector2):
        self.vec = direction
