# src/core/states/pause_state.py
import pygame, esper

from ecs.components.tags.c_tag_pause_menu import CTagPauseMenu
from ecs.systems.s_pause_setup  import sistema_pause_setup
from ecs.systems.s_pause_input  import sistema_pause_input
from ecs.systems.s_pause_render import sistema_pause_render

# ⬇️  Faltaban estos dos imports
from ecs.components.transform   import Transform
from ecs.systems.s_rendering    import sistema_rendering

class PauseState:
    def __init__(self, engine):
        self.engine = engine
        self.world  = engine.mundo
        self.screen = engine.pantalla

    # ---------- ciclo de vida ----------
    def enter(self):
        sistema_pause_setup(self.world)

    def exit(self):
        for ent, _ in list(self.world.get_component(CTagPauseMenu)):
            self.world.delete_entity(ent)

    # ---------- eventos ----------
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.engine.pop_state()      # salir de la pausa
                return
        pygame.event.pump()

    # ---------- lógica ----------
    def update(self, dt: float):
        sistema_pause_input(self.world, dt, self.engine)

    # ---------- dibujo ----------
    def render(self):
        # 1) frame “congelado” del juego
        player_tr = self.world.component_for_entity(
            self.engine.player_ent, Transform
        )
        camera_offset = player_tr.pos
        sistema_rendering(
            self.world,
            self.screen,
            camera_offset,
            self.engine.screen_center
        )

        # 2) overlay semitransparente
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # 3) menú de pausa
        sistema_pause_render(self.world, self.screen)

        pygame.display.flip()
