ENEMY_DATA = {
    "bat": {
        "path": "bat_character",
        "class": "flying",
        "animation_steps": {'idle': 4, 'fly_left': 4, 'fly_up': 4, 'fly_right': 4, 'death': 11},
        "animation_speeds": {'idle': 0.15, 'fly_left': 0.15, 'fly_up': 0.15, 'fly_right': 0.15, 'death': 0.15},
        'size': {'height': 32, 'width': 32},
        "sheets": {
            'idle':'bat_idle.png',
            'fly_left': 'flying_left.png',
            'fly_up': 'flying_up.png',
            'fly_right': 'flying_right.png',
            'death': 'bat_death.png'
            },
        "scale": 1.5,
        "stats": {"health": 50, 'damage': 7, 'attack_cooldown': 500, "speed": (2,3), "detection_radius": 350, "disengage_radius": 450},
    },
    "eye": {
        "path": "Flying_eye",
        "class": "flying",
        "animation_steps": {'idle': 8, 'fly_left': 8, 'attack': 8, 'hurt': 4, 'death': 4},
        "animation_speeds": {'idle': 0.15, 'fly_left': 0.15, 'attack': 0.15, 'hurt': 0.15, 'death': 0.15},
        'size': {'height': 150, 'width': 150},
        "sheets": {
            'idle':'Flight.png',
            'fly_left': 'Flight.png',
            'attack': 'Attack.png',
            'hurt': 'Hurt.png',
            'death': 'Death.png'
            },
        "scale": 1.5,
        "stats": {"health": 50, 'damage': 7, 'attack_cooldown': 500, "speed": (2,3), "detection_radius": 350, "disengage_radius": 450},
    },
    "orc": { 
        "path": "Orc",
        "class": "walking",
        "animation_steps": {'idle': 6, 'walk': 8, 'attack': 6, 'hurt': 4, 'death': 8},
        "animation_speeds": {'idle': 0.15, 'walk': 0.15, 'attack': 0.15,'hurt': 0.15, 'death': 0.10},
        'size': {'height': 100, 'width': 100},
        "sheets": {
            'idle':'Orc-Idle.png',
            'walk': 'Orc-Walk.png',
            'attack': 'Orc-Attack01.png',
            'hurt': 'Orc-Hurt.png',
            'death': 'Orc-Death.png'
            },
        "scale": 2,
        "stats": {"health": 70, 'damage': 8, 'attack_cooldown': 300, 'jump_height': -12, "speed": (2.5,3.5), "detection_radius": 350, "disengage_radius": 450},
        },

    "mushroom": { 
        "path": "Mushroom",
        "class": "walking",
        "animation_steps": {'idle': 4, 'walk': 7, 'attack': 7, 'hurt': 4, 'death': 4},
        "animation_speeds": {'idle': 0.15, 'walk': 0.15, 'attack': 0.2, 'hurt': 0.15, 'death': 0.10},
        'size': {'height': 150, 'width': 150},
        "sheets": {
            'idle':'Idle.png',
            'walk': 'Run.png',
            'attack': 'Attack.png',
            'hurt': 'hurt.png',
            'death': 'Death.png',
            },
        "scale": 1.5,
        "stats": {"health": 120, 'damage': 15, 'attack_cooldown': 700, 'jump_height': -10, "speed": (2,3), "detection_radius": 350, "disengage_radius": 450}
        },
        
    "skeleton": { 
        "path": "Skeleton",
        "class": "walking",
        "animation_steps": {'idle': 4, 'walk': 4, 'attack': 7, 'hurt': 4, 'death': 4},
        "animation_speeds": {'idle': 0.15, 'walk': 0.15, 'attack': 0.15, 'hurt': 0.15, 'death': 0.10},
        'size': {'height': 150, 'width': 150},
        "sheets": {
            'idle':'Idle.png',
            'walk': 'Walk.png',
            'attack': 'Attack.png',
            'hurt': 'hurt.png',
            'death': 'Death.png',
            },
        "scale": 1,
        "stats": {"health": 80, 'damage': 10, 'attack_cooldown': 500, 'jump_height': -11, "speed": (2.5,3.5), "detection_radius": 350, "disengage_radius": 450}
        },
        "skeleton_sewer": { 
        "path": "skeleton_sewer",
        "class": "walking",
        "animation_steps": {'idle': 4, 'walk': 12, 'attack': 7, 'hurt': 3, 'death': 13},
        "animation_speeds": {'idle': 0.15, 'walk': 0.15, 'attack': 0.15, 'hurt': 0.15, 'death': 0.10},
        'size': {'height': 64, 'width': 64},
        "sheets": {
            'idle':'idle.png',
            'walk': 'walk_right.png',
            'attack': 'attack.png',
            'hurt': 'hit.png',
            'death': 'death.png',
            },
        "scale": 1.5,
        "stats": {"health": 80, 'damage': 15, 'attack_cooldown': 500, 'jump_height': -11, "speed": (2.5,3.5), "detection_radius": 350, "disengage_radius": 450}
        },
    "hell_boss": {
        "path": "hell_boss",
        "class": "walking",
        "animation_steps": {'idle': 6, 'walk': 12, 'attack': 15, 'hurt': 5, 'death': 22},
        "animation_speeds": {'idle': 0.15, 'walk': 0.15, 'attack': 0.15, 'hurt': 0.15, 'death': 0.10},
        'size': {'height': 150, 'width': 150},
        "sheets": {
            'idle': 'Idle.png',
            'walk': 'Walk.png',
            'attack': 'Attack.png',
            'hurt': 'hurt.png',
            'death': 'Death.png',
        },
        "scale": 1,
        "stats": {"health": 80, 'damage': 10, 'attack_cooldown': 500, 'jump_height': -11, "speed": (2.5, 3.5),
                  "detection_radius": 350, "disengage_radius": 450}
    },
        }


ENEMY_TYPES = {
    '0': 'bat',
    '1': 'orc',
    '2': 'mushroom',
    '3': 'skeleton',
    '4': 'skeleton_sewer',
    '9':'hell_boss',
}