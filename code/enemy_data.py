ENEMY_DATA = {
    "bat": {
        "path": "bat_character",
        "animation_steps": {'idle': 4, 'fly_left': 4, 'fly_up': 4, 'fly_right': 4, 'death': 11},
        "animation_speeds": {'idle': 0.15, 'fly_left': 0.15, 'fly_up': 0.15, 'fly_right': 0.15, 'death': 0.15},
        "sheets": {
            'idle':'bat_idle.png',
            'fly_left': 'flying_left.png',
            'fly_up': 'flying_up.png',
            'fly_right': 'flying_right.png',
            'death': 'bat_death.png'
            },
        "scale": 1.5,
        "stats": {"health": 50, 'damage': 10, 'attack_cooldown': 500, "speed": (2,3), "detection_radius": 350, "disengage_radius": 450}

    },
    "orc": { #add new enemy types here, and make sure to update the path to the folder the animations are in
        "path": "Orc/Orc",
        "animation_steps": {'idle': 6, 'walk': 8, 'attack': 6, 'hurt': 4, 'death': 8},
        "animation_speeds": {'idle': 0.15, 'walk': 0.15, 'attack': 0.15,'hurt': 0.15, 'death': 0.10},
        "sheets": {
            'idle':'Orc-Idle.png',
            'walk': 'Orc-Walk.png',
            'attack': 'Orc-Attack01.png',
            'hurt': 'Orc-Hurt.png',
            'death': 'Orc-Death.png'
            },
        "scale": 2,
        "stats": {"health": 100, 'damage': 10, 'attack_cooldown': 500, 'jump_height': -12, "speed": (2.5,3.5), "detection_radius": 450, "disengage_radius": 550}
        }
        }


ENEMY_TYPES = {
    '0' : 'bat',
    '1':'ghost',
}