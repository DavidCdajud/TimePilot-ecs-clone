# src/ecs/systems/s_score_render.py
import pygame, esper
from ecs.components.score_board import ScoreBoard

def sistema_score_render(world: esper.World, screen: pygame.Surface) -> None:
    font = pygame.font.Font(None, 28)
    for _, sb in world.get_component(ScoreBoard):
        txt = font.render(f"SCORE  {sb.score:,}", True, (255,255,255))
        screen.blit(txt, (8, 8))          # esquina sup-izq
        break    # solo hay un ScoreBoard
