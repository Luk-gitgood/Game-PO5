from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MUSIC_PATH = BASE_DIR.parent / 'sounds' / 'music'
SFX_PATH = BASE_DIR.parent / 'sounds' / 'sfx'


#Game Setup
BASE_SCREEN_HEIGHT = 720
BASE_SCREEN_WIDTH = 1280

TILE_SIZE = 32

WORLD_WIDTH = 48*32
WORLD_HEIGHT = 32*32
BOTTOM_LAYER = 32*3 + 16

IMAGE_WIDTH = 32
IMAGE_HEIGHT = 32

#UI
PLAYER_BAR_HEIGHT = 20
PLAYER_HEALTH_BAR_WIDTH = 200
UI_FONT_SIZE = 18
UI_FONT = None

ENEMY_BAR_HEIGHT = 5
ENEMY_BAR_WIDTH = 30
BAR_OFFSET_Y = 10

UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = "#e8b923"
HEALTH_COLOR = 'red'

#Weapons
weapon_data = {
    'revolver': {
        'speed': 12,
        'bullet_count': 1,
        'spread': 0,
        'lifetime': 1000,
        'damage': 15,
        'cooldown': 400
    },
    'shotgun': {
        'speed': 10,
        'bullet_count': 5,
        'spread': 15,
        'lifetime': 400,
        'damage': 5,
        'cooldown': 800
    }
}