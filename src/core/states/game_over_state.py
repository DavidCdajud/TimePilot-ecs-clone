# ── src/core/states/game_over_state.py ─────────────────────────
import pygame
from pygame import Color

class GameOverState:
    def __init__(self, engine):
        self.engine  = engine
        self.screen  = engine.pantalla
        f_path       = "assets/fnt/PressStart2P.ttf"
        self.font    = pygame.font.Font(f_path, 16)

        w, h = self.screen.get_size()
        self.text   = self.font.render("GAME  OVER",  True, Color("red"))
        self.rect   = self.text.get_rect(center=(w/2, h*0.45))

        self.prompt = self.font.render("PRESS ENTER", True, Color("white"))
        self.rp     = self.prompt.get_rect(center=(w/2, h*0.60))

        self.blink_time  = 0.0
        self.show_prompt = True

    # pila de estados: dejamos enter/exit vacíos
    def enter(self): ...
    def exit(self):  ...

    # ────────────────────────────────────────────────────────────
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False

            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                # ── import-lazy para evitar el ciclo ────────────
                from core.states.menu_state import MenuState
                # volvemos al menú principal
                self.engine.pop_state()            # quita GameOver
                # quitamos también el viejo MenuState (opcional)
                if self.engine.state_stack and isinstance(self.engine.state_stack[-1], MenuState):
                    self.engine.pop_state()
                self.engine.push_state(MenuState(self.engine))

    # ────────────────────────────────────────────────────────────
    def update(self, dt):
        self.blink_time += dt
        if self.blink_time >= 0.5:
            self.blink_time -= 0.5
            self.show_prompt = not self.show_prompt

    def render(self):
        self.screen.fill(Color("black"))
        self.screen.blit(self.text, self.rect)
        if self.show_prompt:
            self.screen.blit(self.prompt, self.rp)
        pygame.display.flip()
