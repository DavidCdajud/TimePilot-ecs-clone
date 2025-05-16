# ── src/core/states/win_state.py ───────────────────────────────
import pygame
from pygame import Color
from core.service_locator import ServiceLocator as SL

class WinState:
    def __init__(self, engine):
        self.engine  = engine
        self.screen  = engine.pantalla
        w, h         = self.screen.get_size()

        f_path = "assets/fnt/PressStart2P.ttf"
        self.font_big   = pygame.font.Font(f_path, 16)
        self.font_small = pygame.font.Font(f_path, 10)

        self.txt_title  = self.font_big.render("CONGRATS!", True, Color("cyan"))
        self.r_title    = self.txt_title.get_rect(center=(w/2, h*0.45))

        self.txt_press  = self.font_small.render("PRESS ENTER", True, Color("white"))
        self.r_press    = self.txt_press.get_rect(center=(w/2, h*0.65))

        self.blink      = 0.0
        self.show_press = True

    # ---------------------------------------------------
    def enter(self):
        SL.sound_service.stop_bgm()
        SL.sound_service.play_sfx("assets/snd/victory.ogg")

    def exit(self):
        pass

    # ---------------------------------------------------
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False

            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                # Import diferido para evitar dependencias circulares
                from core.states.menu_state import MenuState

                # vaciamos la pila de estados y volvemos al menú
                while self.engine.state_stack:
                    self.engine.pop_state()
                self.engine.push_state(MenuState(self.engine))

    # ---------------------------------------------------
    def update(self, dt: float):
        self.blink += dt
        if self.blink >= 0.5:
            self.blink -= 0.5
            self.show_press = not self.show_press

    # ---------------------------------------------------
    def render(self):
        self.screen.fill(Color("black"))
        self.screen.blit(self.txt_title, self.r_title)
        if self.show_press:
            self.screen.blit(self.txt_press, self.r_press)
        pygame.display.flip()
