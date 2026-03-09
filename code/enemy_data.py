ENEMY_DATA = {
    "bat": {
        "path": "bat_character",
        "animation_steps": {'idle': 4, 'fly_left': 4, 'fly_up': 4, 'fly_right': 4, 'death': 11},
        "animation_speeds": {'idle': 0.15, 'fly_left': 0.15, 'fly_up': 0.15, 'fly_right': 0.15, 'death': 0.15},
        "speed": (2,3),
        "scale": 1.5
    },
    "ghost": { #add new enemy types here, and make sure to update the path to the folder the animations are in
        "path": "ghost_character",
        "animation_steps": {'idle': 6, 'fly_left': 6, 'fly_up': 6, 'fly_right': 6, 'death': 8},
        "speed": (1.5,2.5),
        "scale": 1.8
    }
}
ENEMY_TYPES = {
    '0' : 'bat',
    '1':'ghost',
}