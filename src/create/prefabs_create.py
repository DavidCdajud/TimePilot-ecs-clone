# src/create/prefab_creator.py
from ecs.components.transform import Transform
from ecs.components.velocity import Velocity
from ecs.components.sprite    import Sprite
from ecs.components.animation import Animation
from ecs.components.player_input import PlayerInput
from ecs.components.bullet    import Bullet
from ecs.components.collider  import Collider
from ecs.components.health    import Health


def create_player(world, cfg):
    spawn = cfg["player_spawn"]
    ent = world.create_entity()
    world.add_component(ent, Transform((spawn["x"], spawn["y"])))
    world.add_component(ent, Velocity())
    world.add_component(ent, Sprite("player_sheet", 16, 16))
    world.add_component(ent, Animation(32, 0.08))
    world.add_component(ent, PlayerInput())
    return ent

def create_bullet(world, pos, speed=300):
    ent = world.create_entity()
    world.add_component(ent, Transform(pos))
    world.add_component(ent, Velocity(vx=0, vy=-speed))
    world.add_component(ent, Sprite("player_bullet", 4, 8))
    world.add_component(ent, Bullet(owner="player"))
    world.add_component(ent, Collider(radius=2))
    return ent

def create_enemy(world, pos):
    ent = world.create_entity()
    world.add_component(ent, Transform(pos))
    world.add_component(ent, Velocity())
    world.add_component(ent, Sprite("enemy_01", 16, 16))
    world.add_component(ent, Animation(32, 0.08))
    world.add_component(ent, Collider(radius=8))
    world.add_component(ent, Health(1))
    return ent
