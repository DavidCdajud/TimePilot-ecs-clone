# ───────── src/core/states/pause_state.py (versión final) ─────────
import pygame, esper
from ecs.components.transform      import Transform
from ecs.components.tags.c_tag_pause_menu import CTagPauseMenu
from ecs.systems.s_pause_setup     import sistema_pause_setup
from ecs.systems.s_pause_input     import sistema_pause_input
from ecs.systems.s_pause_render    import sistema_pause_render
from ecs.systems.s_rendering       import sistema_rendering


class PauseState:
    def __init__(self, engine):
        self.engine   = engine
        self.world    = engine.mundo
        self.screen   = engine.pantalla
        self.snapshot : pygame.Surface | None = None   # frame congelado

    # ----------------------------------------------------
    def enter(self) -> None:
        """Se invoca al apilar el estado de pausa."""
        # 1) Fotografiamos el juego **antes** de crear el menú
        self.snapshot = pygame.Surface(self.screen.get_size()).convert()
        player_tr = self.world.component_for_entity(self.engine.player_ent,
                                                    Transform)
        sistema_rendering(
            self.world,              # world del juego
            self.snapshot,           # render en la surface
            player_tr.pos,
            self.engine.screen_center
        )

        # 2) Ahora sí, creamos las entidades del menú
        sistema_pause_setup(self.world)

    # ----------------------------------------------------
    def exit(self) -> None:
        """Se invoca al desapilar la pausa."""
        # borra solo las entidades del menú
        for ent, _ in list(self.world.get_component(CTagPauseMenu)):
            self.world.delete_entity(ent)

        # limpia cadáveres y descarta la imagen congelada
        if hasattr(self.world, "_clear_dead_entities"):
            self.world._clear_dead_entities()
        self.snapshot = None

    # ----------------------------------------------------
    def handle_events(self) -> None:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.engine.pop_state()          # reanudar
                return
        pygame.event.pump()

    # ----------------------------------------------------
    def update(self, dt: float) -> None:
        sistema_pause_input(self.world, dt, self.engine)

    # ----------------------------------------------------
    def render(self) -> None:
        # 1) Dibujamos el frame congelado
        if self.snapshot:
            self.screen.blit(self.snapshot, (0, 0))

        # 2) Overlay semitransparente
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # 3) Menú de pausa (solo una vez)
        sistema_pause_render(self.world, self.screen)
        pygame.display.flip()
