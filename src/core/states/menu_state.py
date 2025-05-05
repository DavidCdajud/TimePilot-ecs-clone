# src/core/states/menu_state.py

import pygame
from pygame import Color
from core.service_locator import ServiceLocator
from core.states.play_state import PlayState

class MenuState:
    def __init__(self, engine):
        self.engine = engine
        self.screen = engine.pantalla
        w, h = self.screen.get_size()

        # ── Carga de logo y fuentes ───────────────────────
        # Usamos images_service en lugar de images
        self.logo = ServiceLocator.images_service.get("assets/img/game_logo.png")
        self.logo_rect = self.logo.get_rect(center=(w/2, h*0.4))

        # Fuente arcade para títulos y texto
        self.font_large  = ServiceLocator.texts_service.get("assets/fnt/PressStart2P.ttf", 2)
        self.font_medium = ServiceLocator.texts_service.get("assets/fnt/PressStart2P.ttf", 10)
        self.font_small  = ServiceLocator.texts_service.get("assets/fnt/PressStart2P.ttf", 6)

        # ── Textos estáticos ─────────────────────────────
        # Top UI
        self.txt_1up      = self.font_small.render("1-UP",       True, Color("red"))
        self.txt_hi_score = self.font_small.render("HI-SCORE 10000", True, Color("red"))
        self.txt_2up      = self.font_small.render("2-UP",       True, Color("red"))
        # “PLAY” encima del logo
        self.txt_play     = self.font_medium.render("PLAY",         True, Color("cyan"))
        # Mensaje central
        self.txt_deposit1 = self.font_medium.render("PLEASE DEPOSIT COIN", True, Color("cyan"))
        self.txt_deposit2 = self.font_medium.render("AND TRY THIS GAME",   True, Color("red"))
        # Crédito abajo
        self.txt_credit   = self.font_small.render("© DevPros 2025", True, Color("white"))

        # Rects con posiciones fijas
        self.r_1up      = self.txt_1up.get_rect(topleft=(20, 10))
        self.r_hi_score = self.txt_hi_score.get_rect(midtop=(w/2, 10))
        self.r_2up      = self.txt_2up.get_rect(topright=(w-20, 10))
        self.r_play     = self.txt_play.get_rect(center=(w/2, h*0.3))
        self.r_dep1     = self.txt_deposit1.get_rect(center=(w/2, h*0.6))
        self.r_dep2     = self.txt_deposit2.get_rect(center=(w/2, h*0.65))
        self.r_credit   = self.txt_credit.get_rect(midbottom=(w/2, h-10))

        # Para parpadeo del deposit
        self.blink_timer = 0.0
        self.show_deposit = True

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                print("[MENU] ENTER pulsado, cambiando a PlayState")
                ps = PlayState(self.engine)
                ps.enter()
                self.engine.state = ps


    def update(self, dt):
        # Parpadeo del mensaje central
        self.blink_timer += dt
        if self.blink_timer >= 0.5:
            self.blink_timer -= 0.5
            self.show_deposit = not self.show_deposit

    def render(self):
        w, h = self.screen.get_size()
        self.screen.fill(Color("black"))

        # ── Top UI ─────────────────────────────────────
        self.screen.blit(self.txt_1up,      self.r_1up)
        self.screen.blit(self.txt_hi_score, self.r_hi_score)
        self.screen.blit(self.txt_2up,      self.r_2up)

        # ── Texto “PLAY” ───────────────────────────────
        self.screen.blit(self.txt_play, self.r_play)

        # ── Logo TIME PILOT ────────────────────────────
        self.screen.blit(self.logo, self.logo_rect)

        # ── Mensaje de inserción de moneda ─────────────
        if self.show_deposit:
            self.screen.blit(self.txt_deposit1, self.r_dep1)
            self.screen.blit(self.txt_deposit2, self.r_dep2)

        # ── Crédito abajo ───────────────────────────────
        self.screen.blit(self.txt_credit, self.r_credit)

        pygame.display.flip()
