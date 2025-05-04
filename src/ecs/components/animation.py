from dataclasses import dataclass

@dataclass
class Animation:
    frames: int                # número total de cuadros en el sheet (fila única)
    frame_duration: float      # segundos por cuadro
    index: int = 0             # fotograma actual
    timer: float = 0.0         # acumulador interno
