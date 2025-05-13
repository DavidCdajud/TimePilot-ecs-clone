# ── src/core/states/play_state.py ──────────────────────────────
import json
import pygame, esper

from ecs.components.transform import Transform
from ecs.components.c_enemy_spawner import CEnemySpawner
from ecs.components.lives           import Lives

# ── Sistemas ───────────────────────────────────────────────────
from ecs.systems.s_enemy_spawn      import sistema_enemy_spawn
from ecs.systems.s_enemy_ai         import sistema_enemy_ai
from ecs.systems.s_enemy_orientation import sistema_enemy_orientation
from ecs.systems.s_input_player     import sistema_input_player
from ecs.systems.s_movement         import sistema_movimiento
from ecs.systems.s_player_rotation  import sistema_player_rotation
from ecs.systems.s_animation        import sistema_animacion
from ecs.systems.s_rendering        import sistema_rendering
from ecs.systems.s_collision        import sistema_colisiones_balas_enemigos
from ecs.systems.s_collision_player_enemy import sistema_colision_player_enemy
from ecs.systems.s_expiration       import sistema_expiracion
from ecs.systems.s_lives_render     import sistema_lives_render
from ecs.systems.s_score_render     import sistema_score_render
from ecs.systems.s_enemy_bullet_collision import sistema_enemy_bullet_collision

# ── Estados ────────────────────────────────────────────────────
from core.states.pause_state     import PauseState
from core.states.game_over_state import GameOverState
from ecs.systems.s_enemy_shot import sistema_enemy_shoot

class PlayState:
    def __init__(self, engine):
        self.engine = engine
        self.screen = engine.pantalla

    # -----------------------------------------------------------
    def enter(self):
        """Se llama al entrar al gameplay desde el menú."""
        self.engine.mundo = esper.World()
        self.engine._crear_prefabs()

    # -----------------------------------------------------------
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.engine.activo = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.engine.push_state(PauseState(self.engine))
                return

    # -----------------------------------------------------------
    def update(self, dt: float):
        world = self.engine.mundo

        # --- Todos los sistemas de juego ----------------------
        sistema_enemy_spawn(world, dt)
        sistema_enemy_ai(world, dt)
        sistema_enemy_orientation(world)
        sistema_enemy_shoot(world, dt)
        sistema_enemy_bullet_collision(world, self.engine)
        sistema_input_player(world, dt)
        sistema_movimiento(world, dt)

        sistema_colision_player_enemy(world, self.engine)

        sistema_player_rotation(world)
        sistema_animacion(world, dt)
        sistema_colisiones_balas_enemigos(world)
        sistema_expiracion(world, dt)

        # --- ¿Game-Over? -------------------------------------
        if not world.get_component(Lives):  # no queda jugador con vidas
            self.engine.push_state(GameOverState(self.engine))
            return

    # -----------------------------------------------------------
    def render(self):
        world = self.engine.mundo

        # Si el jugador fue eliminado, evitar KeyError
        if not world.entity_exists(self.engine.player_ent):
            return

        try:
            player_tr = world.component_for_entity(self.engine.player_ent, Transform)
        except KeyError:
            return

        camera_offset = player_tr.pos
        center = self.engine.screen_center

        self.screen.fill(self.engine.color_fondo)

        # mundo + sprites
        sistema_rendering(world, self.screen, camera_offset, center)

        # marcador de puntos
        sistema_score_render(world, self.screen)

        # iconos de vida
        sistema_lives_render(world, self.screen)

        pygame.display.flip()

    # -----------------------------------------------------------
    def exit(self):
        """Hook por si necesitas limpiar algo al salir del gameplay."""
        pass
