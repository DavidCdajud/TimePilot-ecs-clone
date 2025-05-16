# core/states/game_over_state.py
import pygame
from pygame import Color
from core.service_locator import ServiceLocator as SL

class GameOverState:
    def __init__(self, engine):
        self.engine  = engine
        self.screen  = engine.pantalla
        f_path       = "assets/fnt/PressStart2P.ttf"
        self.font    = pygame.font.Font(f_path, 16)

        w, h = self.screen.get_size()
        self.txt_game_over = self.font.render("GAME  OVER",  True, Color("red"))
        self.txt_press     = self.font.render("PRESS ENTER", True, Color("white"))

        self.r_game_over = self.txt_game_over.get_rect(center=(w/2, h*0.45))
        self.r_press     = self.txt_press.get_rect(center=(w/2, h*0.60))

        self.blink_t = 0.0
        self.show_prompt = True

    # --------------------------------------------------
    def enter(self):
        SL.sound_service.stop_bgm()
        SL.sound_service.play_sfx("assets/snd/game_over.ogg")

    def exit(self): ...

    # --------------------------------------------------
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False

            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                # ↓↓↓ IMPORTACIÓN TARDÍA ↓↓↓  (evita circular-import)
                from core.states.menu_state import MenuState
                self.engine.pop_state()          # quita GameOver
                self.engine.push_state(MenuState(self.engine))

    # --------------------------------------------------
    def update(self, dt: float):
        self.blink_t += dt
        if self.blink_t >= .5:
            self.blink_t -= .5
            self.show_prompt = not self.show_prompt

    # --------------------------------------------------
    def render(self):
        self.screen.fill(Color("black"))
        self.screen.blit(self.txt_game_over, self.r_game_over)
        if self.show_prompt:
            self.screen.blit(self.txt_press, self.r_press)
        pygame.display.flip()
