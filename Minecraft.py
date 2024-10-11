# Import the Ursina library and other required modules
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random
import math

# Initialize Perlin noise
noise = PerlinNoise(octaves=3, seed=random.randint(1, 1000000))

# Create an instance of the Ursina app
app = Ursina()

# Define initial game variables
selected_block = "grass"  # Set the default block type to grass

# Create the player (FirstPersonController)
player = FirstPersonController(
    mouse_sensitivity=Vec2(100, 100),
    position=(0, 5, 0)
)

# Define the textures for each block type
block_textures = {
    "grass": load_texture("grass.png"),
    "dirt": load_texture("dirt.png"),
    "stone": load_texture("stone.png"),
    "bedrock": load_texture("bedrock.png")
}

# Block class for creating block entities
class Block(Entity):
    def __init__(self, position, block_type):
        super().__init__(
            position=position,
            model="cube",  # Using a "cube" model for the block
            scale=1,
            origin_y=-0.5,
            texture=block_textures.get(block_type),
            collider="box"
        )
        self.block_type = block_type

# Hand class for the player's hand
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='cube',
            scale=(0.2, 0.3),
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.4, -0.4),
            texture='white_cube',
            color=color.lime
        )

    def active(self):
        self.position = Vec2(0.1, -0.5)
        self.rotation = Vec3(90, -10, 0)

    def passive(self):
        self.rotation = Vec3(150, -10, 0)
        self.position = Vec2(0.4, -0.4)

# Rain class to simulate rain with blue cubes
class Rain(Entity):
    def __init__(self, count=100):
        super().__init__()
        self.rain_drops = []
        for _ in range(count):
            drop = Entity(
                model='cube',
                scale=(0.1, 0.1, 0.1),
                color=color.blue,
                position=Vec3(random.uniform(-10, 10), random.uniform(10, 20), random.uniform(-10, 10))
            )
            self.rain_drops.append(drop)

    def update(self):
        for drop in self.rain_drops:
            drop.y -= time.dt * 10  # Make the drops fall down
            if drop.y < 0:  # Reset position when hitting the ground
                drop.position = Vec3(random.uniform(-10, 10), random.uniform(10, 20), random.uniform(-10, 10))

# Create the world using Perlin noise
min_height = -5
for x in range(-10, 10):
    for z in range(-10, 10):
        height = noise([x * 0.02, z * 0.02])
        height = math.floor(height * 7.5)
        for y in range(height, min_height - 1, -1):
            if y == min_height:
                block = Block((x, y, z), "bedrock")
            elif y == height:
                block = Block((x, y, z), "grass")
            elif height - y > 2:
                block = Block((x, y, z), "stone")
            else:
                block = Block((x, y, z), "dirt")

# Handle input for placing and removing blocks
def input(key):
    global selected_block
    # Place a block
    if key == 'right mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            block = Block(hit_info.entity.position + hit_info.normal, selected_block)
    # Remove a block (except bedrock)
    if key == 'left mouse down' and mouse.hovered_entity:
        if not mouse.hovered_entity.block_type == "bedrock":
            destroy(mouse.hovered_entity)
    # Change block type selection
    if key == '1':
        selected_block = "grass"
    if key == '2':
        selected_block = "dirt"
    if key == '3':
        selected_block = "stone"


def update():
    if held_keys['right mouse'] or held_keys['left mouse']:
        hand.active()
    else:
        hand.passive()

    rain.update()  # Update rain movement

hand = Hand()

# Create the rain
rain = Rain()

# Additional settings
player.position = Vec3(0, 15, 0)
window.fullscreen = True
Sky(color=color.gray)

# Run the app
app.run()
