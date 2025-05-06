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

class PlayState:
    def __init__(self, engine):
        self.engine = engine
        self.screen = engine.pantalla

    def enter(self):
        """Se llama al iniciar la partida desde el menú."""
        
        # 1) Crear y asignar el mundo ECS
        self.engine.mundo = esper.World()

        # 2) Instanciar prefabs básicos (jugador, nubes, spawner de nubes…)
        self.engine._crear_prefabs()

        # 3) Crear spawner de enemigos
        with open("assets/cfg/enemies.json", encoding="utf-8") as f:
            enemies_cfg = json.load(f)

        enemy_spawner_ent = self.engine.mundo.create_entity()
        self.engine.mundo.add_component(
            enemy_spawner_ent,
            CEnemySpawner(
                configs=enemies_cfg,
                interval=1.0,
                screen_width=self.engine.window_cfg["size"]["w"]
            )
        )

        # Debug: comprobar registro
        cnt = len(list(self.engine.mundo.get_component(CEnemySpawner)))
        print(f"[PLAY.enter] Spawners de enemigos en world: {cnt}")

    def handle_events(self):
        """Procesa eventos de Pygame."""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False
            # Puedes añadir pausa, etc.

    def update(self, dt: float):
        world = self.engine.mundo

        # 1) Spawn de enemigos
        sistema_enemy_spawn(world, dt)

        # 2) IA de enemigos → actualiza velocities para perseguir
        sistema_enemy_ai(world, dt)

        # 3) Orientación de enemigos → elige sprite según vx,vy
        sistema_enemy_orientation(world)

        # 4) Input del jugador → Velocity + disparo
        sistema_input_player(world, dt)

        # 5) Movimiento global de todas las entidades
        sistema_movimiento(world, dt)

        # 6) Rotación de la nave del jugador
        sistema_player_rotation(world)

        # 7) Animaciones (nubes, explosiones, etc.)
        sistema_animacion(world, dt)

        # 8) Colisiones (balas-enemigos, etc.)
        sistema_colisiones_balas_enemigos(world)

        # 9) Expiración de entidades (balas, explosiones, etc.)
        sistema_expiracion(world, dt)



    def render(self):
        """Dibuja el frame con cámara centrada en el jugador."""
        world = self.engine.mundo
        player_tr = world.component_for_entity(self.engine.player_ent, Transform)
        camera_offset = player_tr.pos
        center = self.engine.screen_center

        self.screen.fill(self.engine.color_fondo)
        sistema_rendering(world, self.screen, camera_offset, center)
        pygame.display.flip()
