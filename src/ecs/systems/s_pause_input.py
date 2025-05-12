# src/ecs/systems/s_pause_input.py
import pygame
import esper
from ecs.components.tags.c_tag_pause_menu import CTagPauseMenu

def sistema_pause_input(world: esper.World, dt: float, engine) -> None:
    """
    Procesa únicamente la tecla P (o Esc) para salir del menú de pausa.
    No importamos PauseState aquí.
    """
    for ev in pygame.event.get():
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_p, pygame.K_ESCAPE):
                # Salimos de pausa: llamamos directamente a engine para restaurar PlayState
                from core.states.play_state import PlayState
                engine.state.exit()              # limpiar menú
                engine.state = PlayState(engine)
                engine.state.enter()
        elif ev.type == pygame.QUIT:
            engine.activo = False
