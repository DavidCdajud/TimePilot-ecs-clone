# src/core/game_engine.py  (o donde lo tengas)
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
    """Bucle principal – TimePilot ECS."""

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
        self.delta = 0.0

        # Flags
        self.activo = False
        self.is_paused = False

        # Instancias
        self.mundo: esper.World | None = None
        self.player_ent: int | None = None
        
        #Bullet
        with open("assets/cfg/bullet.json", encoding="utf-8") as f:
            self.bullet_cfg = json.load(f)

        #States
        self.state = MenuState(self)
    # ╭────────────────── Loop principal ───────────────────╮
    def run(self) -> None:
        self.activo = True
        while self.activo:
            # recálculo de delta
            dt = self.reloj.tick(self.fps) / 1000.0

            # +ADDED: delegar eventos al estado
            self.state.handle_events()                         # +ADDED
            self.state.update(dt)                               # +ADDED
            self.state.render()                                 # +ADDED
            # +ADDED─────────────────────────────────────────────────

        # limpieza final
        if self.mundo:
            self.mundo.clear_database()
        pygame.quit()
    # ╰──────────────────────────────────────────────────────╯

    # ───────────────── Prefabs iniciales ──────────────────
    def _crear_prefabs(self) -> None:
        """
        Crea los prefabs iniciales:
        1) Jugador
        2) Horizon de nubes (fila continua abajo)
        3) Spawner dinámico de nubes (arriba, aleatorias)
        4) Spawner de enemigos (con intervalo reducido para pruebas)
        5) Enemigo de prueba inmediato
        """
        # ───── 1) Nave del jugador ─────────────────────────────────
        with open("assets/cfg/player.json", encoding="utf-8") as f:
            player_cfg = json.load(f)
        self.player_ent = create_player_plane(self.mundo, player_cfg)

        # ───── 2) Horizon de nubes ────────────────────────────────
        with open("assets/cfg/clouds.json", encoding="utf-8") as f:
            clouds_cfg = json.load(f)

        large_cfg = next(c for c in clouds_cfg if "large" in c["image"])
        fw = large_cfg["frame_w"]
        fh = large_cfg["frame_h"]
        screen_w = self.window_cfg["size"]["w"]
        screen_h = self.window_cfg["size"]["h"]
        horizon_y = screen_h - fh // 2

        n_tiles = (screen_w // fw) + 2
        for i in range(n_tiles):
            spawn_cfg = large_cfg.copy()
            spawn_cfg["spawn"] = {
                "x": i * fw - fw // 2,
                "y": horizon_y
            }
            create_cloud(self.mundo, spawn_cfg)

        # ───── 3) Spawner dinámico de nubes ────────────────────────
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

        # ───── 4) Spawner de enemigos (intervalo bajo para testing) ──
        with open("assets/cfg/enemies.json", encoding="utf-8") as f:
            enemies_cfg = json.load(f)

        enemy_spawner_ent = self.mundo.create_entity()
        self.mundo.add_component(
            enemy_spawner_ent,
            CEnemySpawner(
                configs=enemies_cfg,
                interval=0.5,                             # intervalo corto para pruebas
                screen_width=screen_w
            )
        )

        # ───── 5) Enemigo de prueba inmediato ───────────────────────
        # Clona el primer tipo de enemigo y fuerza spawn al inicio.
        test_cfg = enemies_cfg[0].copy()
        test_cfg["spawn"] = {"x": screen_w * 0.5, "y": -test_cfg.get("frame_h", 16) / 2}
        create_enemy_plane(self.mundo, test_cfg)
        
    # ────────────────────── Ciclo frame ───────────────────
    def _calcular_tiempo(self) -> None:
        self.reloj.tick(self.fps)
        self.delta = self.reloj.get_time() / 1000.0

    def _procesar_eventos(self) -> None:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.activo = False
            # aquí pondremos sistemas de input más adelante

    def _actualizar(self) -> None:
        if self.is_paused:
            return

        # Cámara y centro de la pantalla
        tr = self.mundo.component_for_entity(self.player_ent, Transform)
        camera_pos = (tr.pos[0], tr.pos[1])

        # 0) Disparo
        sistema_player_shoot(self.mundo, self.bullet_cfg, camera_pos, self.screen_center)
        
        # Enemigos
        sistema_input_player(self.mundo, self.delta)

        # 1) Input → Velocity
        sistema_input_player(self.mundo, self.delta)

        # 2) Movimiento
        sistema_movimiento(self.mundo, self.delta)

        # 3) Rotación de la nave
        sistema_player_rotation(self.mundo)

        # 4) Animación de nubes / otras
        sistema_animacion(self.mundo, self.delta)




    def _dibujar(self) -> None:
        # calcula cámara: sigue la posición world del jugador
        player_tr = self.mundo.component_for_entity(self.player_ent, Transform)
        camera_offset = player_tr.pos

        self.pantalla.fill(self.color_fondo)
        # pasa offset y centro a la función de render
        sistema_rendering(self.mundo, self.pantalla, camera_offset, self.screen_center)
        pygame.display.flip()


    def _limpiar(self) -> None:
        self.mundo.clear_database()
        pygame.quit()

    # ─────────────── Carga de configuración ───────────────
    def _cargar_json_window(self) -> None:
        cfg_path = pathlib.Path("assets/cfg/window.json")
        try:
            with cfg_path.open(encoding="utf-8") as f:
                self.window_cfg = json.load(f)
        except FileNotFoundError:
            # Defaults razonables
            self.window_cfg = {
                "title": "SPACE AVIATOR",
                "size": {"w": 448, "h": 512},
                "bg_color": {"r": 0, "g": 0, "b": 0},
                "framerate": 60,
            }
            print("⚠️  window.json no encontrado; usando valores por defecto.")
