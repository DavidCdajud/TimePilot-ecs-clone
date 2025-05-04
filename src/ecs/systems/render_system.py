import pygame
from esper import Processor

from ecs.components.transform import Transform
from ecs.components.sprite import Sprite
from ecs.components.animation import Animation
from core.service_locator import ServiceLocator


class RenderSystem(Processor):
    def __init__(self, surface: pygame.Surface) -> None:
        self._surface = surface
        self._rm = ServiceLocator.get("resources")  # ResourceManager

    # ------------------------------------------------------------------
    def process(self, dt: float) -> None:
        # 1) limpiar pantalla (temporalmente negro)
        self._surface.fill((0, 0, 0))

        # 2) dibujar cada entidad con Sprite
        for ent, (tr, sp) in self.world.get_components(Transform, Sprite):
            sheet = self._rm.image(sp.sheet_id)

            # --- Índice de fotograma (0 si no hay Animation) ---
            anim = (
                self.world.component_for_entity(ent, Animation)
                if self.world.has_component(ent, Animation)
                else None
            )
            frame_idx = anim.index if anim else 0

            # --- Cálculo robusto de fila y columna --------------------
            cols = sheet.get_width() // sp.frame_w      # cuadros por fila
            if cols == 0:       # seguridad por si frame_w > ancho sheet
                continue

            row = frame_idx // cols
            col = frame_idx % cols

            # Verifica que no se salga
            if (row + 1) * sp.frame_h > sheet.get_height():
                continue  # índice fuera de rango: no dibuja y evita crash

            frame_rect = pygame.Rect(
                col * sp.frame_w,
                row * sp.frame_h,
                sp.frame_w,
                sp.frame_h,
            )

            frame = sheet.subsurface(frame_rect)
            self._surface.blit(frame, frame.get_rect(center=tr.pos))
