# src/core/game_engine.py

import json
import pathlib
import pygame
import esper
from pygame.color import Color

# ── Componentes y sistemas ──────────────────────────────────────
from ecs.components.transform import Transform
from ecs.systems.s_movement import sistema_movimiento
from ecs.systems.s_rendering import sistema_rendering
from ecs.systems.s_animation import sistema_animacion
from ecs.systems.s_input_player import sistema_input_player
from ecs.components.cloud_spawner import CloudSpawner
from ecs.systems.s_cloud_spawner import sistema_spawner_nubes
from ecs.components.score_board import ScoreBoard

# ── Prefabs ─────────────────────────────────────────────────────
from create.prefabs_creator import (
    create_enemy_plane,
    create_player_plane,
    create_cloud,
)
from ecs.components.c_enemy_spawner import CEnemySpawner
from ecs.systems.s_player_rotation import sistema_player_rotation
from ecs.systems.s_player_shoot import sistema_player_shoot

# ── States ──────────────────────────────────────────────────────
from core.states.menu_state import MenuState


class GameEngine:
    """Bucle principal – TimePilot ECS con pila de estados."""

    def __init__(self) -> None:
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
        self.is_paused = False

        # Mundo y jugador
        self.mundo: esper.World | None = None
        self.player_ent: int | None = None

        # Config de bala
        with open("assets/cfg/bullet.json", encoding="utf-8") as f:
            self.bullet_cfg = json.load(f)

        # Pila de estados
        self.state_stack: list = []

    # ────────────────── Gestión de estados ────────────────────

    def push_state(self, new_state):
        """Empuja un estado y llama a su enter()."""
        self.state_stack.append(new_state)
        new_state.enter()

    def pop_state(self):
        if not self.state_stack:
            return
        old = self.state_stack.pop()
        if hasattr(old, "exit"):
            old.exit()

    # ╭────────────────── Loop principal ───────────────────╮
    def run(self) -> None:
        # Arranca con el menú
        self.push_state(MenuState(self))
        self.activo = True
        while self.activo and self.state_stack:
            dt = self.reloj.tick(self.fps) / 1000.0
            current = self.state_stack[-1]

            current.handle_events()
            current.update(dt)
            current.render()

        # limpieza finalks
        while self.state_stack:
            self.pop_state()
        pygame.quit()
    # ╰──────────────────────────────────────────────────────╯

    # ───────────────── Prefabs iniciales ──────────────────
    def _crear_prefabs(self) -> None:
        """
        Crea los prefabs iniciales:
          1) Jugador
          2) Horizon de nubes
          3) Spawner de nubes
          4) Spawner de enemigos
          5) Enemigo de prueba
          6) ScoreBoard
        """
        # 1) Nave del jugador
        with open("assets/cfg/player.json", encoding="utf-8") as f:
            player_cfg = json.load(f)
        self.player_ent = create_player_plane(self.mundo, player_cfg)

        # 2) Horizon de nubes
        with open("assets/cfg/clouds.json", encoding="utf-8") as f:
            clouds_cfg = json.load(f)
        large_cfg = next(c for c in clouds_cfg if "large" in c["image"])
        fw, fh = large_cfg["frame_w"], large_cfg["frame_h"]
        screen_w, screen_h = self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]
        horizon_y = screen_h - fh // 2
        n_tiles = (screen_w // fw) + 2
        for i in range(n_tiles):
            cfg = large_cfg.copy()
            cfg["spawn"] = {"x": i * fw - fw // 2, "y": horizon_y}
            create_cloud(self.mundo, cfg)

        # 3) Spawner dinámico de nubes
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

        # 4) Spawner de enemigos
        with open("assets/cfg/enemies.json", encoding="utf-8") as f:
            enemies_cfg = json.load(f)
        enemy_spawner_ent = self.mundo.create_entity()
        self.mundo.add_component(
            enemy_spawner_ent,
            CEnemySpawner(configs=enemies_cfg, interval=0.5, screen_width=screen_w)
        )

        # 5) Enemigo de prueba inmediato
        test_cfg = enemies_cfg[0].copy()
        test_cfg["spawn"] = {"x": screen_w * 0.5, "y": -test_cfg.get("frame_h", 16) / 2}
        create_enemy_plane(self.mundo, test_cfg)

        # 6) ScoreBoard
        sb_ent = self.mundo.create_entity()
        self.mundo.add_component(sb_ent, ScoreBoard())

    # ─────────────── Carga de configuración ───────────────
    def _cargar_json_window(self) -> None:
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
