from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

#Game Setup
BASE_SCREEN_HEIGHT = 720
BASE_SCREEN_WIDTH = 1280

TILE_SIZE = 32

WORLD_WIDTH = 48*32
WORLD_HEIGHT = 32*32
BOTTOM_LAYER = 32*3 + 16

IMAGE_WIDTH = 32
IMAGE_HEIGHT = 32

#Weapons
weapon_data = {
    'revolver': {
        'speed': 32,
        'bullet_count': 1,
        'spread': 0,
        'lifetime': 1000,
        'damage': 10,
        'cooldown': 400
    },
    'shotgun': {
        'speed': 10,
        'bullet_count': 5,
        'spread': 15,
        'lifetime': 400,
        'damage': 6,
        'cooldown': 800
    }
}