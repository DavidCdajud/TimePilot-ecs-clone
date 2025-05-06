# src/ecs/systems/s_enemy_ai.py

import pygame
import esper
from ecs.components.transform      import Transform
from ecs.components.velocity       import Velocity
from ecs.components.enemy_ai       import EnemyAI
from ecs.components.tags.c_tag_enemy  import CTagEnemy
from ecs.components.tags.c_tag_player import CTagPlayer

def sistema_enemy_ai(world: esper.World, delta: float) -> None:
    # 1) Encuentra al jugador por su tag
    jugadores = list(world.get_component(CTagPlayer))
    if not jugadores:
        return
    player_ent, _ = jugadores[0]

    # 2) Saca su transform (ahora sí existen!)
    player_tr = world.component_for_entity(player_ent, Transform)
    player_pos = pygame.Vector2(player_tr.pos)

    # 3) Debug: cuantos con AI hay
    # ai_ents = [e for e,_ in world.get_component(EnemyAI)]
    # print(f"[DEBUG AI] entidades con EnemyAI: {ai_ents}")

    # 4) Ajusta cada enemigo
    for ent, (tr, vel, ai) in world.get_components(Transform, Velocity, EnemyAI):
        if not world.has_component(ent, CTagEnemy):
            continue
        to_player = player_pos - pygame.Vector2(tr.pos)
        if to_player.length_squared() > 0:
            dir = to_player.normalize()
            vel.vx = dir.x * ai.speed
            vel.vy = dir.y * ai.speed
