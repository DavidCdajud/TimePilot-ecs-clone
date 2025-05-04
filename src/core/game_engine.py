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


# …
# ── Prefabs ─────────────────────────────────────────────────────
from create.prefabs_creator import create_player_plane, create_cloud


# ────────────────────────────────────────────────────────────────
class GameEngine:
    """Bucle principal – TimePilot ECS."""

    def __init__(self) -> None:
        self._cargar_json_window()
        pygame.init()

        # Ventana
        w, h = self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]
        pygame.display.set_caption(self.window_cfg.get("title", "SPACE AVIATOR"))
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

    # ╭────────────────── Loop principal ───────────────────╮
    def run(self) -> None:
        self.mundo = esper.World()
        self._crear_prefabs()

        self.activo = True
        while self.activo:
            self._calcular_tiempo()
            self._procesar_eventos()
            self._actualizar()
            self._dibujar()

        self._limpiar()
    # ╰──────────────────────────────────────────────────────╯

    # ───────────────── Prefabs iniciales ──────────────────
    def _crear_prefabs(self) -> None:
        """
        Crea los prefabs iniciales:
        1) Jugador
        2) Horizon de nubes (fila continua abajo)
        3) Spawner dinámico de nubes (arriba, aleatorias)
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
                move_threshold= 50.0 
            )
)


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

        # 0) Spawner de nubes basado en movimiento — pasamos camera_pos, no delta
        player_tr = self.mundo.component_for_entity(self.player_ent, Transform)
        camera_pos = (player_tr.pos[0], player_tr.pos[1])
        sistema_spawner_nubes(self.mundo, camera_pos)

        # 1) Leer input y actualizar velocidades
        sistema_input_player(self.mundo, self.delta)

        # 2) Movimiento según Velocity
        sistema_movimiento(self.mundo, self.delta)

        # 3) Animaciones (avión + nubes)
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
