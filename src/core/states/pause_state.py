# src/core/states/pause_state.py

import pygame, esper
from ecs.components.tags.c_tag_pause_menu import CTagPauseMenu
from ecs.systems.s_pause_setup import sistema_pause_setup
from ecs.systems.s_pause_input import sistema_pause_input
from ecs.systems.s_pause_render import sistema_pause_render

class PauseState:
    def __init__(self, engine):
        self.engine = engine
        self.world  = engine.mundo
        self.screen = engine.pantalla

    def enter(self):
        sistema_pause_setup(self.world)

    def exit(self):
        for ent, _ in list(self.world.get_component(CTagPauseMenu)):
            self.world.delete_entity(ent)

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False

            # Si aprieta ESC, salimos de la pausa
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                # limpiamos menú
                self.exit()

                # import dinámico aquí, para romper la circularidad
                from core.states.play_state import PlayState

                # volvemos a PlayState
                new_state = PlayState(self.engine)
                new_state.enter()
                self.engine.state = new_state
                return

        # consume el resto de eventos para que no queden en cola
        pygame.event.pump()

    def update(self, dt: float):
        sistema_pause_input(self.world, dt, self.engine)

    def render(self):
        # semitransparente overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        sistema_pause_render(self.world, self.screen)
        pygame.display.flip()
