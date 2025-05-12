# core/states/pause_state.py
import pygame, esper
from ecs.components.transform import Transform
from ecs.components.tags.c_tag_pause_menu import CTagPauseMenu
from ecs.systems.s_pause_setup  import sistema_pause_setup
from ecs.systems.s_pause_input  import sistema_pause_input
from ecs.systems.s_pause_render import sistema_pause_render
from ecs.systems.s_rendering    import sistema_rendering
from core.service_locator       import ServiceLocator as SL

class PauseState:
    def __init__(self, engine):
        self.engine   = engine
        self.world    = engine.mundo
        self.screen   = engine.pantalla
        self.snapshot : pygame.Surface | None = None

    # --------------------------------------------------
    def enter(self):
        SL.sound_service.pause_bgm()
        SL.sound_service.play_sfx("assets/snd/game_paused.ogg")

        # ── frame congelado ──
        self.snapshot = pygame.Surface(self.screen.get_size()).convert()
        p_tr = self.world.component_for_entity(self.engine.player_ent, Transform)
        sistema_rendering(self.world, self.snapshot, p_tr.pos,
                          self.engine.screen_center)

        # ── entidades del menú ──
        sistema_pause_setup(self.world)

    # --------------------------------------------------
    def exit(self):
        for ent, _ in list(self.world.get_component(CTagPauseMenu)):
            self.world.delete_entity(ent)
        # limpia cadáveres y descarta la imagen congelada
        if hasattr(self.world, "_clear_dead_entities"):
            self.world._clear_dead_entities()
        self.snapshot = None
        SL.sound_service.resume_bgm()

    # --------------------------------------------------
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.engine.pop_state()
                return
        pygame.event.pump()

    # --------------------------------------------------
    def update(self, dt: float):
        sistema_pause_input(self.world, dt, self.engine)

    # --------------------------------------------------
    def render(self):
        if self.snapshot:
            self.screen.blit(self.snapshot, (0, 0))

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        sistema_pause_render(self.world, self.screen)
        pygame.display.flip()
