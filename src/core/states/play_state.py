# src/core/states/play_state.py

import json
import pygame
import esper

from ecs.components.transform import Transform
from ecs.components.c_enemy_spawner import CEnemySpawner
from ecs.systems.s_enemy_spawn import sistema_enemy_spawn
from ecs.systems.s_input_player import sistema_input_player
from ecs.systems.s_movement import sistema_movimiento
from ecs.systems.s_player_rotation import sistema_player_rotation
from ecs.systems.s_animation import sistema_animacion
from ecs.systems.s_rendering import sistema_rendering
from ecs.systems.s_enemy_ai import sistema_enemy_ai
from ecs.systems.s_collision import sistema_colisiones_balas_enemigos
from ecs.systems.s_enemy_orientation import sistema_enemy_orientation
from ecs.systems.s_expiration import sistema_expiracion

from core.states.pause_state import PauseState  # <─ importa aquí

class PlayState:
    def __init__(self, engine):
        self.engine = engine
        self.screen = engine.pantalla

    def enter(self):
        """Se llama al iniciar la partida desde el menú."""
        self.engine.mundo = esper.World()
        self.engine._crear_prefabs()
        # … resto idéntico …

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False

            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                # Cambiamos a pausa
                pausa = PauseState(self.engine)
                pausa.enter()
                self.engine.state = pausa
                return

    def update(self, dt: float):
        world = self.engine.mundo
        sistema_enemy_spawn(world, dt)
        sistema_enemy_ai(world, dt)
        sistema_enemy_orientation(world)
        sistema_input_player(world, dt)
        sistema_movimiento(world, dt)
        sistema_player_rotation(world)
        sistema_animacion(world, dt)
        sistema_colisiones_balas_enemigos(world)
        sistema_expiracion(world, dt)

    def render(self):
        world = self.engine.mundo
        player_tr = world.component_for_entity(self.engine.player_ent, Transform)
        camera_offset = player_tr.pos
        center = self.engine.screen_center

        self.screen.fill(self.engine.color_fondo)
        sistema_rendering(world, self.screen, camera_offset, center)
        pygame.display.flip()
