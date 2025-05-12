# src/core/game_engine.py
import json
import pathlib
import pygame
import esper
from pygame.color import Color
from typing import Optional

# ── Componentes y sistemas ──────────────────────────────────────
from ecs.components.transform import Transform
from ecs.systems.s_movement import sistema_movimiento
from ecs.systems.s_rendering import sistema_rendering
from ecs.systems.s_animation import sistema_animacion
from ecs.systems.s_input_player import sistema_input_player
from ecs.systems.s_player_rotation import sistema_player_rotation
from ecs.systems.s_player_shoot import sistema_player_shoot
from ecs.components.cloud_spawner import CloudSpawner
from ecs.systems.s_cloud_spawner import sistema_spawner_nubes

# ── Prefabs ─────────────────────────────────────────────────────
from create.prefabs_creator import (
    create_enemy_plane,
    create_player_plane,
    create_cloud,
)

from ecs.components.c_enemy_spawner import CEnemySpawner
from ecs.components.score_board import ScoreBoard

# ── Estados ─────────────────────────────────────────────────────
from core.states.menu_state import MenuState
from core.states.play_state import PlayState
from core.states.pause_state import PauseState


class GameEngine:
    """Bucle principal – TimePilot ECS."""

    def __init__(self) -> None:
        # Cargar configuración de ventana
        self._cargar_json_window()
        pygame.init()

        # Ventana
        w = self.window_cfg["size"]["w"]
        h = self.window_cfg["size"]["h"]
        title = self.window_cfg.get("title", "SPACE AVIATOR")
        pygame.display.set_caption(title)
        self.pantalla = pygame.display.set_mode((w, h))
        self.screen_center = (w // 2, h // 2)

        # Fondo
        bg = self.window_cfg["bg_color"]
        self.color_fondo = Color(bg["r"], bg["g"], bg["b"])

        # FPS
        self.fps = self.window_cfg.get("framerate", 60)
        self.reloj = pygame.time.Clock()

        # Flags
        self.activo = False

        # Mundo ECS y jugador
        self.mundo: Optional[esper.World] = None
        self.player_ent: Optional[int] = None

        # Carga configuración de bala
        with open("assets/cfg/bullet.json", encoding="utf-8") as f:
            self.bullet_cfg = json.load(f)

        # Iniciar en el menú principal
        self.state = MenuState(self)

    def run(self) -> None:
        """Bucle principal: delega al estado actual."""
        self.activo = True
        while self.activo:
            dt = self.reloj.tick(self.fps) / 1000.0

            # Delegamos a los métodos del estado
            self.state.handle_events()
            self.state.update(dt)
            self.state.render()

        # Al salir, limpiar mundo y Pygame
        if self.mundo:
            self.mundo.clear_database()
        pygame.quit()

    def _crear_prefabs(self) -> None:
        """Prefabs iniciales: jugador, nubes, spawners, enemigo de prueba y marcador."""
        # -- Jugador --
        with open("assets/cfg/player.json", encoding="utf-8") as f:
            player_cfg = json.load(f)
        self.player_ent = create_player_plane(self.mundo, player_cfg)

        # -- Horizon de nubes --
        with open("assets/cfg/clouds.json", encoding="utf-8") as f:
            clouds_cfg = json.load(f)
        large_cfg = next(c for c in clouds_cfg if "large" in c["image"])
        fw, fh = large_cfg["frame_w"], large_cfg["frame_h"]
        screen_w = self.window_cfg["size"]["w"]
        screen_h = self.window_cfg["size"]["h"]
        horizon_y = screen_h - fh // 2
        n_tiles = (screen_w // fw) + 2
        for i in range(n_tiles):
            cfg = large_cfg.copy()
            cfg["spawn"] = {"x": i * fw - fw // 2, "y": horizon_y}
            create_cloud(self.mundo, cfg)

        # -- Spawner dinámico de nubes --
        spawner_ent = self.mundo.create_entity()
        self.mundo.add_component(
            spawner_ent,
            CloudSpawner(
                configs=clouds_cfg,
                screen_width=screen_w,
                screen_height=screen_h,
                min_y=-fh,
                max_y=screen_h * 0.5,
                move_threshold=50.0
            )
        )

        # -- Spawner de enemigos --
        with open("assets/cfg/enemies.json", encoding="utf-8") as f:
            enemies_cfg = json.load(f)
        enemy_spawner_ent = self.mundo.create_entity()
        self.mundo.add_component(
            enemy_spawner_ent,
            CEnemySpawner(
                configs=enemies_cfg,
                interval=0.5,
                screen_width=screen_w
            )
        )

        # -- Enemigo de prueba --
        test_cfg = enemies_cfg[0].copy()
        test_cfg["spawn"] = {"x": screen_w * 0.5,
                             "y": -test_cfg.get("frame_h", 16) / 2}
        create_enemy_plane(self.mundo, test_cfg)

        # -- Marcador de puntuación --
        score_ent = self.mundo.create_entity()
        self.mundo.add_component(score_ent, ScoreBoard())

    def _cargar_json_window(self) -> None:
        """Carga window.json o usa valores por defecto."""
        cfg_path = pathlib.Path("assets/cfg/window.json")
        try:
            with cfg_path.open(encoding="utf-8") as f:
                self.window_cfg = json.load(f)
        except FileNotFoundError:
            self.window_cfg = {
                "title": "SPACE AVIATOR",
                "size": {"w": 448, "h": 512},
                "bg_color": {"r": 0, "g": 0, "b": 0},
                "framerate": 60,
            }
            print("⚠️ window.json no encontrado; usando valores por defecto.")
