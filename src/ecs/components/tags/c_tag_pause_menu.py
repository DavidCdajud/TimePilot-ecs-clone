from dataclasses import dataclass

@dataclass
class CTagPauseMenu:
    """Marca entidades pertenecientes al menú de pausa."""
    pass

@dataclass
class CMenuOption:
    text: str
    pos: tuple[int,int]
    index: int

@dataclass
class CMenuSelected:
    selected_index: int = 0
